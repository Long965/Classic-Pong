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
        self.status = "DISCONNECTED" # Các trạng thái: DISCONNECTED, CONNECTING, WAITING, PLAYING, ENDED
        self.winner = None
        
        # Bộ giải mã JSON hỗ trợ tách gói tin bị dính (Sticky Packets)
        self.decoder = json.JSONDecoder()
        
        # Lưu trạng thái phím bấm gần nhất để tránh spam server
        self.last_input = (None, None) 

    def connect(self):
        """Thiết lập kết nối tới Server"""
        try:
            print(f"🔄 Đang kết nối tới {HOST}:{PORT}...")
            self.client.connect((HOST, PORT))
            
            # [QUAN TRỌNG] Đặt trạng thái CONNECTING ngay lập tức
            # Để GameLoop biết là đang bận xử lý, không tự out ra Menu
            self.status = "CONNECTING"
            
            # Gửi tin nhắn chào hỏi
            self.client.send(Message.connect())
            
            # Bắt đầu luồng nhận tin nhắn ngầm
            thread = threading.Thread(target=self._receive_loop, daemon=True)
            thread.start()
            return True
            
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            self.status = "DISCONNECTED"
            return False

    def _receive_loop(self):
        """Vòng lặp nhận dữ liệu liên tục (Xử lý Stream)"""
        buffer = "" # Bộ đệm chứa chuỗi JSON chưa hoàn chỉnh
        
        while True:
            try:
                chunk = self.client.recv(BUFFER_SIZE)
                if not chunk:
                    print("⚠️ Server đã đóng kết nối.")
                    self.status = "DISCONNECTED"
                    break
                
                # Cộng dồn dữ liệu vào bộ đệm
                buffer += chunk.decode('utf-8')
                
                # Xử lý cắt chuỗi JSON trong bộ đệm
                while buffer:
                    buffer = buffer.lstrip() # Xóa khoảng trắng thừa
                    if not buffer:
                        break
                        
                    try:
                        # raw_decode giúp lấy ra 1 JSON hợp lệ và vị trí kết thúc
                        obj, index = self.decoder.raw_decode(buffer)
                        
                        # Lấy thông tin tin nhắn
                        msg_type = obj.get('type')
                        data = obj.get('data')
                        
                        # Xử lý tin nhắn
                        if msg_type:
                            self._handle_message(msg_type, data)
                        
                        # Cắt phần đã xử lý, giữ lại phần thừa cho vòng lặp sau
                        buffer = buffer[index:]
                        
                    except json.JSONDecodeError:
                        # Dữ liệu chưa đủ 1 JSON -> Đợi recv tiếp
                        break
                        
            except ConnectionResetError:
                print("⚠️ Mất kết nối đột ngột.")
                self.status = "DISCONNECTED"
                break
            except Exception as e:
                print(f"🔥 Lỗi hệ thống: {e}")
                self.status = "DISCONNECTED"
                break

    def _handle_message(self, msg_type, data):
        """Phân loại và xử lý tin nhắn từ Server"""
        
        if msg_type == MSG_PLAYER_ID:
            self.player_id = data.get('id')
            print(f"✅ Đã kết nối! ID của bạn: {self.player_id}")
            # Khi mới vào, tạm thời chuyển sang WAITING để chờ đối thủ
            self.status = "WAITING"

        elif msg_type == MSG_WAIT:
            self.status = "WAITING"
            print("⏳ Đang chờ người chơi thứ 2...")

        elif msg_type == MSG_READY:
            self.status = "PLAYING"
            print("🎮 Trận đấu bắt đầu!")

        elif msg_type == MSG_GAME_STATE:
            if data:
                # Nhận tọa độ -> Chắc chắn là đang chơi
                self.status = "PLAYING"
                self.current_game_state = data

        elif msg_type == MSG_GAME_OVER:
            self.status = "ENDED"
            self.winner = data.get('winner')
            print(f"🏁 Kết thúc! Người thắng: Player {self.winner}")

    def send_input(self, move_up, move_down):
        """
        Gửi phím điều khiển.
        [TỐI ƯU] Chỉ gửi khi trạng thái phím thay đổi để giảm tải Server.
        """
        if self.status != "PLAYING":
            return

        # So sánh input hiện tại với input lần trước gửi
        if (move_up, move_down) != self.last_input:
            try:
                msg = Message.input_data(move_up, move_down)
                self.client.send(msg)
                
                # Cập nhật lại input cuối cùng
                self.last_input = (move_up, move_down)
            except Exception as e:
                print(f"❌ Lỗi gửi input: {e}")