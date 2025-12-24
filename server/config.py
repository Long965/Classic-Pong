# server/config.py
"""
Server configuration
"""
from shared.constants import *

class ServerConfig:
    # Network settings
    HOST = HOST
    PORT = PORT
    MAX_CLIENTS = 10
    BUFFER_SIZE = BUFFER_SIZE
    
    # Game settings
    GAME_FPS = FPS
    ROOM_TIMEOUT = 300  # 5 minutes
    
    # Logging
    LOG_CONNECTIONS = True
    LOG_GAME_EVENTS = True
    
    @staticmethod
    def get_server_info():
        """Get server info string"""
        return f"""
╔════════════════════════════════════════╗
║     CLASSIC PONG - SERVER CONFIG      ║
╠════════════════════════════════════════╣
║ Host: {ServerConfig.HOST:<31}║
║ Port: {ServerConfig.PORT:<31}║
║ Max Clients: {ServerConfig.MAX_CLIENTS:<23}║
║ Game FPS: {ServerConfig.GAME_FPS:<26}║
╚════════════════════════════════════════╝
"""