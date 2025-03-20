from PyQt6.QtWidgets import QMenu, QLabel, QColorDialog, QApplication, QLineEdit, QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QListWidget, QInputDialog, QFileDialog, QMessageBox, QComboBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEvent, QPoint
from PyQt6.QtGui import QColor, QBrush
from datetime import datetime
import sys, os
import psutil
import clr
import json

# Load OpenHardwareMonitor library
dll_path = r"C:\Users\HR-IT-MATTHEW-PC\Desktop\Projects\Applications\Documentation\OpenHardwareMonitorLib.dll"
clr.AddReference(dll_path)
from OpenHardwareMonitor import Hardware

class LogTextEdit(QTextEdit):
    logSubmitted = pyqtSignal()
    
    def keyPressEvent(self, event):
        # Print key and modifier info for debugging.
        print("Key pressed:", event.key(), "Modifiers:", event.modifiers())
        # Check if either Return or Enter is pressed and Shift is held.
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) != 0:
            print("Shift+Enter detected")
            self.logSubmitted.emit()
            event.accept()  # Mark event as handled.
        else:
            super().keyPressEvent(event)

class HardwareMonitor(QThread):
    data_ready = pyqtSignal(str, str)  # Signal to send memory & temperature data

    def __init__(self):
        super().__init__()
        self.computer = Hardware.Computer()
        self.computer.MainboardEnabled = True
        self.computer.CPUEnabled = True
        self.computer.GPUEnabled = True
        self.computer.Open()

    def run(self):
        while True:
            memory = psutil.virtual_memory()
            memory_usage = f"MemUsage: {memory.used // (1024 * 1024)}/{memory.total // (1024 * 1024)}MB ({memory.percent}% used)"
            temperature = "Temp: N/A"

            # Fetch CPU Temperature
            for hardware in self.computer.Hardware:
                hardware.Update()  # Make sure to update first
                if hardware.HardwareType == Hardware.HardwareType.CPU:
                    for sensor in hardware.Sensors:
                        if sensor.SensorType == Hardware.SensorType.Temperature and sensor.Value is not None:
                            temperature = f"CPU Temp: {sensor.Value} °C"
                            break

            self.data_ready.emit(memory_usage, temperature)
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
        self.computer = Hardware.Computer()
        self.computer.MainboardEnabled = True
        self.computer.CPUEnabled = True
        self.computer.GPUEnabled = True
        self.computer.Open()
        
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
        
        self.log_input = QTextEdit(self)
        self.log_input.setPlaceholderText("Enter your log entry here...")
        self.log_input.installEventFilter(self)  # Install the event filter
        layout.addWidget(self.log_input)
        
        combo_layout = QHBoxLayout()
        
        self.log_type_selector = QComboBox(self)
        self.log_type_selector.addItems(["General", "Debugging"])
        self.log_type_selector.currentTextChanged.connect(self.change_log_type)
        combo_layout.addWidget(self.log_type_selector)
        
        self.category_selector = QComboBox(self)
        self.category_selector.addItems(["Problem ★", "Solution ■", "Bug ▲", "Changes ◆", "Just Details"])
        combo_layout.addWidget(self.category_selector)
        
        layout.addLayout(combo_layout)
        
        self.add_log_button = QPushButton("Add Log", self)
        self.add_log_button.clicked.connect(self.add_log)
        layout.addWidget(self.add_log_button)
        
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
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        print("UI setup complete.")

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
        dialog.setGeometry(100, 100, 300, 200)
        dialog.setFixedSize(300, 200)  # Make dialog not resizable
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
            else:
                QMessageBox.warning(dialog, "Caution", "No Name Inserted.")
                
            dialog.close()

        save_button.clicked.connect(save_customization)

        dialog.setLayout(dialog_layout)
        dialog.show()
    
    
    def update_system_info(self, memory_usage, temperature):
        self.memory_usage = memory_usage
        self.temperature = temperature

    def get_system_info(self):
        return self.memory_usage, self.temperature
    

    def add_log(self):
        log_text = self.log_input.toPlainText().strip()
        if log_text:
            print("Adding log entry...")
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%SH]")
            additional_info = ""
        
            category = self.category_selector.currentText()
            indicators = {"Problem ★": "★", "Solution ■": "■", "Bug ▲": "▲", "Changes ◆": "◆", "Just Details": ""}
            category_icon = indicators.get(category, "")
            
            if self.log_type == "Debugging":
                memory_usage, temperature = self.get_system_info()
                additional_info = f" - {memory_usage} | {temperature}"
            elif self.log_type == "General" and self.user_name:
                additional_info = f" - User: {self.user_name}"

            log_entry = f"{category_icon} {timestamp} [{self.log_type}] {log_text}{additional_info}"
            item = QListWidgetItem(log_entry)
            
            # Apply the selected text color
            if hasattr(self, 'text_color') and self.text_color:
                item.setForeground(QBrush(self.text_color))
            else:
                item.setForeground(QBrush(QColor("green")))  # Default color
            
            self.log_list.addItem(item)
            self.log_input.clear()
            print("Log entry added successfully.")
        else:
            QMessageBox.warning(self, "Invalid Input", "Log entry cannot be empty.")
            print("Failed to add log: Empty input.")

    def edit_log(self, item):
        new_text, ok = QInputDialog.getText(self, "Edit Log", "Modify your log entry:", text=item.text())
        if ok:
            if new_text.strip():
                item.setText(new_text)
                print("Log entry edited successfully.")
            else:
                QMessageBox.warning(self, "Invalid Input", "Log entry cannot be empty.")
                print("Failed to edit log: Empty input.")

    def save_logs(self):
        print("Saving logs...")
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Logs", "logs.lds", "Log Documentation System Files (*.lds)")
        if file_name:
            self.current_file = file_name
            with open(file_name, "w", encoding="utf-8") as file:
                for index in range(self.log_list.count()):
                    item = self.log_list.item(index)
                    log_text = item.text()
                    # Get the color of the log item
                    color = item.foreground().color().name()
                    # Extract the category from the log text
                    category = self.category_selector.currentText()
                    # Save the log text and color in the format: log_text|color
                    file.write(f"{log_text}|{color}|{category}\n")
            print(f"Logs saved to {file_name}")

    def open_logs(self, file_path=None):
        print("Opening logs...")
        if not file_path:  # If no file path is provided, use the file dialog
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Logs", "", "Log Documentation System Files (*.lds)")
        if file_path:  # Check if a file was selected or provided
            self.current_file = file_path
            self.log_list.clear()  # Clear the current log list
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    for line in file:
                        line = line.strip()
                        if "|" in line:
                            # Split the line into log text, color, and category
                            parts = line.rsplit("|", 2)
                            if len(parts) == 3:
                                log_text, color, category = parts
                                item = QListWidgetItem(log_text)
                                # Apply the color to the log item
                                item.setForeground(QBrush(QColor(color)))
                                self.log_list.addItem(item)
                                print(f"Loaded log: {log_text} with category: {category}")
                            else:
                                print(f"Skipping invalid line: {line}")
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
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith(".lds"):
                    # Show the drop area and hide the log list
                    self.drop_area.show()
                    self.log_list.hide()
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(".lds"):
                self.open_logs(file_path)  # Pass the file path to open_logs
                break
        else:
            QMessageBox.warning(self, "Invalid File", "Please select a valid .lds file.")
        
        # Restore the log list and hide the drop area
        self.drop_area.hide()
        self.log_list.show()
        event.acceptProposedAction()
    
    def dragLeaveEvent(self, event):
        # Restore the log list and hide the drop area if the drag is canceled
        self.drop_area.hide()
        self.log_list.show()
        event.accept()
            

if __name__ == "__main__":
    print("Starting application...")
    app = QApplication(sys.argv)
    window = LogApp()
    window.show()
    sys.exit(app.exec())