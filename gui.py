import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QPushButton, QMessageBox, QSpacerItem,
    QSizePolicy, QGraphicsOpacityEffect, QStackedWidget, QWidget,
    QTextEdit, QPlainTextEdit, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtSignal
from PyQt6.QtGui import QIntValidator


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
            

class AnimatedClickableLabel(QLabel):
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
            option_label = AnimatedClickableLabel(text, self, wizard=self)
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
        
        
        
        # Find the layout of the clicked option and add the subtext label.
        for option, layout in zip(self.options, self.option_layouts):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                subtext_label.setVisible(True)
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
    
        
        # Find the layout of the clicked option and add the subtext label.
        for option, layout in zip(self.options2, self.option_layouts2):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                subtext_label.setVisible(True)
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
            subtext_label.setValidator(QIntValidator(1, 9999, self))  # Only allow numbers
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
        
        
        # Remove any existing subtext for the clicked option.
        for option, layout in zip(self.options3, self.option_layouts3):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                subtext_label.setVisible(True)
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

        
        for option, layout in zip(self.options4, self.option_layouts4):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                subtext_label.setVisible(True)
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

        
        for option, layout in zip(self.options5, self.option_layouts5):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                subtext_label.setVisible(True)
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
    
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    if wizard.exec() == QDialog.DialogCode.Accepted:
        print("Wizard completed.")
    else:
        print("Wizard cancelled.")
    sys.exit(app.exec())
