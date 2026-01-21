classic_pong_multiplayer/
│
├── server/
│   ├── __init__.py
│   ├── game_server.py          # Server chính quản lý kết nối
│   ├── game_logic.py            # Logic game (ball, paddle physics)
│   ├── room_manager.py          # Quản lý phòng chơi
│   └── config.py                # Cấu hình server
│
├── client/
│   ├── __init__.py
│   ├── game_client.py           # Client chính kết nối server
│   ├── network_handler.py       # Xử lý mạng
│   ├── renderer.py              # Vẽ graphics với Pygame
│   ├── input_handler.py         # Xử lý input từ người chơi
│   └── ui.py                    # Menu, scoreboard
│
├── shared/
│   ├── __init__.py
│   ├── protocol.py              # Protocol giao tiếp client-server
│   ├── constants.py             # Hằng số game (kích thước, tốc độ)
│   └── models.py                # Data models (Ball, Paddle, GameState)
│
├── assets/
│   ├── fonts/
│   └── sounds/
│
├── requirements.txt
├── README.md
└── run_server.py

TV1: phụ trách server & shared
TV2: phụ trách client

## HƯỚNG DẪN THAM GIA TRÒ CHƠI CLASSIC PONG
# BƯỚC 1:
    - Cài đặt các thư viện có trong file requirments.txt
# Bước 2:
    - Mở 1 terminal chạy server
    - python run_server.py
# Bước 3:
    - Mở 1 terminal nếu chơi chế độ 1 mình với AI
    - Mở 2 terminal nếu muốn chơi chế độ solo player vs player
    - Run client bằng cách python run_client.py