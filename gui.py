import sys
import requests
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QTableWidget, QTableWidgetItem, QMessageBox
)


class DataWidget(QWidget):
    """
    A reusable widget that queries data from your Node bridge
    and displays it in a table.
    """
    def __init__(self, title: str, query: str, endpoint="http://localhost:4000/query", refresh_secs=0):
        super().__init__()
        self.title = title
        self.query = query
        self.endpoint = endpoint
        self.refresh_secs = refresh_secs

        # --- Layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel(f"🧭 {title}")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        self.refresh_btn = QPushButton("⟳ Refresh")
        self.refresh_btn.setFixedWidth(100)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border-radius: 8px;
                padding: 6px;
            }
            QPushButton:hover { background-color: #444; }
        """)
        self.refresh_btn.clicked.connect(self.refresh_data)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1f1f1f;
                color: white;
                border: 1px solid #333;
                gridline-color: #333;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #ddd;
                padding: 4px;
            }
        """)
        layout.addWidget(self.table)

        # Optional auto-refresh
        if refresh_secs > 0:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.refresh_data)
            self.timer.start(refresh_secs * 1000)

        self.refresh_data()

    def refresh_data(self):
        """Fetch data from the Node.js bridge and populate the table."""
        try:
            res = requests.post(self.endpoint, json={"query": self.query})
            res.raise_for_status()
            data = res.json()

            if not data:
                self.table.setRowCount(0)
                self.table.setColumnCount(1)
                self.table.setHorizontalHeaderLabels(["No data returned"])
                return

            # Fill the table
            columns = list(data[0].keys())
            self.table.setColumnCount(len(columns))
            self.table.setRowCount(len(data))
            self.table.setHorizontalHeaderLabels(columns)

            for row_idx, row in enumerate(data):
                for col_idx, col_name in enumerate(columns):
                    val = str(row[col_name])
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{e}")
            print(f"[Error] {e}")


class Dashboard(QWidget):
    """
    Example dashboard that uses multiple DataWidget instances.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Dashboard")
        self.setStyleSheet("background-color: #121212; color: white;")
        self.resize(1200, 800)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Example widgets (change queries as needed)
        widget1 = DataWidget("Drumming", "SELECT TOP 10 * FROM dbo.batches")
        widget2 = DataWidget("Ewald", "SELECT TOP 10 * FROM dbo.ewald")
        widget3 = DataWidget("Convo", "SELECT TOP 10 * FROM dbo.convo")

        layout.addWidget(widget1)
        layout.addWidget(widget2)
        layout.addWidget(widget3)

class TitleBar(QFrame):
    """Custom draggable title bar with buttons."""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QFrame {
                background-color: #181818;
                border-bottom: 1px solid #333;
            }
            QLabel {
                color: white;
                font-size: 16px;
                padding-left: 10px;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
                width: 40px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
            }
            QPushButton#close:hover {
                background-color: #b00020;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QLabel("Kongsberg Portal")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.btn_min = QPushButton("–")
        # self.btn_max = QPushButton("□")
        self.btn_close = QPushButton("×")
        self.btn_close.setObjectName("close")

        layout.addWidget(self.btn_min)
        # layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

        self.btn_min.clicked.connect(lambda: parent.showMinimized())
        # self.btn_max.clicked.connect(self.toggle_max_restore)
        self.btn_close.clicked.connect(lambda: parent.close())

        self.start_pos = QPoint()
        self.is_dragging = False

    def toggle_max_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPosition().toPoint()
            self.is_dragging = True

    def mouseMoveEvent(self, event):
        if self.is_dragging and not self.parent.isMaximized():
            diff = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.pos() + diff)
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False


class AnimatedStack(QStackedWidget):
    """Stacked widget with slide transition animation."""
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
        self.setWindowTitle("Kongsberg Portal")
        self.setWindowFlags(Qt.FramelessWindowHint)  # remove default title bar
        self.showMaximized()

        # Dark theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#121212"))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)

        # Main layout
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Title Bar ---
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        # --- Central Layout (Sidebar + Pages) ---
        central = QWidget()
        central_layout = QHBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Sidebar navigation
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

        self.btn_home = QPushButton("Home")
        self.btn_production = QPushButton("Production")
        self.btn_logistics = QPushButton("Logistics")
        self.btn_settings = QPushButton("Settings")

        nav_layout.addWidget(self.btn_home)
        nav_layout.addWidget(self.btn_production)
        nav_layout.addWidget(self.btn_logistics)
        nav_layout.addWidget(self.btn_settings)
        nav_layout.addStretch()

        # --- Pages ---
        self.stack = AnimatedStack()
        home = self.make_page("Home", "Welcome to your full-screen modern Python app!")
        production = self.make_page("Production", "Production data and analytics will be shown here.")
        logistics = self.make_page("Logistics", "Logistics management and tracking information.")
        settings = self.make_page("Settings", "You can customize preferences here.")

        self.stack.addWidget(home)
        self.stack.addWidget(production)
        self.stack.addWidget(logistics)
        self.stack.addWidget(settings)

        # --- Connect buttons ---
        self.btn_home.clicked.connect(lambda: self.stack.setCurrentIndexAnimated(0))
        self.btn_production.clicked.connect(lambda: self.stack.setCurrentIndexAnimated(1))
        self.btn_logistics.clicked.connect(lambda: self.stack.setCurrentIndexAnimated(2))
        self.btn_settings.clicked.connect(lambda: self.stack.setCurrentIndexAnimated(3))

        # Combine sidebar + pages
        central_layout.addWidget(nav)
        central_layout.addWidget(self.stack)
        main_layout.addWidget(central)

        self.setCentralWidget(container)

    def make_page(self, title, text):
        """Creates a simple content page."""
        mySql = Dashboard()
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        text_lbl = QLabel(text)
        text_lbl.setStyleSheet("font-size: 18px; color: #bbbbbb;")
        text_lbl.setWordWrap(True)

        layout.addWidget(title_lbl)
        layout.addWidget(mySql)
        layout.addWidget(text_lbl)
        return page


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec())
