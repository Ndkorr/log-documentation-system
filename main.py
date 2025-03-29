from PyQt6.QtWidgets import QMenu, QDialog, QProgressDialog, QMenuBar, QLabel, QColorDialog, QApplication, QLineEdit, QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QListWidget, QInputDialog, QFileDialog, QMessageBox, QComboBox
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QSettings, QTimer, QThread, pyqtSignal, QEvent, QPoint
from PyQt6.QtGui import QColor, QFont, QBrush, QShortcut, QKeySequence, QAction, QTextDocument
from datetime import datetime
import sys
import psutil
import json
import wmi
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlShutdown
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import os
import subprocess
import re
import random
import string
import names


class DictionaryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dictionary")
        self.setGeometry(100, 100, 700, 450)

        self.main_layout = QHBoxLayout()
        
        # Keyword List
        self.keyword_list = QListWidget(self)
        self.add_static_item("Keywords")  # Add static title
        self.keyword_list.itemClicked.connect(self.display_definition)
        self.keyword_list.setFixedWidth(200)  # Set minimum width for keyword list
        self.main_layout.addWidget(self.keyword_list)
        
        # Definition Section
        self.definition_layout = QVBoxLayout()
        self.definition_list = QListWidget(self)
        self.definition_layout.addWidget(self.definition_list)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_keyword)
        self.button_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("Delete", self)
        self.delete_button.clicked.connect(self.delete_keyword)
        self.button_layout.addWidget(self.delete_button)
        
        self.definition_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.definition_layout)
        
        self.setLayout(self.main_layout)
        self.dictionary = {}  # Store definitions
        
        self.center()

    def add_list_item(self, word):
        item_widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel(word)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(label)
        layout.setContentsMargins(5, 2, 5, 2)
        item_widget.setLayout(layout)
        
        list_item = QListWidgetItem(word)
        list_item.setSizeHint(item_widget.sizeHint())
        
        self.keyword_list.addItem(list_item)
        
    
    def add_static_item(self, text):
        """ Adds a non-clickable, non-deletable item to the list """
        static_item = QListWidgetItem(text)
        static_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Disable interactions
        static_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)  # Center text
        static_item.setBackground(QBrush(QColor(220, 220, 220)))
        static_item.setFont(QLabel().font())  # Use default font
        static_item.setForeground(QBrush(QColor(0, 0, 0)))  # Black text color
        static_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))  # Bold font
        static_item.setData(Qt.ItemDataRole.UserRole, "static")  # Mark as static
        self.keyword_list.addItem(static_item)  # Add to list
        
    def add_keyword(self):
        # Prompt user for a keyword
        word, ok = QInputDialog.getText(self, "Add Keyword", "Enter new keyword:")
    
        if ok and word.strip():  # Ensure input is not empty
            word = word.strip()

            # Check if keyword already exists
            if word in self.dictionary:
                QMessageBox.warning(self, "Duplicate Keyword", "This keyword already exists!")
                return

            # Prompt user for a definition
            definition, ok_def = QInputDialog.getText(self, "Add Definition", f"Enter definition for '{word}':")
        
            if ok_def and definition.strip():
                definition = definition.strip()

                # Store in dictionary
                self.dictionary[word] = definition

                # Add keyword visually
                self.add_list_item(word)

                # Auto-select new item
                self.select_keyword(word)
    
    def select_keyword(self, word):
        """Find and select the keyword in the list."""
        for i in range(self.keyword_list.count()):
            item = self.keyword_list.item(i)
            if item and item.text() == word:
                self.keyword_list.setCurrentRow(i)
                self.display_definition(self.keyword_list.item(i))
                break
            
    def delete_keyword(self):
        """Delete the selected keyword and its definition."""
        selected_item = self.keyword_list.currentItem()
        if selected_item:
            word = selected_item.text()
            if word in self.dictionary:
                del self.dictionary[word]  # Remove the keyword from the dictionary
            self.keyword_list.takeItem(self.keyword_list.row(selected_item))  # Remove the item from the list
            self.definition_list.clear()  # Clear the definition area

    def display_definition(self, item):
        """Display the definition of the selected keyword."""
        word = item.text()  # Get the keyword text from the clicked item
        definition = self.dictionary.get(word, "No definition available.")  # Fetch the definition

        # Clear previous definitions
        self.definition_list.clear()

        # Create a custom widget with QLabel to display the formatted text
        item_widget = QWidget()
        layout = QVBoxLayout()

        title_label = QLabel(f"<b>{word}:</b>")  # Styled title with the keyword
        text_label = QLabel(definition)
        text_label.setWordWrap(True)  # Allow multiline text
        
        # Adjust font size for the definition text
        font = QFont()
        font.setPointSize(11)  # Set the desired font size
        text_label.setFont(font)

        layout.addWidget(title_label)
        layout.addWidget(text_label)
        layout.setContentsMargins(5, 2, 5, 2)

        item_widget.setLayout(layout)

        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())

        self.definition_list.addItem(list_item)
        self.definition_list.setItemWidget(list_item, item_widget)
        
    def center(self):
        """Center the dialog on the screen."""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())


class RestorePointWindow(QDialog):  # Change QWidget to QDialog
    def __init__(self, restore_points, parent=None):
        super().__init__(parent)
        self.restore_points = restore_points  # Store restore points
        self.initUI()
        self.parent_widget = parent

    def initUI(self):
        self.setWindowTitle("Restore Points")
        self.setGeometry(100, 100, 400, 300)
        
        self.main_layout = QVBoxLayout()  # Renamed to avoid conflict with QWidget.layout()
        
        # Restore Points List
        self.restore_list = QListWidget()
        self.restore_list.addItems(self.restore_points.keys())
        self.main_layout.addWidget(self.restore_list)
        
        # Buttons Layout
        self.buttons_layout = QHBoxLayout()

        # Expand Button
        self.expand_button = QPushButton("View Restore Point")
        self.expand_button.clicked.connect(self.expandView)
        self.buttons_layout.addWidget(self.expand_button)

        self.main_layout.addLayout(self.buttons_layout)
        
        # Log Widgets (Initially Hidden)
        self.log_container = QHBoxLayout()
        
        # Latest Logs (Non-editable)
        self.latest_logs = QTextEdit()
        self.latest_logs.setPlaceholderText("Latest Logs")
        self.latest_logs.setReadOnly(True)  # Make it non-editable
        
        # Restore Point Logs (Non-editable)
        self.restore_logs = QTextEdit()
        self.restore_logs.setPlaceholderText("Restore Point Logs")
        self.restore_logs.setReadOnly(True)  # Make it non-editable
        
        self.log_container.addWidget(self.latest_logs)
        self.log_container.addWidget(self.restore_logs)
        
        self.main_layout.addLayout(self.log_container)
        
        # Initially hide log containers
        self.latest_logs.setVisible(False)
        self.restore_logs.setVisible(False)
        
        self.setLayout(self.main_layout)
        
        # center the dialog
        self.center()

    def expandView(self):
        selected_item = self.restore_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select a restore point to view.")
            return

        restore_point_name = selected_item.text()
        restore_logs = self.restore_points.get(restore_point_name, [])

        # Display the restore point logs
        self.restore_logs.clear()  # Clear any existing text
        self.restore_logs.setHtml(f"<b>Restore Point</b><br>" + "<br>".join(restore_logs))  # Add label and use setHtml for rich text logs

        # Display the current logs from the main application
        if self.parent_widget:
            current_logs = []
            for i in range(self.parent_widget.log_list.count()):
                item = self.parent_widget.log_list.item(i)
                label = self.parent_widget.log_list.itemWidget(item)
                if isinstance(label, QLabel):
                    current_logs.append(label.text())  # Get the HTML text from QLabel
            self.latest_logs.clear()  # Clear any existing text
            self.latest_logs.setHtml(f"<b>Latest Logs</b><br>" + "<br>".join(current_logs))  # Use setHtml for rich text logs

        # Animate the horizontal expansion of the window
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        target_width = 800  # Target width for the expanded window
        target_geometry = QRect(
            (screen_geometry.width() - target_width) // 2,  # Center horizontally
            self.geometry().y(),  # Keep the current vertical position
            target_width,
            self.geometry().height()
        )

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)  # Animation duration in milliseconds
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(target_geometry)
        self.animation.finished.connect(self.showLogs)  # Show logs after animation
        self.animation.start()
        
        self.setWindowTitle(f"{restore_point_name}")  # Update title

    def showLogs(self):
        # Hide restore list and show logs
        self.restore_list.setVisible(False)
        self.latest_logs.setVisible(True)
        self.restore_logs.setVisible(True)

        # Add "Restore this Version" button
        self.restore_version_button = QPushButton("Restore this Version")
        self.restore_version_button.clicked.connect(self.restoreVersion)
        self.buttons_layout.addWidget(self.restore_version_button)

        self.expand_button.setText("Back")
        self.expand_button.clicked.disconnect()
        self.expand_button.clicked.connect(self.collapseView)

    def collapseView(self):
        # Animate the horizontal collapse of the window
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        default_width = 400  # Default width for the window
        target_geometry = QRect(
            (screen_geometry.width() - default_width) // 2,  # Center horizontally
            self.geometry().y(),  # Keep the current vertical position
            default_width,
            self.geometry().height()
        )

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(1000)  # Animation duration in milliseconds
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(target_geometry)
        self.animation.finished.connect(self.restoreDefaultView)  # Restore default view after animation
        self.animation.start()
        
        self.setWindowTitle("Restore Points")  # Update title

    def restoreDefaultView(self):
        # Show restore list and hide logs
        self.restore_list.setVisible(True)
        self.latest_logs.setVisible(False)
        self.restore_logs.setVisible(False)

        # Remove "Restore this Version" button
        if hasattr(self, 'restore_version_button'):
            self.buttons_layout.removeWidget(self.restore_version_button)
            self.restore_version_button.deleteLater()
            del self.restore_version_button

        self.expand_button.setText("View Restore Point")
        self.expand_button.clicked.disconnect()
        self.expand_button.clicked.connect(self.expandView)

    def restoreVersion(self):
        selected_item = self.restore_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select a restore point to restore.")
            return

        restore_point_name = selected_item.text()
        if self.parent_widget:
            self.parent_widget.restore_version(restore_point_name)
            QMessageBox.information(self, "Restore Successful", f"Restored to version: {restore_point_name}")
            self.close()  # Close the dialog after restoring

    def center(self):
        """Center the dialog on the screen."""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())
    

class LogTextEdit(QTextEdit):
    logSubmitted = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent  # Explicitly store the parent widget

    def keyPressEvent(self, event):
        print(f"keyPressEvent detected in LogTextEdit: {event.key()} with modifiers {event.modifiers()}")  # Debug log

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            print("Shift+Enter detected inside LogTextEdit!")  # Debug log
            self.logSubmitted.emit()
            event.accept()

        elif event.key() == Qt.Key.Key_S and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            print("Ctrl+S detected inside LogTextEdit!")  # Debug log
            if self.parent_widget:
                self.parent_widget.save_logs()
            event.accept()

        elif event.key() == Qt.Key.Key_Up and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) and self.parent_widget:
            # Move category up
            index = self.parent_widget.category_selector.currentIndex()
            if index > 0:
                self.parent_widget.category_selector.setCurrentIndex(index - 1)
            event.accept()  # Prevent default behavior (cursor movement)

        elif event.key() == Qt.Key.Key_Down and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) and self.parent_widget:
            # Move category down
            index = self.parent_widget.category_selector.currentIndex()
            if index < self.parent_widget.category_selector.count() - 1:
                self.parent_widget.category_selector.setCurrentIndex(index + 1)
            event.accept()  # Prevent default behavior (cursor movement)

        elif event.key() == Qt.Key.Key_Left and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) and self.parent_widget:
            # Move log type left
            index = self.parent_widget.log_type_selector.currentIndex()
            if index > 0:
                self.parent_widget.log_type_selector.setCurrentIndex(index - 1)
            event.accept()

        elif event.key() == Qt.Key.Key_Right and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) and self.parent_widget:
            # Move log type right
            index = self.parent_widget.log_type_selector.currentIndex()
            if index < self.parent_widget.log_type_selector.count() - 1:
                self.parent_widget.log_type_selector.setCurrentIndex(index + 1)
            event.accept()
        
        elif event.key() == Qt.Key.Key_Z and (event.modifiers() & Qt.KeyboardModifier.ControlModifier) and self.parent_widget:
            # Undo action
            if self.parent_widget:
                self.parent_widget.undo()
            event.accept()
        
        elif event.key() == Qt.Key.Key_Y and (event.modifiers() & Qt.KeyboardModifier.ControlModifier) and self.parent_widget:
            # Redo action
            if self.parent_widget:
                self.parent_widget.redo()
            event.accept()
        
        else:
            super().keyPressEvent(event)  # Process other keys normally
            
class HardwareMonitor(QThread):
    data_ready = pyqtSignal(str, str, str)  # Signal to send memory & temperature data

    def __init__(self):
        super().__init__()
        self.wmi_interface = wmi.WMI()  # Initialize WMI interface
    
    def get_gpu_usage(self):
        try:
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0)  # GPU 0
            utilization = nvmlDeviceGetUtilizationRates(handle)
            gpu_usage = f"GPU Usage: {utilization.gpu}%"
            nvmlShutdown()
            return gpu_usage
        except Exception as e:
            return f"GPU Usage: Error ({e})"
    
    def run(self):
        while True:
            # Fetch memory usage using psutil
            memory = psutil.virtual_memory()
            memory_usage = f"MemUsage: {memory.used // (1024 * 1024)}/{memory.total // (1024 * 1024)}MB ({memory.percent}% used)"
            
            # Fetch CPU usage using psutil
            cpu_usage = f"CPU Usage: {psutil.cpu_percent(interval=1)}%"
            # Fetch GPU usage using pynvml
            gpu_usage = self.get_gpu_usage()
            
            # Emit the memory usage data
            self.data_ready.emit(memory_usage, cpu_usage, gpu_usage)
            self.msleep(2000)  # Refresh every 2 seconds


class LogApp(QWidget):
    def __init__(self):
        super().__init__()
        print("Initializing LogApp...")
        self.load_color_from_config()  # Load the saved color
        self.init_ui()
        self.load_keyword_definitions()  # Load keyword definitions
        self.current_file = None
        self.user_name = ""
        self.log_type = "General"
        
        # Add Undo/Redo Stacks
        self.undo_stack = []  # Stores previous log states
        self.redo_stack = []  # Stores undone states
        
        # **Store entire log restore points**
        self.restore_points = {}  # {version_name: log_snapshot}
        
        # Initialize counters for different log types
        self.log_counters = {
            "Problem ★": 0,
            "Solution ■": 0,
            "Bug ▲": 0,
            "Changes ◆": 0,
        }
        
        # Initialize PDF-related attributes
        self.pdf_title = "Log Documentation"  # Default PDF title
        self.pdf_font_size = 12  # Default font size
        self.pdf_line_spacing = 10  # Default line spacing
        
        # Start the hardware monitoring thread
        self.hw_monitor = HardwareMonitor()
        self.hw_monitor.data_ready.connect(self.update_system_info)
        self.hw_monitor.start()
        print("LogApp initialized.")

    def create_menu_bar(self, layout):
        menu_bar = QMenuBar(self)
        layout.setMenuBar(menu_bar)  # Attach menu bar to layout

        # Recent Files Menu
        self.recent_menu = QMenu("Recent", self)
        menu_bar.addMenu(self.recent_menu)
        self.update_recent_files_menu()
        
        # Help Menu
        help_menu = QMenu("Help", self)
        menu_bar.addMenu(help_menu)
        help_action = QAction("How to Use", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        dictionary_action = QAction("Dictionary", self)
        dictionary_action.triggered.connect(self.open_dictionary)
        help_menu.addAction(dictionary_action)
        
        # **Version Control Menu (Fixed Naming)**
        version_menu = QMenu("Version Control", self)
        menu_bar.addMenu(version_menu)

        # Restore Menu
        save_version_action = QAction("Create Restore Point", self)
        save_version_action.triggered.connect(self.create_restore_point)
        
        # **View Log Versions Action (Fix Name & Connect Correctly)**
        view_versions_action = QAction("View Log Versions", self)
        view_versions_action.triggered.connect(self.view_restore_points)
    
        version_menu.addAction(view_versions_action)
        version_menu.addAction(save_version_action)
    
    def update_recent_files_menu(self):
        self.recent_menu.clear()  # Clear previous menu items
        settings = QSettings("MyCompany", "LogDocumentationSystem")
        
        recent_files = settings.value("recent_files", [])
        
        # Ensure recent_files is a list (QSettings may return a single string)
        if not isinstance(recent_files, list):
            recent_files = [recent_files] if recent_files else []
    
        self.recent_files = recent_files  # Store it properly
        
        for file_path in self.recent_files:
            action = QAction(file_path, self)
            action.triggered.connect(lambda checked, path=file_path: self.open_logs(path))
            self.recent_menu.addAction(action)
            
        

    def load_recent_files(self):
        settings = QSettings("MyCompany", "LogDocumentationSystem")
        self.recent_files = settings.value("recent_files", [])
        
        # Ensure it is a list (QSettings may return None or a string instead)
        if not isinstance(self.recent_files, list):
            self.recent_files = []
    
    def save_recent_file(self, file_path):
        if file_path not in self.recent_files:
            self.recent_files.insert(0, file_path)
            self.recent_files = self.recent_files[:5]  # Limit to last 5 files
            
        settings = QSettings("MyCompany", "LogDocumentationSystem")
        settings.setValue("recent_files", self.recent_files)
        
        self.update_recent_files_menu()  # Update the menu dynamically
    
    def show_help(self):
        QMessageBox.information(self, "How to Use", "1. Open or create a log file.\n2. Add logs using the text input.\n3. Save logs to keep them.\n4. Use 'Recent' to quickly access previous logs.")

    
    def init_ui(self):
        print("Setting up UI...")
        self.setWindowTitle("Log Documentation System")
        self.setGeometry(100, 100, 500, 400)
        self.setFixedSize(500, 400)  # Make window not resizable
        self.center()

        layout = QVBoxLayout(self)
        
        self.create_menu_bar(layout)  # Create the menu bar and add it to layout
        self.setLayout(layout)
        
        self.log_input = LogTextEdit(self)
        self.log_input.setPlaceholderText("Enter your log entry here...")
        self.log_input.installEventFilter(self)  # Install the event filter
        layout.addWidget(self.log_input)
        
        combo_layout = QHBoxLayout()
        
        self.log_type_selector = QComboBox(self)
        self.log_type_selector.addItems(["General", "Debugging"])
        self.log_type_selector.currentTextChanged.connect(self.change_log_type)
        combo_layout.addWidget(self.log_type_selector)
        
        self.category_selector = QComboBox(self)
        self.category_selector.addItems(["Just Details", "Problem ★", "Bug ▲", "Changes ◆"])
        combo_layout.addWidget(self.category_selector)
        
        layout.addLayout(combo_layout)
        
        button_layout = QHBoxLayout()
        
        self.add_log_button = QPushButton("Add Log", self)
        self.add_log_button.clicked.connect(self.add_log)
        button_layout.addWidget(self.add_log_button)
        
        self.clear_logs_button = QPushButton("Clear Logs", self)
        self.clear_logs_button.clicked.connect(self.clear_logs)
        button_layout.addWidget(self.clear_logs_button)

        layout.addLayout(button_layout)
        
        self.log_list = QListWidget(self)
        self.log_list.itemDoubleClicked.connect(self.edit_log)
        
        # Set context menu policy to enable right-click menu
        self.log_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.log_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Enable drag-and-drop functionality
        self.setAcceptDrops(True)
        self.drop_area = QLabel("Drag and drop a .lds file here", self)
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setStyleSheet("border: 2px dashed #aaa; padding: 60.49px;")
        self.drop_area.setAcceptDrops(True)  # Enable drag-and-drop for this widget
        self.drop_area.hide()  # Hide the drop area by default
        layout.addWidget(self.drop_area)
        
        layout.addWidget(self.log_list)
        
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Logs", self)
        self.save_button.clicked.connect(self.save_logs)
        button_layout.addWidget(self.save_button)
        
        self.open_button = QPushButton("Open Logs", self)
        self.open_button.clicked.connect(self.open_logs)
        button_layout.addWidget(self.open_button)
        
        self.customize_button = QPushButton("Customize", self)
        self.customize_button.clicked.connect(self.set_user_name)
        button_layout.addWidget(self.customize_button)
        
        # Modify export button
        self.export_button = QPushButton("Export to", self)
        export_menu = QMenu(self.export_button)
        
        # Add "Export to PDF" option
        export_pdf_action = QAction("Export to PDF", self)
        export_pdf_action.triggered.connect(self.export_to_pdf)
        export_menu.addAction(export_pdf_action)

        # Add "Export to HTML" option
        export_html_action = QAction("Export to HTML", self)
        export_html_action.triggered.connect(self.export_to_html)
        export_menu.addAction(export_html_action)

        # Attach the menu to the button
        self.export_button.setMenu(export_menu)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        print("UI setup complete.")

        # Hotkey for Saving Logs
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_logs)
        
        # Hotkey for Opening Logs
        self.open_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        self.open_shortcut.activated.connect(self.open_logs)
        
        # Hotkey for Clearing Logs
        self.clear_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        self.clear_shortcut.activated.connect(self.clear_logs)
        
        # Hotkey for Exporting to PDF
        self.export_pdf_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        self.export_pdf_shortcut.activated.connect(self.export_to_pdf)
        
        # Hotkey for Undo
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo)

        # Hotkey for Redo
        redo_shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_shortcut.activated.connect(self.redo)
        
        # Auto Save Functionality
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save_logs)
        self.auto_save_timer.start(60 * 1000)  # 60 sec in milliseconds
    
    def center(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())
        print("Window centered.")

    def change_log_type(self, text):
        print(f"Changing log type to: {text}")
        self.log_type = text

    def set_user_name(self):
        dialog = QWidget()
        dialog.setWindowTitle("Customize")
        dialog.setGeometry(100, 100, 400, 300)
        dialog.setFixedSize(400, 300)  # Make dialog not resizable
        dialog_layout = QVBoxLayout(dialog)

        # Center the dialog
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        dialog_geometry = dialog.frameGeometry()
        dialog_geometry.moveCenter(screen_geometry.center())
        dialog.move(dialog_geometry.topLeft())
        
        # Name input
        name_label = QLabel("Enter your name:")
        dialog_layout.addWidget(name_label)
        name_input = QLineEdit(self.user_name)
        dialog_layout.addWidget(name_input)
        
        # PDF Title input
        title_label = QLabel("Enter PDF Title:")
        dialog_layout.addWidget(title_label)
        title_input = QLineEdit(self.pdf_title)
        dialog_layout.addWidget(title_input)

        # Font Size input
        font_size_label = QLabel("Font Size:")
        dialog_layout.addWidget(font_size_label)
        font_size_input = QLineEdit(str(self.pdf_font_size))
        dialog_layout.addWidget(font_size_input)

        # Line Spacing input
        spacing_label = QLabel("Line Spacing:")
        dialog_layout.addWidget(spacing_label)
        spacing_input = QLineEdit(str(self.pdf_line_spacing))
        dialog_layout.addWidget(spacing_input)

        # Color selection
        color_label = QLabel("Select text color:")
        dialog_layout.addWidget(color_label)
        color_button = QPushButton("Choose Color")
        dialog_layout.addWidget(color_button)

        # Save button
        save_button = QPushButton("Save")
        dialog_layout.addWidget(save_button)

        # Color selection logic
        def choose_color():
            color = QColorDialog.getColor()
            if color.isValid():
                self.text_color = color
                color_button.setStyleSheet(f"background-color: {color.name()};")
                self.save_color_to_config()
                
        color_button.clicked.connect(choose_color)

        # Save logic
        def save_customization():
            name = name_input.text().strip()
            if name:
                self.user_name = name
                print(f"User name set to: {self.user_name}")
                
                self.pdf_title = title_input.text().strip() or "Log Documentation"  # Default title
                self.pdf_font_size = int(font_size_input.text().strip()) if font_size_input.text().strip().isdigit() else 12  # Default font size
                self.pdf_line_spacing = float(spacing_input.text().strip()) if spacing_input.text().strip().replace(".", "", 1).isdigit() else 1.5  # Default line spacing

                self.save_user_config()
                print(f"User name: {self.user_name}, PDF Title: {self.pdf_title}, Font Size: {self.pdf_font_size}, Line Spacing: {self.pdf_line_spacing}")
            else:
                QMessageBox.warning(dialog, "Caution", "No Name Inserted.")
                self.pdf_title = title_input.text().strip() or "Log Documentation"  # Default title
                self.pdf_font_size = int(font_size_input.text().strip()) if font_size_input.text().strip().isdigit() else 12  # Default font size
                self.pdf_line_spacing = float(spacing_input.text().strip()) if spacing_input.text().strip().replace(".", "", 1).isdigit() else 1.5  # Default line spacing

                self.save_user_config()
                print(f"PDF Title: {self.pdf_title}, Font Size: {self.pdf_font_size}, Line Spacing: {self.pdf_line_spacing}")
                
            dialog.close()

        save_button.clicked.connect(save_customization)

        dialog.setLayout(dialog_layout)
        dialog.show()
    
    def get_system_info(self):
        return self.memory_usage
    
    def update_system_info(self, memory_usage, cpu_usage, gpu_usage=None):
        self.memory_usage = memory_usage
        self.cpu_usage = cpu_usage
        self.gpu_usage = gpu_usage
        
    def add_log(self):
        log_text = self.log_input.toPlainText().strip()
        if log_text:
            
            # Save current state before modification
            self.undo_stack.append(self.get_log_state())  
            self.redo_stack.clear()  # Clear redo stack when adding a new log
            
            print("Adding log entry...")
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%SH]")
            additional_info = ""
        
            category = self.category_selector.currentText()
            indicators = {"Problem ★": "★", "Solution ■": "■", "Bug ▲": "▲", "Changes ◆": "◆", "Just Details": ""}
            category_icon = indicators.get(category, "")
            
            # Set default colors for categories
            category_colors = {
                "Problem ★": "red",
                "Bug ▲": "black",
                "Solution ■": "yellow",
                "Changes ◆": "blue",
            }
            icon_color = category_colors.get(category, "green")  # Fallback to green if category not found
            
            # Auto-increment counter for the selected category
            if category in self.log_counters:
                self.log_counters[category] += 1
                log_number = f" #{self.log_counters[category]}"
        
            else:
                log_number = ""  # If not tracked, don't append a number
            
            if self.log_type == "Debugging":
                memory_usage = self.get_system_info()
                cpu_usage = self.cpu_usage
                gpu_usage = self.gpu_usage
                additional_info = f" - {memory_usage}, {cpu_usage}, {gpu_usage}"
            elif self.log_type == "General" and self.user_name:
                additional_info = f" - User: {self.user_name}"
            
            # Use the customized text color for the main log entry text
            main_text_color = self.text_color.name() if hasattr(self, 'text_color') else "black"  # Default to black

            # Format the log text using format_text
            formatted_log_text = self.format_text(log_text)
            
            # Create the log entry with HTML formatting
            log_entry = (
                f'<span style="color:{icon_color};">{category_icon}</span> '
                f'<span style="color:{main_text_color};">{timestamp} [{self.log_type}] {formatted_log_text}{additional_info}{log_number}</span>'
            )
            
            # Create a QLabel to render the rich text
            label = QLabel()
            label.setText(log_entry)
            label.setTextFormat(Qt.TextFormat.RichText)  # Enable rich text
            label.setOpenExternalLinks(False)  # Disable external links
            label.linkActivated.connect(self.handle_internal_link)  # Connect internal link handler
            label.setWordWrap(False)  # Allow text wrapping
            label.setSizePolicy(label.sizePolicy().horizontalPolicy(), label.sizePolicy().verticalPolicy())

            # Add the QLabel to the QListWidget
            item = QListWidgetItem()
            self.log_list.addItem(item)
            self.log_list.setItemWidget(item, label)
            
            # Scroll to the newly added item
            self.log_list.scrollToItem(item)
            
            # Ensure the list can scroll horizontally
            self.log_list.setWrapping(False)
            self.log_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.log_list.setHorizontalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
            
            # Automatically create a restore point every 10 logs
            if self.log_list.count() % 5 == 0:
                self.auto_create_restore_point()
            
            self.log_input.clear()
            print("Log entry added successfully.")
            
            # **Save updated counters to JSON**
            if self.current_file:
                json_file = self.current_file.replace(".lds", ".json")
                with open(json_file, "w", encoding="utf-8") as json_out:
                    json.dump(self.log_counters, json_out, indent=4)
            
        else:
            QMessageBox.warning(self, "Invalid Input", "Log entry cannot be empty.")
            print("Failed to add log: Empty input.")

    def strip_html(self, html_text):
        """Remove HTML tags from a string."""
        from PyQt6.QtGui import QTextDocument
        doc = QTextDocument()
        doc.setHtml(html_text)
        return doc.toPlainText()
    
    def edit_log(self, item):
        label = self.log_list.itemWidget(item)
        if isinstance(label, QLabel):
            # Get the plain text version of the current log entry
            current_text = self.strip_html(label.text())
    
            # Open a dialog pre-filled with the current log text
            plain_text, ok = QInputDialog.getText(self, "Edit Log", "Modify your log entry:", text="")
            if ok and plain_text.strip():
                timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%SH]")
                category = self.category_selector.currentText()
                indicators = {"Problem ★": "★", "Solution ■": "■", "Bug ▲": "▲", "Changes ◆": "◆", "Just Details": ""}
                category_icon = indicators.get(category, "")

                category_colors = {
                    "Problem ★": "red",
                    "Bug ▲": "black",
                    "Solution ■": "yellow",
                    "Changes ◆": "blue",
                }
                icon_color = category_colors.get(category, "green")
                main_text_color = self.text_color.name() if hasattr(self, 'text_color') else "black"

                updated_text = (
                    f'<span style="color:{icon_color};">{category_icon}</span> '
                    f'<span style="color:{main_text_color};">{timestamp} [{self.log_type}] {plain_text} {" -Edited"}</span>'
                )
                # Update the existing label with the new rich text
                label.setText(updated_text)
                # No need to re-add the widget or duplicate it; this updates the current item.
            elif not plain_text.strip():
                QMessageBox.warning(self, "Invalid Input", "Log entry cannot be empty.")

            
    def save_logs(self):
        print("Saving logs...")
        # Check if a file is already opened
        if self.current_file:
            file_name = self.current_file
        else:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Logs", "logs.lds", "Log Documentation System Files (*.lds)")
    
        if file_name:
            self.current_file = file_name  # Update current file if a new one is chosen
            with open(file_name, "w", encoding="utf-8") as file:
                for index in range(self.log_list.count()):
                    item = self.log_list.item(index)
                    label = self.log_list.itemWidget(item)
                    if isinstance(label, QLabel):
                        file.write(label.text() + "\n")
                        
            
            # **Save the counters to a JSON file**
            json_file = file_name.replace(".lds", ".json")
            with open(json_file, "w", encoding="utf-8") as json_out:
                json.dump(self.log_counters, json_out, indent=4)
        
            print(f"Counters saved to {json_file}")                
            print(f"Logs saved to {file_name}")

        self.setWindowTitle("Log Documentation System - FIle saved")  # Update title
        QTimer.singleShot(2000, lambda: self.setWindowTitle("Log Documentation System"))  # Reset after 2 seconds


    def open_logs(self, file_path=None):
        print("Opening logs...")
        if not file_path:  # If no file path is provided, use the file dialog
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Logs", "", "Log Documentation System Files (*.lds)")
        if file_path:
            self.current_file = file_path
            self.save_recent_file(file_path)
            self.log_list.clear()  # Clear the current log list
            
            # Load restore points
            self.load_restore_points()
            
            # Try loading counters from JSON
            json_file = file_path.replace(".lds", ".json")
            if os.path.exists(json_file):
                try:
                    with open(json_file, "r", encoding="utf-8") as json_in:
                        self.log_counters = json.load(json_in)
                    print(f"Loaded log counters from {json_file}: {self.log_counters}")
                except Exception as e:
                    print(f"Error loading log counters: {e}")
                    self.log_counters = {
                        "Problem ★": 0,
                        "Solution ■": 0,
                        "Bug ▲": 0,
                        "Changes ◆": 0,
                    }
            else:
                # If no JSON file exists, reset counters and detect them manually
                self.log_counters = {
                    "Problem ★": 0,
                    "Solution ■": 0,
                    "Bug ▲": 0,
                    "Changes ◆": 0,
                }
            
            
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()  # Read all lines from the file
                
                # Create a progress dialog
                progress_dialog = QProgressDialog("Loading Please Wait...", "Cancel", 0, len(lines), self)
                progress_dialog.setWindowTitle("Loading Logs")
                progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
                progress_dialog.setMinimumDuration(0)  # Show immediately
                progress_dialog.setValue(0) 
                    
                for i, line in enumerate(lines):
                    if progress_dialog.wasCanceled():
                        self.log_list.clear()   # Clear all log items
                        self.current_file = None  # Reset the current file reference
                        QMessageBox.information(self, "Loading Cancelled", "The loading process has been cancelled.")
                        print("Loading canceled by user.")
                        break
                    line = line.strip()
                        
                    if line:  # Ensure the line is not empty
                        
                        # Create a QLabel and set the saved HTML content
                        label = QLabel()
                        label.setText(line)
                        label.setTextFormat(Qt.TextFormat.RichText)
                        label.setOpenExternalLinks(False)  # Disable external links
                        label.linkActivated.connect(self.handle_internal_link)  # Connect internal link handler
                        label.setWordWrap(False)
                        label.adjustSize()
                        
                        # Create a QListWidgetItem and set its size hint to the label's size
                        item = QListWidgetItem()
                        item.setSizeHint(label.sizeHint())
                        self.log_list.addItem(item)
                        self.log_list.setItemWidget(item, label)
                        print(f"Loaded log: {line}")

                    # Update the progress dialog
                    progress_dialog.setValue(i + 1)
                    QApplication.processEvents()  # Allow the UI to update
                
                progress_dialog.close()
                print(f"Logs loaded successfully from {file_path}")
                
                # If no JSON exists, try detecting counters
                if not os.path.exists(json_file):
                    self.detect_log_counters()
                
                # Scroll to the last item in the log list
                if self.log_list.count() > 0:
                    last_item = self.log_list.item(self.log_list.count() - 1)
                    self.log_list.scrollToItem(last_item)
                    print("Scrolled to the latest log entry.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")
                print(f"Error opening file: {e}")

    
    def eventFilter(self, source, event):
        if source == self.log_input and event.type() == QEvent.Type.KeyPress:
            # Debug: print key code and modifiers
            print("Key pressed in log_input:", event.key(), event.modifiers())
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                print("Shift+Enter detected via eventFilter")
                self.add_log()
                return True  # Consume the event
        return super().eventFilter(source, event)
    
    def show_context_menu(self, pos: QPoint):
        item = self.log_list.itemAt(pos)
        if item:
            menu = QMenu()
            # Get the selected log text
            label = self.log_list.itemWidget(item)
            log_text = self.strip_html(label.text()) if isinstance(label, QLabel) else ""
            
            # Check if the log is a Bug or Problem
            is_resolvable = "▲" in log_text
            
            delete_action = menu.addAction("Delete")
            edit_action = menu.addAction("Edit")
            
            # Add "Fix" option only for Bugs
            fix_action = None
            if is_resolvable:
                fix_action = menu.addAction("Fix")
            
            # Add "Solution" option only for Problems
            solution_action = None
            if "★" in log_text:
                solution_action = menu.addAction("Add Solution")
            
            action = menu.exec(self.log_list.viewport().mapToGlobal(pos))
            
            if action is None:
                return  # Exit function without doing anything
            
            if action == delete_action:
                row = self.log_list.row(item)
                self.log_list.takeItem(row)
                print("Log entry deleted.")
                
            elif action == edit_action:
                self.edit_log(item)
                print("Log entry edited.")
                
            elif action == fix_action:
                self.resolve_log(item)
                print("Log entry resolved.")
                
            elif action == solution_action:
                self.add_solution(item)
                print("Solution added for the problem.")

    def add_solution(self, item):
        """Add a solution log corresponding to a problem log and mark it as Resolved."""
        label = self.log_list.itemWidget(item)
        if isinstance(label, QLabel):
            problem_text = self.strip_html(label.text())
            
            # Check if the problem is already resolved
            if "Resolved" in problem_text:
                QMessageBox.information(self, "Already Resolved", "This problem is already marked as resolved.")
                return
            
            match = re.search(r"★.*?#(\d+)", problem_text)
            if match:
                problem_number = match.group(1)
                solution_text, ok = QInputDialog.getText(self, "Add Solution", f"Enter solution for Problem #{problem_number}:")
                if ok and solution_text.strip():
                    # Add the solution log
                    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%SH]")
                    solution_entry = (
                        f'<span style="color:yellow;">■</span> '
                        f'<span style="color:black;">{timestamp} [Solution] {solution_text.strip()} - Solution #{problem_number}</span>'
                    )
                    solution_label = QLabel()
                    solution_label.setText(solution_entry)
                    solution_label.setTextFormat(Qt.TextFormat.RichText)
                    solution_label.setOpenExternalLinks(False)
                    solution_label.linkActivated.connect(self.handle_internal_link)
                    solution_label.setWordWrap(False)

                    solution_item = QListWidgetItem()
                    self.log_list.addItem(solution_item)
                    self.log_list.setItemWidget(solution_item, solution_label)
                    self.log_list.scrollToItem(solution_item)

                    # Mark the problem log as Resolved
                    updated_problem_text = (
                        f'{label.text()} <span style="background-color: green; color: white;">Resolved</span>'
                    )
                    label.setText(updated_problem_text)

                    print(f"Solution #{problem_number} added successfully and Problem #{problem_number} marked as Resolved.")
                else:
                    QMessageBox.warning(self, "Invalid Input", "Solution entry cannot be empty.")
    
    def save_color_to_config(self):
        config = {"text_color": self.text_color.name() if hasattr(self, 'text_color') else "#008000"}  # Default to green
        with open("config.json", "w") as config_file:
            json.dump(config, config_file)
        print("Color saved to config.json")
    
    def load_color_from_config(self):
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.text_color = QColor(config.get("text_color", "#008000"))  # Default to green
                print(f"Color loaded: {self.text_color.name()}")
        except FileNotFoundError:
            self.text_color = QColor("green")  # Default to green if config file doesn't exist
            print("No config file found. Using default color.")
            
    def dragEnterEvent(self, event):
        print("dragEnterEvent triggered")
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                print("URL:", url.toLocalFile())
                if url.toLocalFile().lower().endswith(".lds"):
                    self.drop_area.show()
                    self.log_list.hide()
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        print("dragMoveEvent triggered")
        event.acceptProposedAction()

    def dropEvent(self, event):
        print("dropEvent triggered")
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(".lds"):
                self.open_logs(file_path)
                break
        else:
            QMessageBox.warning(self, "Invalid File", "Please select a valid .lds file.")
    
        self.drop_area.hide()
        self.log_list.show()
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        print("dragLeaveEvent triggered")
        self.drop_area.hide()
        self.log_list.show()
        event.accept()

        
    def export_to_pdf(self):
        # Create a QTextDocument to hold the aggregated logs.
        doc = QTextDocument()
        
        # Get user-defined values
        font_size = self.pdf_font_size  # User-selected font size
        line_spacing = self.pdf_line_spacing  # User-defined spacing
        title_text = self.pdf_title  # Title set in customization

        # Start building the PDF content
        html_content = f"""
        <html>
            <head>
                <meta charset='utf-8'>
                <style>
                    body {{ font-size: {font_size}pt;
                            line-height: {line_spacing}em;
                            font-family: Arial, sans-serif;
                            }}
                    h1 {{ 
                        text-align: center; 
                        font-size: {font_size + 6}pt; 
                        font-weight: bold; 
                        margin-bottom: {line_spacing * 5}px;
                        }}
                    .log-entry {{ 
                        margin-bottom: {line_spacing * 3}px; 
                        white-space: pre-wrap; 
                        /* Ensures text wrapping */ }}
                    a {{ color: blue; text-decoration: underline; }}
                </style>
            </head>
            <body>
                <h1>{self.pdf_title}</h1>
        """
        
        # Loop through each item in the log list.
        for index in range(self.log_list.count()):
            item = self.log_list.item(index)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel):
                # Append the label's HTML text. You can add additional formatting here if needed.
                text = label.text()
                html_content += f"<p class='log-entry'>{text}</p>"
        
        # Append keyword definitions at the end of the PDF
        html_content += "<hr><h2>Definitions</h2><ul>"
        for keyword, definition in getattr(self, 'keyword_definitions', {}).items():
            html_content += f"<li><b>{keyword}:</b> {definition}</li>"
        html_content += "</ul></body></html>"
    
        doc.setHtml(html_content)
    
        # Create a printer object and configure it for PDF output.
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        file_path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF Files (*.pdf)")
        if file_path:
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
        
            # Optionally, you can show a print dialog to let the user adjust settings.
            # print_dialog = QPrintDialog(printer, self)
            # if print_dialog.exec() != QPrintDialog.DialogCode.Accepted:
            #     return
        
            # Print the document to PDF.
            doc.print(printer)
            
            # Confirmation Dialog
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("PDF Exported")
            msg.setText(f"PDF has been saved successfully!\n\nLocation:\n{file_path}")
            msg.setStandardButtons(QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ok)
        
            # Handle user response (Open PDF if clicked)
            response = msg.exec()
            if response == QMessageBox.StandardButton.Open:
                self.open_pdf(file_path)
                print(f"PDF exported successfully to {file_path}")
    
    def clear_logs(self):
        # Confirm the action with the user (optional)
        reply = QMessageBox.question(self, "Clear Logs", 
                                    "Are you sure you want to clear all logs and drop the current file?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.log_list.clear()   # Clear all log items
            self.current_file = None  # Reset the current file reference
            print("Logs cleared and current file dropped.")
    
    def auto_save_logs(self):
        if self.current_file:
            print("Auto-saving logs...")
            with open(self.current_file, "w", encoding="utf-8") as file:
                for index in range(self.log_list.count()):
                    item = self.log_list.item(index)
                    label = self.log_list.itemWidget(item)
                    if isinstance(label, QLabel):
                        file.write(label.text() + "\n")
            print(f"Logs auto-saved to {self.current_file}")
            self.setWindowTitle("Log Documentation System - Auto-saved")  # Update title
            QTimer.singleShot(8000, lambda: self.setWindowTitle("Log Documentation System"))  # Reset after 2 seconds
        else:
            print("Auto-save skipped: No file selected")

    def save_user_config(self):
        settings = QSettings("MyCompany", "LogDocumentationSystem")
        settings.setValue("username", self.user_name)
        settings.setValue("pdf_title", self.pdf_title)
        settings.setValue("pdf_font_size", self.pdf_font_size)
        settings.setValue("pdf_line_spacing", self.pdf_line_spacing)
        print(f"Saved settings: Username={self.user_name}, PDF Title={self.pdf_title}, Font Size={self.pdf_font_size}, Line Spacing={self.pdf_line_spacing}")

    def load_user_config(self):
        settings = QSettings("MyCompany", "LogDocumentationSystem")
        self.user_name = settings.value("username", "")
        self.pdf_title = settings.value("pdf_title", "Log Documentation")
        self.pdf_font_size = int(settings.value("pdf_font_size", 12))
        self.pdf_line_spacing = float(settings.value("pdf_line_spacing", 1.5))
        print(f"Loaded settings: Username={self.user_name}, PDF Title={self.pdf_title}, Font Size={self.pdf_font_size}, Line Spacing={self.pdf_line_spacing}")

    def open_pdf(self, file_path):
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.call(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open PDF:\n{str(e)}")
    
    def format_text(self, text):
        """Convert Markdown-like syntax into HTML for QLabel."""
        text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)  # *italic* → <i>italic</i>
        text = re.sub(r"_([^_]+)_", r"<u>\1</u>", text)    # _underline_ → <u>underline</u>
        text = re.sub(r"\[([^\]]+)\]\((#.*?)\)", r'<a href="\2">\1</a>', text)  # Internal links only
        
        # Use user-defined keywords from the dictionary
        for keyword, definition in getattr(self, 'keyword_definitions', {}).items():
            text = re.sub(rf"\b{keyword}\b", f'<a href="#{keyword}">{keyword}</a>', text)

        return text
    
    def handle_internal_link(self, link):
        """Handle internal navigation within the document."""
        print(f"Navigating to: {link}")
        
        keyword = link.lstrip("#")  # Remove '#' from link
        if keyword in getattr(self, 'keyword_definitions', {}):
            definition = self.keyword_definitions[keyword]
            QMessageBox.information(self, f"Definition: {keyword}", definition)
        else:
            QMessageBox.warning(self, "Keyword Not Found", f"No definition found for '{keyword}'.")
        
    
    def export_to_html(self):
        # Get user-defined values
        font_size = self.pdf_font_size  # Reuse PDF settings if desired
        line_spacing = self.pdf_line_spacing
        title_text = self.pdf_title

        # Start building the HTML content
        html_content = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <title>{title_text}</title>
                <style>
                    body {{
                        font-size: {font_size}pt;
                        line-height: {line_spacing}em;
                        font-family: Arial, sans-serif;
                    }}
                    h1 {{
                        text-align: center;
                        font-size: {font_size + 6}pt;
                        font-weight: bold;
                        margin-bottom: {line_spacing * 5}px;
                    }}
                    .log-entry {{
                        margin-bottom: {line_spacing * 3}px;
                        white-space: pre-wrap;
                    }}
                    a {{
                        color: blue;
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <h1>{title_text}</h1>
        """

        # Loop through each log entry in the log_list
        for index in range(self.log_list.count()):
            item = self.log_list.item(index)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel):
                # Get the HTML text for the log entry
                text = label.text()
                html_content += f"<p class='log-entry'>{text}</p>"

        # Append keyword definitions at the end of the HTML
        html_content += """
                <hr>
                <h2>Keyword Definitions</h2>
                <ul>
        """
        for keyword, definition in getattr(self, 'keyword_definitions', {}).items():
            html_content += f'<li><a name="{keyword}"><b>{keyword}:</b></a> {definition}</li>'
        html_content += "</ul></body></html>"

        # Ask the user for a file location to save the HTML file
        file_path, _ = QFileDialog.getSaveFileName(self, "Export HTML", "", "HTML Files (*.html)")
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                # Confirmation Dialog
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("HTML Exported")
                msg.setText(f"HTML file has been saved successfully!\n\nLocation:\n{file_path}")
                msg.setStandardButtons(QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ok)

                # Handle user response (Open PDF if clicked)
                response = msg.exec()
                if response == QMessageBox.StandardButton.Open:
                    self.open_pdf(file_path)
                    print(f"PDF exported successfully to {file_path}")
            
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export HTML:\n{e}")

    def detect_log_counters(self):
        """Detect the highest log number for each category in the currently loaded file."""
        print("Detecting highest log counters...")

        # Reset before scanning
        detected_counters = {
            "Problem ★": 0,
            "Solution ■": 0,
            "Bug ▲": 0,
            "Changes ◆": 0,
        }

        pattern = re.compile(r"(Problem ★|Solution ■|Bug ▲|Changes ◆).*?#(\d+)\b")  # Updated regex

        for index in range(self.log_list.count()):
            item = self.log_list.item(index)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel):
                text = self.strip_html(label.text())  # Remove HTML formatting
                match = pattern.search(text)

                if match:
                    category = match.group(1)
                    number = int(match.group(2))
                    detected_counters[category] = max(detected_counters[category], number)
                    
        # Update class counters AFTER the loop to avoid resetting mid-detection
        self.log_counters = detected_counters
        print("Detected log counters:", self.log_counters)
        
    
    def resolve_log(self, item):
        """Mark a Bug as Fixed."""
        label = self.log_list.itemWidget(item)
    
        if isinstance(label, QLabel):
            current_text = label.text()  # Get **existing HTML** (to keep links)

            # Check if it's already fixed
            if "Fixed" in current_text:
                QMessageBox.information(self, "Already Fixe", "This log entry is already marked as fixed.")
                return

            # Modify the text to add "(Fixed)" with green background only for the word "Fixed"
            updated_text = f'{current_text} <span style="background-color: green; color: white;">Fixed</span>'
            label.setText(updated_text)
            print("Log entry marked as fixed with green background only for the word 'Fixed'.")

    def get_log_state(self):
        """Returns a snapshot of the current log list (for undo/redo)."""
        state = []
        for index in range(self.log_list.count()):
            item = self.log_list.item(index)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel):
                state.append(label.text())  # Store log text
        return state

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.get_log_state())  # Save current state before undoing
            last_state = self.undo_stack.pop()  # Get the last saved state
            self.restore_log_state(last_state)
            print("Undo performed.")
        else:
            print("Nothing to undo.")
    
    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.get_log_state())  # Save current state before redoing
            next_state = self.redo_stack.pop()  # Get the redo state
            self.restore_log_state(next_state)
            print("Redo performed.")
        else:
            print("Nothing to redo.")
            
    def restore_log_state(self, state):
        """Restores the log list to a previous state."""
        self.log_list.clear()  # Clear current logs
        for log in state:
            label = QLabel()
            label.setText(log)
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setOpenExternalLinks(False)
            label.linkActivated.connect(self.handle_internal_link)
            label.setWordWrap(False)

            item = QListWidgetItem()
            self.log_list.addItem(item)
            self.log_list.setItemWidget(item, label)
        
    def create_restore_point(self):
        """Save the current logs as a restore point with a timestamped name."""
        version_name, ok = QInputDialog.getText(self, "Create Restore Point", "Enter a version name:")
    
        if not ok or not version_name.strip():
            return  # User canceled

        # Generate 6 random alphanumeric characters
        random_prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        
        # Get the current date in YYYY-MM-DD format
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%SH")
        
        version_name = f"[{current_date}]  -  {version_name.strip()}  |  {random_prefix}"
        
        # Capture all logs in a list
        log_snapshot = [self.log_list.itemWidget(self.log_list.item(i)).text() for i in range(self.log_list.count())]

        # Store the snapshot
        self.restore_points[version_name] = log_snapshot
        self.save_restore_points()  # Save restore points to JSON
        print(f"Restore point '{version_name}' saved.")

    def view_restore_points(self):
        """Show the Restore Points window."""
        if not self.restore_points:
            QMessageBox.information(self, "No Restore Points", "No restore points available.")
            return

        self.restore_window = RestorePointWindow(self.restore_points, self)
        self.restore_window.show()

    def compare_versions(self, version_name):
        """Compare a restore point with the latest log version."""
        if version_name not in self.restore_points:
            QMessageBox.warning(self, "Invalid Version", "This restore point does not exist.")
            return

        old_logs = self.restore_points[version_name]
        new_logs = [self.log_list.itemWidget(self.log_list.item(i)).text() for i in range(self.log_list.count())]

        differences = []
        for i, (old_log, new_log) in enumerate(zip(old_logs, new_logs)):
            if old_log != new_log:
                differences.append(f"Line {i+1} changed:\n- OLD: {old_log}\n- NEW: {new_log}\n")

        # Find logs added after the saved version
        if len(new_logs) > len(old_logs):
            for i in range(len(old_logs), len(new_logs)):
                differences.append(f"New log added: {new_logs[i]}")

        if differences:
            QMessageBox.information(self, "Comparison Result", "\n\n".join(differences))
        else:
            QMessageBox.information(self, "No Differences", "The selected restore point matches the latest version.")

    def restore_version(self, version_name):
        """Restore logs to a selected restore point."""
        if version_name not in self.restore_points:
            QMessageBox.warning(self, "Invalid Version", "This restore point does not exist.")
            return

        self.log_list.clear()  # Clear current logs
        for log_entry in self.restore_points[version_name]:
            label = QLabel()
            label.setText(log_entry)
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setOpenExternalLinks(False)
            label.linkActivated.connect(self.handle_internal_link)
            label.setWordWrap(False)

            item = QListWidgetItem()
            self.log_list.addItem(item)
            self.log_list.setItemWidget(item, label)

        print(f"Logs restored to version: {version_name}")

    def auto_create_restore_point(self):
        """Automatically create a restore point with a randomly generated name."""
        # Predefined lists of names
        person = names.get_first_name()
        places = [
            "New York", "Paris", "London", "Tokyo", "Beijing", "Sydney", "Los Angeles", "Moscow", "Berlin", "Dubai",
            "Rome", "Cairo", "Rio de Janeiro", "Seoul", "Bangkok", "Toronto", "Mexico City", "Singapore", "Hong Kong", "Madrid",
            "Barcelona", "Mumbai", "Delhi", "Shanghai", "Istanbul", "Lisbon", "Vienna", "Amsterdam", "Stockholm", "Oslo",
            "Helsinki", "Copenhagen", "Dublin", "Edinburgh", "Venice", "Prague", "Budapest", "Warsaw", "Athens", "Brussels",
            "Zurich", "Geneva", "Cape Town", "Johannesburg", "Buenos Aires", "Santiago", "Lima", "Bogotá", "Quito", "Havana",
            "Kuala Lumpur", "Jakarta", "Manila", "Ho Chi Minh City", "Taipei", "Osaka", "Kyoto", "Kolkata", "Chennai", "Jakarta",
            "San Francisco", "Chicago", "Boston", "Houston", "Miami", "Las Vegas", "Seattle", "Philadelphia", "Washington D.C.", "Atlanta",
            "San Diego", "Phoenix", "Denver", "Portland", "Honolulu", "Vancouver", "Montreal", "Ottawa", "Calgary", "Quebec City",
            "Guadalajara", "Monterrey", "Medellín", "Recife", "Brasília", "Sao Paulo", "Curitiba", "Salvador", "Fortaleza", "Montevideo",
            "Sofia", "Bucharest", "Belgrade", "Sarajevo", "Zagreb", "Ljubljana", "Skopje", "Tallinn", "Riga", "Vilnius",
            "Bratislava", "Luxembourg", "San Juan", "Reykjavik", "Anchorage", "Honolulu", "Casablanca", "Marrakech", "Tunis", "Algiers",
            "Accra", "Lagos", "Nairobi", "Addis Ababa", "Khartoum", "Luanda", "Harare", "Dar es Salaam", "Kampala", "Dakar",
            "Doha", "Riyadh", "Mecca", "Medina", "Muscat", "Abu Dhabi", "Kuwait City", "Tehran", "Baghdad", "Damascus",
            "Beirut", "Amman", "Jerusalem", "Gaza", "Ankara", "Baku", "Tbilisi", "Yerevan", "Astana", "Bishkek",
            "Tashkent", "Ashgabat", "Dushanbe", "Ulaanbaatar", "Novosibirsk", "Yekaterinburg", "Kazan", "Nizhny Novgorod", "Saint Petersburg", "Sochi",
            "Vladivostok", "Hanoi", "Yangon", "Phnom Penh", "Vientiane", "Male", "Dhaka", "Thimphu", "Colombo", "Port Moresby",
            "Hobart", "Wellington", "Christchurch", "Auckland", "Suva", "Port Vila", "Apia", "Nuku'alofa", "Tarawa", "Majuro",
            "Palikir", "Honiara", "Jakarta", "Makassar", "Medan", "Surabaya", "Bali", "Bandung", "Davao", "Cebu",
            "Baguio", "Iloilo", "Vigan", "Zamboanga", "Tacloban", "Legazpi", "Cagayan de Oro", "Dumaguete", "Puerto Princesa", "Tagaytay",
            "Bacolod", "Pampanga", "Subic", "General Santos", "Batangas", "Santa Cruz", "Antipolo", "Lucena", "Tuguegarao", "Butuan"
        ]
        foods = [
            "Pizza", "Burger", "Pasta", "Sushi", "Tacos", "Ramen", "Dumplings", "Pancakes", "Fried Chicken", "Steak",
            "Salmon", "Lasagna", "Grilled Cheese", "Biryani", "Falafel", "Chow Mein", "Pho", "Shawarma", "Hotdog", "Samosa",
            "Mac and Cheese", "BBQ Ribs", "Peking Duck", "Ceviche", "Paella", "Tuna Tartare", "Goulash", "Jambalaya",
            "Carbonara", "Pad Thai", "Eggs Benedict", "Croissant", "Bruschetta", "Curry", "Kebab", "Kimchi", "Gyoza",
            "Miso Soup", "Bulgogi", "Fish and Chips", "Quesadilla", "Enchiladas", "Tamales", "Chili Con Carne", "Fajitas",
            "Gumbo", "Clam Chowder", "Meatballs", "Ratatouille", "Caprese Salad", "Cordon Bleu", "Poutine", "Pierogi",
            "Beef Stroganoff", "Hummus", "Baba Ganoush", "Empanadas", "Tortellini", "Arroz Con Pollo", "Moussaka", "Frittata",
            "Shepherd’s Pie", "Jollof Rice", "Satay", "Arepas", "Tandoori Chicken", "Chimichanga", "Pita Bread", "Muffins",
            "Cupcakes", "Brownies", "Cheesecake", "Chocolate Cake", "Donuts", "Apple Pie", "Baklava", "Churros", "Gelato",
            "Creme Brulee", "Tiramisu", "Mango Sticky Rice", "Pavlova", "Gulab Jamun", "Macarons", "Strawberry Shortcake",
            "Panna Cotta", "Fruit Salad", "Waffles", "French Toast", "Rice Pudding", "Matcha Ice Cream", "Banana Bread",
            "Carrot Cake", "Scones", "Eclairs", "Mochi", "Halva", "Nougat", "Truffles", "Pecan Pie", "Custard Tart",
            "Marshmallow", "Chocolate Fondue", "Lemon Tart", "Pretzels", "Cornbread", "Bagels", "Garlic Bread", "Spring Rolls",
            "Edamame", "Cabbage Rolls", "Sausages", "Stuffed Peppers", "Meatloaf", "Corn on the Cob", "Pickles", "Baked Beans",
            "Coleslaw", "Potato Salad", "Hush Puppies", "Onion Rings", "Deviled Eggs", "Sushi Rolls", "Tofu", "Tempura",
            "Tteokbokki", "Shakshuka", "Lentil Soup", "Seafood Boil", "Gnocchi", "Borscht", "Lamb Chops", "Chicken Tikka",
            "Vegetable Stir Fry", "Teriyaki Chicken", "Caesar Salad", "Cobb Salad", "Greek Salad", "Tabbouleh", "Poke Bowl",
            "Bento Box", "Lobster Bisque", "Calamari", "Coconut Shrimp", "Stuffed Mushrooms", "Artichoke Dip", "Nachos",
            "Garlic Butter Shrimp", "Oysters Rockefeller", "Scallops", "Bratwurst", "Duck Confit", "Beef Wellington",
            "Surf and Turf", "Sweet and Sour Chicken", "Kung Pao Chicken", "Sesame Chicken", "Honey Glazed Ham",
            "Roast Turkey", "Prime Rib", "Lamb Kebab", "Fried Rice", "Udon Noodles", "Okonomiyaki", "Chicken Parmesan",
            "Baked Ziti", "Cornish Pasty", "Croquettes", "Tostones", "Pho Ga", "Sopa de Lima", "Kimchi Jjigae",
            "Vichyssoise", "Bouillabaisse", "Pork Adobo", "Chicken Inasal", "Pancit", "Bicol Express", "Halo-Halo",
            "Leche Flan", "Turon", "Ensaymada", "Bibingka", "Kare-Kare", "Sinangag", "Longganisa", "Laing", "Pandesal",
            "Sisig", "Chicharon", "Taho", "Lugaw", "Dinuguan", "Crispy Pata", "Inihaw na Liempo", "Pinakbet", "Ginataan",
            "Lumpia", "Arroz Caldo", "Champorado", "Bangus", "Sinigang", "Bulalo", "Dinengdeng", "Lechon Kawali", "Menudo",
            "Paksiw na Baboy", "Tortang Talong", "Ginataang Hipon", "Kaldereta", "Batchoy"
        ]
        animals = [
            "Lion", "Tiger", "Elephant", "Zebra", "Panda", "Kangaroo", "Giraffe", "Dolphin", "Eagle", "Wolf",
            "Cheetah", "Bear", "Rhinoceros", "Hippopotamus", "Crocodile", "Jaguar", "Leopard", "Ostrich", "Parrot", "Otter",
            "Penguin", "Lemur", "Koala", "Sloth", "Armadillo", "Chameleon", "Gorilla", "Chimpanzee", "Orangutan", "Peacock",
            "Buffalo", "Bison", "Moose", "Antelope", "Camel", "Caribou", "Gazelle", "Hyena", "Iguana", "Komodo Dragon",
            "Lynx", "Meerkat", "Narwhal", "Ocelot", "Platypus", "Quokka", "Raccoon", "Seahorse", "Tasmanian Devil", "Walrus",
            "Yak", "Anaconda", "Barracuda", "Blue Whale", "Clownfish", "Dugong", "Emu", "Fennec Fox", "Gecko", "Hammerhead Shark",
            "Indian Cobra", "Jackal", "King Cobra", "Lobster", "Macaw", "Numbat", "Octopus", "Pufferfish", "Quail", "Raven",
            "Scorpion", "Tarantula", "Uakari", "Vulture", "Wolverine", "Xerus", "Yellowfin Tuna", "Zorilla", "Alligator", "Badger",
            "Caiman", "Dingo", "Echidna", "Ferret", "Goat", "Hedgehog", "Indian Star Tortoise", "Jellyfish", "Koi Fish", "Llama",
            "Mongoose", "Nightingale", "Okapi", "Pangolin", "Quetzal", "Roadrunner", "Siberian Husky", "Toucan", "Urial", "Vicuña",
            "Weasel", "X-ray Tetra", "Yak", "Zebra Shark", "Anglerfish", "Butterfly", "Catfish", "Dragonfly", "Electric Eel",
            "Firefly", "Goldfish", "Hermit Crab", "Indian Elephant", "Japanese Spider Crab", "Killer Whale", "Leafy Seadragon",
            "Mandrill", "Nautilus", "Owl", "Pika", "Queen Angelfish", "Red Panda", "Salamander", "Tarsier", "Unicornfish",
            "Vampire Bat", "Woodpecker", "Xenopus", "Yeti Crab", "Zebra Finch", "Aye-Aye", "Basilisk", "Cuttlefish", "Dung Beetle",
            "Eel", "Fossa", "Galápagos Tortoise", "Horseshoe Crab", "Indian Peafowl", "Javan Rhino", "Kiwi", "Leafcutter Ant",
            "Manatee", "Nudibranch", "Oyster", "Peregrine Falcon", "Quagga", "Rattlesnake", "Swan", "Tiger Shark", "Uromastyx",
            "Vampire Squid", "Wombat", "Xenarthra", "Yabby", "Zebra Mussel", "Arabian Oryx", "Bobcat", "Coyote", "Dhole",
            "Eurasian Lynx", "Flying Squirrel", "Groundhog", "Harpy Eagle", "Indian Starling", "Japanese Macaque",
            "Kakapo", "Lace Monitor", "Margay", "Nilgai", "Osprey", "Potoroo", "Quillback", "Ringtail", "Snow Leopard",
            "Tree Kangaroo", "Upland Sandpiper", "Volcano Rabbit", "Warty Frogfish", "Xenops", "Yapok", "Zebra Swallowtail",
            "African Wild Dog", "Blue Jay", "Capybara", "Dusky Dolphin", "Eastern Coral Snake", "Frigatebird", "Greater Kudu",
            "Hawaiian Monk Seal", "Indian Gharial", "Javanese Cat", "Kermode Bear", "Long-Eared Owl", "Mexican Axolotl",
            "Northern Cardinal", "Ocelated Turkey", "Pelican", "Quokka", "Rufous Hummingbird", "Sandhill Crane",
            "Tufted Puffin", "Umbrella Cockatoo", "Venezuelan Poodle Moth", "Western Green Mamba", "Xantus's Hummingbird",
            "Yellow Mongoose", "Zebra Duiker"
        ]
        
        
        # Randomly select one name from each category
        random_place = random.choice(places)
        random_food = random.choice(foods)
        random_animal = random.choice(animals)

        random_choice = [random_animal, random_food, random_place, person]
        #random_choices = random.choice(random_choice)
        
        # Store selected name on a set
        selected_names = set()
        
        # Create a function to remove picked names on a set
        def pick_unique_name():
            while True:
                # Choose a random name from the selected category
                random_choices = random.choice(random_choice)

                # Ensure the name is unique
                if random_choices not in selected_names:
                    selected_names.add(random_choices)  # Mark as used
                    random_choice.remove(random_choices)  # Remove from list
                    return random_choices
        
        # Generate 6 random alphanumeric characters
        random_prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        
        # Get the current date in YYYY-MM-DD format
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%SH")
        
        # Combine the selected names to form a unique restore point name
        restore_point_name = f"[{current_date}]  -  {pick_unique_name()}  |  {random_prefix}"

        # Capture all logs in a list
        log_snapshot = [self.log_list.itemWidget(self.log_list.item(i)).text() for i in range(self.log_list.count())]

        # Store the snapshot
        self.restore_points[restore_point_name] = log_snapshot
        self.save_restore_points()  # Save restore points to JSON
        print(f"Automatic restore point '{restore_point_name}' created.")
    
    def save_restore_points(self):
        """Save restore points to a JSON file."""
        if self.current_file:
            json_file = self.current_file.replace(".lds", "_restore_points.json")
            with open(json_file, "w", encoding="utf-8") as file:
                json.dump(self.restore_points, file, indent=4, ensure_ascii=False)
            print(f"Restore points saved to {json_file}")
        
    def load_restore_points(self):
        """Load restore points from a JSON file."""
        if self.current_file:
            json_file = self.current_file.replace(".lds", "_restore_points.json")
            if os.path.exists(json_file):
                try:
                    with open(json_file, "r", encoding="utf-8") as file:
                        self.restore_points = json.load(file)
                    print(f"Restore points loaded from {json_file}")
                except Exception as e:
                    print(f"Error loading restore points: {e}")
                    self.restore_points = {}
            else:
                self.restore_points = {}
    
    def open_dictionary(self):
        """Open the DictionaryDialog and update keyword definitions."""
        self.dictionary_dialog = DictionaryDialog(self)
        self.dictionary_dialog.dictionary = getattr(self, 'keyword_definitions', {})  # Load existing definitions
        
        # Populate the keyword list in the dialog
        for keyword in sorted(self.dictionary_dialog.dictionary.keys()):
            self.dictionary_dialog.add_list_item(keyword)
    
        self.dictionary_dialog.show()

        # Update keyword definitions when the dialog is closed
        def update_keywords():
            self.keyword_definitions = self.dictionary_dialog.dictionary
            self.save_keyword_definitions()  # Save updated definitions to a file

        self.dictionary_dialog.finished.connect(update_keywords)
        
    def save_keyword_definitions(self):
        """Save keyword definitions to a JSON file."""
        file_path = os.path.join(os.getcwd(), "keyword_definitions.json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(getattr(self, 'keyword_definitions', {}), file, indent=4)
        print(f"Keyword definitions saved to {file_path}")

    def load_keyword_definitions(self):
        """Load keyword definitions from a JSON file."""
        file_path = os.path.join(os.getcwd(), "keyword_definitions.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                self.keyword_definitions = json.load(file)
            print(f"Keyword definitions loaded from {file_path}")
        else:
            self.keyword_definitions = {}
    

if __name__ == "__main__":
    print("Starting application...")
    app = QApplication(sys.argv)
    window = LogApp()
    window.show()
    sys.exit(app.exec())