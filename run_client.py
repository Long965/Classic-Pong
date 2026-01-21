#!/usr/bin/env python3
# run_client.py
"""
Script chạy client
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Thử import class mới trước, nếu không có thì dùng class cũ
try:
    from client.game_client import GameClient
    
    if __name__ == "__main__":
        client = GameClient()
        try:
            client.run()
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            print("\n👋 Thanks for playing!")
            
except ImportError:
    # Fallback: dùng class PongClient từ code cũ
    from client.game_client import PongClient
    
    if __name__ == "__main__":
        client = PongClient()
        client.run()