from PyQt6.QtWidgets import (
    QMainWindow, QFrame, QDateEdit, QSlider, 
    QMenu, QDialog, QProgressDialog, QMenuBar, 
    QLabel, QColorDialog, QApplication, QLineEdit, 
    QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QListWidget, QInputDialog, 
    QFileDialog, QMessageBox, QComboBox, QScrollArea, 
    QSizePolicy, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QSpacerItem, QStackedWidget, QTabWidget, QToolButton,
    QPlainTextEdit
    )
from PyQt6.QtCore import (
    Qt, QDate, QSize, QRect, 
    QPropertyAnimation, QSettings, QTimer, 
    QThread, pyqtSignal, QEvent, QPoint, 
    QEasingCurve, QSequentialAnimationGroup,
    )
from PyQt6.QtGui import (
    QColor, QFont, QBrush, QShortcut, 
    QKeySequence, QAction, QTextDocument, 
    QPixmap, QCursor, QIntValidator
    )
from datetime import datetime
import sys
import psutil
from typing import Optional
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
import shutil
import time


def get_config_dir():
    config_dir = os.path.join(os.getcwd(), "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return config_dir



class AnimatedPushButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        # Modern stylesheet with rounded corners.
        self.setStyleSheet("""
            QPushButton:hover {
                background-color: #E0F0FF;
            }
            QPushButton:pressed {
                background-color: #B0D4FF;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Create and assign a shadow effect.
        self.effect = QGraphicsDropShadowEffect(self)
        self.effect.setBlurRadius(0)
        self.effect.setColor(Qt.GlobalColor.magenta)
        self.effect.setOffset(0)
        self.setGraphicsEffect(self.effect)
        # Animation for the shadow's blur radius.
        self.anim = QPropertyAnimation(self.effect, b"blurRadius")
        self.anim.setDuration(300)
    
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.effect.blurRadius())
        self.anim.setEndValue(15)
        self.anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, a0):
        self.anim.stop()
        self.anim.setStartValue(self.effect.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(a0)
            

class AnimateClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None, wizard=None):
        super().__init__(text, parent)
        self.wizard = wizard  # Store the wizard reference
        # Set an initial style for padding and rounded corners (if desired)
        self.setStyleSheet("""
            font-size: 17px;
            padding: 10px;
            margin-left: 15px;
            margin-right: 15px;
            border: 1px solid transparent;
            border-radius: 15px;
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("selected", False)
        
        # Create a shadow effect that will serve as our "border"
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)  # start with no blur (no glow)
        self.shadow.setColor(Qt.GlobalColor.blue)  # choose your border/glow color
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)
        
        # Animation for the shadow's blur radius
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(300)
        
    def mousePressEvent(self, ev):
        if ev is not None and ev.button() == Qt.MouseButton.LeftButton:
            if self.wizard:  # Use the wizard reference to call the method
                self.wizard.option_clicked(self)
        
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(15)  # Adjust this value to control the "thickness" of the glow
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, a0):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(a0)
    
    def setSelected(self, selected):
        self.setProperty("selected", selected)
        if selected:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid #0078d7;
                border-radius: 15px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #d4acfa, stop: 1 #f27cc3
                    );
                font-weight: bold;
            """)
        else:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid transparent;
                border-radius: 15px;
            """)


class AnimatedClickableLabel2(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None, wizard=None):
        super().__init__(text, parent)
        self.wizard = wizard  # Store the wizard reference
        # Set an initial style for padding and rounded corners (if desired)
        self.setStyleSheet("""
            font-size: 17px;
            padding: 10px;
            margin-left: 15px;
            margin-right: 15px;
            border: 1px solid transparent;
            border-radius: 15px;
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("selected", False)
        
        # Create a shadow effect that will serve as our "border"
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)  # start with no blur (no glow)
        self.shadow.setColor(Qt.GlobalColor.blue)  # choose your border/glow color
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)
        
        # Animation for the shadow's blur radius
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(300)
        
    def mousePressEvent(self, ev):
        if ev is not None and ev.button() == Qt.MouseButton.LeftButton:
            if self.wizard:  # Use the wizard reference to call the method
                self.wizard.option_clicked2(self)
        
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(15)  # Adjust this value to control the "thickness" of the glow
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, a0):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(a0)
    
    def setSelected(self, selected):
        self.setProperty("selected", selected)
        if selected:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid #0078d7;
                border-radius: 15px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #d4acfa, stop: 1 #f27cc3
                    );
                font-weight: bold;
            """)
        else:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid transparent;
                border-radius: 15px;
            """)



class AnimatedClickableLabel3(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None, wizard=None):
        super().__init__(text, parent)
        self.wizard = wizard  # Store the wizard reference
        # Set an initial style for padding and rounded corners (if desired)
        self.setStyleSheet("""
            font-size: 17px;
            padding: 10px;
            margin-left: 15px;
            margin-right: 15px;
            border: 1px solid transparent;
            border-radius: 15px;
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("selected", False)
        
        # Create a shadow effect that will serve as our "border"
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)  # start with no blur (no glow)
        self.shadow.setColor(Qt.GlobalColor.blue)  # choose your border/glow color
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)
        
        # Animation for the shadow's blur radius
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(300)
        
    def mousePressEvent(self, ev):
        if ev is not None and ev.button() == Qt.MouseButton.LeftButton:
            if self.wizard:  # Use the wizard reference to call the method
                self.wizard.option_clicked3(self)
        
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(15)  # Adjust this value to control the "thickness" of the glow
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, a0):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(a0)
    
    def setSelected(self, selected):
        self.setProperty("selected", selected)
        if selected:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid #0078d7;
                border-radius: 15px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #d4acfa, stop: 1 #f27cc3
                    );
                font-weight: bold;
            """)
        else:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid transparent;
                border-radius: 15px;
            """)
            

class AnimatedClickableLabel4(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None, wizard=None):
        super().__init__(text, parent)
        self.wizard = wizard  # Store the wizard reference
        # Set an initial style for padding and rounded corners (if desired)
        self.setStyleSheet("""
            font-size: 17px;
            padding: 10px;
            margin-left: 15px;
            margin-right: 15px;
            border: 1px solid transparent;
            border-radius: 15px;
        """)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("selected", False)
        
        # Create a shadow effect that will serve as our "border"
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)  # start with no blur (no glow)
        self.shadow.setColor(Qt.GlobalColor.blue)  # choose your border/glow color
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)
        
        # Animation for the shadow's blur radius
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(300)
        
    def mousePressEvent(self, ev):
        if ev is not None and ev.button() == Qt.MouseButton.LeftButton:
            if self.wizard:  # Use the wizard reference to call the method
                self.wizard.option_clicked4(self)
        
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(15)  # Adjust this value to control the "thickness" of the glow
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, a0):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(a0)
    
    def setSelected(self, selected):
        self.setProperty("selected", selected)
        if selected:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid #0078d7;
                border-radius: 15px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #d4acfa, stop: 1 #f27cc3
                    );
                font-weight: bold;
            """)
        else:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid transparent;
                border-radius: 15px;
            """)

class AnimatedClickableLabel5(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, text="", parent=None, wizard=None):
        super().__init__(text, parent)
        self.wizard = wizard  # Store the wizard reference
        # Set an initial style for padding and rounded corners (if desired)
        self.setStyleSheet("""
            font-size: 17px;
            padding: 10px;
            margin-left: 15px;
            margin-right: 15px;
            border: 1px solid transparent;
            border-radius: 15px;
        """)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("selected", False)
        
        # Create a shadow effect that will serve as our "border"
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)  # start with no blur (no glow)
        self.shadow.setColor(Qt.GlobalColor.blue)  # choose your border/glow color
        self.shadow.setOffset(0)
        self.setGraphicsEffect(self.shadow)
        
        # Animation for the shadow's blur radius
        self.anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.anim.setDuration(300)
        
    def mousePressEvent(self, ev):
        if ev is not None and ev.button() == Qt.MouseButton.LeftButton:
            if self.wizard:  # Use the wizard reference to call the method
                self.wizard.option_clicked5(self)
        
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(15)  # Adjust this value to control the "thickness" of the glow
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, a0):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(a0)
    
    def setSelected(self, selected):
        self.setProperty("selected", selected)
        if selected:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid #0078d7;
                border-radius: 15px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #d4acfa, stop: 1 #f27cc3
                    );
                font-weight: bold;
            """)
        else:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid transparent;
                border-radius: 15px;
            """)

    
class SetupWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Documentation Setup Wizard")
        self.setFixedSize(550, 450)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.selected_option = None
        self.selected_log_mode = None
        
        # Initialize text box references to None
        self.name_text_box = None
        self.title_text_box = None
        
        self.text_size_box = None
        self.line_spacing_box = None
        self.dictionary_box = None
        
        self.init_ui()

    def init_ui(self):
        # Main vertical layout
        self.stacked_widget = QStackedWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stacked_widget)
        
        # Create the first page (options page).
        self.page1 = QWidget()
        page1_layout = QVBoxLayout(self.page1)
        page1_layout.setSpacing(15)
        page1_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        title_label = QLabel("Log Documentation Setup Wizard")
        title_label.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #d4acfa, stop: 1 #f27cc3
            );
            font-family: Segoe UI;
        """)
        title_label.setContentsMargins(0, 10, 0, 10)
        title_label.setFixedHeight(80)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page1_layout.addWidget(title_label)
        
        # Instruction label
        instruction_label = QLabel("I want to document:")
        instruction_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            font-family: Segoe UI;
            margin-top: 0px;
            margin-left: 25px;    
        """)
        page1_layout.addWidget(instruction_label)
        
        # Option layouts
        self.option_layouts = []
        self.options = []
        option_texts = [
            "Something general, it's up to me.",
            "Bugs and errors",
            "UI/UX Changes",
            "Others:"
        ]
        for text in option_texts:
            # Create a vertical layout for each option
            option_layout = QVBoxLayout()
            option_layout.setSpacing(5)
            
            # Replace OptionLabel with AnimatedClickableLabel
            option_label = AnimateClickableLabel(text, self, wizard=self)
            option_label.clicked.connect(lambda text=text: self.option_clicked(text))
            option_layout.addWidget(option_label)
            
            page1_layout.addLayout(option_layout)
            self.option_layouts.append(option_layout)
            self.options.append(option_label)
        
        # Add a spacer before the buttons to push them to the bottom.
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        page1_layout.addItem(spacer)
        
        # Horizontal layout for Next / Cancel buttons.
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.next_button = AnimatedPushButton("Next")
        self.next_button.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 5px;
            font-size: 14px;
            padding: 6px 12px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
        self.next_button.setEnabled(False)  # Disable by default
        self.next_button.clicked.connect(self.on_next_clicked)
        btn_layout.addWidget(self.next_button)
        
        self.cancel_button = AnimatedPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 15px;
            font-size: 14px;
            padding: 6px 12px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_button)
        
        page1_layout.addLayout(btn_layout)
        self.stacked_widget.addWidget(self.page1)
        
        # Create the second page (new frame).
        self.page2 = QWidget()
        page2_layout = QVBoxLayout(self.page2)
        page2_layout.setSpacing(15)
        page2_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        title_label2 = QLabel("Log Documentation Setup Wizard")
        title_label2.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #d4acfa, stop: 1 #f27cc3
            );
            font-family: Segoe UI;
        """)
        title_label2.setContentsMargins(0, 10, 0, 10)
        title_label2.setFixedHeight(80)
        title_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page2_layout.addWidget(title_label2)
        
        # Instruction label
        instruction_label2 = QLabel("On each lds, I want to:")
        instruction_label2.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            font-family: Segoe UI;
            margin-top: 0px;
            margin-left: 25px;    
        """)
        page2_layout.addWidget(instruction_label2)
        
        # Option layouts
        self.option_layouts2 = []
        self.options2 = []
        option_texts2 = [
            "Set my name to",
            "Set document title to",
            "Proceed on default"
        ]
        for text in option_texts2:
            # Create a vertical layout for each option
            option_layout2 = QVBoxLayout()
            option_layout2.setSpacing(5)
    
            # Replace OptionLabel with AnimatedClickableLabel2
            option_label2 = AnimatedClickableLabel2(text, self, wizard=self)
            option_label2.clicked.connect(lambda text=text: self.option_clicked2(text))
            option_layout2.addWidget(option_label2)
    
            page2_layout.addLayout(option_layout2)
            self.option_layouts2.append(option_layout2)
            self.options2.append(option_label2)

        # Add a spacer before the navigation buttons to push them to the bottom.
        spacer2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        page2_layout.addItem(spacer2)
        
        
        # Navigation buttons for page2.
        btn_layout2 = QHBoxLayout()
        btn_layout2.addStretch()
        self.back_button = AnimatedPushButton("Back")
        self.back_button.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 5px;
            font-size: 14px;
            padding: 6px 12px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
        self.back_button.clicked.connect(self.on_back_clicked)
        btn_layout2.addWidget(self.back_button)

        self.next_button2 = AnimatedPushButton("Next")
        self.next_button2.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 15px;
            font-size: 14px;
            padding: 6px 18px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
        self.next_button2.setEnabled(False)  # Disable by default
        self.next_button2.clicked.connect(self.on_next_clicked2)
        btn_layout2.addWidget(self.next_button2)

        page2_layout.addLayout(btn_layout2)
        self.stacked_widget.addWidget(self.page2)
        
        # Create the third page (options page).
        self.page3 = QWidget()
        page3_layout = QVBoxLayout(self.page3)
        page3_layout.setSpacing(15)
        page3_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        title_label3 = QLabel("Log Documentation Setup Wizard")
        title_label3.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #d4acfa, stop: 1 #f27cc3
            );
            font-family: Segoe UI;
        """)
        title_label3.setContentsMargins(0, 10, 0, 10)
        title_label3.setFixedHeight(80)
        title_label3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page3_layout.addWidget(title_label3)
        
        # Instruction label
        instruction_label3 = QLabel("On exporting document, I want to:")
        instruction_label3.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            font-family: Segoe UI;
            margin-top: 0px;
            margin-left: 25px;    
        """)
        page3_layout.addWidget(instruction_label3)
        
        # Option layouts
        self.option_layouts3 = []
        self.options3 = []
        option_texts3 = [
            "Set the text size to",
            "Set the line spacing to",
            "Proceed on default"
        ]
        for text in option_texts3:
            # Create a vertical layout for each option
            option_layout3 = QVBoxLayout()
            option_layout3.setSpacing(5)
    
            # Replace OptionLabel with AnimatedClickableLabel3
            option_label3 = AnimatedClickableLabel3(text, self, wizard=self)
            option_label3.clicked.connect(lambda text=text: self.option_clicked3(text))
            option_layout3.addWidget(option_label3)
    
            page3_layout.addLayout(option_layout3)
            self.option_layouts3.append(option_layout3)
            self.options3.append(option_label3)

        # Add a spacer before the navigation buttons to push them to the bottom.
        spacer3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        page3_layout.addItem(spacer3)
        
        # Navigation buttons for page2.
        btn_layout3 = QHBoxLayout()
        btn_layout3.addStretch()
        self.back_button2 = AnimatedPushButton("Back")
        self.back_button2.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 5px;
            font-size: 14px;
            padding: 6px 12px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
        self.back_button2.clicked.connect(self.on_back_clicked2)
        btn_layout3.addWidget(self.back_button2)

        self.next_button3 = AnimatedPushButton("Next")
        self.next_button3.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 15px;
            font-size: 14px;
            padding: 6px 18px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
        self.next_button3.setEnabled(False)  # Disable by default
        self.next_button3.clicked.connect(self.on_next_clicked3)
        btn_layout3.addWidget(self.next_button3)
        
        page3_layout.addLayout(btn_layout3)
        self.stacked_widget.addWidget(self.page3)
        
        # Create the fourth page (new frame).
        self.page4 = QWidget()
        page4_layout = QVBoxLayout(self.page4)
        page4_layout.setSpacing(15)
        page4_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        title_label4 = QLabel("Log Documentation Setup Wizard")
        title_label4.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #d4acfa, stop: 1 #f27cc3
            );
            font-family: Segoe UI;
        """)
        title_label4.setContentsMargins(0, 10, 0, 10)
        title_label4.setFixedHeight(80)
        title_label4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page4_layout.addWidget(title_label4)
        
        # Instruction label
        instruction_label4 = QLabel("On exporting document, I want to:")
        instruction_label4.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            font-family: Segoe UI;
            margin-top: 0px;
            margin-left: 25px;    
        """)
        page4_layout.addWidget(instruction_label4)
        
        # Option layouts
        self.option_layouts4 = []
        self.options4 = []
        option_texts4 = [
            "Set font to:",
            "Proceed on default"
        ]
        for text in option_texts4:
            # Create a vertical layout for each option
            option_layout4 = QVBoxLayout()
            option_layout4.setSpacing(5)
    
            # Replace OptionLabel with AnimatedClickableLabel2
            option_label4 = AnimatedClickableLabel4(text, self, wizard=self)
            option_label4.clicked.connect(lambda text=text: self.option_clicked4(text))
            option_layout4.addWidget(option_label4)
    
            page4_layout.addLayout(option_layout4)
            self.option_layouts4.append(option_layout4)
            self.options4.append(option_label4)

        # Add a spacer before the navigation buttons to push them to the bottom.
        spacer4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        page4_layout.addItem(spacer4)
        
        # Navigation buttons for page2.
        btn_layout4 = QHBoxLayout()
        btn_layout4.addStretch()
        self.back_button3 = AnimatedPushButton("Back")
        self.back_button3.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 5px;
            font-size: 14px;
            padding: 6px 12px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
        self.back_button3.clicked.connect(self.on_back_clicked3)
        btn_layout4.addWidget(self.back_button3)

        self.next_button4 = AnimatedPushButton("Next")
        self.next_button4.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 15px;
            font-size: 14px;
            padding: 6px 18px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
        self.next_button4.setEnabled(False)  # Disable by default
        self.next_button4.clicked.connect(self.on_next_clicked4)
        btn_layout4.addWidget(self.next_button4)
        
        page4_layout.addLayout(btn_layout4)
        self.stacked_widget.addWidget(self.page4)
        
        
        # Create the fifth/last page (new frame).
        self.page5 = QWidget()
        page5_layout = QVBoxLayout(self.page5)
        page5_layout.setSpacing(15)
        page5_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        title_label5 = QLabel("Log Documentation Setup Wizard")
        title_label5.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #d4acfa, stop: 1 #f27cc3
            );
            font-family: Segoe UI;
        """)
        title_label5.setContentsMargins(0, 10, 0, 10)
        title_label5.setFixedHeight(80)
        title_label5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page5_layout.addWidget(title_label5)
        
        # Instruction label
        instruction_label5 = QLabel("This application contains a built-in dictionary on\neach log mode. Do you want to create your \nown?:")
        instruction_label5.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            font-family: Segoe UI;
            margin-top: 0px;
            margin-left: 25px;    
        """)
        page5_layout.addWidget(instruction_label5)
        
        # Option layouts
        self.option_layouts5 = []
        self.options5 = []
        option_texts5 = [
            "Yes",
            "No, Use the default"
        ]
        for text in option_texts5:
            # Create a vertical layout for each option
            option_layout5 = QVBoxLayout()
            option_layout5.setSpacing(5)
    
            # Replace OptionLabel with AnimatedClickableLabel2
            option_label5 = AnimatedClickableLabel5(text, self, wizard=self)
            option_label5.clicked.connect(lambda text=text: self.option_clicked5(text))
            option_layout5.addWidget(option_label5)
    
            page5_layout.addLayout(option_layout5)
            self.option_layouts5.append(option_layout5)
            self.options5.append(option_label5)

        # Add a spacer before the navigation buttons to push them to the bottom.
        spacer5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        page5_layout.addItem(spacer5)
        
        # Navigation buttons for page2.
        btn_layout5 = QHBoxLayout()
        btn_layout5.addStretch()
        self.back_button4 = AnimatedPushButton("Back")
        self.back_button4.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 5px;
            font-size: 14px;
            padding: 6px 12px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
        self.back_button4.clicked.connect(self.on_back_clicked4)
        btn_layout5.addWidget(self.back_button4)

        self.next_button5 = AnimatedPushButton("Finish")
        self.next_button5.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 15px;
            font-size: 14px;
            padding: 6px 15px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
        self.next_button5.setEnabled(False)  # Disable by default
        self.next_button5.clicked.connect(self.on_next_clicked5)
        btn_layout5.addWidget(self.next_button5)
        
        page5_layout.addLayout(btn_layout5)
        self.stacked_widget.addWidget(self.page5)
    
    def option_clicked(self, clicked_option):
        # Unselect all options and remove subtext labels.
        for option, layout in zip(self.options, self.option_layouts):
            option.setSelected(False)
            if layout.count() > 1:  # Remove subtext if it exists
                subtext_label = layout.itemAt(1).widget()
                layout.removeWidget(subtext_label)
                subtext_label.deleteLater()
        
        # Select the clicked option.
        clicked_option.setSelected(True)
        self.selected_option = clicked_option.text()
        self.selected_log_mode = clicked_option.text()
        
        # Add the subtext label below the clicked option.
        self.add_subtext(clicked_option)
    
    def add_subtext(self, clicked_option):
        subtext_map = {
            "Something general, it's up to me.": "You can document anything you want.",
            "Bugs and errors": "Document issues and errors encountered.",
            "UI/UX Changes": "Document changes made to the user interface or experience.",
            "Others:": ""
        }
        subtext = subtext_map.get(clicked_option.text(), "")
        
        if clicked_option.text() == "Others:":
            # Combobox as a subtext
            subtext_label = QComboBox()
            subtext_label.addItems([
                "myExercise",
                "Persona note",
                "myWiki"
            ])
            subtext_label.setStyleSheet("""                                  
                QComboBox {
                    margin-left: 25px;
                    margin-right: 105px;
                    margin-bottom: 0px;
                    font-size: 15px;
                    font-family: 'Segoe UI';
                    background: #f7f7fa;
                    border: 1.5px solid #a78bfa;
                    border-radius: 8px;
                    padding: 4px 12px;
                    min-width: 0px;
                    color: #333;
                }
                QComboBox::drop-down {
                    border: none;
                    background: #e0e7ff;
                    width: 28px;
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                }
                QComboBox QAbstractItemView {
                    margin-left: 25px;
                    font-size: 15px;
                    background: #fff;
                    border: 1px solid #a78bfa;
                    selection-background-color: #e0e7ff;
                    selection-color: #333;
                }
            """)
            subtext_label.setFixedWidth(325)
            subtext_label.setFixedHeight(30)
            
            def validate_combo():
                # Enable Next if a valid selection is made (not -1)
                self.next_button.setEnabled(subtext_label.currentIndex() != -1)
                if subtext_label.currentIndex() != -1:
                    self.next_button.setStyleSheet("""
                        margin-bottom: 15px;
                        margin-right: 5px;
                        font-size: 14px;
                        padding: 6px 12px;
                        border: 2px solid #0078d7;
                        border-radius: 8px;
                        color: black;
                        background: qlineargradient(
                            x1: 0, y1: 0, x2: 1, y2: 0,
                            stop: 0 #42f5d7, stop: 1 #14b7fc
                        );
                    """)
                else:
                    self.next_button.setStyleSheet("""
                        margin-bottom: 15px;
                        margin-right: 5px;
                        font-size: 14px;
                        padding: 6px 12px;
                        border: 2px solid #0078d7;
                        border-radius: 8px;
                        color: black;
                    """)
            subtext_label.currentIndexChanged.connect(validate_combo)
            validate_combo()  # Initial validation
        
        else:
            subtext_label = QLabel(subtext)
            subtext_label.setStyleSheet("""
                font-size: 14px;
                font-style: italic;
                margin-left: 25px;
                color: #555555;
            """)
        
            # Enable the "Next" button.
            self.next_button.setEnabled(True)
            self.next_button.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 5px;
                font-size: 14px;
                padding: 6px 12px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #42f5d7, stop: 1 #14b7fc
                );
            """)
        
        # Apply an opacity effect for the fade-in animation.
        opacity_effect = QGraphicsOpacityEffect(subtext_label)
        subtext_label.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0)
        
        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setDuration(500)  # Duration in milliseconds
        fade_anim.setStartValue(0)
        fade_anim.setEndValue(1)
        fade_anim.start()  # Animation will be garbage collected after finishing
        
        # Keep a reference to avoid premature garbage collection.
        # Store the animation reference in a dictionary to avoid garbage collection
        if not hasattr(self, "_animations"):
            self._animations = {}
        self._animations[subtext_label] = fade_anim
        
        
        subtext_label.setVisible(True)
        # Find the layout of the clicked option and add the subtext label.
        for option, layout in zip(self.options, self.option_layouts):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                break
    
    def option_clicked2(self, clicked_option):
        # If "Proceed on default" is clicked, clear all selections.
        if clicked_option.text() == "Proceed on default":
            for option, layout in zip(self.options2, self.option_layouts2):
                option.setSelected(False)
                if layout.count() > 1:  # Remove subtext if it exists
                    subtext_label = layout.itemAt(1).widget()
                    layout.removeWidget(subtext_label)
                    subtext_label.deleteLater()
            
            # Clear references to text boxes
            self.name_text_box = None
            self.title_text_box = None       
            # Select only "Proceed on default".
            clicked_option.setSelected(True)
            self.selected_option = clicked_option.text()
            self.add_subtext2(clicked_option)
            self.validate_both_inputs()
            self.next_button2.setEnabled(True)
            # Enable the "Next" button.
            self.next_button2.setEnabled(True)
            self.next_button2.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 18px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #42f5d7, stop: 1 #14b7fc
                );
            """)
            return

        # If any other option is clicked, toggle its selection.
        if clicked_option.property("selected"):
            # Deselect the option and remove its subtext.
            clicked_option.setSelected(False)
            for option, layout in zip(self.options2, self.option_layouts2):
                if option == clicked_option and layout.count() > 1:
                    subtext_label = layout.itemAt(1).widget()
                    layout.removeWidget(subtext_label)
                    subtext_label.deleteLater()
                    # Clear the reference if this was the text size or line spacing box
                    if option.text() == "Set my name to":
                        self.name_text_box = None
                    elif option.text() == "Set document title to":
                        self.title_text_box = None
                    break
        else:
            # Select the option and add its subtext.
            clicked_option.setSelected(True)
            self.add_subtext2(clicked_option)

        # Ensure "Proceed on default" is deselected if any other option is selected.
        for option, layout in zip(self.options2, self.option_layouts2):
            if option.text() == "Proceed on default":
                if option.property("selected"):
                    # Remove subtext if "Proceed on default" is deselected.
                    if layout.count() > 1:
                        subtext_label = layout.itemAt(1).widget()
                        layout.removeWidget(subtext_label)
                        subtext_label.deleteLater()
                option.setSelected(False)
                break
        self.validate_both_inputs()

    def add_subtext2(self, clicked_option):
        subtext_map = {
            "Set my name to": "",
            "Set document title to": "",
            "Proceed on default": "Continue with the default settings."
        }
        subtext = subtext_map.get(clicked_option.text(), "")
        # Handle "Proceed on default" differently (no text box).
        if clicked_option.text() == "Proceed on default":
            # Clear references to text boxes since they are being removed.
            self.name_text_box = None
            self.title_text_box = None
            
            subtext_label = QLabel(subtext)
            subtext_label.setEnabled(True)
            subtext_label.setStyleSheet("""
                font-size: 14px;
                font-style: italic;
                margin-left: 25px;
                color: #555555;
            """)
            # Enable the "Next" button.
            self.next_button2.setEnabled(True)
            self.next_button2.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 18px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #42f5d7, stop: 1 #14b7fc
                );
            """)
        else:
            # For other options, use a text box.
            subtext_label = QPlainTextEdit(subtext)
            subtext_label.setStyleSheet("""
                font-size: 14px;
                font-style: italic;
                margin-left: 25px;
                margin-right: 105px;
                border: none;
                color: #555555;
            """)
            subtext_label.setFixedHeight(25)  # Adjust height to match QLabel's appearance
            subtext_label.setPlaceholderText("Enter your input here...")  # Add placeholder text
            subtext_label.setFocus()
            
            a = clicked_option.text() == "Set my name to"
            
            # Store references to the text boxes for validation.
            if clicked_option.text() == "Set my name to":
                self.next_button2.setEnabled(False)
                self.next_button2.setStyleSheet("""
                    margin-bottom: 15px;
                    margin-right: 15px;
                    font-size: 14px;
                    padding: 6px 18px;
                    border: 2px solid #0078d7;
                    border-radius: 8px;
                    color: black;
                """)
                self.name_text_box = subtext_label
                
            elif clicked_option.text() == "Set document title to":
                self.next_button2.setEnabled(False)
                self.next_button2.setStyleSheet("""
                    margin-bottom: 15px;
                    margin-right: 15px;
                    font-size: 14px;
                    padding: 6px 18px;
                    border: 2px solid #0078d7;
                    border-radius: 8px;
                    color: black;
                """)
                self.title_text_box = subtext_label

            # Connect the textChanged signal to the validation method.
            subtext_label.textChanged.connect(self.validate_both_inputs)
                
            
        
        # Apply an opacity effect for the fade-in animation.
        opacity_effect = QGraphicsOpacityEffect(subtext_label)
        subtext_label.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0)
    
        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setDuration(500)  # Duration in milliseconds
        fade_anim.setStartValue(0)
        fade_anim.setEndValue(1)
        fade_anim.start()  # Animation will be garbage collected after finishing
    
        # Keep a reference to avoid premature garbage collection.
        if not hasattr(self, "_animations"):
            self._animations = {}
        self._animations[subtext_label] = fade_anim
    
        subtext_label.setVisible(True)
        # Find the layout of the clicked option and add the subtext label.
        for option, layout in zip(self.options2, self.option_layouts2):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                break
    
    def option_clicked3(self, clicked_option):
        # If "Proceed on default" is clicked, clear all selections.
        if clicked_option.text() == "Proceed on default":
            for option, layout in zip(self.options3, self.option_layouts3):
                option.setSelected(False)
                if layout.count() > 1:  # Remove subtext if it exists
                    subtext_label = layout.itemAt(1).widget()
                    layout.removeWidget(subtext_label)
                    subtext_label.deleteLater()
                    
            # Clear references to text boxes
            self.text_size_box = None
            self.line_spacing_box = None        
            # Select only "Proceed on default".
            clicked_option.setSelected(True)
            self.selected_option = clicked_option.text()
            self.add_subtext3(clicked_option)
            self.validate_both_inputs2()
            # Enable the "Next" button.
            self.next_button3.setEnabled(True)
            self.next_button3.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 18px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #42f5d7, stop: 1 #14b7fc
                );
            """)
            return

        # If any other option is clicked, toggle its selection.
        if clicked_option.property("selected"):
            # Deselect the option and remove its subtext.
            clicked_option.setSelected(False)
            for option, layout in zip(self.options3, self.option_layouts3):
                if option == clicked_option and layout.count() > 1:
                    subtext_label = layout.itemAt(1).widget()
                    layout.removeWidget(subtext_label)
                    subtext_label.deleteLater()
                    # Clear the reference if this was the text size or line spacing box
                    if option.text() == "Set the text size to":
                        self.text_size_box = None
                    elif option.text() == "Set the line spacing to":
                        self.line_spacing_box = None
                    break
            self.validate_both_inputs2()
        else:
            # Select the option and add its subtext.
            clicked_option.setSelected(True)
            self.add_subtext3(clicked_option)

        # Ensure "Proceed on default" is deselected if any other option is selected.
        for option, layout in zip(self.options3, self.option_layouts3):
            if option.text() == "Proceed on default":
                if option.property("selected"):
                    # Remove subtext if "Proceed on default" is deselected.
                    if layout.count() > 1:
                        subtext_label = layout.itemAt(1).widget()
                        layout.removeWidget(subtext_label)
                        subtext_label.deleteLater()
                option.setSelected(False)
                break

    def add_subtext3(self, clicked_option):
        subtext_map = {
            "Set the text size to": "",
            "Set the line spacing to": "",
            "Proceed on default": "Continue with the default settings."
        }
        subtext = subtext_map.get(clicked_option.text(), "")
        # Handle "Proceed on default" differently (no text box).
        if clicked_option.text() == "Proceed on default":
            # Clear references to text boxes since they are being removed.
            self.text_size_box = None
            self.line_spacing_box = None
            
            subtext_label = QLabel(subtext)
            subtext_label.setEnabled(True)
            subtext_label.setStyleSheet("""
                font-size: 14px;
                font-style: italic;
                margin-left: 25px;
                color: #555555;
            """)
            # Enable the "Next" button.
            self.next_button3.setEnabled(True)
            self.next_button3.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 18px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #42f5d7, stop: 1 #14b7fc
                );
            """)
        else:
            # Use QLineEdit for numeric input
            subtext_label = QLineEdit("")
            subtext_label.setValidator(QIntValidator(1, 99, self))  # Only allow numbers
            subtext_label.setStyleSheet("""
                font-size: 14px;
                font-style: italic;
                margin-left: 25px;
                margin-right: 105px;
                border: none;
                color: #555555;
            """)
            subtext_label.setFixedHeight(25)  # Adjust height to match QLabel's appearance
            subtext_label.setPlaceholderText("Enter your input here...")  # Add placeholder text
            subtext_label.setFocus()
            
            
            # Store references to the text boxes for validation.
            if clicked_option.text() == "Set the text size to":
                self.next_button3.setEnabled(False)
                self.next_button3.setStyleSheet("""
                    margin-bottom: 15px;
                    margin-right: 15px;
                    font-size: 14px;
                    padding: 6px 18px;
                    border: 2px solid #0078d7;
                    border-radius: 8px;
                    color: black;
                """)
                self.text_size_box = subtext_label
                
            elif clicked_option.text() == "Set the line spacing to":
                self.next_button3.setEnabled(False)
                self.next_button3.setStyleSheet("""
                    margin-bottom: 15px;
                    margin-right: 15px;
                    font-size: 14px;
                    padding: 6px 18px;
                    border: 2px solid #0078d7;
                    border-radius: 8px;
                    color: black;
                """)
                self.line_spacing_box = subtext_label

            # Connect the textChanged signal to the validation method.
            subtext_label.textChanged.connect(self.validate_both_inputs2)
                
            
        
        # Apply an opacity effect for the fade-in animation.
        opacity_effect = QGraphicsOpacityEffect(subtext_label)
        subtext_label.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0)
    
        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setDuration(500)  # Duration in milliseconds
        fade_anim.setStartValue(0)
        fade_anim.setEndValue(1)
        fade_anim.start()  # Animation will be garbage collected after finishing
    
        # Keep a reference to avoid premature garbage collection.
        if not hasattr(self, "_animations"):
            self._animations = {}
        self._animations[subtext_label] = fade_anim
        
        subtext_label.setVisible(True)
        # Remove any existing subtext for the clicked option.
        for option, layout in zip(self.options3, self.option_layouts3):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                break
    
    def option_clicked4(self, clicked_option):
        # If "Proceed on default" is clicked, clear all selections and text box.
        if clicked_option.text() == "Proceed on default":
            for option, layout in zip(self.options4, self.option_layouts4):
                option.setSelected(False)
                if layout.count() > 1:
                    subtext_label = layout.itemAt(1).widget()
                    layout.removeWidget(subtext_label)
                    subtext_label.deleteLater()
            
            clicked_option.setSelected(True)
            self.add_subtext4(clicked_option)
            self.selected_option = clicked_option.text()
            self.next_button4.setEnabled(True)
            self.next_button4.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 18px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #42f5d7, stop: 1 #14b7fc
                );
            """)
            return

        # If the editable option is clicked
        if clicked_option.property("selected"):
            # Deselect and remove subtext
            clicked_option.setSelected(False)
            for option, layout in zip(self.options4, self.option_layouts4):
                if option == clicked_option and layout.count() > 1:
                    subtext_label = layout.itemAt(1).widget()
                    layout.removeWidget(subtext_label)
                    subtext_label.deleteLater()
                    break
            self.next_button4.setEnabled(False)
            self.next_button4.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 18px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
            """)
        else:
            # Select and add subtext (text box)
            clicked_option.setSelected(True)
            self.add_subtext4(clicked_option)
            # Deselect "Proceed on default"
            for option, layout in zip(self.options4, self.option_layouts4):
                if option.text() == "Proceed on default":
                    if option.property("selected"):
                        if layout.count() > 1:
                            subtext_label = layout.itemAt(1).widget()
                            layout.removeWidget(subtext_label)
                            subtext_label.deleteLater()
                    option.setSelected(False)
                    break

    def add_subtext4(self, clicked_option):
        if clicked_option.text() == "Proceed on default":
            subtext_label = QLabel("Continue with the default settings.")
            subtext_label.setStyleSheet("""
                font-size: 14px;
                font-style: italic;
                margin-left: 25px;
                color: #555555;
            """)
            # Enable the "Next" button.
            self.next_button4.setEnabled(True)
            self.next_button4.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 18px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #42f5d7, stop: 1 #14b7fc
                );
            """)
        else:
            # Combobox as a subtext
            subtext_label = QComboBox()
            subtext_label.addItems([
                "Arial",
                "Times New Roman",
                "Courier New",
                "Verdana",
                "Tahoma",
                "Segoe UI",
                "Calibri",
                "Helvetica",
                "Georgia",
                "Consolas"
            ])
            subtext_label.setStyleSheet("""                                  
                QComboBox {
                    margin-left: 25px;
                    font-size: 15px;
                    font-family: 'Segoe UI';
                    background: #f7f7fa;
                    border: 1.5px solid #a78bfa;
                    border-radius: 8px;
                    padding: 4px 12px;
                    min-width: 200px;
                    color: #333;
                }
                QComboBox::drop-down {
                    border: none;
                    background: #e0e7ff;
                    width: 28px;
                    border-top-right-radius: 8px;
                    border-bottom-right-radius: 8px;
                }
                QComboBox QAbstractItemView {
                    margin-left: 25px;
                    font-size: 15px;
                    background: #fff;
                    border: 1px solid #a78bfa;
                    selection-background-color: #e0e7ff;
                    selection-color: #333;
                }
            """)
            subtext_label.setFixedWidth(125)
            subtext_label.setFixedHeight(30)
            
            def validate_combo():
                # Enable Next if a valid selection is made (not -1)
                self.next_button4.setEnabled(subtext_label.currentIndex() != -1)
                if subtext_label.currentIndex() != -1:
                    self.next_button4.setStyleSheet("""
                        margin-bottom: 15px;
                        margin-right: 15px;
                        font-size: 14px;
                        padding: 6px 18px;
                        border: 2px solid #0078d7;
                        border-radius: 8px;
                        color: black;
                        background: qlineargradient(
                            x1: 0, y1: 0, x2: 1, y2: 0,
                            stop: 0 #42f5d7, stop: 1 #14b7fc
                        );
                    """)
                else:
                    self.next_button.setStyleSheet("""
                        margin-bottom: 15px;
                        margin-right: 15px;
                        font-size: 14px;
                        padding: 6px 15px;
                        border: 2px solid #0078d7;
                        border-radius: 8px;
                        color: black;
                    """)
            subtext_label.currentIndexChanged.connect(validate_combo)
            validate_combo()  # Initial validation

        # Fade-in animation (optional, as in previous pages)
        opacity_effect = QGraphicsOpacityEffect(subtext_label)
        subtext_label.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0)
        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setDuration(500)
        fade_anim.setStartValue(0)
        fade_anim.setEndValue(1)
        fade_anim.start()
        if not hasattr(self, "_animations"):
            self._animations = {}
        self._animations[subtext_label] = fade_anim

        subtext_label.setVisible(True)
        for option, layout in zip(self.options4, self.option_layouts4):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                break
    
    def option_clicked5(self, clicked_option):
        # If "Proceed on default" is clicked, clear all selections and text box.
        if clicked_option.text() == "No, Use the default":
            for option, layout in zip(self.options5, self.option_layouts5):
                option.setSelected(False)
                if layout.count() > 1:
                    subtext_label = layout.itemAt(1).widget()
                    layout.removeWidget(subtext_label)
                    subtext_label.deleteLater()
            self.dictionary_box = None
            clicked_option.setSelected(True)
            self.add_subtext5(clicked_option)
            self.validate_font_input2()
            self.next_button5.setEnabled(True)
            self.next_button5.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 15px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #42f5d7, stop: 1 #14b7fc
                );
            """)
            return

        # If the editable option is clicked
        if clicked_option.property("selected"):
            # Deselect and remove subtext
            clicked_option.setSelected(False)
            for option, layout in zip(self.options5, self.option_layouts5):
                if option == clicked_option and layout.count() > 1:
                    subtext_label = layout.itemAt(1).widget()
                    layout.removeWidget(subtext_label)
                    subtext_label.deleteLater()
                    self.dictionary_box = None
                    break
            self.next_button5.setEnabled(False)
            self.next_button5.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 15px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
            """)
        else:
            # Select and add subtext (text box)
            clicked_option.setSelected(True)
            self.add_subtext5(clicked_option)
            # Deselect "Proceed on default"
            for option, layout in zip(self.options5, self.option_layouts5):
                if option.text() == "No, Use the default":
                    if option.property("selected"):
                        if layout.count() > 1:
                            subtext_label = layout.itemAt(1).widget()
                            layout.removeWidget(subtext_label)
                            subtext_label.deleteLater()
                    option.setSelected(False)
                    break

    def add_subtext5(self, clicked_option):
        if clicked_option.text() == "No, Use the default":
            self.dictionary_box = None
            subtext_label = QLabel("Continue with the default settings.")
            subtext_label.setStyleSheet("""
                font-size: 14px;
                font-style: italic;
                margin-left: 25px;
                color: #555555;
            """)
        else:
            subtext_label = QPlainTextEdit("")
            subtext_label.setStyleSheet("""
                font-size: 14px;
                font-style: italic;
                margin-left: 25px;
                margin-right: 105px;
                border: none;
                color: #555555;
            """)
            subtext_label.setFixedHeight(25)
            subtext_label.setPlaceholderText("Enter dictionary name...")
            subtext_label.setFocus()
            self.dictionary_box = subtext_label
            subtext_label.textChanged.connect(self.validate_font_input2)
            self.next_button5.setEnabled(False)
            self.next_button5.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 15px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
            """)

        # Fade-in animation (optional, as in previous pages)
        opacity_effect = QGraphicsOpacityEffect(subtext_label)
        subtext_label.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0)
        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setDuration(500)
        fade_anim.setStartValue(0)
        fade_anim.setEndValue(1)
        fade_anim.start()
        if not hasattr(self, "_animations"):
            self._animations = {}
        self._animations[subtext_label] = fade_anim

        subtext_label.setVisible(True)
        for option, layout in zip(self.options5, self.option_layouts5):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                break
    
    
    def on_next_clicked(self):
        self.stacked_widget.setCurrentWidget(self.page2)
    
    def on_back_clicked(self):
        # Optionally reset or preserve state when going back.
        self.stacked_widget.setCurrentWidget(self.page1)
    
    def on_back_clicked2(self):
        # Optionally reset or preserve state when going back.
        self.stacked_widget.setCurrentWidget(self.page2)
        
    def on_back_clicked3(self):
        # Optionally reset or preserve state when going back.
        self.stacked_widget.setCurrentWidget(self.page3)
    
    def on_back_clicked4(self):
        # Optionally reset or preserve state when going back.
        self.stacked_widget.setCurrentWidget(self.page4)
    
    def on_next_clicked2(self):
        self.stacked_widget.setCurrentWidget(self.page3)
    
    def on_next_clicked3(self):
        self.stacked_widget.setCurrentWidget(self.page4)
    
    def on_next_clicked4(self):
        self.stacked_widget.setCurrentWidget(self.page5)
        
    def on_next_clicked5(self):
        self.accept()
    
    def validate_both_inputs(self):
        # Check if the text boxes exist and are filled.
        name_filled = self.name_text_box and self.name_text_box.toPlainText().strip()
        title_filled = self.title_text_box and self.title_text_box.toPlainText().strip()

        # Enable the "Next" button if:
        # - Only one option is selected and its text box is filled, OR
        # - Both options are selected and both text boxes are filled.
        if (self.name_text_box and name_filled) or (self.title_text_box and title_filled):
            if (self.name_text_box and self.title_text_box and name_filled and title_filled) or \
               (not self.name_text_box or not self.title_text_box):
                self.next_button2.setEnabled(True)
                self.next_button2.setStyleSheet("""
                    margin-bottom: 15px;
                    margin-right: 15px;
                    font-size: 14px;
                    padding: 6px 18px;
                    border: 2px solid #0078d7;
                    border-radius: 8px;
                    color: black;
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #42f5d7, stop: 1 #14b7fc
                    );
                """)
                return

        # Disable the "Next" button if the conditions are not met.
        self.next_button2.setEnabled(False)
        self.next_button2.setStyleSheet("""
            margin-bottom: 15px;
            margin-right: 15px;
            font-size: 14px;
            padding: 6px 18px;
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
        """)
    
    def validate_both_inputs2(self):
        text_size_selected = self.text_size_box is not None
        line_spacing_selected = self.line_spacing_box is not None
        text_size_filled = text_size_selected and self.text_size_box and self.text_size_box.text().strip()
        line_spacing_filled = line_spacing_selected and self.line_spacing_box and self.line_spacing_box.text().strip()

        enable = False
        if text_size_selected and line_spacing_selected:
            enable = bool(text_size_filled and line_spacing_filled)
        elif text_size_selected:
            enable = bool(text_size_filled)
        elif line_spacing_selected:
            enable = bool(line_spacing_filled)
        # If neither is selected, "Proceed on default" must be selected, which is handled elsewhere

        if enable:
            self.next_button3.setEnabled(True)
            self.next_button3.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 18px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #42f5d7, stop: 1 #14b7fc
                );
            """)
        else:
            self.next_button3.setEnabled(False)
            self.next_button3.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 18px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
            """) 

    def validate_font_input2(self):
        if self.dictionary_box and self.dictionary_box.toPlainText().strip():
            self.next_button5.setEnabled(True)
            self.next_button5.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 15px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #42f5d7, stop: 1 #14b7fc
                );
            """)
        else:
            self.next_button5.setEnabled(False)
            self.next_button5.setStyleSheet("""
                margin-bottom: 15px;
                margin-right: 15px;
                font-size: 14px;
                padding: 6px 15px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                color: black;
            """)




class NavigationPane(QFrame):
    fileDoubleClicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.setFixedWidth(0)  # Start hidden
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
class ClickableLabelBurger(QLabel):
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
        
        
    def mousePressEvent(self, ev):
        self.clicked()  # Call the connected slot
        super().mousePressEvent(ev)
        
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(15)  # Adjust this value to control the "thickness" of the glow
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, a0):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(a0)
        
    def clicked(self):
        # Placeholder method; override in subclass or connect externally.
        pass
        

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
        
    def mousePressEvent(self, ev):
        self.clicked.emit()
        super().mousePressEvent(ev)
        
    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(15)  # Adjust this value to control the "thickness" of the glow
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, a0):
        self.anim.stop()
        self.anim.setStartValue(self.shadow.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(a0)

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
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        
        # Create the navigation pane
        self.nav_pane = NavigationPane(self)
        self.nav_pane.fileDoubleClicked.connect(self.open_logs)
        main_layout.addWidget(self.nav_pane)
        
        # Create main content area.
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(content_widget, 0)
        
        # Top bar with hamburger icon.
        top_bar = QHBoxLayout()
        self.hamburger_label = ClickableLabelBurger("☰")
        font = QFont()
        font.setPointSize(26)
        self.hamburger_label.setFont(font)
        self.hamburger_label.setStyleSheet("margin: 10px; padding: 5px; border-radius: 5px;")
        # Connect the hamburger click event to toggle navigation pane.
        self.hamburger_label.clicked = self.toggle_nav_pane
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
            selected_mode = wizard.selected_log_mode
            if selected_mode == "Something general, it's up to me.":
                log_type = "General"
            elif selected_mode == "Bugs and errors":
                log_type = "Debugging"
            else:
                QMessageBox.information(self, "Not Available", "This log mode is not available yet.")
                return

            # Gather all wizard data
            setup_data = {
                "log_type": log_type,
                "user_name": wizard.name_text_box.toPlainText().strip() if wizard.name_text_box else "",
                "pdf_title": wizard.title_text_box.toPlainText().strip() if wizard.title_text_box else "Log Documentation",
                "pdf_font_size": int(wizard.text_size_box.text()) if wizard.text_size_box and wizard.text_size_box.text().isdigit() else 12,
                "pdf_line_spacing": float(wizard.line_spacing_box.text()) if wizard.line_spacing_box and wizard.line_spacing_box.text() else 1.5,
                "pdf_font": wizard.page4.findChild(QComboBox).currentText() if wizard.page4.findChild(QComboBox) else "Arial",
                "custom_dictionary": wizard.dictionary_box.toPlainText().strip() if wizard.dictionary_box else "",
            }
            self.launch_main_app(setup_data)

    def open_project(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "LDS Files  (*.ldsg *.ldsd)")
        if file_path:
            # Determine mode by file extension.
            if file_path.endswith("ldsg"):
                log_mode = "General"
            elif file_path.endswith("ldsd"):
                log_mode = "Debugging"
            else:
                log_mode = "General"  # fallback
            setup_data = {"file_path": file_path, "log_type": log_mode}
            self.launch_main_app(setup_data)

    def open_logs(self, file_path):
        # Determine log type by file extension:
        if file_path.endswith("ldsg"):
            log_mode = "General"
        elif file_path.endswith("ldsd"):
            log_mode = "Debugging"
        else:
            log_mode = "General"  # Fallback if extension is not recognized.
    
        setup_data = {
            "file_path": os.path.abspath(file_path),
            "log_type": log_mode
        }
        self.launch_main_app(setup_data)

    def open_documentations(self):
        QMessageBox.information(self, "Documentation", "Documentation goes here...")

    def launch_main_app(self, setup_data):
        from main import LogApp
        file_path = setup_data.get("file_path", None)
        log_type = setup_data.get("log_type", "General")

        self.main_window = LogApp(log_mode=log_type, file_path=file_path)

        # Only set attributes if present in setup_data (i.e., from wizard)
        if "user_name" in setup_data:
            self.main_window.user_name = setup_data["user_name"]
        if "pdf_title" in setup_data:
            self.main_window.pdf_title = setup_data["pdf_title"]
        if "pdf_font_size" in setup_data:
            self.main_window.pdf_font_size = setup_data["pdf_font_size"]
        if "pdf_line_spacing" in setup_data:
            self.main_window.pdf_line_spacing = setup_data["pdf_line_spacing"]
        if "pdf_font" in setup_data:
            self.main_window.pdf_font = setup_data["pdf_font"]
        if "custom_dictionary" in setup_data:
            self.main_window.custom_dictionary = setup_data["custom_dictionary"]
            # Force the main window to use the custom dictionary file
            self.main_window.keyword_definitions_file = self.main_window.get_keyword_definitions_file()
            self.main_window.load_keyword_definitions()

        # Save config only if new project (wizard)
        if "user_name" in setup_data:
            self.main_window.save_user_config()
    
        self.main_window.show()
        self.close()
    
    def toggle_nav_pane(self):
        # Animate the width of the navigation pane.
        start_width = self.nav_pane.width()
        end_width = 300 if not self.nav_open else 0  # 200px width when open.
        self.animation = QPropertyAnimation(self.nav_pane, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(end_width)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.animation.start()
        
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


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Logs")
        self.resize(350, 150)
        self.setFixedSize(350, 150)
        layout = QVBoxLayout(self)
        
        # Date range filter section.
        date_range_layout = QHBoxLayout()
        
        start_label = QLabel("Start Date:")
        date_range_layout.addWidget(start_label)
        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.start_date_edit)
        
        end_label = QLabel("End Date:")
        date_range_layout.addWidget(end_label)
        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.end_date_edit)
        
        layout.addLayout(date_range_layout)
        
        # Log type filter section.
        type_layout = QHBoxLayout()
        type_label = QLabel("Select Log Type:")
        type_layout.addWidget(type_label)
