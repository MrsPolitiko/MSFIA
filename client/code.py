import sys
import socket
import threading
import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.dirname(os.path.dirname(sys.executable)) + r'\Lib\site-packages\PyQt5\Qt5\plugins'
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTextEdit, QLineEdit, QHBoxLayout, QSlider, QLabel)
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QSoundEffect


class ChatClient(QMainWindow):
    def __init__(self, host='127.0.0.1', port=5555):
        super().__init__()
        self.host = host
        self.port = port
        self.client_socket = None
        self.receive_thread = None

        self.init_ui()
        self.init_audio()
        self.connect_to_server()

    def init_ui(self):
        self.setWindowTitle('Корпоративный чат')
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        self.message_display.setAcceptRichText(True)
        layout.addWidget(self.message_display)

        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_input)

        control_layout = QHBoxLayout()
        self.volume_label = QLabel("Громкость уведомлений:")
        control_layout.addWidget(self.volume_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        control_layout.addWidget(self.volume_slider)

        layout.addLayout(control_layout)

    def init_audio(self):
        self.sound_effect = QSoundEffect()
        self.sound_effect.setSource(QUrl.fromLocalFile("notification.wav"))
        self.sound_effect.setVolume(0.5)
        # Добавляем таймер для проверки завершения воспроизведения
        self.sound_timer = QTimer()
        self.sound_timer.timeout.connect(self.check_sound_status)
        self.sound_timer.start(100)  # Проверяем каждые 100 мс

    def check_sound_status(self):
        # Если звук закончил играть, останавливаем таймер
        if not self.sound_effect.isPlaying():
            self.sound_timer.stop()

    def set_volume(self, value):
        volume = value / 100
        self.sound_effect.setVolume(volume)

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
            self.display_message("[*] Подключено к серверу", is_system=True)

            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
        except Exception as e:
            self.display_message(f"[!] Ошибка подключения: {str(e)}", is_system=True)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    # Проверяем, является ли сообщение системным (от сервера)
                    if message.startswith("[Сервер]"):
                        self.display_message(message, is_system=True)
                    else:
                        self.display_message(message)
                    self.play_notification_sound()
            except Exception as e:
                self.display_message(f"[!] Ошибка соединения: {str(e)}", is_system=True)
                self.client_socket.close()
                break

    def display_message(self, message, is_system=False, is_my_message=False):
        if is_system:
            self.message_display.append(f"<span style='color:gray'>{message}</span>")
        elif is_my_message:
            self.message_display.append(f"<span style='color:blue; font-weight:600'>Вы: {message}</span>")
        else:
            self.message_display.append(message)

    def play_notification_sound(self):
        if self.sound_effect.isLoaded():
            # Если звук уже играет, останавливаем его перед повторным воспроизведением
            if self.sound_effect.isPlaying():
                self.sound_effect.stop()
            self.sound_effect.play()
            self.sound_timer.start()  # Запускаем таймер проверки

    def send_message(self):
        message = self.message_input.text()
        if message.lower() == 'exit':
            self.client_socket.close()
            self.close()
        elif message:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.display_message(message, is_my_message=True)
                self.message_input.clear()
            except Exception as e:
                self.display_message(f"[!] Ошибка отправки: {str(e)}", is_system=True)

    def closeEvent(self, event):
        if self.client_socket:
            self.client_socket.close()
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if len(sys.argv) > 2:
        chat = ChatClient(sys.argv[1], int(sys.argv[2]))
    else:
        chat = ChatClient()

    chat.show()
    sys.exit(app.exec_())