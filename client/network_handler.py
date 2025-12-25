import socket
import threading
import json
from shared.constants import HOST, PORT, BUFFER_SIZE, MSG_PLAYER_ID, MSG_GAME_STATE, MSG_WAIT, MSG_GAME_OVER, MSG_READY
from shared.protocol import Message

class NetworkHandler:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_id = None
        self.current_game_state = None
        self.status = "DISCONNECTED"
        self.winner = None
        # Bộ giải mã JSON hỗ trợ cắt chuỗi
        self.decoder = json.JSONDecoder()

    def connect(self):
        """Thiết lập kết nối"""
        try:
            self.client.connect((HOST, PORT))
            self.client.send(Message.connect())
            
            thread = threading.Thread(target=self._receive_loop, daemon=True)
            thread.start()
            return True
        except Exception as e:
            print(f"❌ Lỗi kết nối Server: {e}")
            return False

    def _receive_loop(self):
        """
        Vòng lặp nhận tin thông minh:
        Tự động tách các gói tin bị dính vào nhau (Sticky Packets)
        """
        buffer = "" # Bộ đệm chứa dữ liệu chưa xử lý
        
        while True:
            try:
                # 1. Nhận dữ liệu thô
                chunk = self.client.recv(BUFFER_SIZE)
                if not chunk:
                    print("⚠️ Server đã đóng kết nối.")
                    self.status = "DISCONNECTED"
                    break
                
                # 2. Cộng dồn vào bộ đệm
                buffer += chunk.decode('utf-8')
                
                # 3. Vòng lặp cắt và xử lý từng JSON trong bộ đệm
                while buffer:
                    buffer = buffer.lstrip() # Xóa khoảng trắng thừa đầu dòng
                    if not buffer:
                        break
                        
                    try:
                        # raw_decode giúp lấy ra 1 JSON hợp lệ và vị trí kết thúc của nó
                        obj, index = self.decoder.raw_decode(buffer)
                        
                        # Lấy thông tin từ object JSON vừa tách được
                        msg_type = obj.get('type')
                        data = obj.get('data')
                        
                        if msg_type:
                            # In log trừ tin nhắn GAME_STATE (để đỡ rác màn hình)
                            if msg_type != MSG_GAME_STATE:
                                print(f"📩 Đã tách tin nhắn: {msg_type}")
                            self._handle_message(msg_type, data)
                        
                        # Cắt phần đã xử lý khỏi bộ đệm, giữ lại phần thừa (nếu có) cho vòng lặp sau
                        buffer = buffer[index:]
                        
                    except json.JSONDecodeError:
                        # Nếu dữ liệu chưa đủ để tạo thành JSON hoàn chỉnh, đợi recv tiếp
                        break
                        
            except ConnectionResetError:
                print("⚠️ Mất kết nối đột ngột.")
                break
            except Exception as e:
                print(f"🔥 Lỗi hệ thống: {e}")
                break

    def _handle_message(self, msg_type, data):
        """Xử lý logic game"""
        if msg_type == MSG_PLAYER_ID:
            self.player_id = data.get('id')
            print(f"✅ ID nhận được: {self.player_id}")

        elif msg_type == MSG_WAIT:
            self.status = "WAITING"
            print("⏳ Đang chờ người chơi khác...")

        elif msg_type == MSG_READY:
            self.status = "PLAYING"
            print("🎮 Trận đấu bắt đầu! Sẵn sàng nhận tọa độ...")

        elif msg_type == MSG_GAME_STATE:
            if data:
                self.status = "PLAYING"
                self.current_game_state = data
                # Debug nhẹ để biết tọa độ có về không
                # print(f"Ball: {data.get('ball', {}).get('x')}") 

        elif msg_type == MSG_GAME_OVER:
            self.status = "ENDED"
            self.winner = data.get('winner')
            print(f"🏁 Người thắng: Player {self.winner}")

    def send_input(self, move_up, move_down):
        """Gửi input"""
        if self.status != "PLAYING": return
        try:
            msg = Message.input_data(move_up, move_down)
            self.client.send(msg)
        except:
            pass