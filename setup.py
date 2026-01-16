import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFileDialog, QMessageBox, QMenu, QDialog, QComboBox, QLineEdit,
    QGraphicsDropShadowEffect, QFrame, QListWidget, QListWidgetItem, QToolButton,
    QGraphicsBlurEffect
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QSettings, QPropertyAnimation, QEasingCurve, QEvent, QRect
from PyQt6.QtGui import QFont, QAction
from gui import SetupWizard
from main import LogApp


class NavigationPane(QFrame):
    fileDoubleClicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.setMinimumWidth(0)  # Start hidden
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        label = QLabel("Recent Files:")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(label)
        
        self.list_widget = QListWidget()
        item_font = QFont("Arial", 14)
        self.list_widget.setFont(item_font)
        self.list_widget.setSpacing(10)
        layout.addWidget(self.list_widget)
        
        # Load recent files from QSettings (for demonstration)
        settings = QSettings("MyCompany", "LogDocumentationSystem")
        recent_files = settings.value("recent_files", [])
        if not isinstance(recent_files, list):
            recent_files = [recent_files] if recent_files else []
        for file_path in recent_files:
            filename = os.path.basename(file_path)
            item = QListWidgetItem(filename)
            item.setToolTip(file_path)
            self.list_widget.addItem(item)
            
        # Connect double-click signal to our handler.
        self.list_widget.itemDoubleClicked.connect(self.handle_item_double_clicked)
        
    def handle_item_double_clicked(self, item: QListWidgetItem):
        # Retrieve the full file path from the tooltip.
        file_path = item.toolTip()
        # Emit the custom signal with the full file path.
        self.fileDoubleClicked.emit(file_path)

# A simple clickable label for the hamburger icon.
class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Create a shadow effect that will serve as our "border"
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)  # start with no blur (no glow)
        self.shadow.setColor(Qt.GlobalColor.blue)  # choose your border/glow color
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)
        
        # Animation for the shadow's blur radius
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(300)
        
        
    def mousePressEvent(self, event):
        # emit the signal so external code can connect, or allow assignment to .clicked
        try:
            self.clicked.emit()
        except Exception:
            pass
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(15)  # Adjust this value to control the "thickness" of the glow
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(event)


# Minimal clickable label for text-only clickable elements.
class AnimatedClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)    
        
        # Create a shadow effect that will serve as our "border"
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)  # start with no blur (no glow)
        self.shadow.setColor(Qt.GlobalColor.blue)  # choose your border/glow color
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)
        
        # Animation for the shadow's blur radius
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(300)
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(15)  # Adjust this value to control the "thickness" of the glow
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(event)

