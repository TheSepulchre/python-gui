import sys
# Inject a themed QApplication subclass so the rest of the module can keep using
# "from PySide6.QtWidgets import QApplication" unchanged while getting a light
# modern theme with blue accents applied automatically.
import PySide6.QtWidgets as _qtwidgets
from PySide6.QtGui import QColor, QPalette

# Theme palette/colors
_THEME = {
    "bg": "#F4F8FF",         # main window background (very light)
    "panel": "#FFFFFF",      # cards / panels
    "text": "#0B2545",       # primary text (dark blue)
    "muted": "#546E86",      # secondary text
    "accent": "#1E5FB8",     # blue accent
    "border": "#E6EEF8",     # subtle borders
    "table_alt": "#F8FBFF",  # table alternate row
}

# Global stylesheet (light, modern, blue accents)
_GLOBAL_STYLESHEET = f"""
QMainWindow {{
    background-color: {_THEME["bg"]};
}}

QFrame#titlebar, QFrame {{
    background-color: {_THEME["panel"]};
    color: {_THEME["text"]};
}}

QLabel {{
    color: {_THEME["text"]};
}}

QPushButton {{
    background-color: transparent;
    color: {_THEME["text"]};
    border: 1px solid transparent;
    padding: 8px 10px;
    border-radius: 8px;
}}
QPushButton:hover {{
    background-color: rgba(30,95,184,0.08);
    border-color: {_THEME["border"]};
}}
QPushButton:pressed {{
    background-color: rgba(30,95,184,0.14);
}}

# Sidebar styling (applies to nav QFrame and its buttons)
QFrame {{
    /* default frame rules */
}}
QFrame[sidebar="true"] {{
    background-color: {_THEME["panel"]};
    border-right: 1px solid {_THEME["border"]};
}}
QFrame[sidebar="true"] QPushButton {{
    text-align: left;
    padding: 12px 18px;
    color: {_THEME["text"]};
    font-weight: 500;
}}
QFrame[sidebar="true"] QPushButton:hover {{
    background-color: rgba(30,95,184,0.08);
    color: {_THEME["accent"]};
}}

QTableWidget {{
    background-color: {_THEME["panel"]};
    color: {_THEME["text"]};
    gridline-color: {_THEME["border"]};
    selection-background-color: {_THEME["accent"]};
    selection-color: white;
}}
QHeaderView::section {{
    background-color: {_THEME["bg"]};
    color: {_THEME["muted"]};
    padding: 6px;
    border: 1px solid {_THEME["border"]};
}}

QStackedWidget {{
    background-color: transparent;
}}

QScrollBar:vertical, QScrollBar:horizontal {{
    background: transparent;
    width: 10px;
    height: 10px;
}}
QScrollBar::handle {{
    background: {_THEME["border"]};
    border-radius: 6px;
}}
QScrollBar::handle:hover {{
    background: {_THEME["muted"]};
}}
"""

class ThemedApplication(_qtwidgets.QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prefer Fusion for consistent rendering across platforms
        try:
            self.setStyle("Fusion")
        except Exception:
            pass

        # Set a light QPalette that matches the stylesheet
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(_THEME["bg"]))
        palette.setColor(QPalette.WindowText, QColor(_THEME["text"]))
        palette.setColor(QPalette.Base, QColor(_THEME["panel"]))
        palette.setColor(QPalette.AlternateBase, QColor(_THEME["table_alt"]))
        palette.setColor(QPalette.ToolTipBase, QColor(_THEME["panel"]))
        palette.setColor(QPalette.ToolTipText, QColor(_THEME["text"]))
        palette.setColor(QPalette.Text, QColor(_THEME["text"]))
        palette.setColor(QPalette.Button, QColor(_THEME["panel"]))
        palette.setColor(QPalette.ButtonText, QColor(_THEME["text"]))
        palette.setColor(QPalette.BrightText, QColor("#ffffff"))
        palette.setColor(QPalette.Highlight, QColor(_THEME["accent"]))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)

        # Apply global stylesheet
        self.setStyleSheet(_GLOBAL_STYLESHEET)


# Replace QApplication in PySide6.QtWidgets module so downstream "from ... import QApplication"
# picks up ThemedApplication automatically.
_qtwidgets.QApplication = ThemedApplication
import requests
from PySide6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QTableWidget, QTableWidgetItem, QMessageBox
)
class DataTable(QWidget):
    """
    A single table widget that can run any SQL query
    on-demand when a button is pressed.
    """
    def __init__(self, title="Data Viewer", endpoint="http://localhost:3000/query"):
        super().__init__()
        self.endpoint = endpoint

        # --- Layout setup ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title_label = QLabel(title)
        layout.addWidget(title_label)

        # Table
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Buttons row
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Add buttons with predefined queries
        self.buttons = {
            "Drumming": "SELECT TOP 10 * FROM dbo.batches",
            "Ewald": "SELECT TOP 10 * FROM dbo.ewald",
            "Convo": "SELECT TOP 10 * FROM dbo.convo",
            "Mixing": "SELECT TOP 10 * FROM dbo.Mixing",
        }

        for label, query in self.buttons.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, q=query: self.run_query(q))
            button_layout.addWidget(btn)

        button_layout.addStretch()

    def run_query(self, query: str):
        """Fetch data from the Node.js bridge and populate the table."""
        try:
            res = requests.post(self.endpoint, json={"query": query})
            res.raise_for_status()
            data = res.json()

            if not data:
                self.table.setRowCount(0)
                self.table.setColumnCount(1)
                self.table.setHorizontalHeaderLabels(["No data"])
                return

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


class TitleBar(QFrame):
    """Custom draggable title bar with buttons."""
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QLabel("Kongsberg Portal")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.btn_min = QPushButton("–")
        self.btn_close = QPushButton("×")
        self.btn_close.setObjectName("close")

        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_close)

        self.btn_min.clicked.connect(lambda: parent.showMinimized())
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
        #palette = QPalette()
        #palette.setColor(QPalette.Window, QColor("#EAEAEA"))
        #palette.setColor(QPalette.WindowText, Qt.black)
        #self.setPalette(palette)

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
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel(title)
        text_lbl = QLabel(text)
        text_lbl.setWordWrap(True)

        layout.addWidget(title_lbl)
        if title == "Production":
            # Each table is a unique instance with its own query
            self.data_table = DataTable("Database Browser")
            layout.addWidget(self.data_table)
        layout.addWidget(text_lbl)
        return page


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec())
