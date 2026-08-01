import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QPushButton, QMessageBox, QSpacerItem,
    QSizePolicy, QGraphicsOpacityEffect, QStackedWidget, QWidget,
    QTextEdit, QPlainTextEdit, QLineEdit, QComboBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QIntValidator


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
    clicked = pyqtSignal(object)
    
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
            self.clicked.emit(self)
        
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
        self._title_labels = []
        self._title_gradient_offset = 0
        self._title_gradient_start = QColor("#d4acfa")
        self._title_gradient_end = QColor("#f27cc3")

        # Initialize text box references to None
        self.name_text_box = None
        self.title_text_box = None

        self.text_size_box = None
        self.line_spacing_box = None
        self.font_combo_box = None
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
        self._register_title_label(title_label)
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
        self._register_title_label(title_label2)
        title_label2.setContentsMargins(0, 10, 0, 10)
        title_label2.setFixedHeight(80)
        title_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page2_layout.addWidget(title_label2)

        choices_scroll_area = QScrollArea(self.page2)
        choices_scroll_area.setWidgetResizable(True)
        choices_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        choices_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        choices_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        choices_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        choices_scroll_area.viewport().setAutoFillBackground(False)

        choices_widget = QWidget()
        choices_widget.setAutoFillBackground(False)
        choices_layout = QVBoxLayout(choices_widget)
        choices_layout.setSpacing(15)
        choices_layout.setContentsMargins(0, 0, 0, 0)

        # Instruction label
        instruction_label2 = QLabel("On each lds, I want to:")
        instruction_label2.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            font-family: Segoe UI;
            margin-top: 0px;
            margin-left: 25px;
        """)
        choices_layout.addWidget(instruction_label2)

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
            option_label2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            option_label2.clicked.connect(lambda text=text: self.option_clicked2(text))
            option_layout2.addWidget(option_label2)

            choices_layout.addLayout(option_layout2)
            self.option_layouts2.append(option_layout2)
            self.options2.append(option_label2)

        instruction_label3 = QLabel("On exporting document, I want to:")
        instruction_label3.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            font-family: Segoe UI;
            margin-top: 0px;
            margin-left: 25px;    
        """)
        choices_layout.addWidget(instruction_label3)

        self.option_layouts3 = []
        self.options3 = []
        option_texts3 = [
            "Set the font size to",
            "Set the line spacing to",
            "Proceed on default"
        ]
        for text in option_texts3:
            option_layout3 = QVBoxLayout()
            option_layout3.setSpacing(5)

            option_label3 = AnimatedClickableLabel3(text, self, wizard=self)
            option_label3.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            option_label3.clicked.connect(lambda text=text: self.option_clicked3(text))
            option_layout3.addWidget(option_label3)

            choices_layout.addLayout(option_layout3)
            self.option_layouts3.append(option_layout3)
            self.options3.append(option_label3)

        instruction_label4 = QLabel("On exporting document, Set font:")
        instruction_label4.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            font-family: Segoe UI;
            margin-top: 0px;
            margin-left: 25px;    
        """)
        choices_layout.addWidget(instruction_label4)

        self.option_layouts4 = []
        self.options4 = []
        option_texts4 = [
            "Set font to:",
            "Proceed on default"
        ]
        for text in option_texts4:
            option_layout4 = QVBoxLayout()
            option_layout4.setSpacing(5)

            option_label4 = AnimatedClickableLabel4(text, self, wizard=self)
            option_label4.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            option_label4.clicked.connect(lambda text=text: self.option_clicked4(text))
            option_layout4.addWidget(option_label4)

            choices_layout.addLayout(option_layout4)
            self.option_layouts4.append(option_layout4)
            self.options4.append(option_label4)

        instruction_label6 = QLabel("Do you want to use infinite page setup?")
        instruction_label6.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            font-family: Segoe UI;
            margin-top: 0px;
            margin-left: 25px;
        """)
        choices_layout.addWidget(instruction_label6)

        self.option_layouts6 = []
        self.options6 = []
        option_texts6 = [
            "Yes",
            "No - Continue with default"
        ]
        for text in option_texts6:
            option_layout6 = QVBoxLayout()
            option_layout6.setSpacing(5)

            option_label6 = AnimatedClickableLabel5(text, self, wizard=self)
            option_label6.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            option_label6.clicked.connect(self.option_clicked6)
            option_layout6.addWidget(option_label6)
            option_label6.setVisible(False)
            option_label6.setEnabled(False)

            choices_layout.addLayout(option_layout6)
            self.option_layouts6.append(option_layout6)
            self.options6.append(option_label6)
        self.infinite_choice_widget = instruction_label6
        instruction_label6.setVisible(False)
        instruction_label6.setEnabled(False)
        self._refresh_infinite_page_choice()

        choices_layout.addStretch()
        choices_scroll_area.setWidget(choices_widget)
        page2_layout.addWidget(choices_scroll_area)

        # Add a spacer before the navigation buttons to push them to the bottom.
        spacer2 = QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
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
        self.next_button3 = self.next_button2
        self.next_button4 = self.next_button2

        page2_layout.addLayout(btn_layout2)
        self.stacked_widget.addWidget(self.page2)

        # Create the fifth/last page (new frame).
        self.page5 = QWidget()
        page5_layout = QVBoxLayout(self.page5)
        page5_layout.setSpacing(15)
        page5_layout.setContentsMargins(0, 0, 0, 0)

        # Title label
        title_label5 = QLabel("Log Documentation Setup Wizard")
        self._register_title_label(title_label5)
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
            option_label5.clicked.connect(self.option_clicked5)
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
        self._start_title_gradient_animation()

    def _register_title_label(self, title_label):
        self._title_labels.append(title_label)
        self._apply_title_gradient()

    def _animated_title_color(self, base_color):
        if self._title_gradient_offset == 0:
            return QColor(base_color)

        hue = base_color.hsvHue()
        if hue < 0:
            hue = 0
        return QColor.fromHsv(
            (hue + self._title_gradient_offset) % 360,
            base_color.hsvSaturation(),
            base_color.value(),
        )

    def _apply_title_gradient(self):
        start_color = self._animated_title_color(self._title_gradient_start).name()
        end_color = self._animated_title_color(self._title_gradient_end).name()
        gradient = self._current_title_gradient_css(start_color, end_color)
        title_style = f"""
            font-size: 25px;
            font-weight: bold;
            background: {gradient};
            font-family: Segoe UI;
        """
        for title_label in self._title_labels:
            title_label.setStyleSheet(title_style)
        self._apply_animated_accent_styles(gradient)

    def _current_title_gradient_css(self, start_color=None, end_color=None):
        if start_color is None:
            start_color = self._animated_title_color(self._title_gradient_start).name()
        if end_color is None:
            end_color = self._animated_title_color(self._title_gradient_end).name()
        return (
            "qlineargradient("
            "x1: 0, y1: 0, x2: 1, y2: 0, "
            f"stop: 0 {start_color}, stop: 1 {end_color}"
            ")"
        )

    def _choice_label_style(self, selected=False):
        background = f"background: {self._current_title_gradient_css()};" if selected else ""
        font_weight = "font-weight: bold;" if selected else ""
        border = "1px solid #0078d7" if selected else "1px solid transparent"
        return f"""
            font-size: 17px;
            padding: 10px;
            margin-left: 15px;
            margin-right: 15px;
            border: {border};
            border-radius: 15px;
            {background}
            {font_weight}
        """

    def _animated_button_style(self, margin_right="15px", padding="6px 18px", enabled=False):
        background = f"background: {self._current_title_gradient_css()};" if enabled else ""
        return f"""
            margin-bottom: 15px;
            margin-right: {margin_right};
            font-size: 14px;
            padding: {padding};
            border: 2px solid #0078d7;
            border-radius: 8px;
            color: black;
            {background}
        """

    def _clear_group_selection(self, options, layouts, keep=None):
        for option, layout in zip(options, layouts):
            if option is keep:
                option.setSelected(True)
                if layout.count() > 1:
                    subtext_widget = layout.itemAt(1).widget()
                    if subtext_widget is not None:
                        layout.removeWidget(subtext_widget)
                        subtext_widget.deleteLater()
                continue
            option.setSelected(False)
            if layout.count() > 1:
                subtext_widget = layout.itemAt(1).widget()
                if subtext_widget is not None:
                    layout.removeWidget(subtext_widget)
                    subtext_widget.deleteLater()

    def _refresh_infinite_page_choice(self):
        is_uiux = getattr(self, "log_type", None) == "UIMode"
        if hasattr(self, "infinite_choice_widget"):
            self.infinite_choice_widget.setVisible(is_uiux)
            self.infinite_choice_widget.setEnabled(is_uiux)
        if hasattr(self, "options6"):
            for option, layout in zip(self.options6, self.option_layouts6):
                option.setVisible(is_uiux)
                option.setEnabled(is_uiux)
                if not is_uiux:
                    option.setSelected(False)
                    if layout.count() > 1:
                        subtext_widget = layout.itemAt(1).widget()
                        if subtext_widget is not None:
                            layout.removeWidget(subtext_widget)
                            subtext_widget.deleteLater()

    def _all_choice_options(self):
        return (
            getattr(self, "options", [])
            + getattr(self, "options2", [])
            + getattr(self, "options3", [])
            + getattr(self, "options4", [])
            + getattr(self, "options5", [])
            + getattr(self, "options6", [])
        )

    def _apply_animated_accent_styles(self, gradient=None):
        for option in self._all_choice_options():
            option.setStyleSheet(self._choice_label_style(selected=bool(option.property("selected"))))

        if hasattr(self, "next_button"):
            self.next_button.setStyleSheet(
                self._animated_button_style(margin_right="5px", padding="6px 12px", enabled=self.next_button.isEnabled())
            )
        if hasattr(self, "next_button2"):
            self.next_button2.setStyleSheet(
                self._animated_button_style(enabled=self.next_button2.isEnabled())
            )
        if hasattr(self, "next_button5"):
            self.next_button5.setStyleSheet(
                self._animated_button_style(padding="6px 15px", enabled=self.next_button5.isEnabled())
            )

    def _start_title_gradient_animation(self):
        self._title_gradient_timer = QTimer(self)
        self._title_gradient_timer.timeout.connect(self._animate_title_gradient)
        self._title_gradient_timer.start(60)

    def _animate_title_gradient(self):
        self._title_gradient_offset = (self._title_gradient_offset + 1) % 360
        self._apply_title_gradient()

    def get_setup_data(self):
        # Collect all relevant data from the wizard's fields
        return {
            "user_name": (
                self.name_text_box.toPlainText().strip() if self.name_text_box else ""
            ),
            "pdf_title": (
                self.title_text_box.toPlainText().strip() if self.title_text_box else ""
            ),
            "pdf_font_size": (
                int(self.text_size_box.text())
                if self.text_size_box and self.text_size_box.text().isdigit()
                else 12
            ),
            "pdf_line_spacing": (
                float(self.line_spacing_box.text())
                if self.line_spacing_box and self.line_spacing_box.text()
                else 1.5
            ),
            "pdf_font": (
                self.font_combo_box.currentText()
                if self.font_combo_box
                else "Arial"
            ),
            "custom_dictionary": (
                self.dictionary_box.toPlainText().strip() if self.dictionary_box else ""
            ),
            "infinite_page_setup": self._option_selected(self.options6, "Yes") if hasattr(self, "options6") else False,
            "log_type": getattr(self, "log_type", "General"),
        }

    def option_clicked(self, clicked_option):
        self._clear_group_selection(self.options, self.option_layouts, clicked_option)
        self.selected_option = clicked_option.text()
        if self.selected_option == "Bugs and errors":
            self.log_type = "Debugging"
        elif self.selected_option == "UI/UX Changes":
            self.log_type = "UIMode"
        else:
            self.log_type = "General"
        self._refresh_infinite_page_choice()
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
                self.next_button.setStyleSheet(
                    self._animated_button_style(
                        margin_right="5px",
                        padding="6px 12px",
                        enabled=self.next_button.isEnabled(),
                    )
                )
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
            self.next_button.setStyleSheet(
                self._animated_button_style(margin_right="5px", padding="6px 12px", enabled=True)
            )

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
        self._clear_group_selection(self.options2, self.option_layouts2, clicked_option)
        self.name_text_box = None
        self.title_text_box = None
        self.selected_option = clicked_option.text()
        if clicked_option.text() == "Proceed on default":
            self.name_text_box = None
            self.title_text_box = None
        self.add_subtext2(clicked_option)
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
            self.validate_required_choices()
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
        self._clear_group_selection(self.options3, self.option_layouts3, clicked_option)
        self.text_size_box = None
        self.line_spacing_box = None
        self.selected_option = clicked_option.text()
        self.add_subtext3(clicked_option)
        self.validate_both_inputs2()

    def add_subtext3(self, clicked_option):
        subtext_map = {
            "Set the font size to": "",
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
            self.validate_required_choices()
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
            if clicked_option.text() == "Set the font size to":
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
        self._clear_group_selection(self.options4, self.option_layouts4, clicked_option)
        self.font_combo_box = None
        self.selected_option = clicked_option.text()
        self.add_subtext4(clicked_option)
        self.validate_required_choices()

    def add_subtext4(self, clicked_option):
        if clicked_option.text() == "Proceed on default":
            self.font_combo_box = None
            subtext_label = QLabel("Continue with the default settings.")
            subtext_label.setStyleSheet("""
                font-size: 14px;
                font-style: italic;
                margin-left: 25px;
                color: #555555;
            """)
            self.validate_required_choices()
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
            self.font_combo_box = subtext_label

            def validate_combo():
                self.validate_required_choices()
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

    def option_clicked6(self, clicked_option):
        if getattr(self, "log_type", None) != "UIMode":
            return
        self._clear_group_selection(self.options6, self.option_layouts6, clicked_option)
        subtext_map = {
            "Yes": "This will disable pages and spaces and use one resizable infinite canvas.",
            "No - Continue with default": "Continue with the default paged setup.",
        }
        subtext_label = QLabel(subtext_map.get(clicked_option.text(), ""))
        subtext_label.setWordWrap(True)
        subtext_label.setStyleSheet("""
            font-size: 14px;
            font-style: italic;
            margin-left: 25px;
            margin-right: 105px;
            color: #555555;
        """)

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

        for option, layout in zip(self.options6, self.option_layouts6):
            if option == clicked_option:
                layout.addWidget(subtext_label)
                subtext_label.setVisible(True)
                break
        self.validate_required_choices()

    def option_clicked5(self, clicked_option):
        self._clear_group_selection(self.options5, self.option_layouts5, clicked_option)
        self.dictionary_box = None
        self.add_subtext5(clicked_option)
        self.validate_font_input2()

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
        self.stacked_widget.setCurrentWidget(self.page2)

    def on_back_clicked4(self):
        # Optionally reset or preserve state when going back.
        self.stacked_widget.setCurrentWidget(self.page2)

    def on_next_clicked2(self):
        self.stacked_widget.setCurrentWidget(self.page5)

    def on_next_clicked3(self):
        self.stacked_widget.setCurrentWidget(self.page5)

    def on_next_clicked4(self):
        self.stacked_widget.setCurrentWidget(self.page5)

    def on_next_clicked5(self):
        self.accept()

    def _set_merged_next_enabled(self, enabled):
        self.next_button2.setEnabled(enabled)
        self.next_button2.setStyleSheet(self._animated_button_style(enabled=enabled))

    def _option_selected(self, options, text):
        return any(option.text() == text and option.property("selected") for option in options)

    def _lds_choices_valid(self):
        if self._option_selected(self.options2, "Proceed on default"):
            return True

        name_selected = self.name_text_box is not None
        title_selected = self.title_text_box is not None
        if not name_selected and not title_selected:
            return False

        name_valid = not name_selected or bool(self.name_text_box.toPlainText().strip())
        title_valid = not title_selected or bool(self.title_text_box.toPlainText().strip())
        return name_valid and title_valid

    def _export_size_choices_valid(self):
        if self._option_selected(self.options3, "Proceed on default"):
            return True

        text_size_selected = self.text_size_box is not None
        line_spacing_selected = self.line_spacing_box is not None
        if not text_size_selected and not line_spacing_selected:
            return False

        text_size_valid = not text_size_selected or bool(self.text_size_box.text().strip())
        line_spacing_valid = not line_spacing_selected or bool(self.line_spacing_box.text().strip())
        return text_size_valid and line_spacing_valid

    def _export_font_choices_valid(self):
        if self._option_selected(self.options4, "Proceed on default"):
            return True
        return self._option_selected(self.options4, "Set font to:")

    def _infinite_page_choice_valid(self):
        if getattr(self, "log_type", None) != "UIMode":
            return True
        return (
            self._option_selected(self.options6, "Yes")
            or self._option_selected(self.options6, "No - Continue with default")
        )

    def validate_required_choices(self):
        enabled = (
            self._lds_choices_valid()
            and self._export_size_choices_valid()
            and self._export_font_choices_valid()
            and self._infinite_page_choice_valid()
        )
        self._set_merged_next_enabled(enabled)
        return enabled

    def validate_both_inputs(self):
        self.validate_required_choices()

    def validate_both_inputs2(self):
        self.validate_required_choices()

    def validate_font_input2(self):
        if self.dictionary_box and self.dictionary_box.toPlainText().strip():
            self.next_button5.setEnabled(True)
        else:
            self.next_button5.setEnabled(False)
        self.next_button5.setStyleSheet(
            self._animated_button_style(padding="6px 15px", enabled=self.next_button5.isEnabled())
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    if wizard.exec() == QDialog.DialogCode.Accepted:
        print("Wizard completed.")
    else:
        print("Wizard cancelled.")
    sys.exit(app.exec())
