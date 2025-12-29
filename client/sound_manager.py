# client/sound_manager.py
import pygame
import os

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        
        # Khởi tạo mixer
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize sound system: {e}")
            self.enabled = False
            return

        # Đường dẫn thư mục âm thanh
        # Lưu ý: Bạn cần tạo thư mục assets/sounds và chép file .wav vào nếu muốn có tiếng
        self.sound_dir = os.path.join("assets", "sounds")
        
        # Danh sách các âm thanh cần load
        self.sound_files = {
            'paddle_hit': 'hit.wav',
            'wall_hit': 'wall.wav',
            'score': 'score.wav',
            'game_over': 'game_over.wav'
        }
        
        self._load_sounds()

    def _load_sounds(self):
        """Load các file âm thanh nếu tồn tại"""
        if not self.enabled: return

        if not os.path.exists(self.sound_dir):
            # Nếu chưa có thư mục thì thôi, không báo lỗi
            return

        for name, filename in self.sound_files.items():
            path = os.path.join(self.sound_dir, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(0.4) # Âm lượng 40%
                except:
                    pass

    def play(self, name):
        """Phát âm thanh an toàn"""
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass