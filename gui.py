import sys
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QHBoxLayout, QStackedWidget, QFrame
)
from PySide6.QtGui import QPalette, QColor


class AnimatedStack(QStackedWidget):
    """Stacked widget with slide transition animation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.setDuration(400)

    def setCurrentIndexAnimated(self, index):
        if index == self.currentIndex():
            return

        current_rect = self.geometry()
        direction = 1 if index > self.currentIndex() else -1

        # start animation
        next_rect = QRect(current_rect)
        next_rect.moveLeft(current_rect.width() * direction)

        self.widget(index).setGeometry(next_rect)
        self.widget(index).show()

        self.anim.stop()
        self.anim.setStartValue(next_rect)
        self.anim.setEndValue(current_rect)
        self.anim.start()

        self.setCurrentIndex(index)


class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Python UI Example")
        self.showFullScreen()

        # Dark palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#121212"))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)

        # --- Layout ---
        container = QWidget()
        main_layout = QHBoxLayout(container)

        # Left navigation panel
        nav = QFrame()
        nav.setFixedWidth(220)
        nav.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
            QPushButton {
                color: white;
                border: none;
                text-align: left;
                padding: 15px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
            }
        """)

        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(0, 40, 0, 0)

        # Navigation buttons
        self.btn_home = QPushButton("🏠 Home")
        self.btn_settings = QPushButton("⚙️ Settings")
        self.btn_about = QPushButton("ℹ️ About")
        nav_layout.addWidget(self.btn_home)
        nav_layout.addWidget(self.btn_settings)
        nav_layout.addWidget(self.btn_about)
        nav_layout.addStretch()

        # --- Pages ---
        self.stack = AnimatedStack()

        home = self.make_page("Home", "Welcome to the modern Python app!")
        settings = self.make_page("Settings", "Here you can change your preferences.")
        about = self.make_page("About", "Created with ❤️ using PySide6.")

        self.stack.addWidget(home)
        self.stack.addWidget(settings)
        self.stack.addWidget(about)

        # Button actions
        self.btn_home.clicked.connect(lambda: self.stack.setCurrentIndexAnimated(0))
        self.btn_settings.clicked.connect(lambda: self.stack.setCurrentIndexAnimated(1))
        self.btn_about.clicked.connect(lambda: self.stack.setCurrentIndexAnimated(2))

        # --- Combine ---
        main_layout.addWidget(nav)
        main_layout.addWidget(self.stack)
        self.setCentralWidget(container)

    def make_page(self, title, text):
        """Creates a simple page layout"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")

        text_lbl = QLabel(text)
        text_lbl.setStyleSheet("font-size: 18px; color: #bbbbbb;")
        text_lbl.setWordWrap(True)

        layout.addWidget(title_lbl)
        layout.addWidget(text_lbl)
        return page


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec())