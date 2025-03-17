from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QListWidget, QInputDialog, QFileDialog, QMessageBox, QComboBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime
import sys, os
import psutil
import clr

# Load OpenHardwareMonitor library
dll_path = r"C:\Users\HR-IT-MATTHEW-PC\Desktop\Projects\Applications\Documentation\OpenHardwareMonitorLib.dll"
clr.AddReference(dll_path)
from OpenHardwareMonitor import Hardware

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
        layout.addWidget(self.log_input)
        
        self.log_type_selector = QComboBox(self)
        self.log_type_selector.addItems(["General", "Debugging"])
        self.log_type_selector.currentTextChanged.connect(self.change_log_type)
        layout.addWidget(self.log_type_selector)
        
        self.add_log_button = QPushButton("Add Log", self)
        self.add_log_button.clicked.connect(self.add_log)
        layout.addWidget(self.add_log_button)
        
        self.log_list = QListWidget(self)
        self.log_list.itemDoubleClicked.connect(self.edit_log)
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
        name, ok = QInputDialog.getText(self, "Customize", "Enter your name:", text=self.user_name)
        if ok:
            if name.strip():
                self.user_name = name.strip()
                print(f"User name set to: {self.user_name}")
            else:
                QMessageBox.warning(self, "Invalid Input", "Name cannot be empty.")
    
    
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
            
            if self.log_type == "Debugging":
                memory_usage, temperature = self.get_system_info()
                additional_info = f" - {memory_usage} | {temperature}"
            elif self.log_type == "General" and self.user_name:
                additional_info = f" - User: {self.user_name}"

            log_entry = f"{timestamp} [{self.log_type}] {log_text}{additional_info}"
            self.log_list.addItem(log_entry)
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
            with open(file_name, "w") as file:
                for index in range(self.log_list.count()):
                    file.write(self.log_list.item(index).text() + "\n")
            print(f"Logs saved to {file_name}")

    def open_logs(self):
        print("Opening logs...")
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Logs", "", "Log Documentation System Files (*.lds)")
        if file_name:
            self.current_file = file_name
            self.log_list.clear()
            with open(file_name, "r") as file:
                for line in file:
                    self.log_list.addItem(line.strip())
            print(f"Logs loaded from {file_name}")

if __name__ == "__main__":
    print("Starting application...")
    app = QApplication(sys.argv)
    window = LogApp()
    window.show()
    sys.exit(app.exec())