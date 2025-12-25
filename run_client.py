# run_client.py
from client.game_client import PongClient

if __name__ == "__main__":
    # Khởi tạo đối tượng từ Class PongClient
    client = PongClient()
    # Gọi phương thức run() của Class đó
    client.run()