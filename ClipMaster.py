import sys
import pyperclip
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QPen, QCursor

clipboard_history = []

class ClipboardThread(QThread):
    new_clipboard = pyqtSignal(str)
    
    def run(self):
        last_copied = ""
        while True:
            try:
                copied_text = pyperclip.paste().strip()
                if copied_text and copied_text != last_copied:
                    self.new_clipboard.emit(copied_text)
                    last_copied = copied_text
                    time.sleep(0.5)
                time.sleep(1)
            except Exception as e:
                print(f"Clipboard error: {e}")
                time.sleep(1)

class ClipboardGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = None  
        self.initUI()
        pyperclip.copy("")  
        self.clipboard_thread = ClipboardThread(self)
        self.clipboard_thread.new_clipboard.connect(self.add_to_history)
        self.clipboard_thread.start()

    def initUI(self):
      
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(200, 200, 400, 500)

        main_layout = QVBoxLayout()

        title = QLabel("Clipboard Manager", self)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: white;
            text-shadow: 0 0 5px blue;
            background-color: rgba(0, 0, 0, 150);
            padding: 5px;
            border-radius: 5px;
        """)
        main_layout.addWidget(title)

        self.history_text = QTextEdit(self)
        self.history_text.setReadOnly(True)
        self.history_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 150);
                color: white;
                border: 2px solid blue;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        self.history_text.setFont(QFont("Arial", 12))
        self.update_cursor() 
        self.history_text.textChanged.connect(self.update_cursor)  
        main_layout.addWidget(self.history_text)

        btn_layout = QHBoxLayout()

        clear_btn = QPushButton("Clear History", self)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 150);
                border: 2px solid blue;
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(30, 144, 255, 200);
            }
        """)
        clear_btn.clicked.connect(self.clear_history)
        btn_layout.addWidget(clear_btn)

        stop_btn = QPushButton("Stop Manager", self)
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 150);
                border: 2px solid blue;
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 69, 0, 200);
            }
        """)
        stop_btn.clicked.connect(self.stop_manager)
        btn_layout.addWidget(stop_btn)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self.animation_radius = 30
        self.animation_step = 2
        QTimer(self, timeout=self.update_animation).start(50)

    def update_cursor(self):
      
        if self.history_text.toPlainText().strip():
            self.history_text.setCursor(QCursor(Qt.IBeamCursor))
        else:
            self.history_text.setCursor(QCursor(Qt.ArrowCursor))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor(30, 144, 255, 200), 2))
        center_x, center_y = self.width() // 2, self.height() // 2
        painter.drawEllipse(center_x - self.animation_radius, center_y - self.animation_radius, 
                            self.animation_radius * 2, self.animation_radius * 2)

    def update_animation(self):
        self.animation_radius += self.animation_step
        if self.animation_radius >= 40 or self.animation_radius <= 20:
            self.animation_step = -self.animation_step
        self.update()

    def add_to_history(self, text):
        if text not in clipboard_history and text.strip():
            clipboard_history.insert(0, text)
            current_text = self.history_text.toPlainText()
            if current_text:
                new_text = f"{text}\n{' ' * 20}\n{current_text}"
            else:
                new_text = text
            self.history_text.setPlainText(new_text)
            print(f"New Copy: {text}")

    def clear_history(self):
        clipboard_history.clear()
        self.history_text.clear()
        print("Clipboard history cleared.")

    def stop_manager(self):
        if hasattr(self, 'clipboard_thread'):
            self.clipboard_thread.terminate()
            self.clipboard_thread.wait()
            print("\nClipboard Manager Stopped.")
            print("Clipboard History:")
            for i, text in enumerate(clipboard_history, 1):
                print(f"{i}. {text}")
        QApplication.quit()

def main():
    app = QApplication(sys.argv)
    window = ClipboardGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
