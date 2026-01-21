# shared/protocol.py
"""
Protocol giao tiếp giữa client và server
"""
import json
from shared.constants import *

class Message:
    @staticmethod
    def create(msg_type, data=None):
        """Tạo message để gửi"""
        message = {
            'type': msg_type,
            'data': data or {}
        }
        return json.dumps(message).encode('utf-8')
    
    @staticmethod
    def parse(raw_data):
        """Parse message nhận được"""
        try:
            message = json.loads(raw_data.decode('utf-8'))
            return message['type'], message.get('data', {})
        except:
            return None, None
    
    @staticmethod
    def connect():
        """Client gửi yêu cầu kết nối"""
        return Message.create(MSG_CONNECT)
    
    @staticmethod
    def ready():
        """Client báo sẵn sàng chơi"""
        return Message.create(MSG_READY)
    
    @staticmethod
    def game_state(state):
        """Server gửi game state"""
        return Message.create(MSG_GAME_STATE, state.to_dict())
    
    @staticmethod
    def input_data(move_up, move_down):
        """Client gửi input"""
        return Message.create(MSG_INPUT, {
            'move_up': move_up,
            'move_down': move_down
        })
    
    @staticmethod
    def disconnect():
        """Thông báo disconnect"""
        return Message.create(MSG_DISCONNECT)
    
    @staticmethod
    def wait():
        """Server báo chờ player 2"""
        return Message.create(MSG_WAIT, {'message': 'Waiting for another player...'})
    
    @staticmethod
    def player_id(player_id):
        """Server gửi player ID"""
        return Message.create(MSG_PLAYER_ID, {'id': player_id})
    
    @staticmethod
    def game_over(winner):
        """Thông báo game over"""
        return Message.create(MSG_GAME_OVER, {'winner': winner})
    
    @staticmethod
    def play_again():
        """Client muốn chơi lại"""
        return Message.create(MSG_PLAY_AGAIN)
    
    @staticmethod
    def restart():
        """Server restart game"""
        return Message.create(MSG_RESTART)
    
    @staticmethod
    def ai_mode(difficulty="medium"):
        """Client yêu cầu chơi với AI"""
        return Message.create(MSG_AI_MODE, {'difficulty': difficulty})