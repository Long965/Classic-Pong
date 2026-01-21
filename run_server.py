#!/usr/bin/env python3
# run_server.py
"""
Script chạy server
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.game_server import GameServer
from server.config import ServerConfig

def main():
    """Main entry point"""
    print(ServerConfig.get_server_info())
    
    server = GameServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n⚠️ Server interrupted by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
    finally:
        server.stop()

if __name__ == "__main__":
    main()