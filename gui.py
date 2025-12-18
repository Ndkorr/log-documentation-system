import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QPushButton, QMessageBox, QSpacerItem,
    QSizePolicy, QGraphicsOpacityEffect, QStackedWidget, QWidget,
    QTextEdit, QPlainTextEdit
)
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtSignal

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
    
    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self.effect.blurRadius())
        self.anim.setEndValue(0)
        self.anim.start()
        super().leaveEvent(event)
            

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
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.wizard:  # Use the wizard reference to call the method
                self.wizard.option_clicked(self)
        
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
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.wizard:  # Use the wizard reference to call the method
                self.wizard.option_clicked2(self)
        
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
            border-radius: 5px;
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
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.wizard:  # Use the wizard reference to call the method
                self.wizard.option_clicked3(self)
        
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
    
    def setSelected(self, selected):
        self.setProperty("selected", selected)
        if selected:
            self.setStyleSheet("""
                font-size: 17px;
                padding: 10px;
                margin-left: 15px;
                margin-right: 15px;
                border: 1px solid #0078d7;
                border-radius: 5px;
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
                border-radius: 5px;
            """)

    
class SetupWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Documentation Setup Wizard")
        self.setFixedSize(550, 450)
        self.setStyleSheet("background-color: #FFFFFF;")
        self.selected_option = None
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
            "My Exercise"
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
            "Set the font to",
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
        
        self.stacked_widget.addWidget(self.page3)
    
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
            "My Exercise": "Document your exercise or practice activities."
        }
        subtext = subtext_map.get(clicked_option.text(), "")
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
            # Select only "Proceed on default".
            clicked_option.setSelected(True)
            self.selected_option = clicked_option.text()
            self.add_subtext2(clicked_option)
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

    def add_subtext2(self, clicked_option):
        subtext_map = {
            "Set my name to": "",
            "Set document title to": "",
            "Proceed on default": "Continue with the default settings."
        }
        subtext = subtext_map.get(clicked_option.text(), "")
        # Handle "Proceed on default" differently (no text box).
        if clicked_option.text() == "Proceed on default":
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
            
            if clicked_option.text() == "Set my name to" or "Set document title to":
                if subtext_label != None:
                    # Connect the textChanged signal to a custom method to handle input validation.
                    subtext_label.textChanged.connect(lambda: self.validate_input_with_error_handling(subtext_label))
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
        # Unselect all options and remove subtext labels.
        for option, layout in zip(self.options3, self.option_layouts3):
            option.setSelected(False)
            if layout.count() > 1:  # Remove subtext if it exists
                subtext_label = layout.itemAt(1).widget()
                layout.removeWidget(subtext_label)
                subtext_label.deleteLater()
    
        # Select the clicked option.
        clicked_option.setSelected(True)
        self.selected_option = clicked_option.text()
        # Add the subtext label below the clicked option.
        self.add_subtext3(clicked_option)

    def add_subtext3(self, clicked_option):
        subtext_map = {
            "Set the text size to": "",
            "Set the line spacing to": "",
            "Set the font to": "",
            "Proceed on default": "Continue with the default settings."
        }
        subtext = subtext_map.get(clicked_option.text(), "")

        # Handle "Proceed on default" differently (no text box).
        if clicked_option.text() == "Proceed on default":
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

            # Connect the textChanged signal to a custom method to handle input validation.
            subtext_label.textChanged.connect(lambda: self.validate_input_with_error_handling(subtext_label))
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
        for option, layout in zip(self.options3, self.option_layouts3):
            if option == clicked_option:
                # Remove existing subtext widgets before adding the new one.
                while layout.count() > 1:
                    widget = layout.itemAt(1).widget()
                    layout.removeWidget(widget)
                    widget.deleteLater()
                layout.addWidget(subtext_label)
                break
    
    
    def on_next_clicked(self):
        self.stacked_widget.setCurrentWidget(self.page2)
    
    def on_back_clicked(self):
        # Optionally reset or preserve state when going back.
        self.stacked_widget.setCurrentWidget(self.page1)
    
    def on_next_clicked2(self):
        self.stacked_widget.setCurrentWidget(self.page3)
    
    def on_back_clicked2(self):
        # Optionally reset or preserve state when going back.
        self.stacked_widget.setCurrentWidget(self.page2)
    
    def validate_input_with_error_handling(self, text_box):
        # Check if the text box is empty or unchanged.
        if text_box.toPlainText().strip():
            # Enable the "Next" button if there is input.
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
            # Disable the "Next" button if the input is empty or unchanged.
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
            
    def validate_input_with_error_handling2(self, text_box2):
        # Check if the text box is empty or unchanged.
        if text_box2.toPlainText().strip():
            # Enable the "Next" button if there is input.
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
            # Disable the "Next" button if the input is empty or unchanged.
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    if wizard.exec() == QDialog.DialogCode.Accepted:
        print("Wizard completed.")
    else:
        print("Wizard cancelled.")
    sys.exit(app.exec())
