from PyQt6.QtWidgets import (
    QMainWindow, QFrame, QDateEdit, QSlider, 
    QMenu, QDialog, QProgressDialog, QMenuBar, 
    QLabel, QColorDialog, QApplication, QLineEdit, 
    QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QListWidget, QInputDialog, 
    QFileDialog, QMessageBox, QComboBox, QScrollArea, 
    QSizePolicy, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QSpacerItem, QStackedWidget, QTabWidget, QToolButton,
    QPlainTextEdit, QCheckBox, QSpinBox, QFontComboBox
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
#from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlShutdown
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import os
import subprocess
import re
import random
import string
import names
import shutil
import time


def get_config_dir(base_path=None):
    if base_path:
        config_dir = os.path.join(base_path, "config")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return config_dir
    else:
        # Only return, do not create in root
        return os.path.join(os.getcwd(), "config")


def get_screen_at_cursor():
    # Get the screen where the cursor is currently located.
    # Falls back to primary screen if detection fails.
    
    screen = QApplication.screenAt(QCursor.pos())
    if screen is None:
        screen = QApplication.primaryScreen()
    return screen


class FileNameDialog(QDialog):
    def __init__(self, extension, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log File Name")
        self.setFixedSize(350, 120)
        layout = QVBoxLayout(self)
        label = QLabel(f"Enter log file name (*.{extension}):")
        layout.addWidget(label)
        hbox = QHBoxLayout()
        self.name_edit = QLineEdit()
        hbox.addWidget(self.name_edit)
        self.ext_label = QLabel(f".{extension}")
        self.ext_label.setStyleSheet("color: gray;")
        hbox.addWidget(self.ext_label)
        layout.addLayout(hbox)
        btn_box = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(ok_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

    def get_filename(self):
        return self.name_edit.text().strip()


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
        self.type_combo = QComboBox(self)
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
        screen = get_screen_at_cursor()
        screen_geometry = screen.availableGeometry() if screen else QApplication.primaryScreen().availableGeometry()
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
        screen = get_screen_at_cursor()
        screen_geometry = screen.availableGeometry() if screen else QApplication.primaryScreen().availableGeometry()
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
    
    def center(self):
        # Center the dialog on the screen where cursor is located
        screen = get_screen_at_cursor()
        screen_geometry = screen.availableGeometry()
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

        # Animate the horizontal expansion of the window on the cursor's screen
        screen = get_screen_at_cursor()
        screen_geometry = screen.availableGeometry() if screen else QApplication.primaryScreen().availableGeometry()
        target_width = 800  # Target width for the expanded window
        target_geometry = QRect(
            screen_geometry.left() + (screen_geometry.width() - target_width) // 2,  # Center horizontally on active screen
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
        screen = get_screen_at_cursor()
        screen_geometry = screen.availableGeometry() if screen else QApplication.primaryScreen().availableGeometry()
        default_width = 400  # Default width for the window
        target_geometry = QRect(
            screen_geometry.left() + (screen_geometry.width() - default_width) // 2,  # Center horizontally on active screen
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
        # Center the dialog on the screen where cursor is located
        screen = get_screen_at_cursor()
        screen_geometry = screen.availableGeometry()
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


class ClickableLogLabel(QLabel):
    # Custom label for logs that responds to clicks and provides highlighting
    clicked = pyqtSignal()
    doubleClicked = pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_selected = False
        self.base_style_template = """
            QLabel {{
                background-color: {background};
                color: #333333;
                font-size: {font_size}pt;
                font-family: "{font_family}";
                margin: 2px 0px;
                padding: 5px;
            }}
        """
        self.important_style_template = """
            QLabel {{
                background-color: {background};
                color: #333333;
                font-size: {font_size}pt;
                font-family: "{font_family}";
                margin: 2px 0px;
                padding: 5px;
                border-left: 5px solid {accent};
            }}
        """
        self.selected_style = """
            QLabel {
                background-color: #e3f2fd;
                color: #333333;
                font-size: 11px;
                margin: 2px 0px;
                padding: 5px;
                border-left: 3px solid #2196F3;
            }
        """
        self.setStyleSheet(self.current_base_style())

    def selected_background_color(self):
        background = self.property("log_background") or "transparent"
        mode = self.property("colored_selection_mode") or "darker"
        custom_color = self.property("colored_selection_color") or "#d6eaff"
        
        if mode == "custom":
            return custom_color
        
        # For logs without background, use the fixed highlight color (uniform)
        if background == "transparent":
            return custom_color
        
        # For logs with colored backgrounds, apply lighter/darker transformation
        color = QColor(background)
        if not color.isValid():
            return custom_color
        if mode == "lighter":
            return color.lighter(115).name()
        return color.darker(115).name()

    def current_base_style(self):
        background = self.property("log_background") or "transparent"
        accent = self.property("important_accent_color") or "#f39c12"
        font_size = self.property("viewer_text_size") or 11
        font_family = self.property("viewer_font_family") or "Arial"
        template = self.important_style_template if self.property("important") else self.base_style_template
        return template.format(
            background=background,
            accent=accent,
            font_size=font_size,
            font_family=font_family,
        )
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)
    
    def set_selected(self, selected):
        self.is_selected = selected
        if selected:
            accent = self.property("selection_accent_color") or "#2196F3"
            border_width = 5 if self.property("important") else 3
            self.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.selected_background_color()};
                    color: #222222;
                    font-size: {self.property("viewer_text_size") or 11}pt;
                    font-family: "{self.property("viewer_font_family") or "Arial"}";
                    margin: 2px 0px;
                    padding: 5px;
                    border-left: {border_width}px solid {accent};
                }}
            """)
        else:
            self.setStyleSheet(self.current_base_style())
    
    def enterEvent(self, event):
        if not self.is_selected:
            accent = self.property("important_accent_color") or "#f39c12"
            border = f"border-left: 5px solid {accent};" if self.property("important") else ""
            hover_style = f"""
                QLabel {{
                    background-color: #f5f5f5;
                    color: #333333;
                    font-size: {self.property("viewer_text_size") or 11}pt;
                    font-family: "{self.property("viewer_font_family") or "Arial"}";
                    margin: 2px 0px;
                    padding: 5px;
                    {border}
                }}
            """
            self.setStyleSheet(hover_style)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        if not self.is_selected:
            self.setStyleSheet(self.current_base_style())
        super().leaveEvent(event)


class LogsViewerWindow(QMainWindow):
    # Window to display all logs in a vertical scrollable view with fixed width
    def __init__(self, log_list, parent=None):
        super().__init__(None)
        self.parent_widget = parent
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle("Logs Viewer")
        self.setFixedWidth(600)
        self.selected_log_label = None  # Track the currently selected log
        
        # Pick the relevant screen from cursor position, then fall back.
        screen = get_screen_at_cursor()
        if not screen and self.parent_widget and hasattr(self.parent_widget, "screen"):
            screen = self.parent_widget.screen()
        if not screen:
            screen = QApplication.primaryScreen()

        if screen:
            # use availableGeometry() to avoid taskbar; use screen.geometry() for full resolution height
            screen_rect = screen.geometry()
            target_height = screen_rect.height()
            self.setFixedHeight(target_height)
            self.resize(self.width(), target_height)
        else:
            self.resize(700, 600)  # fallback
            
        self.log_list = log_list
        self.last_loaded_count = 0  # Track how many logs we've already added
        self.setup_ui()
        self.position_on_rightmost()
        
        # Connect to parent signals for real-time sync
        if parent and hasattr(parent, 'logAdded'):
            parent.logAdded.connect(self.on_log_added)
        if parent and hasattr(parent, 'logsCleared'):
            parent.logsCleared.connect(self.on_logs_cleared)
        if parent and hasattr(parent, 'logEdited'):
            parent.logEdited.connect(self.on_log_edited)
        if parent and hasattr(parent, 'logDeleted'):
            parent.logDeleted.connect(self.on_log_deleted)
        if parent and hasattr(parent, 'filterChanged'):
            parent.filterChanged.connect(self.on_filter_changed)
        if parent and hasattr(parent, 'importanceChanged'):
            parent.importanceChanged.connect(self.refresh_logs)

    def viewer_pref(self, name, default):
        return getattr(self.parent_widget, name, default)

    def apply_viewer_theme(self):
        dark_mode = self.viewer_pref("viewer_dark_mode", False)
        bg = "#1f2329" if dark_mode else "#FFFFFF"
        scrollbar_bg = "#2b3038" if dark_mode else "#EEEEEE"
        handle_bg = "#5c6673" if dark_mode else "#CCCCCC"
        handle_hover = "#788391" if dark_mode else "#AAAAAA"
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {bg};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {scrollbar_bg};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {handle_bg};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {handle_hover};
            }}
        """)
        if hasattr(self, "logs_container"):
            self.logs_container.setStyleSheet(f"background-color: {bg};")
        if hasattr(self, "logs_layout"):
            self.logs_layout.setSpacing(int(self.viewer_pref("viewer_line_spacing", 2)))

    def configure_viewer_label(self, log_label, log_text, source_index):
        log_label.setText(log_text)
        log_label.setTextFormat(Qt.TextFormat.RichText)
        log_label.setWordWrap(bool(self.viewer_pref("viewer_word_wrap", True)))
        log_label.setOpenExternalLinks(False)
        log_label.setProperty("source_index", source_index)
        log_label.setProperty("viewer_text_size", int(self.viewer_pref("viewer_text_size", 11)))
        log_label.setProperty("viewer_font_family", self.viewer_pref("viewer_font_family", "Arial"))
        log_label.setProperty("colored_selection_mode", self.viewer_pref("viewer_colored_selection_mode", "darker"))
        log_label.setProperty("colored_selection_color", self.viewer_pref("viewer_colored_selection_color", "#d6eaff"))
        log_label.setProperty("selection_accent_color", self.viewer_pref("viewer_selection_accent_color", "#2196F3"))
        if self.parent_widget and hasattr(self.parent_widget, "is_important_log"):
            log_label.setProperty("important", self.parent_widget.is_important_log(log_text))
            log_label.setProperty("log_background", self.parent_widget.get_log_background_color(log_text))
            log_label.setProperty("important_accent_color", getattr(self.parent_widget, "important_accent_color", "#f39c12"))
        log_label.set_selected(False)
        log_label.clicked.connect(lambda lbl=log_label: self.on_log_clicked(lbl))
        log_label.doubleClicked.connect(lambda lbl=log_label: self.on_log_double_clicked(lbl))
        
    def setup_ui(self):
        # Set up the UI with fixed width and scrollable height
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area for logs
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Create a container widget for logs
        self.logs_container = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_container)
        self.logs_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.logs_container)
        main_layout.addWidget(self.scroll_area)
        self.apply_viewer_theme()
        
        spacer = QSpacerItem(20, 150, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.logs_layout.addItem(spacer)
        self.logs_layout.addStretch()
        
        # Set window size: fixed width, variable height
        self.setFixedWidth(700)
        self.resize(700, 600)
    
    def refresh_logs(self):
        selected_source_index = None
        if self.selected_log_label is not None:
            selected_source_index = self.selected_log_label.property("source_index")
        # Reload all logs from the log_list - used when loading from file
        self.load_logs()
        if selected_source_index is not None:
            for i in range(self.logs_layout.count() - 2):
                widget = self.logs_layout.itemAt(i).widget()
                if isinstance(widget, ClickableLogLabel) and widget.property("source_index") == selected_source_index:
                    self.on_log_clicked(widget)
                    break
        # Scroll to bottom to show latest logs
        scrollbar = self.scroll_area.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())    
        
    def load_logs(self, visible_only=False):
        # Load all logs from the log_list into the viewer.
        # Keep the final spacer/stretch and clear only existing log widgets.
        self.selected_log_label = None
        while self.logs_layout.count() > 2:
            child = self.logs_layout.takeAt(0)
            if child and child.widget():
                child.widget().deleteLater()

        # Add all logs from the log_list before the spacer/stretch
        for i in range(self.log_list.count()):
            item = self.log_list.item(i)
            widget = self.log_list.itemWidget(item)
            if visible_only and item and item.isHidden():
                continue

            if widget and isinstance(widget, QLabel):
                log_label = ClickableLogLabel()
                self.configure_viewer_label(log_label, widget.text(), i)
                # Insert before the spacer/stretch
                insert_index = max(0, self.logs_layout.count() - 2)
                self.logs_layout.insertWidget(insert_index, log_label)

        self.last_loaded_count = self.log_list.count()

    def on_filter_changed(self):
        # Rebuild from currently visible logs after filter changes.
        self.load_logs(visible_only=True)
    
    def on_log_added(self, log_text):
        # Handle a single new log emitted from the main app; build the viewer label from the provided text.
        if self.last_loaded_count < self.log_list.count():
            log_label = ClickableLogLabel()
            self.configure_viewer_label(log_label, log_text, self.last_loaded_count)
            insert_index = max(0, self.logs_layout.count() - 2)
            self.logs_layout.insertWidget(insert_index, log_label)
            self.last_loaded_count += 1
    
    def on_logs_cleared(self):
        # Handle logs cleared from main app.
        # Clear all logs but keep spacer and stretch
        self.selected_log_label = None
        while self.logs_layout.count() > 2:
            child = self.logs_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.last_loaded_count = 0
        
    def on_log_edited(self, index):
        # Handle log edited from main app - refresh the specific log.
        self.refresh_logs()

    def on_log_deleted(self, index):
        # Handle log deleted from main app - remove it from viewer
        # Remove from viewer layout (accounting for spacer/stretch at end)
        if 0 <= index < self.logs_layout.count() - 2:
            child = self.logs_layout.takeAt(index)
            if child and child.widget() is self.selected_log_label:
                self.selected_log_label = None
            if child and child.widget():
                child.widget().deleteLater()
            self.last_loaded_count -= 1

    def on_log_clicked(self, clicked_widget):
        # Highlight the clicked log and clear previous selection.
        if not isinstance(clicked_widget, ClickableLogLabel):
            return

        if self.selected_log_label and self.selected_log_label is not clicked_widget:
            try:
                self.selected_log_label.set_selected(False)
            except RuntimeError:
                self.selected_log_label = None

        clicked_widget.set_selected(True)
        self.selected_log_label = clicked_widget

    def on_log_double_clicked(self, clicked_widget):
        # Bring main window to front and focus the matching source log row.
        source_index = clicked_widget.property("source_index")
        if source_index is None or not self.parent_widget:
            return

        if self.parent_widget.isMinimized():
            self.parent_widget.showNormal()
        self.parent_widget.raise_()
        self.parent_widget.activateWindow()

        if 0 <= source_index < self.parent_widget.log_list.count():
            item = self.parent_widget.log_list.item(source_index)
            if item:
                self.parent_widget.log_list.setCurrentItem(item)
                self.parent_widget.log_list.scrollToItem(item)
                self.parent_widget.log_list.setFocus()
    
    def position_on_rightmost(self):
        # Position the window on the rightmost part of the screen where cursor is
        screen = get_screen_at_cursor()
        
        if screen:
            screen_rect = screen.availableGeometry()
            # Position at the right edge of the screen
            x = screen_rect.right() - self.width()
            y = screen_rect.top()
            self.move(x, y)


