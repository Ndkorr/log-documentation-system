from PyQt6.QtWidgets import QMenu, QLabel, QColorDialog, QApplication, QLineEdit, QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QListWidget, QInputDialog, QFileDialog, QMessageBox, QComboBox
from PyQt6.QtCore import Qt, QSettings, QTimer, QThread, pyqtSignal, QEvent, QPoint
from PyQt6.QtGui import QColor, QBrush, QShortcut, QKeySequence
from datetime import datetime
import sys
import psutil
import json
import wmi
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlShutdown
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QTextDocument
import os
import subprocess

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
        
        # Initialize PDF-related attributes
        self.pdf_title = "Log Documentation"  # Default PDF title
        self.pdf_font_size = 12  # Default font size
        self.pdf_line_spacing = 10  # Default line spacing
        
        # Start the hardware monitoring thread
        self.hw_monitor = HardwareMonitor()
        self.hw_monitor.data_ready.connect(self.update_system_info)
        self.hw_monitor.start()
        print("LogApp initialized.")

    def init_ui(self):
        print("Setting up UI...")
        self.setWindowTitle("Log Documentation System")
        self.setGeometry(100, 100, 500, 400)
        self.setFixedSize(500, 400)  # Make window not resizable
        self.center()

        layout = QVBoxLayout()
        
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
        
        self.export_pdf_button = QPushButton("Export to PDF", self)
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        button_layout.addWidget(self.export_pdf_button)
        
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
        self.auto_save_timer.start(5 * 60 * 1000)  # 5 minutes in milliseconds
    
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
            
            if self.log_type == "Debugging":
                memory_usage = self.get_system_info()
                cpu_usage = self.cpu_usage
                gpu_usage = self.gpu_usage
                additional_info = f" - {memory_usage}, {cpu_usage}, {gpu_usage}"
            elif self.log_type == "General" and self.user_name:
                additional_info = f" - User: {self.user_name}"
            
            # Use the customized text color for the main log entry text
            main_text_color = self.text_color.name() if hasattr(self, 'text_color') else "black"  # Default to black

            
            # Create the log entry with HTML formatting
            log_entry = (
                f'<span style="color:{icon_color};">{category_icon}</span> '
                f'<span style="color:{main_text_color};">{timestamp} [{self.log_type}] {log_text}{additional_info}</span>'
            )
            
            # Create a QLabel to render the rich text
            label = QLabel()
            label.setText(log_entry)
            label.setTextFormat(Qt.TextFormat.RichText)  # Enable rich text
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
            print(f"Logs saved to {file_name}")

        self.setWindowTitle("Log Documentation System - FIle saved")  # Update title
        QTimer.singleShot(2000, lambda: self.setWindowTitle("Log Documentation System"))  # Reset after 2 seconds


    def open_logs(self, file_path=None):
        print("Opening logs...")
        if not file_path:  # If no file path is provided, use the file dialog
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Logs", "", "Log Documentation System Files (*.lds)")
        if file_path:
            self.current_file = file_path
            self.log_list.clear()  # Clear the current log list
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    for line in file:
                        line = line.strip()
                        if line:  # Ensure the line is not empty
                            # Create a QLabel and set the saved HTML content
                            label = QLabel()
                            label.setText(line)
                            label.setTextFormat(Qt.TextFormat.RichText)
                            label.setWordWrap(False)
                            label.adjustSize()
                        
                            # Create a QListWidgetItem and set its size hint to the label's size
                            item = QListWidgetItem()
                            item.setSizeHint(label.sizeHint())
                            self.log_list.addItem(item)
                            self.log_list.setItemWidget(item, label)
                            print(f"Loaded log: {line}")
                print(f"Logs loaded successfully from {file_path}")
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
        else:
            print("Auto-save skipped: No file selected")
        
        self.setWindowTitle("Log Documentation System - Auto-saved")  # Update title
        QTimer.singleShot(8000, lambda: self.setWindowTitle("Log Documentation System"))  # Reset after 2 seconds

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
      

if __name__ == "__main__":
    print("Starting application...")
    app = QApplication(sys.argv)
    window = LogApp()
    window.show()
    sys.exit(app.exec())