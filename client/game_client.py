# client/game_client.py
"""
Client chính - Main game loop
"""
import time
from client.network_handler import NetworkHandler
from client.renderer import Renderer
from client.input_handler import InputHandler
from client.ui import UI
from shared.constants import *

class GameClient:
    def __init__(self):
        self.network = NetworkHandler()
        self.renderer = Renderer()
        self.input_handler = InputHandler()
        self.ui = UI()
        self.running = True
        self.game_started = False
        self.player_id = None
        self.waiting_for_restart = False
        
        # Setup callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Setup network callbacks"""
        self.network.set_callback(MSG_PLAYER_ID, self._on_player_id)
        self.network.set_callback(MSG_WAIT, self._on_wait)
        self.network.set_callback(MSG_READY, self._on_ready)
        self.network.set_callback(MSG_GAME_STATE, self._on_game_state)
        self.network.set_callback(MSG_GAME_OVER, self._on_game_over)
        self.network.set_callback(MSG_DISCONNECT, self._on_disconnect)
        self.network.set_callback(MSG_RESTART, self._on_restart)
    
    def _on_player_id(self, player_id):
        """Callback khi nhận player ID"""
        self.player_id = player_id
    
    def _on_wait(self):
        """Callback khi phải chờ"""
        self.ui.set_screen("waiting")
    
    def _on_ready(self):
        """Callback khi game ready"""
        print("🎮 Starting game now!")
        self.game_started = True
        self.ui.set_screen("playing")
        # Send ready confirmation to server
        self.network.send_ready()
    
    def _on_game_state(self, game_state):
        """Callback khi nhận game state"""
        pass  # Handled in main loop
    
    def _on_game_over(self, winner):
        """Callback khi game over"""
        self.game_started = False
        result = self.ui.show_game_over(winner, self.player_id)
        
        if result == "play_again":
            # Gửi yêu cầu chơi lại
            self.network.send_play_again()
            self.waiting_for_restart = True
            self.ui.set_screen("waiting_restart")
        elif result == "exit":
            self.running = False
    
    def _on_disconnect(self):
        """Callback khi disconnect"""
        self.running = False
        self.ui.show_disconnected()
    
    def _on_restart(self):
        """Callback khi restart game"""
        print("🎮 Game restarted!")
        self.game_started = True
        self.waiting_for_restart = False
        self.ui.set_screen("playing")
    
    def run(self):
        """Main game loop"""
        try:
            # Show main menu
            choice = self.ui.show_main_menu()
            
            if choice == "exit":
                self.cleanup()
                return
            
            # Handle menu choice
            ai_mode = False
            ai_difficulty = "medium"
            
            if choice == "ai_mode":
                # Show difficulty menu
                difficulty = self.ui.show_ai_difficulty_menu()
                if difficulty is None:  # Back button
                    self.run()  # Restart menu
                    return
                ai_mode = True
                ai_difficulty = difficulty
            
            # Connect to server
            self.ui.show_connecting()
            if not self.network.connect(ai_mode=ai_mode, ai_difficulty=ai_difficulty):
                print("❌ Failed to connect to server")
                self.cleanup()
                return
            
            # Main loop
            while self.running and self.network.is_connected():
                self.input_handler.process_events()
                
                # Check quit
                if self.input_handler.should_quit():
                    break
                
                # Handle different states
                if self.ui.current_screen == "waiting":
                    self.renderer.draw_waiting()
                    self.renderer.update()
                
                elif self.ui.current_screen == "waiting_restart":
                    self.renderer.draw_waiting_restart()
                    self.renderer.update()
                
                elif self.ui.current_screen == "playing" and self.game_started:
                    # Send input
                    move_up, move_down = self.input_handler.get_movement()
                    self.network.send_input(move_up, move_down)
                    
                    # Render game
                    game_state = self.network.get_game_state()
                    if game_state:
                        self.renderer.draw_game(game_state, self.player_id)
                        self.renderer.update()
                
                # Small delay to prevent CPU overload
                time.sleep(0.001)
        
        except Exception as e:
            print(f"❌ Error in game loop: {e}")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n🧹 Cleaning up...")
        self.network.disconnect()
        self.renderer.quit()
        print("✅ Cleanup complete")


def main():
    """Entry point"""
    print("🎮 Classic Pong - Multiplayer Client")
    print("=" * 40)
    print("Controls:")
    print("  - W/Arrow Up: Move paddle up")
    print("  - S/Arrow Down: Move paddle down")
    print("  - ESC: Exit game")
    print("=" * 40)
    
    client = GameClient()
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        print("\n👋 Thanks for playing!")


if __name__ == "__main__":
    main()