<<<<<<< HEAD
        self.type_combo = QComboBox(self) 
=======
        self.type_combo = QComboBox(self)
>>>>>>> 1ff3872a2ef1a50d1f9e78d823fa28d57c4110a6
        self.type_combo.addItem("All")
        self.type_combo.addItems(["Just Details", "Problem ★" , "Solution ■", "Bug ▲", "Changes ◆"])  # Updated options
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Buttons for applying or canceling.
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Filter", self)
        self.apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_btn)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def get_filters(self):
        # Return the selected start date, end date strings, and log type.
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        log_type = self.type_combo.currentText()
        return start_date, end_date, log_type



class ClickableLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        # Set pointer cursor to indicate clickability
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.original_pixmap: Optional[QPixmap] = None
        self.original_pixmap = None
        # Store the original stylesheet so we can revert back on hover out.
        self.base_style = "font-size: 15px; padding: 5px;"
        self.setStyleSheet(self.base_style)
        # Optionally, prepare a drop shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        self.shadow.setOffset(0, 0)

    def enterEvent(self, event):
        hover_style = self.base_style + "background-color: #f0f0f0;"
        self.setStyleSheet(hover_style)
        # Create a new drop shadow effect every time on hover
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        super().enterEvent(event)

    def leaveEvent(self, a0):
        # Revert to the original style when not hovered.
        self.setStyleSheet(self.base_style)
        self.setGraphicsEffect(None)
        super().leaveEvent(a0) 
    
    def mousePressEvent(self, ev):
        # Use the stored original pixmap if available, otherwise fall back to the current pixmap
        if hasattr(self, "original_pixmap") and self.original_pixmap:
            self.viewer = ImageViewerWindow(self.original_pixmap)
            self.viewer.show()
        elif self.pixmap():
            self.viewer = ImageViewerWindow(self.pixmap())
            self.viewer.show()
        super().mousePressEvent(ev)