class LogApp(QWidget):
    # Signals for real-time sync with LogsViewerWindow
    logAdded = pyqtSignal(str)      # Emitted when a new log is added
    logsCleared = pyqtSignal()      # Emitted when logs are cleared
    logEdited = pyqtSignal(int)     # Emitted when a log is edited (index)
    logDeleted = pyqtSignal(int)    # Emitted when a log is deleted (index)
    filterChanged = pyqtSignal()    # Emitted when log filter visibility changes
    importanceChanged = pyqtSignal()

    IMPORTANT_MARKER = "<!-- LDS_IMPORTANT:1 -->"
    NOT_IMPORTANT_MARKER = "<!-- LDS_IMPORTANT:0 -->"

    DEFAULT_COUNTERS = {
        "Problem ★": 0,
        "Solution ■": 0,
        "Bug ▲": 0,
        "Changes ◆": 0,
        "Just Details": 0,
        "Importance": 0,
    }

    DEFAULT_LOG_THEME_COLORS = {
        "important_accent_color": "#f39c12",
        "bug_background_color": "#ffd9d9",
        "problem_background_color": "#fff4bf",
        "resolved_background_color": "#d8f5df",
        "default_background_color": "transparent",
    }

    DEFAULT_VIEWER_PREFERENCES = {
        "viewer_dark_mode": False,
        "viewer_line_spacing": 2,
        "viewer_text_size": 11,
        "viewer_font_family": "Arial",
        "viewer_word_wrap": True,
        "viewer_colored_selection_mode": "darker",
        "viewer_colored_selection_color": "#d6eaff",
        "viewer_selection_accent_color": "#2196F3",
    }
    
    def __init__(self, setup_data=None, log_mode="General", file_path=None, parent=None):
        super().__init__(parent)
        self.current_file = file_path
        # Use setup_data to initialize user/project config
        if setup_data:
            self.user_name = setup_data.get("user_name", "")
            self.pdf_title = setup_data.get("pdf_title", "Log Documentation")
            self.pdf_font_size = setup_data.get("pdf_font_size", 12)
            self.pdf_line_spacing = setup_data.get("pdf_line_spacing", 1.5)
            self.pdf_font = setup_data.get("pdf_font", "Arial")
            self.custom_dictionary = setup_data.get("custom_dictionary", "")
        else:
            # fallback to loading config from file or defaults
            self.load_user_config()
        print("Initializing LogApp...")
        self.log_mode = setup_data.get("log_type", "General") if setup_data else "General"
        self.log_type = "General" if log_mode == "General" else "Debugging"
        self.load_default_log_theme_colors()
        self.load_user_config()
        self.load_color_from_config()  # Load the saved color
        self.init_ui()
        self.custom_dictionary = getattr(self, "custom_dictionary", "")
        self.keyword_definitions = {}
        self.keyword_definitions_file = self.get_keyword_definitions_file()
        self.load_keyword_definitions()  # Load keyword definitions

        self.unsaved_changes = False

        # Add Undo/Redo Stacks
        self.undo_stack = []  # Stores previous log states
        self.redo_stack = []  # Stores undone states

        # **Store entire log restore points**
        self.restore_points = {}  # {version_name: log_snapshot}

        # Initialize counters for different log types
        self.log_counters = dict(self.DEFAULT_COUNTERS)

        # Start the hardware monitoring thread
        self.hw_monitor = HardwareMonitor()
        self.hw_monitor.data_ready.connect(self.update_system_info)
        self.hw_monitor.start()
        self.logs_viewer = LogsViewerWindow(self.log_list, self)
        self.logs_viewer.show()
        print("LogApp initialized.")

        # If a file_path is provided, load the logs immediately.
        if file_path:
            self.open_logs(file_path)

    def is_important_log(self, html_text):
        return self.IMPORTANT_MARKER in html_text

    def load_default_log_theme_colors(self):
        for key, value in self.DEFAULT_LOG_THEME_COLORS.items():
            setattr(self, key, value)
        for key, value in self.DEFAULT_VIEWER_PREFERENCES.items():
            setattr(self, key, value)

    def set_importance_marker(self, html_text, important):
        html_text = html_text.replace(self.IMPORTANT_MARKER, "").replace(self.NOT_IMPORTANT_MARKER, "")
        marker = self.IMPORTANT_MARKER if important else self.NOT_IMPORTANT_MARKER
        return f"{marker}{html_text}"

    def get_log_background_color(self, html_text):
        plain_text = self.strip_html(html_text)
        if "Fixed" in plain_text or "Resolved" in plain_text or "■" in plain_text or "Solution #" in plain_text:
            return getattr(self, "resolved_background_color", self.DEFAULT_LOG_THEME_COLORS["resolved_background_color"])
        if "▲" in plain_text:
            return getattr(self, "bug_background_color", self.DEFAULT_LOG_THEME_COLORS["bug_background_color"])
        if "★" in plain_text:
            return getattr(self, "problem_background_color", self.DEFAULT_LOG_THEME_COLORS["problem_background_color"])
        return getattr(self, "default_background_color", self.DEFAULT_LOG_THEME_COLORS["default_background_color"])

    def apply_log_label_style(self, label, important=False):
        background = self.get_log_background_color(label.text())
        accent_color = getattr(self, "important_accent_color", self.DEFAULT_LOG_THEME_COLORS["important_accent_color"])
        border = f"border-left: 5px solid {accent_color};" if important else ""
        padding = "padding-left: 6px;" if important else "padding-left: 0px;"
        if important:
            label.setStyleSheet(f"QLabel {{ background-color: {background}; {border} {padding} }}")
        else:
            label.setStyleSheet(f"QLabel {{ background-color: {background}; {padding} }}")

    def refresh_log_label_styles(self):
        for index in range(self.log_list.count()):
            item = self.log_list.item(index)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel):
                self.apply_log_label_style(label, self.is_important_log(label.text()))
        if hasattr(self, "logs_viewer") and self.logs_viewer:
            self.logs_viewer.refresh_logs()

    def count_important_logs(self):
        count = 0
        for index in range(self.log_list.count()):
            item = self.log_list.item(index)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel) and self.is_important_log(label.text()):
                count += 1
        return count

    def update_importance_counter(self):
        self.log_counters["Importance"] = self.count_important_logs()

    def configure_log_label(self, label, html_text, word_wrap=False):
        label.setText(html_text)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setOpenExternalLinks(False)
        try:
            label.linkActivated.disconnect(self.handle_internal_link)
        except TypeError:
            pass
        label.linkActivated.connect(self.handle_internal_link)
        label.setWordWrap(word_wrap)
        self.apply_log_label_style(label, self.is_important_log(html_text))

    def create_menu_bar(self, layout):
        menu_bar = QMenuBar(self)
        layout.setMenuBar(menu_bar)  # Attach menu bar to layout

        # Recent Files Menu
        self.recent_menu = QMenu("Recent", self)
        menu_bar.addMenu(self.recent_menu)
        self.update_recent_files_menu()

        # View Menu
        view_menu = QMenu("View", self)
        menu_bar.addMenu(view_menu)

        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self.open_preferences)
        view_menu.addAction(preferences_action)

        editor_playground_action = QAction("Editor's Playground", self)
        editor_playground_action.triggered.connect(self.open_editor_playground)
        view_menu.addAction(editor_playground_action)

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

    def open_preferences(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Log Viewer Preferences")
        dialog.setFixedSize(360, 340)

        layout = QVBoxLayout(dialog)

        dark_mode_input = QCheckBox("Dark mode")
        dark_mode_input.setChecked(bool(getattr(self, "viewer_dark_mode", False)))
        layout.addWidget(dark_mode_input)

        wrap_input = QCheckBox("Word wrapping")
        wrap_input.setChecked(bool(getattr(self, "viewer_word_wrap", True)))
        layout.addWidget(wrap_input)

        line_spacing_layout = QHBoxLayout()
        line_spacing_layout.addWidget(QLabel("Line spacing:"))
        line_spacing_input = QSpinBox()
        line_spacing_input.setRange(0, 24)
        line_spacing_input.setValue(int(getattr(self, "viewer_line_spacing", 2)))
        line_spacing_layout.addWidget(line_spacing_input)
        layout.addLayout(line_spacing_layout)

        text_size_layout = QHBoxLayout()
        text_size_layout.addWidget(QLabel("Text size:"))
        text_size_input = QSpinBox()
        text_size_input.setRange(4, 32)
        text_size_input.setValue(int(getattr(self, "viewer_text_size", 11)))
        text_size_layout.addWidget(text_size_input)
        layout.addLayout(text_size_layout)

        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font:"))
        font_input = QFontComboBox()
        font_input.setCurrentFont(QFont(getattr(self, "viewer_font_family", "Arial")))
        font_layout.addWidget(font_input)
        layout.addLayout(font_layout)

        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Selected colored log:"))
        selection_mode_input = QComboBox()
        selection_mode_input.addItems(["Darker", "Lighter", "Choose Color"])
        current_mode = getattr(self, "viewer_colored_selection_mode", "darker")
        mode_to_label = {
            "darker": "Darker",
            "lighter": "Lighter",
            "custom": "Choose Color",
        }
        selection_mode_input.setCurrentText(mode_to_label.get(current_mode, "Darker"))
        selection_layout.addWidget(selection_mode_input)
        layout.addLayout(selection_layout)

        selected_color = {"value": getattr(self, "viewer_colored_selection_color", "#d6eaff")}
        color_button = QPushButton("Selected Highlight Color")
        color_button.setEnabled(selection_mode_input.currentText() == "Choose Color")
        color_button.setStyleSheet(f"background-color: {selected_color['value']};")
        layout.addWidget(color_button)

        accent_color = {"value": getattr(self, "viewer_selection_accent_color", "#2196F3")}
        accent_button = QPushButton("Selection Border Accent Color")
        accent_button.setStyleSheet(f"background-color: {accent_color['value']};")
        layout.addWidget(accent_button)

        def choose_selection_color():
            color = QColorDialog.getColor(QColor(selected_color["value"]), dialog)
            if color.isValid():
                selected_color["value"] = color.name()
                color_button.setStyleSheet(f"background-color: {selected_color['value']};")

        def choose_accent_color():
            color = QColorDialog.getColor(QColor(accent_color["value"]), dialog)
            if color.isValid():
                accent_color["value"] = color.name()
                accent_button.setStyleSheet(f"background-color: {accent_color['value']};")

        def update_selection_color_enabled(text):
            color_button.setEnabled(text == "Choose Color")

        selection_mode_input.currentTextChanged.connect(update_selection_color_enabled)
        color_button.clicked.connect(choose_selection_color)
        accent_button.clicked.connect(choose_accent_color)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def save_preferences():
            self.viewer_dark_mode = dark_mode_input.isChecked()
            self.viewer_word_wrap = wrap_input.isChecked()
            self.viewer_line_spacing = line_spacing_input.value()
            self.viewer_text_size = text_size_input.value()
            self.viewer_font_family = font_input.currentFont().family()
            selection_label_to_mode = {
                "Darker": "darker",
                "Lighter": "lighter",
                "Choose Color": "custom",
            }
            self.viewer_colored_selection_mode = selection_label_to_mode.get(selection_mode_input.currentText(), "darker")
            self.viewer_colored_selection_color = selected_color["value"]
            self.viewer_selection_accent_color = accent_color["value"]
            self.save_user_config()
            if hasattr(self, "logs_viewer") and self.logs_viewer:
                self.logs_viewer.apply_viewer_theme()
                self.logs_viewer.refresh_logs()
            dialog.accept()

        save_button.clicked.connect(save_preferences)
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec()

    def open_editor_playground(self):
        QMessageBox.information(
            self,
            "Editor's Playground",
            "Editor's playground will be added here."
        )

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
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
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

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.isMinimized():
            self.showNormal()
        self.raise_()
        self.activateWindow()

    def center(self):
        screen = get_screen_at_cursor()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())
        print("Window centered.")

    def change_log_type(self, text):
        print(f"Changing log type to: {text}")
        self.log_type = text

    def set_user_name(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Customize")
        dialog.setGeometry(100, 100, 400, 300)
        dialog.setFixedSize(400, 300)  # Make dialog not resizable
        dialog_layout = QVBoxLayout(dialog)

        # Center the dialog on the screen where cursor is located
        screen = get_screen_at_cursor()
        screen_geometry = screen.availableGeometry() if screen else QApplication.primaryScreen().availableGeometry()
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
            color = QColorDialog.getColor(getattr(self, 'text_color', QColor("green")), dialog)
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
                self.pdf_title = title_input.text().strip() or "Log Documentation"
                self.pdf_font_size = int(font_size_input.text().strip()) if font_size_input.text().strip().isdigit() else 12
                self.pdf_line_spacing = float(spacing_input.text().strip()) if spacing_input.text().strip().replace(".", "", 1).isdigit() else 1.5
                # Save to project config if a project is open
                if self.current_file:
                    project_folder = os.path.dirname(self.current_file or "")
                    config_folder = os.path.join(project_folder, "config")
                    os.makedirs(config_folder, exist_ok=True)
                    config_path = os.path.join(config_folder, "user_config.json")
                    # Load existing config if present
                    config = {}
                    if os.path.exists(config_path):
                        with open(config_path, "r", encoding="utf-8") as f:
                            config = json.load(f)
                    config.update({
                        "user_name": self.user_name,
                        "pdf_title": self.pdf_title,
                        "pdf_font_size": self.pdf_font_size,
                        "pdf_line_spacing": self.pdf_line_spacing,
                        "text_color": self.text_color.name() if hasattr(self, 'text_color') else "#008000"
                    })
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=4)
                else:
                    # Fallback to global config if no project open
                    self.save_user_config()
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Caution", "No Name Inserted.")

        save_button.clicked.connect(save_customization)
        dialog.setLayout(dialog_layout)
        dialog.exec()

    def get_system_info(self):
        return self.memory_usage

    def update_system_info(self, memory_usage, cpu_usage, gpu_usage=None):
        self.memory_usage = memory_usage
        self.cpu_usage = cpu_usage
        self.gpu_usage = gpu_usage

    def add_log(self):
        self.unsaved_changes = True
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

            # Auto-increment counter for the selected category.
            # Ensure missing keys from older counter files are created on the fly.
            if category not in self.log_counters:
                self.log_counters[category] = 0
            self.log_counters[category] += 1
            log_number = f" #{self.log_counters[category]}"

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
            self.configure_log_label(label, log_entry, word_wrap=False)
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

            # Emit signal for real-time sync with LogsViewerWindow
            self.logAdded.emit(log_entry)

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
                status_date = datetime.now().strftime("[%Y-%m-%d %H:%M:%SH]")
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

                existing_html = label.text()
                existing_plain = self.strip_html(existing_html)
                kept_status_badges = []
                if "Resolved" in existing_html:
                    kept_status_badges.append('<span style="background-color: green; color: white;">Resolved</span>')
                if "Fixed" in existing_html:
                    kept_status_badges.append('<span style="background-color: green; color: white;">Fixed</span>')

                counter_match = re.search(r"(#\d+)\s*$", existing_plain)
                log_number = f" {counter_match.group(1)}" if counter_match else ""

                user_info = f" - User: {self.user_name}" if getattr(self, "user_name", "") else ""
                status_prefix = f"  |  {status_date}{user_info}{log_number}"
                edited_badge = '<span style="background-color: green; color: white;">Edited</span>'
                all_status_badges = kept_status_badges + [edited_badge]
                status_suffix = f"{status_prefix} " + " ".join(all_status_badges)

                updated_text = (
                    f'<span style="color:{icon_color};">{category_icon}</span> '
                    f'<span style="color:{main_text_color};">{timestamp} [{self.log_type}] {plain_text}{status_suffix}</span>'
                )
                # Update the existing label with the new rich text
                updated_text = self.set_importance_marker(updated_text, self.is_important_log(existing_html))
                self.configure_log_label(label, updated_text, word_wrap=False)
                # No need to re-add the widget or duplicate it; this updates the current item.
            elif not plain_text.strip():
                QMessageBox.warning(self, "Invalid Input", "Log entry cannot be empty.")

    def save_logs(self):
        self.unsaved_changes = False
        print("Saving logs...")
        # If file is already created, save as usual (for autosave compatibility)
        if self.current_file:
            file_name = self.current_file
            project_folder = os.path.dirname(file_name)
            config_folder = os.path.join(project_folder, "config")
            os.makedirs(config_folder, exist_ok=True)
        else:
            project_folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
            if not project_folder:
                return
            config_folder = os.path.join(project_folder, "config")
            os.makedirs(config_folder, exist_ok=True)
            ext = "ldsg" if self.log_type == "General" else "ldsd"
            # Use the custom dialog
            dlg = FileNameDialog(ext, self)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                return
            file_base = dlg.get_filename()
            if not file_base:
                return
            file_name = os.path.join(project_folder, f"{file_base}.{ext}")
            self.current_file = file_name

        # Save the log file
        with open(file_name, "w", encoding="utf-8") as file:
            for index in range(self.log_list.count()):
                item = self.log_list.item(index)
                label = self.log_list.itemWidget(item)
                if isinstance(label, QLabel):
                    file.write(label.text() + "\n")

        # Save config files in the config subfolder
        self.update_importance_counter()
        with open(os.path.join(config_folder, "counters.json"), "w", encoding="utf-8") as f:
            json.dump(self.log_counters, f, indent=4)
        with open(os.path.join(config_folder, "restore_points.json"), "w", encoding="utf-8") as f:
            json.dump(self.restore_points, f, indent=4)
        with open(os.path.join(config_folder, "keyword_definitions.json"), "w", encoding="utf-8") as f:
            json.dump(self.keyword_definitions, f, indent=4)
        self.save_user_config()

        print(f"Logs saved to {file_name}")
        print(f"Config saved to {config_folder}")

        self.setWindowTitle("Log Documentation System - File saved")  # Update title
        QTimer.singleShot(2000, lambda: self.setWindowTitle("Log Documentation System"))   # Reset after 2 seconds

    def open_logs(self, file_path=None):
        print("Opening logs...")
        if not file_path:  # If no file path is provided, use the file dialog
            filter_str = "General Logs (*.ldsg)" if self.log_type == "General" else "Debugging Logs (*.ldsd)"
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Logs", "", filter_str)
        if not file_path:
            return
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"Log file was not found:\n{file_path}")
            return

        self.current_file = file_path
        self.save_recent_file(file_path)
        self.log_list.clear()
        self.load_user_config()

        # Use project folder and config subfolder
        project_folder = os.path.dirname(file_path)
        config_folder = os.path.join(project_folder, "config")

        # Load log counters
        counters_path = os.path.join(config_folder, "counters.json")
        if os.path.exists(counters_path):
            try:
                with open(counters_path, "r", encoding="utf-8") as f:
                    loaded_counters = json.load(f)
                    self.log_counters = dict(self.DEFAULT_COUNTERS)
                    if isinstance(loaded_counters, dict):
                        self.log_counters.update(loaded_counters)
            except Exception as e:
                print(f"Error loading log counters: {e}")
                self.log_counters = dict(self.DEFAULT_COUNTERS)
        else:
            self.detect_log_counters()

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
            progress_dialog.setFixedSize(300, 100)
            progress_dialog.setWindowFlag(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
            progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
            progress_dialog.setMinimumDuration(0)  # Show immediately
            progress_dialog.setValue(0)
            
            # Position dialog on the screen where cursor is (multi-monitor support)
            screen = get_screen_at_cursor()
            if screen:
                screen_rect = screen.availableGeometry()
                # Center the progress dialog on the cursor's screen
                x = screen_rect.left() + (screen_rect.width() - progress_dialog.width()) // 2
                y = screen_rect.top() + (screen_rect.height() - progress_dialog.height()) // 2
                progress_dialog.move(x, y) 
            
            if hasattr(self, 'logs_viewer') and self.logs_viewer:
                self.logs_viewer.hide()

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
                    self.configure_log_label(label, line, word_wrap=False)
                    label.adjustSize()

                    # Create a QListWidgetItem and set its size hint to the label's size
                    item = QListWidgetItem()
                    item.setSizeHint(label.sizeHint())
                    self.log_list.addItem(item)
                    self.log_list.setItemWidget(item, label)
                    self.logAdded.emit(label.text())
                    print(f"Loaded log: {line}")

                # Update the progress dialog
                progress_dialog.setValue(i + 1)
                QApplication.processEvents()  # Allow the UI to update

            progress_dialog.close()
            self.update_importance_counter()
            self.save_log_counters()
            self.refresh_log_label_styles()
            print(f"Logs loaded successfully from {file_path}")
            
            if hasattr(self, 'logs_viewer') and self.logs_viewer:
                self.logs_viewer.show()

            # Scroll to the last item in the log list
            if self.log_list.count() > 0:
                last_item = self.log_list.item(self.log_list.count() - 1)
                self.log_list.scrollToItem(last_item)
                print("Scrolled to the latest log entry.")

        except FileNotFoundError:
            QMessageBox.warning(self, "File Not Found", f"Log file was not found:\n{file_path}\n\nReturning to welcome screen.")
            try:
                from setup import WelcomeWindow
                self.welcome_window = WelcomeWindow()
                self.welcome_window.show()
            except Exception as setup_error:
                QMessageBox.critical(self, "Error", f"Could not open welcome screen: {setup_error}")
            if hasattr(self, "logs_viewer") and self.logs_viewer:
                self.logs_viewer.close()
            self.close()
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
            can_mark_important = "Fixed" not in log_text and "Resolved" not in log_text and "■" not in log_text
            is_important = self.is_important_log(label.text()) if isinstance(label, QLabel) else False

            delete_action = menu.addAction("Delete")
            edit_action = menu.addAction("Edit")

            importance_action = None
            if can_mark_important:
                importance_action = menu.addAction("Remove Importance" if is_important else "Mark as Important")

            # Add "Fix" option only for Bugs
            fix_action = None
            if is_resolvable:
                fix_action = menu.addAction("Fix")

            # Add "Solution" option only for Problems
            solution_action = None
            if "★" in log_text:
                solution_action = menu.addAction("Add Solution")

            # Add "View All Logs" option
            view_all_action = menu.addAction("View All Logs")
            
            action = menu.exec(self.log_list.viewport().mapToGlobal(pos))
            
            if action is None:
                return  # Exit function without doing anything

            if action == delete_action:
                row = self.log_list.row(item)
                self.log_list.takeItem(row)
                self.logDeleted.emit(row)  # Emit signal
                print("Log entry deleted.")

            elif action == edit_action:
                row = self.log_list.row(item)
                self.edit_log(item)
                self.logEdited.emit(row)  # Emit signal
                print("Log entry edited.")

            elif action == importance_action:
                self.set_log_importance(item, not is_important)
            
            elif action == view_all_action:
                self.open_logs_viewer()
                print("Opened Logs Viewer window.")

            elif action == fix_action:
                self.resolve_log(item)
                print("Log entry resolved.")

            elif action == solution_action:
                self.add_solution(item)
                print("Solution added for the problem.")

    def set_log_importance(self, item, important):
        label = self.log_list.itemWidget(item)
        if not isinstance(label, QLabel):
            return

        updated_text = self.set_importance_marker(label.text(), important)
        self.configure_log_label(label, updated_text, word_wrap=False)
        self.update_importance_counter()
        self.save_log_counters()
        self.unsaved_changes = True
        self.importanceChanged.emit()

    def add_solution(self, item):
        # Add a solution log corresponding to a problem log and mark it as Resolved
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
                    self.configure_log_label(solution_label, solution_entry, word_wrap=False)

                    solution_item = QListWidgetItem()
                    self.log_list.addItem(solution_item)
                    self.log_list.setItemWidget(solution_item, solution_label)
                    self.log_list.scrollToItem(solution_item)

                    # Mark the problem log as Resolved
                    updated_problem_text = (
                        f'{label.text()} <span style="background-color: green; color: white;">Resolved</span>'
                    )
                    updated_problem_text = self.set_importance_marker(updated_problem_text, False)
                    self.configure_log_label(label, updated_problem_text, word_wrap=False)
                    self.update_importance_counter()
                    self.save_log_counters()
                    self.importanceChanged.emit()

                    print(f"Solution #{problem_number} added successfully and Problem #{problem_number} marked as Resolved.")
                else:
                    QMessageBox.warning(self, "Invalid Input", "Solution entry cannot be empty.")

    def save_color_to_config(self):
        color_value = self.text_color.name() if hasattr(self, 'text_color') else "#008000"
        if self.current_file:
            project_folder = os.path.dirname(self.current_file)
            config_folder = os.path.join(project_folder, "config")
            os.makedirs(config_folder, exist_ok=True)
            config_path = os.path.join(config_folder, "user_config.json")
            # Load existing config if present
            config = {}
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            config["text_color"] = color_value
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            print(f"Color saved to {config_path}")
        else:
            # Fallback to global config if no project open
            settings = QSettings("MyCompany", "LogDocumentationSystem")
            settings.setValue("text_color", color_value)
            print("Color saved to global settings")

    def load_color_from_config(self):
        if self.current_file:
            project_folder = os.path.dirname(self.current_file)
            config_folder = os.path.join(project_folder, "config")
            config_path = os.path.join(config_folder, "user_config.json")
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.text_color = QColor(config.get("text_color", "#008000"))
                    print(f"Color loaded from {config_path}: {self.text_color.name()}")
            except Exception:
                self.text_color = QColor("#008000")
                print("No project color config found. Using default color.")
        else:
            # Fallback to global config if no project open
            settings = QSettings("MyCompany", "LogDocumentationSystem")
            color = settings.value("text_color", "#008000")
            self.text_color = QColor(color)
            print("Color loaded from global settings")

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
            QMessageBox.warning(
                self,
                "Invalid File",
                "Please select a valid" + f"{filter_json}" + "file.",
            )

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
            # Reset log counters
            self.log_counters = {key: 0 for key in self.log_counters}
            self.save_log_counters()
            # Emit signal for real-time sync with LogsViewerWindow
            self.logsCleared.emit()
            print("Logs cleared and current file dropped.")

    def auto_save_logs(self):
        if self.current_file:
            print("Auto-saving logs...")
            self.update_importance_counter()
            with open(self.current_file, "w", encoding="utf-8") as file:
                for index in range(self.log_list.count()):
                    item = self.log_list.item(index)
                    label = self.log_list.itemWidget(item)
                    if isinstance(label, QLabel):
                        file.write(label.text() + "\n")
            print(f"Logs auto-saved to {self.current_file}")
            self.save_log_counters()
            self.setWindowTitle("Log Documentation System - Auto-saved")  # Update title
            QTimer.singleShot(8000, lambda: self.setWindowTitle("Log Documentation System"))  # Reset after 2 seconds
        else:
            print("Auto-save skipped: No file selected")

    def save_user_config(self):
        if self.current_file:
            project_folder = os.path.dirname(self.current_file)
            config_folder = os.path.join(project_folder, "config")
            os.makedirs(config_folder, exist_ok=True)
            config_path = os.path.join(config_folder, "user_config.json")
            config = {
                "user_name": self.user_name,
                "pdf_title": self.pdf_title,
                "pdf_font_size": self.pdf_font_size,
                "pdf_line_spacing": self.pdf_line_spacing,
                "pdf_font": self.pdf_font,
                "custom_dictionary": self.custom_dictionary,
                "text_color": self.text_color.name() if hasattr(self, 'text_color') else "#008000",
                "important_accent_color": getattr(self, "important_accent_color", self.DEFAULT_LOG_THEME_COLORS["important_accent_color"]),
                "bug_background_color": getattr(self, "bug_background_color", self.DEFAULT_LOG_THEME_COLORS["bug_background_color"]),
                "problem_background_color": getattr(self, "problem_background_color", self.DEFAULT_LOG_THEME_COLORS["problem_background_color"]),
                "resolved_background_color": getattr(self, "resolved_background_color", self.DEFAULT_LOG_THEME_COLORS["resolved_background_color"]),
                "default_background_color": getattr(self, "default_background_color", self.DEFAULT_LOG_THEME_COLORS["default_background_color"]),
                "viewer_dark_mode": getattr(self, "viewer_dark_mode", self.DEFAULT_VIEWER_PREFERENCES["viewer_dark_mode"]),
                "viewer_line_spacing": getattr(self, "viewer_line_spacing", self.DEFAULT_VIEWER_PREFERENCES["viewer_line_spacing"]),
                "viewer_text_size": getattr(self, "viewer_text_size", self.DEFAULT_VIEWER_PREFERENCES["viewer_text_size"]),
                "viewer_font_family": getattr(self, "viewer_font_family", self.DEFAULT_VIEWER_PREFERENCES["viewer_font_family"]),
                "viewer_word_wrap": getattr(self, "viewer_word_wrap", self.DEFAULT_VIEWER_PREFERENCES["viewer_word_wrap"]),
                "viewer_colored_selection_mode": getattr(self, "viewer_colored_selection_mode", self.DEFAULT_VIEWER_PREFERENCES["viewer_colored_selection_mode"]),
                "viewer_colored_selection_color": getattr(self, "viewer_colored_selection_color", self.DEFAULT_VIEWER_PREFERENCES["viewer_colored_selection_color"]),
                "viewer_selection_accent_color": getattr(self, "viewer_selection_accent_color", self.DEFAULT_VIEWER_PREFERENCES["viewer_selection_accent_color"]),
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            print(f"User config saved to {config_path}")
        else:
            # Fallback to global config if no project open
            settings = QSettings("MyCompany", "LogDocumentationSystem")
            settings.setValue("username", self.user_name)
            settings.setValue("pdf_title", self.pdf_title)
            settings.setValue("pdf_font_size", self.pdf_font_size)
            settings.setValue("pdf_line_spacing", self.pdf_line_spacing)
            settings.setValue("pdf_font", self.pdf_font)
            settings.setValue("custom_dictionary", self.custom_dictionary)
            settings.setValue("text_color", self.text_color.name() if hasattr(self, 'text_color') else "#008000")
            for key, default_value in self.DEFAULT_LOG_THEME_COLORS.items():
                settings.setValue(key, getattr(self, key, default_value))
            for key, default_value in self.DEFAULT_VIEWER_PREFERENCES.items():
                settings.setValue(key, getattr(self, key, default_value))
            print("User config saved to global settings")

    def load_user_config(self):
        self.load_default_log_theme_colors()
        # Try to load from project config first
        if hasattr(self, "current_file") and self.current_file:
            project_folder = os.path.dirname(self.current_file)
            config_folder = os.path.join(project_folder, "config")
            config_path = os.path.join(config_folder, "user_config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.user_name = data.get("user_name", "")
                    self.pdf_title = data.get("pdf_title", "Log Documentation")
                    self.pdf_font_size = int(data.get("pdf_font_size", 12))
                    self.pdf_line_spacing = float(data.get("pdf_line_spacing", 1.5))
                    self.pdf_font = data.get("pdf_font", "Arial")
                    self.custom_dictionary = data.get("custom_dictionary", "")
                    self.text_color = QColor(data.get("text_color", "#008000"))
                    for key, default_value in self.DEFAULT_LOG_THEME_COLORS.items():
                        setattr(self, key, data.get(key, default_value))
                    for key, default_value in self.DEFAULT_VIEWER_PREFERENCES.items():
                        setattr(self, key, data.get(key, default_value))
                return
        # Fallback to global config
        settings = QSettings("MyCompany", "LogDocumentationSystem")
        self.user_name = settings.value("username", "")
        self.pdf_title = settings.value("pdf_title", "Log Documentation")
        self.pdf_font_size = int(settings.value("pdf_font_size", 12))
        self.pdf_line_spacing = float(settings.value("pdf_line_spacing", 1.5))
        self.pdf_font = settings.value("pdf_font", "Arial")
        self.custom_dictionary = settings.value("custom_dictionary", "")
        self.text_color = QColor(settings.value("text_color", "#008000"))
        for key, default_value in self.DEFAULT_LOG_THEME_COLORS.items():
            setattr(self, key, settings.value(key, default_value))
        for key, default_value in self.DEFAULT_VIEWER_PREFERENCES.items():
            value = settings.value(key, default_value)
            if isinstance(default_value, bool):
                value = value in (True, "true", "True", "1", 1)
            elif isinstance(default_value, int):
                value = int(value)
            setattr(self, key, value)

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
        text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)  # *italic* â†’ <i>italic</i>
        text = re.sub(r"_([^_]+)_", r"<u>\1</u>", text)    # _underline_ â†’ <u>underline</u>
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
            "Just Details": 0,
            "Importance": 0,
        }

        icon_to_category = {"★": "Problem ★", "■": "Solution ■", "▲": "Bug ▲", "◆": "Changes ◆"}
        pattern = re.compile(r"([★■▲◆]).*?#(\d+)\b")
        details_pattern = re.compile(r"\[(General|Debugging)\].*?#(\d+)\b")

        for index in range(self.log_list.count()):
            item = self.log_list.item(index)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel):
                text = self.strip_html(label.text())  # Remove HTML formatting
                if self.is_important_log(label.text()):
                    detected_counters["Importance"] += 1
                match = pattern.search(text)

                if match:
                    category = icon_to_category.get(match.group(1))
                    number = int(match.group(2))
                    if category:
                        detected_counters[category] = max(detected_counters[category], number)
                elif not any(icon in text for icon in ["★", "■", "▲", "◆"]):
                    details_match = details_pattern.search(text)
                    if details_match:
                        details_number = int(details_match.group(2))
                        detected_counters["Just Details"] = max(detected_counters["Just Details"], details_number)

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
            updated_text = self.set_importance_marker(updated_text, False)
            self.configure_log_label(label, updated_text, word_wrap=False)
            print("Log entry marked as fixed with green background only for the word 'Fixed'.")
            self.update_importance_counter()
            self.save_log_counters()
            self.importanceChanged.emit()

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
            self.configure_log_label(label, log, word_wrap=False)

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
            self.configure_log_label(label, log_entry, word_wrap=False)

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
            "Zurich", "Geneva", "Cape Town", "Johannesburg", "Buenos Aires", "Santiago", "Lima", "BogotÃ¡", "Quito", "Havana",
            "Kuala Lumpur", "Jakarta", "Manila", "Ho Chi Minh City", "Taipei", "Osaka", "Kyoto", "Kolkata", "Chennai", "Jakarta",
            "San Francisco", "Chicago", "Boston", "Houston", "Miami", "Las Vegas", "Seattle", "Philadelphia", "Washington D.C.", "Atlanta",
            "San Diego", "Phoenix", "Denver", "Portland", "Honolulu", "Vancouver", "Montreal", "Ottawa", "Calgary", "Quebec City",
            "Guadalajara", "Monterrey", "MedellÃ­n", "Recife", "BrasÃ­lia", "Sao Paulo", "Curitiba", "Salvador", "Fortaleza", "Montevideo",
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
            "Shepherdâ€™s Pie", "Jollof Rice", "Satay", "Arepas", "Tandoori Chicken", "Chimichanga", "Pita Bread", "Muffins",
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
            "Mongoose", "Nightingale", "Okapi", "Pangolin", "Quetzal", "Roadrunner", "Siberian Husky", "Toucan", "Urial", "VicuÃ±a",
            "Weasel", "X-ray Tetra", "Yak", "Zebra Shark", "Anglerfish", "Butterfly", "Catfish", "Dragonfly", "Electric Eel",
            "Firefly", "Goldfish", "Hermit Crab", "Indian Elephant", "Japanese Spider Crab", "Killer Whale", "Leafy Seadragon",
            "Mandrill", "Nautilus", "Owl", "Pika", "Queen Angelfish", "Red Panda", "Salamander", "Tarsier", "Unicornfish",
            "Vampire Bat", "Woodpecker", "Xenopus", "Yeti Crab", "Zebra Finch", "Aye-Aye", "Basilisk", "Cuttlefish", "Dung Beetle",
            "Eel", "Fossa", "GalÃ¡pagos Tortoise", "Horseshoe Crab", "Indian Peafowl", "Javan Rhino", "Kiwi", "Leafcutter Ant",
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
        # random_choices = random.choice(random_choice)

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
            config_folder = get_config_dir(project_folder)
        else:
            config_folder = get_config_dir()
        self.dictionary_dialog = DictionaryDialog(self, config_folder=config_folder)
        self.dictionary_dialog.dictionary = getattr(self, 'keyword_definitions', {})
        for keyword in sorted(self.dictionary_dialog.dictionary.keys()):
            self.dictionary_dialog.add_list_item(keyword)
        self.dictionary_dialog.show()
    
    def open_logs_viewer(self):
        # Open the Logs Viewer window to display all logs in vertical scrollable view.
        # Uses a persistent instance to avoid reload time. On subsequent calls,
        # just brings the existing viewer to focus
        # Check if viewer already exists
        
        if not hasattr(self, 'logs_viewer') or self.logs_viewer is None:
            # Create new viewer only on first call
            self.logs_viewer = LogsViewerWindow(self.log_list, self)
            self.logs_viewer.position_on_rightmost()
            self.logs_viewer.show()
        else:
            self.logs_viewer.position_on_rightmost()
            # Viewer already exists, just bring it to focus
            self.logs_viewer.raise_()
            self.logs_viewer.activateWindow()
            if self.logs_viewer.isHidden():
                self.logs_viewer.show()

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
                    # item.setHidden(True)
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
        self.filterChanged.emit()

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
        self.filterChanged.emit()

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
        if getattr(self, "current_file", None):
            project_folder = os.path.dirname(self.current_file or "")
            config_dir = get_config_dir(project_folder)
        else:
            config_dir = get_config_dir()
        if getattr(self, "custom_dictionary", ""):
            # Sanitize the name for file usage
            safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', self.custom_dictionary)
            return os.path.join(config_dir, f"{safe_name}_definitions.json")
        else:
            return os.path.join(config_dir, "keyword_definitions.json")

    def closeEvent(self, event):
        should_close = False
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.save_logs()
                event.accept()
                should_close = True
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
                should_close = True
            else:
                event.ignore()
        else:
            event.accept()
            should_close = True

        if should_close and hasattr(self, "logs_viewer") and self.logs_viewer:
            self.logs_viewer.close()


if __name__ == "__main__":
    pass