# SetupWindow: used when creating a new project.
class SetupWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  # Increase spacing between widgets
        
        layout.addWidget(QLabel("Log Type:"))
        self.log_type_combo = QComboBox()
        self.log_type_combo.addItems(["General", "Debugging"])
        layout.addWidget(self.log_type_combo)
        
        layout.addWidget(QLabel("User Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        layout.addWidget(QLabel("PDF Title:"))
        self.pdf_title_input = QLineEdit()
        layout.addWidget(self.pdf_title_input)
        
        # Instead of buttons, use clickable text for OK/Cancel.
        self.ok_label = AnimatedClickableLabel("OK")
        self.ok_label.setStyleSheet("color: blue; text-decoration: underline; margin: 10px;")
        self.ok_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ok_label.clicked.connect(self.accept)
        layout.addWidget(self.ok_label)
        
        self.cancel_label = AnimatedClickableLabel("Cancel")
        self.cancel_label.setStyleSheet("color: blue; text-decoration: underline; margin: 10px;")
        self.cancel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cancel_label.clicked.connect(self.reject)
        layout.addWidget(self.cancel_label)

    def get_setup_data(self):
        return {
            "log_type": self.log_type_combo.currentText(),
            "user_name": self.name_input.text().strip(),
            "pdf_title": self.pdf_title_input.text().strip(),
        }

# WelcomeWindow: initial launcher window with a large hamburger icon and clickable text links.
class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to LDS")
        self.resize(800, 450)
        self.setFixedSize(800, 450)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.central_widget = central_widget
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create the navigation pane as a child of central_widget so it can overlay content.
        # Make the nav pane a frameless subwindow child so it overlays content
        self.nav_pane = NavigationPane(self.central_widget)
        self.nav_pane.setWindowFlags(
            self.nav_pane.windowFlags()
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.SubWindow
        )
        # Start hidden with width 0 using geometry (do not use setFixedWidth/setMaximumWidth)
        self.nav_pane.setMinimumWidth(0)
        self.nav_pane.setGeometry(0, 0, 0, self.central_widget.height())
        self.nav_pane.fileDoubleClicked.connect(self.open_logs)
        # ensure it is on top when shown
        self.nav_pane.raise_()
        self.nav_pane.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.nav_pane.move(0, 0)
        self.nav_pane.show()

        # Create main content area.
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content_widget, 0)

        # Top bar with hamburger icon.
        top_bar = QHBoxLayout()
        self.hamburger_label = ClickableLabel("☰")
        font = QFont()
        font.setPointSize(26)
        self.hamburger_label.setFont(font)
        self.hamburger_label.setStyleSheet("margin: 10px; padding: 5px; border-radius: 5px;")
        # Connect the hamburger click event to toggle navigation pane.
        self.hamburger_label.clicked.connect(self.toggle_nav_pane)
        top_bar.addWidget(self.hamburger_label, alignment=Qt.AlignmentFlag.AlignLeft)
        top_bar.addStretch()
        content_layout.addLayout(top_bar)

        # Title label
        title_label = QLabel("WELCOME TO LDS")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Inter SemiBold", 34, QFont.Weight.Bold))
        title_label.setStyleSheet("color: black; margin-top: 0px; margin-bottom: 30px;")
        content_layout.addWidget(title_label)

        # Clickable text for actions.
        self.create_new_label = AnimatedClickableLabel("Create New Project")
        self.create_new_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.create_new_label.setFont(QFont("Arial", 18))
        self.create_new_label.setStyleSheet("""margin-right: 250px;
            margin-left: 250px;
            margin-bottom: 5px;
            padding: 10px;
            border-radius: 15px;
        """)
        self.create_new_label.clicked.connect(self.create_new_project)
        content_layout.addWidget(self.create_new_label)

        self.open_project_label = AnimatedClickableLabel("Open Project")
        self.open_project_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.open_project_label.setFont(QFont("Arial", 18))
        self.open_project_label.setStyleSheet("""
            margin-right: 290px;
            margin-left: 290px;
            margin-bottom: 5px;
            padding: 10px;
            border-radius: 15px;
        """)
        self.open_project_label.clicked.connect(self.open_project)
        content_layout.addWidget(self.open_project_label)

        self.docs_label = AnimatedClickableLabel("Documentations")
        self.docs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.docs_label.setFont(QFont("Arial", 18))
        self.docs_label.setStyleSheet("""
            margin-right: 270px;
            margin-left: 270px;
            margin-bottom: 5px;
            padding: 10px;
            border-radius: 15px;
        """)
        self.docs_label.clicked.connect(self.open_documentations)
        content_layout.addWidget(self.docs_label)

        content_layout.addStretch()

        # Flag to track if nav pane is open.
        self.nav_open = False

        self.central_widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if (
            obj == self.central_widget
            and self.nav_open
            and event.type() == QEvent.Type.MouseButtonPress
        ):
            # Ignore clicks on the hamburger label
            if self.hamburger_label.geometry().contains(event.position().toPoint()):
                return False
            # Check if click is outside nav_pane
            if not self.nav_pane.geometry().contains(event.position().toPoint()):
                self.toggle_nav_pane()
                return True  # Eat the event
        return super().eventFilter(obj, event)

    def show_recent_menu(self):
        # Load recent projects from QSettings.
        settings = QSettings("MyCompany", "LogDocumentationSystem")
        recent_files = settings.value("recent_files", [])
        if not isinstance(recent_files, list):
            recent_files = [recent_files] if recent_files else []

        # Create a QMenu and add recent file actions.
        menu = QMenu()
        for file_path in recent_files:
            action = QAction(file_path, self)
            action.triggered.connect(lambda checked, path=file_path: self.open_logs(path))
            menu.addAction(action)
        # Show the menu just below the hamburger icon.
        menu.exec(self.hamburger_label.mapToGlobal(QPoint(0, self.hamburger_label.height())))

    def create_new_project(self):
        wizard = SetupWizard(self)
        if wizard.exec() == QDialog.DialogCode.Accepted:
            setup_data = wizard.get_setup_data()
            # Prompt for project folder
            folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
            if not folder:
                return
            config_folder = os.path.join(folder, "config")
            os.makedirs(config_folder, exist_ok=True)
            config_path = os.path.join(config_folder, "user_config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(setup_data, f, indent=4)
            setup_data["file_path"] = None
            self.launch_main_app(setup_data)

    def open_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "LDS Files (*.lds *.ldsg *.ldsd)"
        )
        if file_path:
            setup_data = self.get_setup_data_for_file(file_path)
            self.launch_main_app(setup_data)

    def open_logs(self, file_path):
        setup_data = self.get_setup_data_for_file(file_path)
        self.launch_main_app(setup_data)

    def get_setup_data_for_file(self, file_path):
        # Determine log type by extension
        if file_path.endswith("ldsg"):
            log_mode = "General"
        elif file_path.endswith("ldsd"):
            log_mode = "Debugging"
        else:
            log_mode = "General"
        # Locate user_config.json in the same project folder
        project_folder = os.path.dirname(file_path)
        config_path = os.path.join(project_folder, "config", "user_config.json")
        user_name = ""
        pdf_title = "Log Documentation"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    user_name = config.get("user_name", "")
                    pdf_title = config.get("pdf_title", "Log Documentation")
            except Exception:
                pass
        return {
            "file_path": file_path,
            "log_type": log_mode,
            "user_name": user_name,
            "pdf_title": pdf_title,
        }

    def open_documentations(self):
        QMessageBox.information(self, "Documentation", "Documentation goes here...")

    def launch_main_app(self, setup_data):
        from main import LogApp  # Import your LogApp class

        file_path = setup_data.get("file_path", None)
        # Create LogApp with mode and file_path parameters.
        self.main_window = LogApp(
            log_mode=setup_data.get("log_type", "General"), file_path=file_path
        )

        # Optionally pass other settings like user name and PDF title
        self.main_window.user_name = setup_data.get("user_name", "")
        self.main_window.pdf_title = setup_data.get("pdf_title", "Log Documentation")

        self.main_window.show()
        self.close()

    def toggle_nav_pane(self):
        # Animate the geometry of the overlay navigation pane so it slides over content
        start_rect = self.nav_pane.geometry()
        if start_rect.isNull() or start_rect.width() == 0:
            # ensure we have a valid starting rect anchored to the central widget
            start_rect = QRect(0, 0, 0, self.central_widget.height())
        end_width = 300 if not self.nav_open else 0
        end_rect = QRect(0, 0, end_width, self.central_widget.height())

        self.animation = QPropertyAnimation(self.nav_pane, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        # ensure it's on top when opening
        if not self.nav_open:
            self.nav_pane.raise_()
            self.nav_pane.show()
        self.animation.start()

        # hide the pane after the close animation finishes
        self.animation.finished.connect(
            lambda: (
                self.nav_pane.hide() if self.nav_pane.geometry().width() == 0 else None
            )
        )

        # Change the hamburger icon if needed.
        if not self.nav_open:
            self.hamburger_label.setText("X")  # Change icon to "X" when open.
            font = QFont()
            font.setPointSize(26)  # Set a smaller font size
            font.setBold(True)  # Make it bold
            self.hamburger_label.setFont(font)
        else:
            self.hamburger_label.setText("☰")  # Change back to hamburger.

        self.nav_open = not self.nav_open

    def resizeEvent(self, a0):
        # keep nav_pane stretched vertically and pinned to the left of central widget
        try:
            w = self.central_widget.width()
            h = self.central_widget.height()
            # nav_pane anchored at left; width is controlled by animation (maxWidth)
            self.nav_pane.setFixedHeight(h)
            self.nav_pane.move(0, 0)
        except Exception:
            pass
        super().resizeEvent(a0)


def main():
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