# Subclass QScrollArea to enable panning with mouse drag.
class PannableScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setMouseTracking(True)
        self.dragging = False
        self.last_pos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.last_pos = event.pos()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.pos() - self.last_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_pos = event.pos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().mouseReleaseEvent(event)


# Image Viewer Window with zoom overlay and mouse wheel zooming.
class ImageViewerWindow(QMainWindow):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Viewer")
        self.original_pixmap = pixmap  # Original image
        self.fit_scale = 1.0  # Scale factor to fit the window (computed on show)
        self.zoom_percent = 0  # Relative zoom percentage deviation (0 means fit-to-window)
        self.current_scale = 1.0  # Actual scale applied

        # Central widget and layout.
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Use the pannable scroll area instead of a standard QScrollArea.
        self.scroll_area = PannableScrollArea(self)
        layout.addWidget(self.scroll_area)

        # Image label inside the scroll area.
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setPixmap(self.original_pixmap)
        self.scroll_area.setWidget(self.image_label)

        # Overlay widget to display zoom info.
        self.overlay = QLabel(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 100); color: white; padding: 3px;")
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.overlay.move(10, 10)
        self.overlay.resize(230, 30)
        self.overlay.setText("Zoom: 100%   Size: -")

        # Install an event filter on the viewport for mouse wheel zoom.
        self.scroll_area.viewport().installEventFilter(self)

        # Set a reasonable default window size.
        self.resize(800, 600)

    def showEvent(self, event):
        """Compute the fit-to-window scale factor when the window is shown."""
        super().showEvent(event)
        viewport_size = self.scroll_area.viewport().size()
        if self.original_pixmap:
            pixmap_size = self.original_pixmap.size()
            scale_w = viewport_size.width() / pixmap_size.width()
            scale_h = viewport_size.height() / pixmap_size.height()
            self.fit_scale = min(scale_w, scale_h)
            # Start at fit-to-window (zoom_percent = 0).
            self.zoom_percent = 0
            self.current_scale = self.fit_scale
            self.update_image()
            self.update_overlay()

    def eventFilter(self, source, event):
        # Use mouse wheel events over the scroll area's viewport for zooming.
        if source == self.scroll_area.viewport() and event.type() == QEvent.Type.Wheel:
            self.handle_wheel_event(event)
            return True  # Consume the event.
        return super().eventFilter(source, event)

    def handle_wheel_event(self, event):
        """Adjust zoom based on mouse wheel scrolling (% per notch)."""
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_by(20)
        else:
            self.zoom_by(-20)

    def zoom_by(self, delta_percent):
        """Adjust the zoom percentage and update the image."""
        self.zoom_percent += delta_percent
        # Clamp the zoom percent between -100% and +500% relative to fit-to-window.
        self.zoom_percent = max(-100, min(500, self.zoom_percent))
        self.current_scale = self.fit_scale * (1 + self.zoom_percent / 100.0)
        self.update_image()
        self.update_overlay()

    def update_image(self):
        """Scale the original pixmap using the current scale and update the label."""
        if self.original_pixmap:
            new_width = int(self.original_pixmap.width() * self.current_scale)
            new_height = int(self.original_pixmap.height() * self.current_scale)
            scaled_pixmap = self.original_pixmap.scaled(
                QSize(new_width, new_height),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def update_overlay(self):
        """Update the overlay text to show current zoom and original image dimensions."""
        if self.original_pixmap:
            # Use original dimensions for static size information.
            original_width = self.original_pixmap.width()
            original_height = self.original_pixmap.height()
            # Show zoom relative to the fit-to-window baseline (0 means fit).
            zoom_text = f"{'+' if self.zoom_percent > 0 else ''}{self.zoom_percent}%"
            self.overlay.setText(f"Zoom: {zoom_text}   Original Size: {original_width}x{original_height}px")

class ClickableDefinitionLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.full_definition = ""  # Initialize the full_definition attribute
        
        # Set pointer cursor to indicate clickability
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # Store the original stylesheet so we can revert back on hover out.
        self.base_style = "font-size: 15px; padding: 5px;"
        self.setStyleSheet(self.base_style)
        # Optionally, prepare a drop shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 160))
        self.shadow.setOffset(0, 0)

    def enterEvent(self, event):
        hover_style = self.base_style + "background-color: #f0f0f0;"
        self.setStyleSheet(hover_style)
        # Create a new drop shadow effect every time on hover
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Revert to the original style when not hovered.
        self.setStyleSheet(self.base_style)
        self.setGraphicsEffect(None)
        super().leaveEvent(event)    
    
    def mousePressEvent(self, event):
        viewer = DefinitionViewer(self.full_definition, self)
        viewer.exec()
        super().mousePressEvent(event)
        

class DefinitionViewer(QDialog):
    def __init__(self, full_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Full Definition")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Use a scroll area to handle very long text
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        content_widget = QLabel(full_text, self)
        content_widget.setWordWrap(True)
        content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_area.setWidget(content_widget)

        self.setLayout(layout)
        self.center() 
        
        # Start the zoom-in animation when the dialog is shown
        self.start_zoom_animation()   
            
    def start_zoom_animation(self):
        """Animate the zoom-in effect for the dialog."""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        center_point = screen_geometry.center()

        # Start with a small size at the center of the screen
        start_geometry = QRect(
            center_point.x() - 50,  # Small width
            center_point.y() - 50,  # Small height
            100,  # Initial width
            100   # Initial height
        )

        # End with the dialog's normal geometry
        end_geometry = self.geometry()

        # Set the dialog's initial geometry
        self.setGeometry(start_geometry)

        # Create the animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)  # Animation duration in milliseconds
        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(end_geometry)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # Smooth easing curve

        # Start the animation
        self.animation.start()
        
    def center(self):
        """Center the dialog on the screen."""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

class DictionaryDialog(QDialog):
    def __init__(self, parent=None, config_folder=None):
        super().__init__(parent)
        self.setWindowTitle("Dictionary")
        self.setGeometry(100, 100, 700, 450)
        self.setFixedSize(700, 450)
        self.config_folder = config_folder or get_config_dir()

        self.main_layout = QHBoxLayout()
        
        # Left side layout (Search + Keyword List)
        self.left_layout = QVBoxLayout()
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Search keywords...")
        self.search_box.setFixedWidth(200)
        self.search_box.textChanged.connect(self.search_keywords)
        self.left_layout.addWidget(self.search_box)
        
        self.keyword_list = QListWidget(self)
        self.keyword_list.itemClicked.connect(self.display_definition)
        self.keyword_list.setFixedWidth(200)
        self.left_layout.addWidget(self.keyword_list)
        
        # Add a static item at the top
        self.add_static_item("Keywords")
        
        self.main_layout.addLayout(self.left_layout)
        
        # Definition Section
        self.definition_layout = QVBoxLayout()
        # Replace the normal QLabel with our ClickableDefinitionLabel.
        self.definition_label = ClickableDefinitionLabel(self)
        self.definition_label.setWordWrap(True)
        self.definition_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.definition_label.setStyleSheet("font-size: 15px; padding: 5px;")
        self.definition_label.setText("Select a keyword to view its definition.")
        # Store the full definition text separately
        self.definition_label.full_definition = "Select a keyword to view its definition."
        self.definition_layout.addWidget(self.definition_label)
        
        # Create a container layout for the "Example" label and the image preview label with no spacing.
        self.image_container_layout = QVBoxLayout()
        self.image_container_layout.setSpacing(0)  # No spacing between the "Example" label and the image preview
        
        # New "Example" label; initially hidden
        self.example_label = QLabel("Example", self)
        self.example_label.setStyleSheet("font-weight: bold;")
        self.example_label.setVisible(False)
        self.image_container_layout.addWidget(self.example_label)
        
        # Add image preview label (clickable)
        self.image_label = ClickableLabel(self)
        self.image_label.setFixedHeight(100)  # Preview height; adjust as needed.
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")
        self.image_label.setVisible(False)
        self.image_container_layout.addWidget(self.image_label)
        
        # Add the container layout to the definition layout.
        self.definition_layout.addLayout(self.image_container_layout)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_keyword)
        self.button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit", self)
        self.edit_button.clicked.connect(self.edit_keyword)
        self.button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete", self)
        self.delete_button.clicked.connect(self.delete_keyword)
        self.button_layout.addWidget(self.delete_button)
        
        self.definition_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.definition_layout)
        
        self.setLayout(self.main_layout)
        self.dictionary = {}  # Store definitions
        self.keyword_images = {}
        
        # Load previously saved definitions and images.
        self.load_keyword_definitions()
        
        
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
                
                # Ask the user if they want to add an example image.
                add_img = QMessageBox.question(
                    self,
                    "Add Image?",
                    "Do you want to add an example image for this keyword?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                image_path = None
                if add_img == QMessageBox.StandardButton.Yes:
                    file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
                    if file_path:
                        # Define a local folder to store keyword images.
                        local_dir = os.path.join(self.config_folder, "keyword_images")
                        if not os.path.exists(local_dir):
                            os.makedirs(local_dir)
                        # Create a unique filename using the keyword and current timestamp.
                        unique_name = f"{word}_{int(time.time())}{os.path.splitext(file_path)[1]}"
                        dest_path = os.path.join(local_dir, unique_name)
                        try:
                            shutil.copy(file_path, dest_path)
                            image_path = dest_path
                        except Exception as e:
                            QMessageBox.warning(self, "Image Error", f"Could not copy image:\n{e}")
                
                # Store in dictionary
                self.dictionary[word] = definition
                if image_path:
                    self.keyword_images[word] = image_path

                # Add keyword visually
                self.add_list_item(word)

                # Auto-select new item
                self.select_keyword(word)
                
                # Save the updated dictionary and image paths.
                self.save_keyword_definitions()
    
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
            
            # Confirmation Dialog
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Caution")
            msg.setText(f"Are you sure you want to delete '{word}'?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if msg.exec() == QMessageBox.StandardButton.Yes:
                if word in self.dictionary:
                    del self.dictionary[word]  # Remove the keyword from the dictionary
                self.keyword_list.takeItem(self.keyword_list.row(selected_item))  # Remove the item from the list
                self.definition_label.clear()  # Clear the definition area
            
            else:
                pass

    def display_definition(self, item):
        word = item.text()
        full_def = self.dictionary.get(word, "No definition available.")
        # For preview purposes, truncate if too long (e.g., show first 200 characters)
        preview_text = full_def if len(full_def) <= 780 else full_def[:780] + "..."
        formatted_definition = f"<b>{word}:</b><br>{preview_text}"
        self.definition_label.setText(formatted_definition)
        self.definition_label.full_definition = full_def

        image_path = self.keyword_images.get(word)
        if image_path:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Store the original pixmap before scaling
                self.image_label.original_pixmap = pixmap
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(), 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setVisible(True)
                self.example_label.setVisible(True)
            else:
                self.image_label.clear()
                self.image_label.setVisible(False)
                self.example_label.setVisible(False)
        else:
            self.image_label.clear()
            self.image_label.setVisible(False)
            self.example_label.setVisible(False)
        
    def center(self):
        """Center the dialog on the screen."""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())
    
    def edit_keyword(self):
        """Edit the definition and/or image of the selected keyword."""
        selected_item = self.keyword_list.currentItem()
        if selected_item:
            # Prevent editing of static items
            if selected_item.data(Qt.ItemDataRole.UserRole) == "static":
                return
        
            word = selected_item.text()
            current_def = self.dictionary.get(word, "")
            current_image = self.keyword_images.get(word, None)

            # Prompt the user to edit the definition
            new_def, ok = QInputDialog.getText(self, "Edit Definition", f"Edit definition for '{word}':", text=current_def)
            if ok and new_def.strip():
                self.dictionary[word] = new_def.strip()

            # Ask the user if they want to update the image
            update_image = QMessageBox.question(
                self,
                "Update Image?",
                f"Do you want to update the image for '{word}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if update_image == QMessageBox.StandardButton.Yes:
                file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
                if file_path:
                    # Define a local folder to store keyword images
                    local_dir = os.path.join(self.config_folder, "keyword_images")
                    if not os.path.exists(local_dir):
                        os.makedirs(local_dir)
                
                    # Create a unique filename using the keyword and current timestamp
                    unique_name = f"{word}_{int(time.time())}{os.path.splitext(file_path)[1]}"
                    dest_path = os.path.join(local_dir, unique_name)
                    try:
                        shutil.copy(file_path, dest_path)
                        self.keyword_images[word] = dest_path
                    except Exception as e:
                        QMessageBox.warning(self, "Image Error", f"Could not copy image:\n{e}")

            # Update the displayed definition and image
            self.display_definition(selected_item)

            # Save the updated definitions and images
            self.save_keyword_definitions()
    
    def search_keywords(self, text):
        """Filter the keyword list based on the search box."""
        for i in range(self.keyword_list.count()):
            item = self.keyword_list.item(i)
            if item is not None:
                # Do not hide static item
                if item.data(Qt.ItemDataRole.UserRole) == "static":
                    item.setHidden(False)
                else:
                    # Show items containing the search text (case-insensitive)
                    item.setHidden(text.lower() not in item.text().lower())
    
    
    def save_keyword_definitions(self):
        definitions_file = os.path.join(self.config_folder, "keyword_definitions.json")
        with open(definitions_file, "w", encoding="utf-8") as file:
            json.dump(getattr(self, 'keyword_definitions', {}), file, indent=4)
        images_file = os.path.join(self.config_folder, "keyword_images.json")
        with open(images_file, "w", encoding="utf-8") as file:
            json.dump(getattr(self, 'keyword_images', {}), file, indent=4)

    def load_keyword_definitions(self):
        """Load keyword definitions and image paths from separate JSON files."""
        config_dir = get_config_dir()
        definitions_file = os.path.join(self.config_folder, "keyword_definitions.json")
        images_file = os.path.join(self.config_folder, "keyword_images.json")

        # Load definitions
        if os.path.exists(definitions_file):
            with open(definitions_file, "r", encoding="utf-8") as file:
                self.keyword_definitions = json.load(file)
            print(f"Keyword definitions loaded from {definitions_file}")
        else:
            self.keyword_definitions = {}

        # Load image paths
        if os.path.exists(images_file):
            with open(images_file, "r", encoding="utf-8") as file:
                self.keyword_images = json.load(file)
            print(f"Keyword images loaded from {images_file}")
        else:
            self.keyword_images = {}
    
    def get_config_dir():
        config_dir = os.path.join(os.getcwd(), "config")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return config_dir
            

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
    def __init__(self, log_mode="General", file_path=None):
        super().__init__()
        print("Initializing LogApp...")
        self.log_mode = log_mode
        self.log_type = "General" if log_mode == "General" else "Debugging"
        self.load_user_config()
        self.load_color_from_config()  # Load the saved color
        self.init_ui()
        self.custom_dictionary = getattr(self, "custom_dictionary", "")
        self.keyword_definitions = {}
        self.keyword_definitions_file = self.get_keyword_definitions_file()
        self.load_keyword_definitions()  # Load keyword definitions
        self.current_file = None
        
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
        
        
        # Start the hardware monitoring thread
        self.hw_monitor = HardwareMonitor()
        self.hw_monitor.data_ready.connect(self.update_system_info)
        self.hw_monitor.start()
        print("LogApp initialized.")
        
        # If a file_path is provided, load the logs immediately.
        if file_path:
            self.open_logs(file_path)

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
        
        # Dictionary Menu
        dictionary_action = QAction("Dictionary", self)
        dictionary_action.triggered.connect(self.open_dictionary)
        help_menu.addAction(dictionary_action)
        
        # Add Filter Logs action under Help.
        filter_action = QAction("Filter Logs", self)
        filter_action.triggered.connect(self.open_filter_dialog)
        help_menu.addAction(filter_action)
        
        # Optionally, add a Clear Filter action.
        clear_filter_action = QAction("Clear Filters", self)
        clear_filter_action.triggered.connect(self.clear_filters)
        help_menu.addAction(clear_filter_action)
        
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
        self.recent_menu.clear()
        settings = QSettings("MyCompany", "LogDocumentationSystem")
        recent_files = settings.value("recent_files", [])
        if not isinstance(recent_files, list):
            recent_files = [recent_files] if recent_files else []

        self.recent_files = recent_files
        for file_path in self.recent_files:
            # Filter based on current log type
            if self.log_type == "General" and not file_path.endswith("ldsg"):
                continue
            if self.log_type == "Debugging" and not file_path.endswith("ldsd"):
                continue
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
        
        log_type_label = QLabel(f"Log Type: {self.log_type}", self)
        if self.log_type == "General":
            log_type_label.setStyleSheet("""
            border: 1px solid black;
            background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #d4acfa, stop: 1 #f27cc3
            );
            font-weight: bold;
            """)
        else:
            log_type_label.setStyleSheet("""
            border: 1px solid black;
            background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #42f5d7, stop: 1 #14b7fc
            );
            font-weight: bold;
            """)
        
        combo_layout.addWidget(log_type_label)
        
        self.category_selector = QComboBox(self)
        if self.log_type == "General":
            self.category_selector.addItems(["Just Details", "Problem ★", "Bug ▲", "Changes ◆"])
        else:
            self.category_selector.addItems(["Just Details", "Bug ▲"])    
        
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
        filter_json = ".ldsg" if self.log_type == "General" else ".ldsd"
        self.drop_area = QLabel("Drag and drop a " + f"{filter_json}" + " file here", self)
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
            
            # Save updated counters to JSON
            self.save_log_counters()
            
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
        # If file is already created, save as usual (for autosave compatibility)
        if self.current_file:
            file_name = self.current_file
            project_folder = os.path.dirname(file_name)
            config_folder = os.path.join(project_folder, "config")
            os.makedirs(config_folder, exist_ok=True)
        else:
            # Prompt for a folder to save the project
            project_folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
            if not project_folder:
                return
            config_folder = os.path.join(project_folder, "config")
            os.makedirs(config_folder, exist_ok=True)
            # Use default log file name based on log type
            log_filename = "logs.ldsg" if self.log_type == "General" else "logs.ldsd"
            file_name = os.path.join(project_folder, log_filename)
            self.current_file = file_name  # Set for autosave

        # Save the log file
        with open(file_name, "w", encoding="utf-8") as file:
            for index in range(self.log_list.count()):
                item = self.log_list.item(index)
                label = self.log_list.itemWidget(item)
                if isinstance(label, QLabel):
                    file.write(label.text() + "\n")

        # Save config files in the config subfolder
        with open(os.path.join(config_folder, "counters.json"), "w", encoding="utf-8") as f:
            json.dump(self.log_counters, f, indent=4)
        with open(os.path.join(config_folder, "restore_points.json"), "w", encoding="utf-8") as f:
            json.dump(self.restore_points, f, indent=4)
        with open(os.path.join(config_folder, "keyword_definitions.json"), "w", encoding="utf-8") as f:
            json.dump(self.keyword_definitions, f, indent=4)

        print(f"Logs saved to {file_name}")
        print(f"Config saved to {config_folder}")

        self.setWindowTitle("Log Documentation System - FIle saved")  # Update title
        QTimer.singleShot(2000, lambda: self.setWindowTitle("Log Documentation System"))  # Reset after 2 seconds


    def open_logs(self, file_path=None):
        print("Opening logs...")
        if not file_path:  # If no file path is provided, use the file dialog
            filter_str = "General Logs (*.ldsg)" if self.log_type == "General" else "Debugging Logs (*.ldsd)"
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Logs", "", filter_str)
        if not file_path:
            return
        

        self.current_file = file_path
        self.save_recent_file(file_path)
        self.log_list.clear()

        # --- NEW: Use project folder and config subfolder ---
        project_folder = os.path.dirname(file_path)
        config_folder = os.path.join(project_folder, "config")

        # Load log counters
        counters_path = os.path.join(config_folder, "counters.json")
        if os.path.exists(counters_path):
            try:
                with open(counters_path, "r", encoding="utf-8") as f:
                    self.log_counters = json.load(f)
            except Exception as e:
                print(f"Error loading log counters: {e}")
                self.log_counters = {"Problem ★": 0, "Solution ■": 0, "Bug ▲": 0, "Changes ◆": 0}
        else:
            self.log_counters = {"Problem ★": 0, "Solution ■": 0, "Bug ▲": 0, "Changes ◆": 0}

        # Load restore points
        restore_path = os.path.join(config_folder, "restore_points.json")
        if os.path.exists(restore_path):
            try:
                with open(restore_path, "r", encoding="utf-8") as f:
                    self.restore_points = json.load(f)
            except Exception as e:
                print(f"Error loading restore points: {e}")
                self.restore_points = {}
        else:
            self.restore_points = {}

        # Load keyword definitions
        keywords_path = os.path.join(config_folder, "keyword_definitions.json")
        if os.path.exists(keywords_path):
            try:
                with open(keywords_path, "r", encoding="utf-8") as f:
                    self.keyword_definitions = json.load(f)
            except Exception as e:
                print(f"Error loading keyword definitions: {e}")
                self.keyword_definitions = {}
        else:
            self.keyword_definitions = {}
            
            
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
                        f'<span style="color:black;">{timestamp} [General] {solution_text.strip()} - Solution #{problem_number}</span>'
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
        filter_json = ".ldsg" if self.log_type == "General" else ".ldsd"
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                print("URL:", url.toLocalFile())
                if url.toLocalFile().lower().endswith(filter_json):
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
        filter_json = ".ldsg" if self.log_type == "General" else ".ldsd"
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(filter_json):
                self.open_logs(file_path)
                break
        else:
            QMessageBox.warning(self, "Invalid File", "Please select a valid" + f"{filter_json}" + "file.")
    
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
        font_family = self.pdf_font if hasattr(self, "pdf_font") else "Arial"

        # Start building the PDF content
        html_content = f"""
        <html>
            <head>
                <meta charset='utf-8'>
                <style>
                    body {{ font-size: {font_size}pt;
                            line-height: {line_spacing}em;
                            font-family: '{font_family}', Arial, sans-serif;
                            }}
                    h1 {{ 
                        text-align: center; 
                        font-size: {font_size + 6}pt; 
                        font-weight: bold; 
                        margin-bottom: {line_spacing * 5}px;
                        font-family: '{font_family}', Arial, sans-serif;
                        }}
                    .log-entry {{ 
                        margin-bottom: {line_spacing * 3}px; 
                        white-space: pre-wrap;
                        font-family: '{font_family}', Arial, sans-serif; 
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
        settings.setValue("pdf_font", self.pdf_font)
        settings.setValue("custom_dictionary", self.custom_dictionary)
        print(f"Loaded settings: Username={self.user_name}, PDF Title={self.pdf_title}, Font Size={self.pdf_font_size}, Line Spacing={self.pdf_line_spacing}, Font={self.pdf_font}, CustomDict={self.custom_dictionary}")

    def load_user_config(self):
        settings = QSettings("MyCompany", "LogDocumentationSystem")
        self.user_name = settings.value("username", "")
        self.pdf_title = settings.value("pdf_title", "Log Documentation")
        self.pdf_font_size = int(settings.value("pdf_font_size", 12))
        self.pdf_line_spacing = float(settings.value("pdf_line_spacing", 1.5))
        self.pdf_font = settings.value("pdf_font", "Arial")
        self.custom_dictionary = settings.value("custom_dictionary", "")
        print(f"Loaded settings: Username={self.user_name}, PDF Title={self.pdf_title}, Font Size={self.pdf_font_size}, Line Spacing={self.pdf_line_spacing}, Font={self.pdf_font}, CustomDict={self.custom_dictionary}")

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
        font_family = self.pdf_font if hasattr(self, "pdf_font") else "Arial"

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
        """Save restore points to a JSON file in the config folder."""
        if self.current_file:
            project_folder = os.path.dirname(self.current_file)
            config_folder = os.path.join(project_folder, "config")
            os.makedirs(config_folder, exist_ok=True)
            json_file = os.path.join(config_folder, "restore_points.json")
            with open(json_file, "w", encoding="utf-8") as file:
                json.dump(self.restore_points, file, indent=4, ensure_ascii=False)
            print(f"Restore points saved to {json_file}")
        
    def load_restore_points(self):
        """Load restore points from a JSON file in the config folder."""
        if self.current_file:
            project_folder = os.path.dirname(self.current_file)
            config_folder = os.path.join(project_folder, "config")
            json_file = os.path.join(config_folder, "restore_points.json")
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
        if self.current_file:
            project_folder = os.path.dirname(self.current_file)
            config_folder = os.path.join(project_folder, "config")
        else:
            config_folder = get_config_dir()
        self.dictionary_dialog = DictionaryDialog(self, config_folder=config_folder)
        self.dictionary_dialog.dictionary = getattr(self, 'keyword_definitions', {})
        for keyword in sorted(self.dictionary_dialog.dictionary.keys()):
            self.dictionary_dialog.add_list_item(keyword)
        self.dictionary_dialog.show()
        def update_keywords():
            self.keyword_definitions = self.dictionary_dialog.dictionary
            self.save_keyword_definitions()
        self.dictionary_dialog.finished.connect(update_keywords)
        
    def save_keyword_definitions(self):
        """Save keyword definitions to a JSON file."""
        file_path = self.get_keyword_definitions_file()
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(getattr(self, 'keyword_definitions', {}), file, indent=4)
        print(f"Keyword definitions saved to {file_path}")

    def load_keyword_definitions(self):
        """Load keyword definitions from a JSON file."""
        file_path = self.get_keyword_definitions_file()
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                self.keyword_definitions = json.load(file)
            print(f"Keyword definitions loaded from {file_path}")
        else:
            self.keyword_definitions = {}
    
    def open_filter_dialog(self):
        """Open the filter dialog and apply filtering if the user accepts."""
        dialog = FilterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            start_date, end_date, log_type = dialog.get_filters()
            self.filter_logs(start_date, end_date, log_type)
                   

    def filter_logs(self, start_date, end_date, log_type):
        # Convert dates.
        start_date = QDate.fromString(start_date, "yyyy-MM-dd")
        end_date = QDate.fromString(end_date, "yyyy-MM-dd")
    
        # Define a mapping from descriptive log type to its icon.
        log_type_icons = {
            "Problem ★": "★",
            "Solution ■": "■",
            "Bug ▲": "▲",
            "Changes ◆": "◆"
        }
        # Extract the icon that should be present.
        expected_icon = log_type_icons.get(log_type, "")
    
        for i in range(self.log_list.count()):
            item = self.log_list.item(i)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel):
                plain_text = self.strip_html(label.text())
                date_match = re.search(r"\[(\d{4}-\d{2}-\d{2})", plain_text)
                if date_match:
                    log_date = QDate.fromString(date_match.group(1), "yyyy-MM-dd")
                else:
                    #item.setHidden(True)
                    continue
            
                date_ok = start_date <= log_date <= end_date

                if log_type == "All":
                    # Check if expected icon is in the plain text.
                    type_ok = True
                    
                elif log_type == "Just Details":
                    # "Just Details" should not contain any of the icons.
                    type_ok = not any(icon in plain_text for icon in ["★", "■", "▲", "◆"])
                    
                else:
                    expected_icon = log_type_icons.get(log_type, "")
                    type_ok = expected_icon in plain_text

                if item is not None:
                    item.setHidden(not (date_ok and type_ok))
                    
    def clear_filters(self):
        """Reset filtering to show all logs."""
        for i in range(self.log_list.count()):
            item = self.log_list.item(i)
            item.setHidden(False)
            
            # Scroll to the last item in the log list
            if self.log_list.count() > 0:
                last_item = self.log_list.item(self.log_list.count() - 1)
                self.log_list.scrollToItem(last_item)
                print("Scrolled to the latest log entry.")
    
    def strip_html(self, html_text):
        doc = QTextDocument()
        doc.setHtml(html_text)
        return doc.toPlainText()
    
    def save_log_counters(self):
        """Save the log counters to a JSON file in the config folder."""
        if self.current_file:
            project_folder = os.path.dirname(self.current_file)
            config_folder = os.path.join(project_folder, "config")
            os.makedirs(config_folder, exist_ok=True)
            json_file = os.path.join(config_folder, "counters.json")
            try:
                with open(json_file, "w", encoding="utf-8") as json_out:
                    json.dump(self.log_counters, json_out, indent=4)
                print(f"Log counters saved to {json_file}")
            except Exception as e:
                print(f"Error saving log counters: {e}")
    
    def get_keyword_definitions_file(self):
        # Use custom dictionary if set, else default
        config_dir = get_config_dir()
        if getattr(self, "custom_dictionary", ""):
            # Sanitize the name for file usage
            safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', self.custom_dictionary)
            return os.path.join(config_dir, f"{safe_name}_definitions.json")
        else:
            return os.path.join(config_dir, "keyword_definitions.json")
    
    


if __name__ == "__main__":
    print("Starting application...")
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec())