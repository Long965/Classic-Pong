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

