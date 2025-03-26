from PyQt6.QtWidgets import QMenu, QProgressDialog, QMenuBar, QLabel, QColorDialog, QApplication, QLineEdit, QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QListWidget, QInputDialog, QFileDialog, QMessageBox, QComboBox
from PyQt6.QtCore import Qt, QSettings, QTimer, QThread, pyqtSignal, QEvent, QPoint
from PyQt6.QtGui import QColor, QTextDocument, QTextCursor, QBrush, QShortcut, QKeySequence, QAction
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
import fitz

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
        self.current_file = None
        self.user_name = ""
        self.log_type = "General"
        
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
        self.category_selector.addItems(["Just Details", "Problem ★", "Solution ■", "Bug ▲", "Changes ◆"])
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
        
        # Auto Save Functionality
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save_logs)
        self.auto_save_timer.start(30 * 1000)  # 30 sec in milliseconds
    
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
                timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
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
            delete_action = menu.addAction("Delete")
            edit_action = menu.addAction("Edit")
            action = menu.exec(self.log_list.viewport().mapToGlobal(pos))
            if action == delete_action:
                row = self.log_list.row(item)
                self.log_list.takeItem(row)
                print("Log entry deleted.")
            elif action == edit_action:
                self.edit_log(item)
                print("Log entry edited.")
    
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
        
        # Append explanations at the end of the PDF
        html_content += "<hr><h2>Definitions</h2><ul>"        
        
        keyword_definitions = {
            "TensorFlow": "TensorFlow is an open-source machine learning framework developed by Google.",
            "PyQt": "PyQt is a set of Python bindings for Qt libraries used for GUI development.",
            "AI": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines."
        }
        
        for keyword, definition in keyword_definitions.items():
            # Add a bookmark for each keyword definition
            definition_anchor = f"def_{keyword}"

            # Add the definition with a bookmark
            html_content += f'<li><b name="{definition_anchor}">{keyword}:</b> {definition}</li>'


        html_content += "</body></html>"
    
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
        
        # Define keywords and their descriptions
        keyword_definitions = {
            "TensorFlow": "TensorFlow is an open-source machine learning framework developed by Google.",
            "PyQt": "PyQt is a set of Python bindings for Qt libraries used for GUI development.",
            "AI": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines."
        }

        # Replace keywords with HTML links
        for keyword, definition in keyword_definitions.items():
            text = re.sub(rf"\b{keyword}\b", f'<a href="#{keyword}">{keyword}</a>', text)
        
        return text
    
    def handle_internal_link(self, link):
        """Handle internal navigation within the document."""
        print(f"Navigating to: {link}")
        
        keyword_definitions = {
            "TensorFlow": "TensorFlow is an open-source machine learning framework developed by Google.",
            "PyQt": "PyQt is a set of Python bindings for Qt libraries used for GUI development.",
            "AI": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines."
        }
        keyword = link.lstrip("#")  # Remove '#' from link
        if keyword in keyword_definitions:
            QMessageBox.information(self, keyword, keyword_definitions[keyword])
        
        # Example: Scroll to a specific log entry or section
        for index in range(self.log_list.count()):
            item = self.log_list.item(index)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel) and link in label.text():
                self.log_list.scrollToItem(item)
                print(f"Scrolled to item containing: {link}")
                break 
    
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

        # Append definitions or any additional sections as needed
        html_content += """
                <hr>
                <h2>Definitions</h2>
                <ul>
                    <li><b id="TensorFlow">TensorFlow:</b> TensorFlow is an open-source machine learning framework developed by Google.</li>
                    <li><b id="PyQt">PyQt:</b> PyQt is a set of Python bindings for Qt libraries used for GUI development.</li>
                    <li><b id="AI">AI:</b> Artificial Intelligence (AI) refers to the simulation of human intelligence in machines.</li>
                </ul>
            </body>
        </html>
        """
        
        #

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



if __name__ == "__main__":
    print("Starting application...")
    app = QApplication(sys.argv)
    window = LogApp()
    window.show()
    sys.exit(app.exec())