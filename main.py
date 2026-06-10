from PyQt6.QtWidgets import (
    QMainWindow, QFrame, QDateEdit, QSlider, 
    QMenu, QDialog, QProgressDialog, QMenuBar, 
    QLabel, QColorDialog, QApplication, QLineEdit, 
    QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QListWidget, QInputDialog, 
    QFileDialog, QMessageBox, QComboBox, QScrollArea, 
    QSizePolicy, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
    QSpacerItem, QStackedWidget, QTabWidget, QToolButton,
    QPlainTextEdit, QCheckBox, QSpinBox, QFontComboBox, QAbstractItemView
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
    QPixmap, QCursor, QIntValidator, QPalette
    )
from datetime import datetime, timezone
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
import uuid
import difflib
import zipfile


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


def apply_neutral_dialog_style(widget):
    if widget is None:
        return
    widget.setStyleSheet("""
        QDialog, QProgressDialog {
            background-color: #f5f5f5;
            color: #111111;
        }
        QLabel, QCheckBox {
            color: #111111;
        }
        QLineEdit, QTextEdit, QPlainTextEdit, QListWidget, QComboBox, QDateEdit {
            background-color: #ffffff;
            color: #111111;
            border: 1px solid #b8b8b8;
            padding: 4px;
        }
        QPushButton {
            background-color: #f0f0f0;
            color: #111111;
            border: 1px solid #b8b8b8;
            padding: 6px;
        }
    """)


def prompt_text_input(parent, title, label, text=""):
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setFixedSize(380, 140)
    apply_neutral_dialog_style(dialog)

    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel(label))

    line_edit = QLineEdit(dialog)
    line_edit.setText(text)
    layout.addWidget(line_edit)

    button_row = QHBoxLayout()
    ok_button = QPushButton("OK", dialog)
    cancel_button = QPushButton("Cancel", dialog)
    button_row.addWidget(ok_button)
    button_row.addWidget(cancel_button)
    layout.addLayout(button_row)

    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)

    accepted = dialog.exec() == QDialog.DialogCode.Accepted
    return line_edit.text(), accepted


def prompt_log_content_input(parent, title, prefix_text, text=""):
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setFixedSize(520, 190)
    apply_neutral_dialog_style(dialog)

    layout = QVBoxLayout(dialog)
    layout.addWidget(QLabel("Modify your log entry:"))

    prefix_label = QLabel(prefix_text)
    prefix_label.setWordWrap(True)
    prefix_label.setStyleSheet(
        "background-color: #ececec; color: #444444; border: 1px solid #c8c8c8; padding: 6px;"
    )
    layout.addWidget(prefix_label)

    text_edit = QLineEdit(dialog)
    text_edit.setText(text)
    layout.addWidget(text_edit)

    button_row = QHBoxLayout()
    ok_button = QPushButton("OK", dialog)
    cancel_button = QPushButton("Cancel", dialog)
    button_row.addWidget(ok_button)
    button_row.addWidget(cancel_button)
    layout.addLayout(button_row)

    ok_button.clicked.connect(dialog.accept)
    cancel_button.clicked.connect(dialog.reject)

    accepted = dialog.exec() == QDialog.DialogCode.Accepted
    return text_edit.text(), accepted


def show_neutral_message_box(parent, icon, title, text, buttons):
    box = QMessageBox(parent)
    box.setIcon(icon)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(buttons)
    apply_neutral_dialog_style(box)
    return box.exec()


class FileNameDialog(QDialog):
    def __init__(self, extension, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log File Name")
        self.setFixedSize(350, 120)
        apply_neutral_dialog_style(self)
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
    def __init__(self, parent=None, category_options=None, current_filters=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Logs")
        self.resize(400, 250)
        self.setFixedSize(400, 250)
        apply_neutral_dialog_style(self)
        self.parent_widget = parent
        self._updating_items = False  # Flag to prevent recursive updates
        
        layout = QVBoxLayout(self)
        
        # Date range filter section
        date_range_layout = QHBoxLayout()
        
        start_label = QLabel("Start Date:")
        date_range_layout.addWidget(start_label)
        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-70000))
        date_range_layout.addWidget(self.start_date_edit)
        
        end_label = QLabel("End Date:")
        date_range_layout.addWidget(end_label)
        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.end_date_edit)
        
        layout.addLayout(date_range_layout)
        
        # Log type filter section with checkboxes
        type_label = QLabel("Select Log Types:")
        layout.addWidget(type_label)
        
        # Create a QListWidget with checkable items
        self.type_list = QListWidget(self)
        self.type_list.setMaximumHeight(120)
        
        # Add "All" option
        all_item = QListWidgetItem("All")
        all_item.setFlags(all_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        all_item.setCheckState(Qt.CheckState.Checked)
        self.type_list.addItem(all_item)
        
        # Add category options - all checked by default
        if category_options:
            for category in category_options:
                item = QListWidgetItem(category)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)  # All checked by default
                self.type_list.addItem(item)
        
        # Load saved filter preferences
        self.load_filter_preferences()
        
        # Connect signals for checkbox toggling and "All" functionality
        self.type_list.itemChanged.connect(self.on_item_changed)
        self.type_list.itemClicked.connect(self.on_item_clicked)
        
        layout.addWidget(self.type_list)
        
        # Buttons for applying or canceling
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Filter", self)
        self.apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.apply_btn)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def on_item_clicked(self, item):
        # Toggle checkbox when clicking on the item text
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)

    def on_item_changed(self, item):
        # Handle checkbox logic: manage All and individual selections
        if self._updating_items:
            return
        
        self._updating_items = True
        
        if item.text() == "All":
            # When "All" is toggled
            if item.checkState() == Qt.CheckState.Checked:
                # Check all items when "All" is checked
                for i in range(1, self.type_list.count()):
                    self.type_list.item(i).setCheckState(Qt.CheckState.Checked)
            else:
                # Uncheck all items when "All" is unchecked
                for i in range(1, self.type_list.count()):
                    self.type_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        else:
            # When an individual category is toggled, uncheck "All"
            all_item = self.type_list.item(0)
            if all_item.checkState() == Qt.CheckState.Checked:
                all_item.setCheckState(Qt.CheckState.Unchecked)
            
            # Check if all individual items are now unchecked
            # If so, auto-check "All"
            all_unchecked = True
            for i in range(1, self.type_list.count()):
                if self.type_list.item(i).checkState() == Qt.CheckState.Checked:
                    all_unchecked = False
                    break
            
            if all_unchecked:
                all_item.setCheckState(Qt.CheckState.Checked)
                # Also check all items since "All" was auto-selected
                for i in range(1, self.type_list.count()):
                    self.type_list.item(i).setCheckState(Qt.CheckState.Checked)
        
        self._updating_items = False
        self.save_filter_preferences()

    def get_filters(self):
        # Return the selected start date, end date, and list of selected log types.
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        # Collect all checked items (excluding "All")
        selected_types = []
        for i in range(1, self.type_list.count()):
            item = self.type_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_types.append(item.text())
        
        return start_date, end_date, selected_types

    def save_filter_preferences(self):
        # Save filter preferences to config.
        if not self.parent_widget:
            return
        try:
            settings = QSettings("LDS", "LogApp")
            # Save checked categories
            checked_categories = []
            for i in range(1, self.type_list.count()):
                item = self.type_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    checked_categories.append(item.text())
            settings.setValue("filter/checked_categories", checked_categories)
        except Exception:
            pass

    def load_filter_preferences(self):
        # Load filter preferences from config.
        try:
            settings = QSettings("LDS", "LogApp")
            checked_categories = settings.value("filter/checked_categories", None)
            
            if checked_categories:
                # Uncheck "All" and all items first
                self.type_list.item(0).setCheckState(Qt.CheckState.Unchecked)
                for i in range(1, self.type_list.count()):
                    self.type_list.item(i).setCheckState(Qt.CheckState.Unchecked)
                
                # Check only the saved categories
                for i in range(1, self.type_list.count()):
                    item = self.type_list.item(i)
                    if item.text() in checked_categories:
                        item.setCheckState(Qt.CheckState.Checked)
        except Exception:
            pass


class ClickableLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        # Set pointer cursor to indicate clickability
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.original_pixmap: Optional[QPixmap] = None
        self.original_pixmap = None
        self.is_selected = False
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
        # Compute the fit-to-window scale factor when the window is shown
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
        # Adjust zoom based on mouse wheel scrolling (% per notch)
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_by(20)
        else:
            self.zoom_by(-20)

    def zoom_by(self, delta_percent):
        # Adjust the zoom percentage and update the image
        self.zoom_percent += delta_percent
        # Clamp the zoom percent between -100% and +500% relative to fit-to-window.
        self.zoom_percent = max(-100, min(500, self.zoom_percent))
        self.current_scale = self.fit_scale * (1 + self.zoom_percent / 100.0)
        self.update_image()
        self.update_overlay()

    def update_image(self):
        # Scale the original pixmap using the current scale and update the label
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
        # Update the overlay text to show current zoom and original image dimensions.
        if self.original_pixmap:
            # Use original dimensions for static size information.
            original_width = self.original_pixmap.width()
            original_height = self.original_pixmap.height()
            # Show zoom relative to the fit-to-window baseline (0 means fit).
            zoom_text = f"{'+' if self.zoom_percent > 0 else ''}{self.zoom_percent}%"
            self.overlay.setText(f"Zoom: {zoom_text}   Original Size: {original_width}x{original_height}px")
    
    def keyPressEvent(self, event):
        # Allow closing the viewer with the Escape key.
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

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
        apply_neutral_dialog_style(self)
        
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

class KeywordDialog(QDialog):
    # Unified dialog for adding/editing keywords with multiple images
    def __init__(self, keyword="", definition="", image_paths=None, parent=None):
        super().__init__(parent)
        self.keyword = keyword
        self.definition = definition
        self.image_paths = image_paths or []  # List of image paths
        self.is_editing = bool(keyword)  # True if editing existing keyword
        self.clipboard = QApplication.clipboard()
        self._clipboard_monitor_connected = False
        
        self.init_ui()
        self._connect_clipboard_monitor()
        self.update_paste_image_button_visibility()
        self.center()
    
    def init_ui(self):
        self.setWindowTitle("Add Keyword" if not self.is_editing else "Edit Keyword")
        self.setFixedSize(600, 600)
        apply_neutral_dialog_style(self)
        
        layout = QVBoxLayout(self)
        
        # Keyword field
        layout.addWidget(QLabel("Keyword:"))
        self.keyword_input = QLineEdit(self)
        self.keyword_input.setText(self.keyword)
        if self.is_editing:
            self.keyword_input.setReadOnly(True)  # Can't change keyword name when editing
        layout.addWidget(self.keyword_input)
        
        # Definition field
        layout.addWidget(QLabel("Definition:"))
        self.definition_input = QTextEdit(self)
        self.definition_input.setPlainText(self.definition)
        self.definition_input.setFixedHeight(150)
        layout.addWidget(self.definition_input)
        
        # Images section
        layout.addWidget(QLabel("Examples (Images):"))
        
        # Image list with scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        self.images_container = QWidget()
        self.images_layout = QVBoxLayout(self.images_container)
        self.images_layout.setSpacing(8)
        
        # Populate existing images
        self.image_widgets = []
        for img_path in self.image_paths:
            self.add_image_widget(img_path)
        
        self.images_layout.addStretch()
        scroll_area.setWidget(self.images_container)
        scroll_area.setFixedHeight(250)
        layout.addWidget(scroll_area)
        
        # Add image button
        add_image_btn = QPushButton("+ Add Image")
        add_image_btn.clicked.connect(self.add_image)
        layout.addWidget(add_image_btn)

        self.paste_image_btn = QPushButton("Paste Image")
        self.paste_image_btn.clicked.connect(self.paste_image_from_clipboard)
        self.paste_image_btn.setVisible(False)
        layout.addWidget(self.paste_image_btn)
        
        # OK/Cancel buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def _connect_clipboard_monitor(self):
        if self.clipboard is None or self._clipboard_monitor_connected:
            return
        try:
            self.clipboard.dataChanged.connect(self.update_paste_image_button_visibility)
            self._clipboard_monitor_connected = True
        except Exception:
            self._clipboard_monitor_connected = False

    def _disconnect_clipboard_monitor(self):
        if self.clipboard is None or not self._clipboard_monitor_connected:
            return
        try:
            self.clipboard.dataChanged.disconnect(self.update_paste_image_button_visibility)
        except Exception:
            pass
        self._clipboard_monitor_connected = False

    def _clipboard_has_image(self):
        try:
            mime = self.clipboard.mimeData()
            if mime and mime.hasImage():
                return True
            pixmap = self.clipboard.pixmap()
            return not pixmap.isNull()
        except Exception:
            return False

    def update_paste_image_button_visibility(self):
        if hasattr(self, "paste_image_btn"):
            self.paste_image_btn.setVisible(self._clipboard_has_image())

    def _add_image_from_pixmap(self, pixmap, ext=".png"):
        if pixmap.isNull():
            return False

        config_folder = self.parent().config_folder if self.parent() else get_config_dir()
        images_folder = os.path.join(config_folder, "keyword_images")
        if not os.path.exists(images_folder):
            os.makedirs(images_folder)

        utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        keyword_safe = self.keyword_input.text().strip().replace(" ", "_") or "keyword"
        dest_filename = f"{keyword_safe}_{utc_now}{'UTC'}{ext}"
        dest_path = os.path.join(images_folder, dest_filename)

        if not pixmap.save(dest_path, "PNG"):
            return False

        relative_path = os.path.relpath(dest_path, config_folder)
        self.image_paths.append(relative_path)
        self.add_image_widget(relative_path)
        return True
    
    def add_image_widget(self, image_path):
        
        # Construct full path if relative path is provided
        config_folder = self.parent().config_folder if self.parent() else get_config_dir()
        if not os.path.isabs(image_path):
            full_path = os.path.join(config_folder, image_path)
        else:
            full_path = image_path
        
        # Create a widget for displaying and managing a single image
        img_widget = QWidget()
        img_layout = QHBoxLayout(img_widget)
        img_layout.setContentsMargins(0, 0, 0, 0)
        
        # Display image thumbnail
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                thumbnail = pixmap.scaledToHeight(40, Qt.TransformationMode.SmoothTransformation)
                thumb_label = QLabel()
                thumb_label.setPixmap(thumbnail)
                img_layout.addWidget(thumb_label)
        
        # Image path label
        path_label = QLabel(os.path.basename(image_path))
        img_layout.addWidget(path_label)
        img_layout.addStretch()
        
        # Move up button
        move_up_btn = QPushButton("↑")
        move_up_btn.setFixedWidth(30)
        move_up_btn.clicked.connect(lambda: self.move_image_up(img_widget))
        img_layout.addWidget(move_up_btn)
        
        # Move down button
        move_down_btn = QPushButton("↓")
        move_down_btn.setFixedWidth(30)
        move_down_btn.clicked.connect(lambda: self.move_image_down(img_widget))
        img_layout.addWidget(move_down_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.remove_image_widget(img_widget, image_path))
        img_layout.addWidget(delete_btn)
        
        img_widget.setLayout(img_layout)
        self.images_layout.insertWidget(len(self.image_widgets), img_widget)
        self.image_widgets.append((img_widget, image_path))
    
    def add_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        if file_path:
            config_folder = self.parent().config_folder if self.parent() else get_config_dir()
            images_folder = os.path.join(config_folder, "keyword_images")
            if not os.path.exists(images_folder):
                os.makedirs(images_folder)

            ext = os.path.splitext(file_path)[1] or ".png"
            timestamp = int(time.time() * 1000)
            keyword_safe = self.keyword_input.text().strip().replace(" ", "_") or "keyword"
            dest_filename = f"{keyword_safe}_{timestamp}{ext}"
            dest_path = os.path.join(images_folder, dest_filename)

            shutil.copy2(file_path, dest_path)

            relative_path = os.path.relpath(dest_path, config_folder)

            self.image_paths.append(relative_path)
            self.add_image_widget(relative_path)

    def paste_image_from_clipboard(self):
        clipboard = self.clipboard or QApplication.clipboard()
        if clipboard is None:
            return

        pixmap = clipboard.pixmap()
        if pixmap.isNull():
            try:
                pixmap = QPixmap.fromImage(clipboard.image())
            except Exception:
                pixmap = QPixmap()

        if self._add_image_from_pixmap(pixmap):
            self.update_paste_image_button_visibility()
    
    def remove_image_widget(self, widget, image_path):
        idx = self.images_layout.indexOf(widget)
        if idx >= 0:
            self.images_layout.removeWidget(widget)
            widget.deleteLater()

        self.image_widgets = [(w, p) for w, p in self.image_widgets if w is not widget]

        config_folder = self.parent().config_folder if self.parent() else get_config_dir()
        full_path = os.path.join(config_folder, image_path) if not os.path.isabs(image_path) else image_path
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            print(f"Error deleting image {full_path}: {e}")

        if image_path in self.image_paths:
            self.image_paths.remove(image_path)

    
    def move_image_up(self, widget):
        # Move image up in the list
        idx = self.images_layout.indexOf(widget)
        if idx > 0:
            self.images_layout.insertWidget(idx - 1, self.images_layout.takeAt(idx).widget())
            self.image_widgets[idx], self.image_widgets[idx - 1] = self.image_widgets[idx - 1], self.image_widgets[idx]
    
    def move_image_down(self, widget):
        # Move image down in the list
        idx = self.images_layout.indexOf(widget)
        if idx < len(self.image_widgets) - 1:
            self.images_layout.insertWidget(idx + 1, self.images_layout.takeAt(idx).widget())
            self.image_widgets[idx], self.image_widgets[idx + 1] = self.image_widgets[idx + 1], self.image_widgets[idx]
    
    def get_data(self):
        # Return the keyword, definition, and image paths
        # Update image_paths from current widget order
        self.image_paths = [p for _, p in self.image_widgets]
        return self.keyword_input.text().strip(), self.definition_input.toPlainText(), self.image_paths
    
    def center(self):
        # Center the dialog on the screen
        screen = get_screen_at_cursor()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())
    
    def accept(self):
        # Override accept to validate required fields"""
        keyword = self.keyword_input.text().strip()
        definition = self.definition_input.toPlainText().strip()

        # Check if keyword is empty
        if not keyword:
            show_neutral_message_box(
                self,
                QMessageBox.Icon.Warning,
                "Validation Error",
                "Keyword is required. Please enter a keyword.",
                QMessageBox.StandardButton.Ok
            )
            return

        # Check if definition is empty
        if not definition:
            show_neutral_message_box(
                self,
                QMessageBox.Icon.Warning,
                "Validation Error",
                "Definition is required. Please enter a definition.",
                QMessageBox.StandardButton.Ok
            )
            return

        # All validation passed, accept the dialog
        super().accept()

    def done(self, result):
        self._disconnect_clipboard_monitor()
        super().done(result)
        
class DictionaryDialog(QDialog):
    def __init__(self, parent=None, config_folder=None):
        super().__init__(parent)
        self.setWindowTitle("Dictionary")
        self.setGeometry(100, 100, 700, 450)
        self.setFixedSize(700, 450)
        apply_neutral_dialog_style(self)
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
        
        # Put the layout into a widget so it can be scrolled
        self.image_container_widget = QWidget()
        self.image_container_widget.setLayout(self.image_container_layout)
        
        # Scroll area that will contain the image container widget
        self.image_scroll_area = QScrollArea(self)
        self.image_scroll_area.setWidgetResizable(True)
        self.image_scroll_area.setWidget(self.image_container_widget)
        #self.image_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # hide vertical scroll bar
        self.image_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.image_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.image_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Limit the visual height of the image box (adjust value as needed)
        self.image_scroll_area.setFixedHeight(220)
        self.image_scroll_area.setStyleSheet("border: none; background: none;")
        
        # New "Example" label; initially hidden
        self.example_label = QLabel("Example", self)
        self.example_label.setStyleSheet("font-weight: bold;")
        self.example_label.setVisible(False)
        self.image_container_layout.addWidget(self.example_label)
        
        # Add image preview label (clickable)
        self.image_label = ClickableLabel(self)
        self.image_label.setFixedHeight(150)  # Preview height; adjust as needed.
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: none; background: none;")
        self.image_label.setVisible(False)
        self.image_container_layout.addWidget(self.image_label)
        
        # Add the container layout to the definition layout.
        self.definition_layout.addWidget(self.image_scroll_area)
        
        self._dynamic_image_widgets = []
        
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

        self.export_button = QPushButton("Export", self)
        self.export_button.clicked.connect(self.export_dictionary_package)
        self.button_layout.addWidget(self.export_button)

        self.import_button = QPushButton("Import", self)
        self.import_button.clicked.connect(self.import_dictionary_package)
        self.button_layout.addWidget(self.import_button)
        
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
        # Adds a non-clickable, non-deletable item to the list
        static_item = QListWidgetItem(text)
        static_item.setFlags(Qt.ItemFlag.NoItemFlags)  # Disable interactions
        static_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)  # Center text
        static_item.setBackground(QBrush(QColor(220, 220, 220)))
        static_item.setFont(QLabel().font())  # Use default font
        static_item.setForeground(QBrush(QColor(0, 0, 0)))  # Black text color
        static_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))  # Bold font
        static_item.setData(Qt.ItemDataRole.UserRole, "static")  # Mark as static
        self.keyword_list.addItem(static_item)  # Add to list
    
    def refresh_keyword_list(self):
        # Clear and rebuild the keyword list sorted alphabetically
        self.keyword_list.clear()

        # Add static header
        self.add_static_item("Keywords")

        # Sort keywords alphabetically and add them
        sorted_keywords = sorted(self.dictionary.keys())
        for keyword in sorted_keywords:
            self.add_list_item(keyword)

    def _keyword_search_score(self, query: str, candidate: str):
        q = (query or "").strip().lower()
        c = (candidate or "").strip().lower()
        if not q or not c:
            return None
        if q == c:
            return 5000
        if c.startswith(q):
            return 4200 - len(c)
        if q in c:
            return 3300 - c.find(q)

        # Token-aware matching for multi-word queries/candidates.
        q_tokens = [t for t in re.split(r"\s+", q) if t]
        c_tokens = [t for t in re.split(r"\s+", c) if t]
        if q_tokens and c_tokens:
            matched_tokens = 0
            token_score = 0
            for qt in q_tokens:
                best_ratio = 0.0
                for ct in c_tokens:
                    ratio = difflib.SequenceMatcher(None, qt, ct).ratio()
                    if ratio > best_ratio:
                        best_ratio = ratio
                if best_ratio >= 0.80:
                    matched_tokens += 1
                    token_score += int(best_ratio * 100)
            if matched_tokens:
                return 2200 + (matched_tokens * 100) + token_score - len(c)

        ratio = difflib.SequenceMatcher(None, q, c).ratio()
        if ratio >= 0.72:
            return int(1500 + ratio * 500) - len(c)
        return None
    
    def add_keyword(self):
        dialog = KeywordDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            keyword, definition, image_paths = dialog.get_data()
            if keyword.strip():
                self.dictionary[keyword] = definition
                self.keyword_images[keyword] = image_paths
                self.save_keyword_definitions()
                self.refresh_keyword_list()
    
    def select_keyword(self, word):
        # Find and select the keyword in the list.
        for i in range(self.keyword_list.count()):
            item = self.keyword_list.item(i)
            if item and item.text() == word:
                self.keyword_list.setCurrentRow(i)
                self.display_definition(self.keyword_list.item(i))
                break
            
    def delete_keyword(self):
        selected_item = self.keyword_list.currentItem()
        if selected_item:
            word = selected_item.text()
            if word == "Keywords" or word == "":
                return

            # Delete image files
            import shutil
            if word in self.keyword_images:
                for rel_path in self.keyword_images[word]:
                    full_path = os.path.join(self.config_folder, rel_path)
                    if os.path.exists(full_path):
                        try:
                            os.remove(full_path)
                        except Exception as e:
                            print(f"Error deleting image {full_path}: {e}")

            # Delete from dictionaries
            if word in self.dictionary:
                del self.dictionary[word]
            if word in self.keyword_images:
                del self.keyword_images[word]

            self.save_keyword_definitions()
            self.refresh_keyword_list()

            # Clear the definition display
            self.definition_label.setText("Select a keyword to view its definition.")
            self.definition_label.full_definition = ""
            self.example_label.setVisible(False)
            self.image_label.setVisible(False)

    def display_definition(self, item):
        word = item.text()
        if word == "Keywords":
            return
    
        full_def = self.dictionary.get(word, "No definition available.")
        preview_text = full_def if len(full_def) <= 780 else full_def[:780] + "..."
        formatted_definition = f"<b>{word}:</b><br>{preview_text}"
        self.definition_label.setText(formatted_definition)
        self.definition_label.full_definition = full_def
        
        # Remove previous dynamic thumbnails safely
        for w in getattr(self, "_dynamic_image_widgets", []):
            try:
                self.image_container_layout.removeWidget(w)
                w.setParent(None)
                w.deleteLater()
            except Exception:
                pass
        self._dynamic_image_widgets = []
        
        # Clear/hide static preview
        self.image_label.clear()
        self.image_label.setVisible(False)
    
        image_paths = self.keyword_images.get(word, [])
        if image_paths:
            self.example_label.setVisible(True)
            # Show ALL images
            for rel_path in image_paths:
                full_path = os.path.join(self.config_folder, rel_path)
                if os.path.exists(full_path):
                    pixmap = QPixmap(full_path)
                    if not pixmap.isNull():
                        image_label = ClickableLabel(self)
                        image_label.original_pixmap = pixmap
                        scaled = pixmap.scaledToHeight(150, Qt.TransformationMode.SmoothTransformation)
                        image_label.setPixmap(scaled)
                        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.image_container_layout.addWidget(image_label)
                        self._dynamic_image_widgets.append(image_label)
        else:
            self.example_label.setVisible(False)
    
    def edit_keyword(self):
        selected_item = self.keyword_list.currentItem()
        if selected_item:
            word = selected_item.text()
            if word == "Keywords":
                return

            definition = self.dictionary.get(word, "")
            image_paths = self.keyword_images.get(word, [])

            dialog = KeywordDialog(word, definition, image_paths, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_keyword, new_definition, new_image_paths = dialog.get_data()

                # If keyword name changed, handle image reorganization
                if new_keyword != word:
                    # Move old images to new keyword name
                    old_images = self.keyword_images.get(word, [])
                    new_images = []

                    for old_rel_path in old_images:
                        old_full_path = os.path.join(self.config_folder, old_rel_path)
                        if os.path.exists(old_full_path):
                            # Get extension
                            ext = os.path.splitext(old_rel_path)[1]
                            # Extract timestamp from filename
                            parts = os.path.basename(old_rel_path).split('_')
                            timestamp = parts[-1].replace(ext, '')  # Last part before extension

                            # Create new filename with new keyword name
                            new_keyword_safe = new_keyword.replace(" ", "_")
                            new_filename = f"{new_keyword_safe}_{timestamp}{ext}"
                            new_full_path = os.path.join(self.config_folder, "keyword_images", new_filename)

                            # Rename the file
                            import shutil
                            shutil.move(old_full_path, new_full_path)

                            # Store new relative path
                            new_rel_path = os.path.relpath(new_full_path, self.config_folder)
                            new_images.append(new_rel_path)

                    # Remove old keyword entry
                    del self.dictionary[word]
                    if word in self.keyword_images:
                        del self.keyword_images[word]

                    # Add new keyword with reorganized images
                    self.dictionary[new_keyword] = new_definition
                    self.keyword_images[new_keyword] = new_images
                else:
                    # Keyword name didn't change, just update definition and images
                    self.dictionary[new_keyword] = new_definition
                    self.keyword_images[new_keyword] = new_image_paths

                self.save_keyword_definitions()
                self.refresh_keyword_list()
    
    def search_keywords(self, text):
        query = (text or "").strip()
        self.keyword_list.clear()
        self.add_static_item("Keywords")

        if not query:
            for keyword in sorted(self.dictionary.keys()):
                self.add_list_item(keyword)
            return

        ranked = []
        for keyword in self.dictionary.keys():
            score = self._keyword_search_score(query, keyword)
            if score is not None:
                ranked.append((score, keyword))

        ranked.sort(key=lambda x: (-x[0], x[1].casefold()))
        for _score, keyword in ranked:
            self.add_list_item(keyword)
    
    
    def save_keyword_definitions(self):
        definitions_file = os.path.join(self.config_folder, "keyword_definitions.json")
        with open(definitions_file, "w", encoding="utf-8") as file:
            json.dump(self.dictionary, file, ensure_ascii=False, indent=2)

        # Now keyword_images stores lists of paths
        images_file = os.path.join(self.config_folder, "keyword_images.json")
        with open(images_file, "w", encoding="utf-8") as file:
            json.dump(self.keyword_images, file, ensure_ascii=False, indent=2)

    def load_keyword_definitions(self):
        # Load keyword definitions and image paths from separate JSON files
        definitions_file = os.path.join(self.config_folder, "keyword_definitions.json")
        images_file = os.path.join(self.config_folder, "keyword_images.json")

        # Load definitions
        if os.path.exists(definitions_file):
            with open(definitions_file, "r", encoding="utf-8") as file:
                self.dictionary = json.load(file)
        else:
            self.dictionary = {}

        # Load image paths (now stores lists)
        if os.path.exists(images_file):
            with open(images_file, "r", encoding="utf-8") as file:
                self.keyword_images = json.load(file)
                # Ensure all values are lists for backward compatibility
                for key in self.keyword_images:
                    if not isinstance(self.keyword_images[key], list):
                        self.keyword_images[key] = [self.keyword_images[key]]
        else:
            self.keyword_images = {}

        # Only refresh once after loading everything
        self.refresh_keyword_list()

    def export_dictionary_package(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Dictionary Package",
            "",
            "LDS Dictionary (*.ldsdict)"
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".ldsdict"):
            file_path += ".ldsdict"

        try:
            with zipfile.ZipFile(file_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("keyword_definitions.json", json.dumps(self.dictionary, ensure_ascii=False, indent=2))
                zf.writestr("keyword_images.json", json.dumps(self.keyword_images, ensure_ascii=False, indent=2))

                for keyword, rel_paths in self.keyword_images.items():
                    if not isinstance(rel_paths, list):
                        rel_paths = [rel_paths]
                    for rel_path in rel_paths:
                        rel_path = str(rel_path).replace("\\", "/")
                        full_path = os.path.join(self.config_folder, rel_path)
                        if not os.path.isfile(full_path):
                            continue
                        arcname = f"images/{os.path.basename(rel_path)}"
                        zf.write(full_path, arcname=arcname)

            show_neutral_message_box(
                self,
                QMessageBox.Icon.Information,
                "Export Complete",
                f"Dictionary package saved:\n{file_path}",
                QMessageBox.StandardButton.Ok,
            )
        except Exception as e:
            show_neutral_message_box(
                self,
                QMessageBox.Icon.Critical,
                "Export Failed",
                f"Failed to export dictionary package:\n{e}",
                QMessageBox.StandardButton.Ok,
            )

    def import_dictionary_package(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Dictionary Package",
            "",
            "LDS Dictionary (*.ldsdict)"
        )
        if not file_path:
            return

        reply = show_neutral_message_box(
            self,
            QMessageBox.Icon.Question,
            "Import Dictionary",
            "Import will replace the current dictionary entries in this project. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                names = set(zf.namelist())
                if "keyword_definitions.json" not in names:
                    raise ValueError("Package missing keyword_definitions.json")

                imported_dictionary = json.loads(zf.read("keyword_definitions.json").decode("utf-8"))
                if not isinstance(imported_dictionary, dict):
                    raise ValueError("Invalid keyword_definitions.json format")

                imported_images_map = {}
                if "keyword_images.json" in names:
                    imported_images_map = json.loads(zf.read("keyword_images.json").decode("utf-8"))
                    if not isinstance(imported_images_map, dict):
                        imported_images_map = {}

                images_dir = os.path.join(self.config_folder, "keyword_images")
                os.makedirs(images_dir, exist_ok=True)

                normalized_images_map = {}
                for keyword, rel_paths in imported_images_map.items():
                    if not isinstance(rel_paths, list):
                        rel_paths = [rel_paths]
                    new_rel_paths = []
                    for rel_path in rel_paths:
                        rel_norm = str(rel_path).replace("\\", "/")
                        img_name = os.path.basename(rel_norm)
                        zip_path = f"images/{img_name}"
                        if zip_path not in names:
                            continue
                        target_name = img_name
                        base, ext = os.path.splitext(img_name)
                        counter = 1
                        target_full = os.path.join(images_dir, target_name)
                        while os.path.exists(target_full):
                            target_name = f"{base}_{counter}{ext}"
                            target_full = os.path.join(images_dir, target_name)
                            counter += 1
                        with zf.open(zip_path, "r") as src, open(target_full, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        new_rel_paths.append(os.path.relpath(target_full, self.config_folder))
                    normalized_images_map[str(keyword)] = new_rel_paths

                self.dictionary = {str(k): str(v) for k, v in imported_dictionary.items()}
                self.keyword_images = normalized_images_map
                self.save_keyword_definitions()
                self.refresh_keyword_list()

                self.definition_label.setText("Select a keyword to view its definition.")
                self.definition_label.full_definition = ""
                self.example_label.setVisible(False)
                self.image_label.setVisible(False)

            show_neutral_message_box(
                self,
                QMessageBox.Icon.Information,
                "Import Complete",
                "Dictionary package imported successfully.",
                QMessageBox.StandardButton.Ok,
            )
        except Exception as e:
            show_neutral_message_box(
                self,
                QMessageBox.Icon.Critical,
                "Import Failed",
                f"Failed to import dictionary package:\n{e}",
                QMessageBox.StandardButton.Ok,
            )
    
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
        apply_neutral_dialog_style(self)
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

        # If user selected a custom highlight, use it
        if mode == "custom":
            return custom_color

        # For logs without a background, prefer explicit viewer hover color
        if background == "transparent":
            hover = self.property("viewer_hover_color")
            if hover:
                return hover
            return "#e3f2fd"

        # For logs with colored backgrounds, apply lighter/darker transformation
        color = QColor(background)
        if not color.isValid():
            return "#e3f2fd"
        if mode == "lighter":
            return color.lighter(110).name()
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
            hover_color = self.property("viewer_hover_color") or getattr(self.parent(), "viewer_hover_color", None) or self.selected_background_color()
            hover_style = f"""
                QLabel {{
                    background-color: {hover_color};
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


class EditorLogLabel(QLabel):
    def mousePressEvent(self, event):
        owner = self.property("scroll_guard_owner")
        if owner and owner._should_preserve_log_scroll():
            if event.button() == Qt.MouseButton.LeftButton:
                owner.select_editor_log_label(self)
                event.accept()
                return
            if event.button() == Qt.MouseButton.RightButton:
                owner.select_editor_log_label(self)
                owner.show_context_menu_at_global_pos(event.globalPosition().toPoint())
                event.accept()
                return
        super().mousePressEvent(event)


class LogListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._suppress_auto_scroll = False

    def scrollTo(self, index, hint=QAbstractItemView.ScrollHint.EnsureVisible):
        if self._suppress_auto_scroll:
            return
        super().scrollTo(index, hint)

    def scrollToItem(self, item, hint=QAbstractItemView.ScrollHint.EnsureVisible):
        if self._suppress_auto_scroll:
            return
        super().scrollToItem(item, hint)


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
        self.scroll_area.viewport().installEventFilter(self)
        self.position_on_rightmost()
        
        # Add keyboard shortcuts for arrow key navigation
        self.up_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        self.up_shortcut.activated.connect(self.navigate_up)

        self.down_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        self.down_shortcut.activated.connect(self.navigate_down)
        
        # Add keyboard shortcuts for horizontal scrolling
        self.left_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self.left_shortcut.activated.connect(self.scroll_left)

        self.right_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self.right_shortcut.activated.connect(self.scroll_right)
        
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
        if dark_mode:
            bg = "#1f2329"
        else:
            bg = self.viewer_pref("viewer_background_color", "#FFFFFF")  #
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
        log_label.setProperty("log_background", self.viewer_pref("viewer_log_background_color", "#FFFFFF"))
        log_label.setProperty("viewer_hover_color", self.viewer_pref("viewer_hover_color", "#f0f0f0"))
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
        visible_only = False
        if self.parent_widget:
            visible_only = bool(
                getattr(self.parent_widget, "active_filter", None)
                or getattr(self.parent_widget, "important_filter_active", False)
            )
        previous_scroll_value = None
        scrollbar = self.scroll_area.verticalScrollBar()
        if scrollbar:
            previous_scroll_value = scrollbar.value()
        # Reload all logs from the log_list - used when loading from file
        self.load_logs(visible_only=visible_only)
        if selected_source_index is not None:
            for i in range(self.logs_layout.count() - 2):
                widget = self.logs_layout.itemAt(i).widget()
                if isinstance(widget, ClickableLogLabel) and widget.property("source_index") == selected_source_index:
                    self.on_log_clicked(widget)
                    break
        if scrollbar:
            if visible_only and previous_scroll_value is not None:
                scrollbar.setValue(previous_scroll_value)
            else:
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
        scrollbar = self.scroll_area.verticalScrollBar()
        previous_scroll_value = scrollbar.value() if scrollbar else None
        self.load_logs(visible_only=True)
        if scrollbar and previous_scroll_value is not None:
            scrollbar.setValue(previous_scroll_value)
    
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
        # Bring main window to front and sync the matching source log row.
        source_index = clicked_widget.property("source_index")
        if source_index is None or not self.parent_widget:
            return

        previous_focus = None
        try:
            previous_focus = self.parent_widget.focusWidget()
        except Exception:
            previous_focus = None

        if self.parent_widget.isMinimized():
            self.parent_widget.showNormal()
        self.parent_widget.raise_()
        self.parent_widget.activateWindow()

        if 0 <= source_index < self.parent_widget.log_list.count():
            item = self.parent_widget.log_list.item(source_index)
            if item:
                item_label = self.parent_widget.log_list.itemWidget(item)
                if self.parent_widget._should_preserve_log_scroll() and isinstance(item_label, QLabel):
                    self.parent_widget.select_editor_log_label(item_label, scroll_to_item=True)
                else:
                    self.parent_widget.log_list.blockSignals(True)
                    try:
                        self.parent_widget.log_list.setCurrentItem(item)
                    finally:
                        self.parent_widget.log_list.blockSignals(False)
                    self.parent_widget.apply_editor_selected_log_highlight()

                try:
                    if previous_focus and previous_focus is not self.parent_widget.log_list:
                        previous_focus.setFocus(Qt.FocusReason.OtherFocusReason)
                except Exception:
                    pass
    
    def position_on_rightmost(self):
        # Position the window on the rightmost part of the screen where cursor is
        screen = get_screen_at_cursor()
        
        if screen:
            screen_rect = screen.availableGeometry()
            # Position at the right edge of the screen
            x = screen_rect.right() - self.width()
            y = screen_rect.top()
            self.move(x, y)
            
    def navigate_up(self):
        # Navigate to the previous log using Up arrow keys
        if self.selected_log_label is None:
            return

        # Store the current horizontal scroll position
        h_scrollbar = self.scroll_area.horizontalScrollBar()
        h_position = h_scrollbar.value()

        current_index = self.logs_layout.indexOf(self.selected_log_label)
        if current_index > 0:
            previous_widget = self.logs_layout.itemAt(current_index - 1).widget()
            if isinstance(previous_widget, ClickableLogLabel):
                self.on_log_clicked(previous_widget)
                self.scroll_area.ensureWidgetVisible(previous_widget)
                # Restore the horizontal scroll position
                h_scrollbar.setValue(h_position)

    def navigate_down(self):
        # Navigate to the next log using Down arrow key
        if self.selected_log_label is None:
            return

        # Store the current horizontal scroll position
        h_scrollbar = self.scroll_area.horizontalScrollBar()
        h_position = h_scrollbar.value()

        current_index = self.logs_layout.indexOf(self.selected_log_label)
        if current_index < self.logs_layout.count() - 3:  # Account for spacer/stretch
            next_widget = self.logs_layout.itemAt(current_index + 1).widget()
            if isinstance(next_widget, ClickableLogLabel):
                self.on_log_clicked(next_widget)
                self.scroll_area.ensureWidgetVisible(next_widget)
                # Restore the horizontal scroll position
                h_scrollbar.setValue(h_position)
                
    def scroll_left(self):
        # Scroll left horizontally
        h_scrollbar = self.scroll_area.horizontalScrollBar()
        h_scrollbar.setValue(h_scrollbar.value() - 20)  # Scroll 20px left

    def scroll_right(self):
        # Scroll right horizontally
        h_scrollbar = self.scroll_area.horizontalScrollBar()
        h_scrollbar.setValue(h_scrollbar.value() + 20)  # Scroll 20px right
    
    
    def keyPressEvent(self, event):
        # Navigate using arrow up and down keys (only when a log is selected)
        if event.key() == Qt.Key.Key_Up and self.selected_log_label is not None:
            current_index = self.logs_layout.indexOf(self.selected_log_label)
            if current_index > 0:
                previous_widget = self.logs_layout.itemAt(current_index - 1).widget()
                if isinstance(previous_widget, ClickableLogLabel):
                    self.on_log_clicked(previous_widget)
                    # Ensure the widget is visible in the scroll area
                    self.scroll_area.ensureWidgetVisible(previous_widget)
            event.accept()
            return

        elif event.key() == Qt.Key.Key_Down and self.selected_log_label is not None:
            current_index = self.logs_layout.indexOf(self.selected_log_label)
            if current_index < self.logs_layout.count() - 3:  # Account for spacer/stretch
                next_widget = self.logs_layout.itemAt(current_index + 1).widget()
                if isinstance(next_widget, ClickableLogLabel):
                    self.on_log_clicked(next_widget)
                    # Ensure the widget is visible in the scroll area
                    self.scroll_area.ensureWidgetVisible(next_widget)
            event.accept()
            return

        # For other keys, call the parent implementation
        super().keyPressEvent(event)
    
    def eventFilter(self, obj, event):
        # Intercept key and wheel events from the scroll area viewport
        if obj == self.scroll_area.viewport():
            if event.type() == QEvent.Type.KeyPress:
                self.keyPressEvent(event)
                if event.isAccepted():
                    return True
            elif event.type() == QEvent.Type.Wheel:
                # Handle mouse wheel - Shift determines which scrollbar
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    scrollbar = self.scroll_area.horizontalScrollBar()
                else:
                    scrollbar = self.scroll_area.verticalScrollBar()

                delta = event.angleDelta().y()
                scrollbar.setValue(scrollbar.value() - delta // 8)
                event.accept()
                return True
        return super().eventFilter(obj, event)


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
    CATEGORY_STYLE_MARKER_PREFIX = "<!-- LDS_CAT_STYLE:"
    CATEGORY_STYLE_MARKER_SUFFIX = " -->"

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
        "viewer_background_color": "#FFFFFF",
        "viewer_hover_color": "#f0f0f0",
    }

    DEFAULT_VIEWER_DARK_PRESET = {
        "viewer_background_color": "#1f2329",
        "viewer_hover_color": "#2b3038",
        "viewer_colored_selection_color": "#3d5572",
        "viewer_selection_accent_color": "#8ab4f8",
    }

    DEFAULT_EDITOR_PREFERENCES = {
        "editor_dark_mode": False,
        "editor_background_color": "#FFFFFF",
        "editor_body_background_color": "#F0F0F0",
        "editor_button_foreground_color": "#111111",
        "editor_button_background_color": "#F0F0F0",
        "editor_hover_color": "#cde8ff",
    }

    DEFAULT_EDITOR_DARK_PRESET = {
        "editor_background_color": "#1f2329",
        "editor_body_background_color": "#2b3038",
        "editor_button_foreground_color": "#f4f4f4",
        "editor_button_background_color": "#3a414c",
        "editor_hover_color": "#3d5572",
    }

    DEFAULT_EDITOR_CATEGORIES = [
        {"id": "problem", "icon": "★", "category": "Problem", "background": "#fff4bf", "foreground": "#111111", "deletable": False},
        {"id": "bug", "icon": "▲", "category": "Bug", "background": "#ffd9d9", "foreground": "#111111", "deletable": False},
        {"id": "solution", "icon": "■", "category": "Solution", "background": "#d8f5df", "foreground": "#111111", "deletable": False},
        {"id": "changes", "icon": "◆", "category": "Changes", "background": "#d8f5df", "foreground": "#111111", "deletable": False},
        {"id": "details", "icon": "", "category": "Just Details", "background": "transparent", "foreground": "#111111", "deletable": False},
    ]

    CATEGORY_ICON_OPTIONS = [
        "",
        "★", "☆",
        "▲", "△",
        "◆", "◇",
        "■", "□",
        "●", "○",
        "✦", "✧",
        "✓", "✔",
        "!", "?", "#", "@",
        "→", "←",
        "⚑", "⚠",
    ]
    
    def __init__(self, setup_data=None, log_mode="General", file_path=None, parent=None):
        super().__init__(parent)
        if file_path:
            filename, ext = os.path.splitext(os.path.basename(file_path))
            self.current_file = filename   # just the name without extension
            self.current_ext = ext
            self.fileName = self.current_file
        self.current_file = file_path
        self._load_was_canceled = False
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
        self.active_filter = None
        self.important_filter_active = False
        
        self._important_sort_backup = None

        # Start the hardware monitoring thread
        self.hw_monitor = HardwareMonitor()
        self.hw_monitor.data_ready.connect(self.update_system_info)
        self.hw_monitor.start()
        self.logs_viewer = LogsViewerWindow(self.log_list, self)
        self.logs_viewer.show()
        # Load and apply saved filters on initialization
        self.load_and_apply_saved_filters()
        print("LogApp initialized.")

        # If a file_path is provided, load the logs immediately.
        if file_path:
            self.open_logs(file_path)

    def is_important_log(self, html_text):
        return self.IMPORTANT_MARKER in html_text

    def _parse_category_style_marker(self, html_text: str):
        if not isinstance(html_text, str):
            return None
        start = html_text.find(self.CATEGORY_STYLE_MARKER_PREFIX)
        if start == -1:
            return None
        end = html_text.find(self.CATEGORY_STYLE_MARKER_SUFFIX, start)
        if end == -1:
            return None
        payload = html_text[start + len(self.CATEGORY_STYLE_MARKER_PREFIX):end]
        # payload format: id=<val>;bg=<val>;fg=<val>
        parts = [p.strip() for p in payload.split(";") if p.strip()]
        out = {}
        for p in parts:
            if "=" not in p:
                continue
            k, v = p.split("=", 1)
            out[k.strip()] = v.strip()
        if not out:
            return None
        return out

    def _category_style_marker(self, cid: str, bg: str, fg: str) -> str:
        cid_val = str(cid or "")
        bg_val = str(bg or "transparent")
        fg_val = str(fg or "#111111")
        return f"{self.CATEGORY_STYLE_MARKER_PREFIX}id={cid_val};bg={bg_val};fg={fg_val}{self.CATEGORY_STYLE_MARKER_SUFFIX}"

    def _extract_icon_from_log_html(self, html_text: str) -> str:
        if not isinstance(html_text, str):
            return ""
        m = re.search(r"(?:<!--.*?-->\s*)*<span[^>]*>([^<]*)</span>\s*<span", html_text, re.DOTALL)
        if not m:
            return ""
        return (m.group(1) or "").strip()

    def _extract_category_number_from_log_html(self, html_text: str) -> Optional[int]:
        if not isinstance(html_text, str):
            return None
        plain = self.strip_html(html_text)
        m = re.search(r"#(\d+)\s*$", plain)
        if not m:
            return None
        try:
            return int(m.group(1))
        except Exception:
            return None

    def _category_config_by_id(self, cid: str):
        self._ensure_editor_categories()
        cid = str(cid or "").strip()
        if not cid:
            return None
        for c in getattr(self, "editor_categories", []):
            if str(c.get("id", "")).strip() == cid:
                return c
        return None

    def _category_config_by_icon(self, icon: str, categories=None):
        if categories is None:
            self._ensure_editor_categories()
            categories = getattr(self, "editor_categories", [])
        icon = str(icon or "").strip()
        if icon == "":
            # Prefer the "Just Details" default when icon is blank
            for c in categories:
                if str(c.get("category", "")).strip() == "Just Details":
                    return c
        for c in categories:
            if str(c.get("icon", "")).strip() == icon:
                return c
        return None

    def normalize_logs_to_categories_and_rebuild_counters(self, previous_categories=None):
        if not hasattr(self, "log_list") or not self.log_list:
            return
        self._ensure_editor_categories()

        counters = {}
        for i in range(self.log_list.count()):
            item = self.log_list.item(i)
            label = self.log_list.itemWidget(item)
            if not isinstance(label, QLabel):
                continue
            html_text = label.text()

            marker = self._parse_category_style_marker(html_text) or {}
            cid = str(marker.get("id", "")).strip()
            cfg = self._category_config_by_id(cid) if cid else None
            if not cfg and previous_categories is not None:
                icon = self._extract_icon_from_log_html(html_text)
                previous_cfg = self._category_config_by_icon(icon, previous_categories)
                if previous_cfg:
                    previous_id = str(previous_cfg.get("id", "")).strip()
                    cfg = self._category_config_by_id(previous_id)
            if not cfg:
                icon = self._extract_icon_from_log_html(html_text)
                cfg = self._category_config_by_icon(icon)
            if not cfg:
                continue

            cid = str(cfg.get("id", "")).strip() or uuid.uuid4().hex
            cfg["id"] = cid

            existing_n = self._extract_category_number_from_log_html(html_text)
            if existing_n is not None:
                counters[cid] = max(counters.get(cid, 0), existing_n)
            else:
                counters[cid] = counters.get(cid, 0) + 1

            icon = str(cfg.get("icon", "")).strip()
            fg = str(cfg.get("foreground", "#111111"))
            bg = str(cfg.get("background", "transparent"))

            # Remove any existing cat-style marker and replace with the new one
            if self.CATEGORY_STYLE_MARKER_PREFIX in html_text:
                start = html_text.find(self.CATEGORY_STYLE_MARKER_PREFIX)
                end = html_text.find(self.CATEGORY_STYLE_MARKER_SUFFIX, start)
                if end != -1:
                    html_text = html_text[:start] + html_text[end + len(self.CATEGORY_STYLE_MARKER_SUFFIX):]

            style_marker = self._category_style_marker(cid, bg, fg)

            # Replace the first visible icon span even if hidden markers/comments come first.
            icon_span_pattern = r"^((?:\s|<!--.*?-->)*?)<span[^>]*>[^<]*</span>"
            replacement = r"\1" + f'<span style="color:{fg};">{icon}</span>'
            if re.search(icon_span_pattern, html_text, re.DOTALL):
                html_text = re.sub(icon_span_pattern, replacement, html_text, count=1, flags=re.DOTALL)
            else:
                html_text = f'<span style="color:{fg};">{icon}</span> ' + html_text

            # Update the main content span color so foreground changes apply to
            # existing logs, not only newly created ones.
            text_span_pattern = r"^((?:\s|<!--.*?-->)*?<span[^>]*>[^<]*</span>\s*)<span[^>]*>"
            text_span_replacement = r"\1" + f'<span style="color:{fg};">'
            if re.search(text_span_pattern, html_text, re.DOTALL):
                html_text = re.sub(text_span_pattern, text_span_replacement, html_text, count=1, flags=re.DOTALL)

            html_text = style_marker + html_text
            html_text = self.set_importance_marker(html_text, self.is_important_log(label.text()))
            label.setText(html_text)
            self.apply_log_label_style(label, self.is_important_log(html_text))

        self.log_counters = counters
        self.save_log_counters()

    def _current_category_config(self):
        self._ensure_editor_categories()
        if not hasattr(self, "category_selector") or not self.category_selector:
            return None
        cid = self.category_selector.currentData(Qt.ItemDataRole.UserRole)
        if cid:
            for c in getattr(self, "editor_categories", []):
                if str(c.get("id", "")).strip() == str(cid).strip():
                    return c
        # Fallback: match by category name only (best-effort).
        current = self.category_selector.currentText()
        if not isinstance(current, str):
            return None
        text = current.strip()
        name = text
        # If label is "Name ICON", strip the last char icon.
        if len(text) >= 2 and text[-2] == " ":
            name = text[:-2]
        for c in getattr(self, "editor_categories", []):
            if str(c.get("category", "")).strip() == name:
                return c
        return None

    def load_default_log_theme_colors(self):
        for key, value in self.DEFAULT_LOG_THEME_COLORS.items():
            setattr(self, key, value)
        for key, value in self.DEFAULT_VIEWER_PREFERENCES.items():
            setattr(self, key, value)
        for key, value in self.DEFAULT_EDITOR_PREFERENCES.items():
            setattr(self, key, value)

    def set_importance_marker(self, html_text, important):
        html_text = html_text.replace(self.IMPORTANT_MARKER, "").replace(self.NOT_IMPORTANT_MARKER, "")
        marker = self.IMPORTANT_MARKER if important else self.NOT_IMPORTANT_MARKER
        return f"{marker}{html_text}"

    def get_log_background_color(self, html_text):
        marker = self._parse_category_style_marker(html_text)
        if marker and "bg" in marker:
            return marker["bg"]
        plain_text = self.strip_html(html_text)
        if "Fixed" in plain_text or "Resolved" in plain_text or "■" in plain_text or "Solution #" in plain_text:
            return getattr(self, "resolved_background_color", self.DEFAULT_LOG_THEME_COLORS["resolved_background_color"])
        if "▲" in plain_text:
            return getattr(self, "bug_background_color", self.DEFAULT_LOG_THEME_COLORS["bug_background_color"])
        if "★" in plain_text:
            return getattr(self, "problem_background_color", self.DEFAULT_LOG_THEME_COLORS["problem_background_color"])
        return getattr(self, "default_background_color", self.DEFAULT_LOG_THEME_COLORS["default_background_color"])

    def apply_log_label_style(self, label, important=False):
        accent_color = getattr(self, "important_accent_color", self.DEFAULT_LOG_THEME_COLORS["important_accent_color"])
        border = f"border-left: 5px solid {accent_color};" if important else ""
        padding = "padding-left: 6px;" if important else "padding-left: 0px;"
        # Keep the label transparent so the QListWidgetItem background / hover can show through
        label.setStyleSheet(f"QLabel {{ background-color: transparent; {border} {padding} }}")

    def refresh_log_label_styles(self):
        for index in range(self.log_list.count()):
            item = self.log_list.item(index)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel):
                bg = self.get_log_background_color(label.text())
                try:
                    if isinstance(bg, str) and bg.strip() and bg.strip().lower() != "transparent":
                        item.setBackground(QBrush(QColor(bg)))
                    else:
                        item.setBackground(QBrush())
                except Exception:
                    item.setBackground(QBrush())
                self.apply_log_label_style(label, self.is_important_log(label.text()))
        self.apply_editor_selected_log_highlight()

    def _capture_log_list_scroll(self):
        if not hasattr(self, "log_list") or not self.log_list:
            return None
        vertical_scrollbar = self.log_list.verticalScrollBar()
        horizontal_scrollbar = self.log_list.horizontalScrollBar()
        return (
            vertical_scrollbar.value() if vertical_scrollbar else None,
            horizontal_scrollbar.value() if horizontal_scrollbar else None,
            vertical_scrollbar,
            horizontal_scrollbar,
        )

    def _restore_log_list_scroll(self, scroll_state):
        if not scroll_state:
            return
        previous_vertical, previous_horizontal, vertical_scrollbar, horizontal_scrollbar = scroll_state
        if vertical_scrollbar and previous_vertical is not None:
            vertical_scrollbar.setValue(previous_vertical)
        if horizontal_scrollbar and previous_horizontal is not None:
            horizontal_scrollbar.setValue(previous_horizontal)

    def apply_editor_selected_log_highlight(self, restore_scroll=True):
        if not hasattr(self, "log_list") or not self.log_list:
            return
        scroll_state = self._capture_log_list_scroll() if restore_scroll else None
        preserve_scroll = self._should_preserve_log_scroll()
        selected_label = self.editor_selected_log_label if preserve_scroll else None
        # restore each item's base background and label style
        for i in range(self.log_list.count()):
            item = self.log_list.item(i)
            label = self.log_list.itemWidget(item)
            if isinstance(label, QLabel):
                bg = self.get_log_background_color(label.text())
                try:
                    if isinstance(bg, str) and bg.strip() and bg.strip().lower() != "transparent":
                        item.setBackground(QBrush(QColor(bg)))
                    else:
                        item.setBackground(QBrush())
                except Exception:
                    item.setBackground(QBrush())
                self.apply_log_label_style(label, self.is_important_log(label.text()))
        # apply hover/highlight to the currently selected item
        if preserve_scroll and selected_label:
            for i in range(self.log_list.count()):
                item = self.log_list.item(i)
                label = self.log_list.itemWidget(item)
                if label is selected_label:
                    hover_color = getattr(self, "editor_hover_color", self.DEFAULT_EDITOR_PREFERENCES.get("editor_hover_color", "#cde8ff"))
                    try:
                        item.setBackground(QBrush(QColor(hover_color)))
                    except Exception:
                        item.setBackground(QBrush())
                    if isinstance(label, QLabel):
                        self.apply_log_label_style(label, self.is_important_log(label.text()))
                    break
        else:
            current = self.log_list.currentItem()
            if current:
                hover_color = getattr(self, "editor_hover_color", self.DEFAULT_EDITOR_PREFERENCES.get("editor_hover_color", "#cde8ff"))
                try:
                    current.setBackground(QBrush(QColor(hover_color)))
                except Exception:
                    current.setBackground(QBrush())
                sel_label = self.log_list.itemWidget(current)
                if isinstance(sel_label, QLabel):
                    self.apply_log_label_style(sel_label, self.is_important_log(sel_label.text()))
        if restore_scroll:
            self._restore_log_list_scroll(scroll_state)
            QTimer.singleShot(0, lambda state=scroll_state: self._restore_log_list_scroll(state))

    def select_editor_log_label(self, label, scroll_to_item=False):
        if not isinstance(label, QLabel):
            return
        self.editor_selected_log_label = label
        if scroll_to_item:
            item = None
            for i in range(self.log_list.count()):
                current_item = self.log_list.item(i)
                if self.log_list.itemWidget(current_item) is label:
                    item = current_item
                    break
            if item:
                previous_suppression = getattr(self.log_list, "_suppress_auto_scroll", False)
                self.log_list._suppress_auto_scroll = False
                try:
                    self.log_list.scrollToItem(item)
                finally:
                    self.log_list._suppress_auto_scroll = previous_suppression
        self.apply_editor_selected_log_highlight(restore_scroll=not scroll_to_item)
    
    def on_editor_log_selection_changed(self, current, previous):
        if previous:
            prev_label = self.log_list.itemWidget(previous)
            if isinstance(prev_label, QLabel):
                self.apply_log_label_style(prev_label, self.is_important_log(prev_label.text()))
        self.apply_editor_selected_log_highlight()

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
        # update menu badge if present
        try:
            self.update_important_menu_label()
        except Exception:
            pass
    def position_view_badge(self):
        # Position the small badge over the View menu action
        try:
            if not hasattr(self, "menu_bar") or not hasattr(self, "view_menu_action") or not hasattr(self, "view_badge"):
                return
            rect = self.menu_bar.actionGeometry(self.view_menu_action)
            if rect.isValid():
                self.view_badge.adjustSize()
                x = rect.right() - (self.view_badge.width() // 2)
                y = rect.top() + (rect.height() - self.view_badge.height()) // 2 - 2
                x = max(0, min(x, self.menu_bar.width() - self.view_badge.width()))
                y = max(0, min(y, self.menu_bar.height() - self.view_badge.height()))
                self.view_badge.move(x, y)
                self.view_badge.raise_()
        except Exception:
            pass
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.position_view_badge)
        
    def toggle_view_important(self, checked: bool):
        self.important_filter_active = checked
        self.reapply_all_filters()

    def update_important_menu_label(self):
        count = int(self.log_counters.get("Importance", 0))
        if hasattr(self, "important_action") and isinstance(self.important_action, QAction):
            self.important_action.setText(f"Important ({count})")
        # update overlay badge
        if hasattr(self, "view_badge"):
            if count <= 0:
                self.view_badge.hide()
            else:
                self.view_badge.setText("99+" if count > 99 else str(count))
                self.view_badge.adjustSize()
                self.view_badge.show()
                QTimer.singleShot(0, self.position_view_badge)

    def configure_log_label(self, label, html_text, word_wrap=False):
        label.setText(html_text)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setOpenExternalLinks(False)
        label.setProperty("scroll_guard_owner", self)
        try:
            label.linkActivated.disconnect(self.handle_internal_link)
        except TypeError:
            pass
        label.linkActivated.connect(self.handle_internal_link)
        label.setWordWrap(word_wrap)
        self.apply_log_label_style(label, self.is_important_log(html_text))

    def _contrast_text_color_for_bg(self, bg_hex: str) -> str:
        color = QColor(bg_hex)
        if not color.isValid():
            return "#111111"
        r, g, b, _a = color.getRgb()
        # Perceived luminance: pick black on light backgrounds, white on dark.
        luminance = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)
        return "#111111" if luminance > 150 else "#FFFFFF"

    def _set_preview_button_color(self, button: QPushButton, bg_hex: str):
        fg = self._contrast_text_color_for_bg(bg_hex)
        button.setStyleSheet(
            f"background-color: {bg_hex}; color: {fg}; border: 1px solid {fg}; padding: 6px;"
        )

    def _ensure_editor_categories(self):
        cats = getattr(self, "editor_categories", None)
        if not isinstance(cats, list) or not cats:
            self.editor_categories = list(self.DEFAULT_EDITOR_CATEGORIES)
            return
        normalized = []
        for c in cats:
            if not isinstance(c, dict):
                continue
            normalized.append(
                {
                    "id": str(c.get("id", "")).strip(),
                    "icon": str(c.get("icon", "")),
                    "category": str(c.get("category", "")),
                    "background": str(c.get("background", "transparent")),
                    "foreground": str(c.get("foreground", "#111111")),
                    "deletable": bool(c.get("deletable", True)),
                }
            )
        if not normalized:
            normalized = list(self.DEFAULT_EDITOR_CATEGORIES)

        defaults = list(getattr(self, "editor_categories_default", list(self.DEFAULT_EDITOR_CATEGORIES)))
        defaults_by_id = {str(d.get("id", "")).strip(): d for d in defaults if str(d.get("id", "")).strip()}
        defaults_by_name = {str(d.get("category", "")).strip(): d for d in defaults}

        # Preserve the saved order while still enforcing that default rows exist and stay non-deletable.
        merged = []
        seen_default_names = set()
        for c in normalized:
            cid = str(c.get("id", "")).strip()
            name = str(c.get("category", "")).strip()
            default_entry = defaults_by_id.get(cid) or defaults_by_name.get(name)
            if default_entry:
                default_name = str(default_entry.get("category", "")).strip()
                if default_name in seen_default_names:
                    continue
                default_id = str(default_entry.get("id", "")).strip()
                merged.append(
                    {
                        "id": default_id or cid or uuid.uuid4().hex,
                        "icon": str(c.get("icon", default_entry.get("icon", ""))),
                        "category": default_name,
                        "background": str(c.get("background", default_entry.get("background", "transparent"))),
                        "foreground": str(c.get("foreground", default_entry.get("foreground", "#111111"))),
                        "deletable": False,
                    }
                )
                seen_default_names.add(default_name)
                continue

            merged.append(
                {
                    "id": cid or uuid.uuid4().hex,
                    "icon": str(c.get("icon", "")),
                    "category": name,
                    "background": str(c.get("background", "transparent")),
                    "foreground": str(c.get("foreground", "#111111")),
                    "deletable": True,
                }
            )

        # Append any default categories that were missing from persisted data.
        for d in defaults:
            default_name = str(d.get("category", "")).strip()
            if default_name in seen_default_names:
                continue
            dd = dict(d)
            if not str(dd.get("id", "")).strip():
                dd["id"] = uuid.uuid4().hex
            dd["deletable"] = False
            merged.append(dd)

        self.editor_categories = merged

    def refresh_category_selector(self):
        if not hasattr(self, "category_selector") or not self.category_selector:
            return
        self._ensure_editor_categories()
        current = self.category_selector.currentText()
        current_id = self.category_selector.currentData(Qt.ItemDataRole.UserRole)
        self.category_selector.blockSignals(True)
        self.category_selector.clear()
        visible_categories = []
        for c in self.editor_categories:
            category_name = str(c.get("category", "")).strip()
            if self.log_type == "General" and category_name == "Solution":
                continue
            if self.log_type == "Debugging" and category_name not in {"Just Details", "Bug"}:
                continue
            visible_categories.append(c)

        for c in visible_categories:
            cid = str(c.get("id", "")).strip() or uuid.uuid4().hex
            c["id"] = cid
            icon = c.get("icon", "").strip()
            name = c.get("category", "").strip() or "Untitled"
            label = f"{name} {icon}".strip()
            self.category_selector.addItem(label, cid)
        idx = self.category_selector.findText(current)
        if current_id:
            for i in range(self.category_selector.count()):
                if self.category_selector.itemData(i, Qt.ItemDataRole.UserRole) == current_id:
                    self.category_selector.setCurrentIndex(i)
                    break
            else:
                if idx >= 0:
                    self.category_selector.setCurrentIndex(idx)
        elif idx >= 0:
            self.category_selector.setCurrentIndex(idx)
        self.category_selector.blockSignals(False)

    def get_filterable_category_options(self):
        self._ensure_editor_categories()
        options = []
        for c in self.editor_categories:
            category_name = str(c.get("category", "")).strip()
            if self.log_type == "General" and category_name == "Solution":
                continue
            if self.log_type == "Debugging" and category_name not in {"Just Details", "Bug"}:
                continue
            icon = str(c.get("icon", "")).strip()
            label = f"{category_name} {icon}".strip()
            if label:
                options.append(label)
        return options

    def _color_combo(self, initial: str):
        combo = QComboBox()
        options = [
            "transparent",
            "#FFFFFF",
            "#F0F0F0",
            "#111111",
            "#1f2329",
            "#2b3038",
            "#3a414c",
            "#cde8ff",
            "#3d5572",
            "#ffd9d9",
            "#fff4bf",
            "#d8f5df",
            "Custom...",
        ]
        combo.addItems(options)
        if initial in options:
            combo.setCurrentText(initial)
        else:
            combo.setCurrentText("Custom...")
        return combo

    def open_editor_categories(self):
        self._ensure_editor_categories()

        dialog = QDialog(self)
        dialog.setWindowTitle("Categories")
        dialog.setFixedSize(640, 320)
        dialog.setStyleSheet("""
            QDialog { background-color: #f5f5f5; color: #111111; }
            QLabel { color: #111111; }
            QPushButton { padding: 6px; }
            QLineEdit { padding: 4px; }
        """)

        layout = QVBoxLayout(dialog)

        reset_btn = QPushButton("Reset Defaults")
        layout.addWidget(reset_btn)

        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        scroll_contents = QWidget()
        rows_layout = QVBoxLayout(scroll_contents)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(6)
        scroll.setWidget(scroll_contents)
        layout.addWidget(scroll)

        row_widgets = []

        def refresh_move_buttons():
            total = len(row_widgets)
            for idx, (_container, data) in enumerate(row_widgets):
                up_btn = data.get("_move_up_btn")
                down_btn = data.get("_move_down_btn")
                if up_btn is not None:
                    up_btn.setEnabled(idx > 0)
                if down_btn is not None:
                    down_btn.setEnabled(idx < total - 1)

        def refresh_icon_choices():
            used_by_other = {}
            for _container, data in row_widgets:
                row_id = str(data.get("id", "")).strip()
                icon_value = str(data.get("icon", "")).strip()
                if icon_value:
                    used_by_other.setdefault(icon_value, set()).add(row_id)

            for _container, data in row_widgets:
                combo = data.get("_icon_widget")
                if combo is None:
                    continue
                row_id = str(data.get("id", "")).strip()
                current_icon = str(data.get("icon", "")).strip()
                allow_default_icons = bool(data.get("_allow_default_icons", True))
                if allow_default_icons:
                    base_options = list(self.CATEGORY_ICON_OPTIONS)
                else:
                    default_icons = {
                        str(c.get("icon", "")).strip()
                        for c in getattr(self, "editor_categories_default", list(self.DEFAULT_EDITOR_CATEGORIES))
                    }
                    base_options = [icon for icon in self.CATEGORY_ICON_OPTIONS if icon not in default_icons]

                available = []
                for icon_option in base_options:
                    if icon_option == "" and current_icon != "":
                        owners = used_by_other.get(icon_option, set())
                        if owners and owners != {row_id}:
                            continue
                    owners = used_by_other.get(icon_option, set())
                    if not owners or owners == {row_id}:
                        available.append(icon_option)
                if current_icon and current_icon not in available:
                    available.append(current_icon)
                combo.blockSignals(True)
                combo.clear()
                combo.addItems(available)
                combo.setCurrentText(current_icon if current_icon in available else "")
                combo.blockSignals(False)

        def enforce_unique_icons(changed_id=None):
            seen = {}
            for _container, data in row_widgets:
                icon_value = str(data.get("icon", "")).strip()
                if not icon_value:
                    continue
                if icon_value not in seen:
                    seen[icon_value] = str(data.get("id", "")).strip()
                    continue
                current_id = str(data.get("id", "")).strip()
                if changed_id and current_id != changed_id:
                    data["icon"] = ""
                else:
                    data["icon"] = ""

            for _container, data in row_widgets:
                combo = data.get("_icon_widget")
                if combo is not None:
                    desired = str(data.get("icon", "")).strip()
                    if combo.currentText() != desired:
                        combo.blockSignals(True)
                        combo.setCurrentText(desired)
                        combo.blockSignals(False)
            refresh_icon_choices()

        def icon_combo(initial: str, allow_default_icons: bool = True):
            combo = QComboBox()
            if allow_default_icons:
                options = list(self.CATEGORY_ICON_OPTIONS)
            else:
                default_icons = {
                    str(c.get("icon", "")).strip()
                    for c in getattr(self, "editor_categories_default", list(self.DEFAULT_EDITOR_CATEGORIES))
                }
                options = [icon for icon in self.CATEGORY_ICON_OPTIONS if icon not in default_icons]
            combo.addItems(options)
            combo.setCurrentText(initial if initial in options else (options[0] if options else ""))
            return combo

        def make_row(cat: dict):
            row = QHBoxLayout()
            row.setSpacing(8)

            cat_w = QLineEdit(cat.get("category", ""))
            bg_btn = QPushButton("Background")
            fg_btn = QPushButton("Foreground")
            up_btn = QPushButton("↑")
            down_btn = QPushButton("↓")
            del_btn = QPushButton("X")
            up_btn.setFixedWidth(28)
            down_btn.setFixedWidth(28)
            del_btn.setFixedWidth(28)

            deletable = bool(cat.get("deletable", True))
            icon_w = icon_combo(cat.get("icon", ""), allow_default_icons=not deletable)
            if not deletable:
                cat_w.setEnabled(False)
                del_btn.setEnabled(False)

            current_value = {
                "id": str(cat.get("id", "")).strip() or uuid.uuid4().hex,
                "icon": cat.get("icon", ""),
                "category": cat.get("category", ""),
                "background": cat.get("background", "transparent"),
                "foreground": cat.get("foreground", "#111111"),
                "deletable": deletable,
            }
            current_value["_icon_widget"] = icon_w
            current_value["_allow_default_icons"] = not deletable
            current_value["_bg_button"] = bg_btn
            current_value["_fg_button"] = fg_btn
            current_value["_move_up_btn"] = up_btn
            current_value["_move_down_btn"] = down_btn

            self._set_preview_button_color(bg_btn, str(current_value["background"]))
            self._set_preview_button_color(fg_btn, str(current_value["foreground"]))

            def on_icon_changed(text):
                current_value["icon"] = text
                enforce_unique_icons(changed_id=current_value["id"])

            icon_w.currentTextChanged.connect(on_icon_changed)
            cat_w.textChanged.connect(lambda t: current_value.__setitem__("category", t))

            def choose_color_for(key: str, btn: QPushButton):
                start = QColor(str(current_value[key]))
                chosen = QColorDialog.getColor(start, dialog)
                if chosen.isValid():
                    current_value[key] = chosen.name()
                    self._set_preview_button_color(btn, str(current_value[key]))

            def set_transparent_for(key: str, btn: QPushButton):
                current_value[key] = "transparent"
                self._set_preview_button_color(btn, "transparent")

            def open_bg_menu():
                menu = QMenu(dialog)
                pick = QAction("Pick Color", dialog)
                transparent = QAction("Transparent", dialog)
                pick.triggered.connect(lambda: choose_color_for("background", bg_btn))
                transparent.triggered.connect(lambda: set_transparent_for("background", bg_btn))
                menu.addAction(pick)
                menu.addAction(transparent)
                menu.exec(bg_btn.mapToGlobal(bg_btn.rect().bottomLeft()))

            def open_fg_menu():
                menu = QMenu(dialog)
                pick = QAction("Pick Color", dialog)
                pick.triggered.connect(lambda: choose_color_for("foreground", fg_btn))
                menu.addAction(pick)
                menu.exec(fg_btn.mapToGlobal(fg_btn.rect().bottomLeft()))

            bg_btn.clicked.connect(open_bg_menu)
            fg_btn.clicked.connect(open_fg_menu)

            row.addWidget(icon_w)
            row.addWidget(cat_w)
            row.addWidget(bg_btn)
            row.addWidget(fg_btn)
            row.addWidget(up_btn)
            row.addWidget(down_btn)
            row.addWidget(del_btn)

            container = QWidget()
            container.setLayout(row)

            def move_row(delta: int):
                current_index = None
                for i, (w, _data) in enumerate(row_widgets):
                    if w is container:
                        current_index = i
                        break
                if current_index is None:
                    return
                new_index = current_index + delta
                if new_index < 0 or new_index >= len(row_widgets):
                    return
                row_widgets.insert(new_index, row_widgets.pop(current_index))
                rows_layout.removeWidget(container)
                rows_layout.insertWidget(new_index, container)
                refresh_move_buttons()

            up_btn.clicked.connect(lambda: move_row(-1))
            down_btn.clicked.connect(lambda: move_row(1))

            def delete_row():
                if not current_value["deletable"]:
                    return
                container.setParent(None)
                for i, (w, _data) in enumerate(list(row_widgets)):
                    if w is container:
                        row_widgets.pop(i)
                        break
                refresh_move_buttons()

            del_btn.clicked.connect(delete_row)

            row_widgets.append((container, current_value))
            rows_layout.addWidget(container)
            refresh_move_buttons()

        def rebuild_rows(cats: list):
            for i in reversed(range(rows_layout.count())):
                item = rows_layout.takeAt(i)
                w = item.widget()
                if w is not None:
                    w.setParent(None)
            row_widgets.clear()
            for cat in cats:
                make_row(cat)
            enforce_unique_icons()
            refresh_icon_choices()
            refresh_move_buttons()

        rebuild_rows(self.editor_categories)

        add_btn = QPushButton("Add")
        layout.addWidget(add_btn)
        add_btn.clicked.connect(lambda: make_row({"id": uuid.uuid4().hex, "icon": "", "category": "New Category", "background": "transparent", "foreground": "#111111", "deletable": True}))

        button_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        button_row.addWidget(save_btn)
        button_row.addWidget(cancel_btn)
        layout.addLayout(button_row)

        def save_categories():
            previous_categories = [dict(c) for c in getattr(self, "editor_categories", [])]
            enforce_unique_icons()
            cats = []
            icon_usage = {}
            name_usage = {}
            for _container, data in row_widgets:
                name = str(data.get("category", "")).strip()
                if not name:
                    continue
                icon_value = str(data.get("icon", "")).strip()
                icon_usage.setdefault(icon_value, []).append(name or "Untitled")
                name_usage.setdefault(name.casefold(), []).append(name)
                cats.append(
                    {
                        "id": str(data.get("id", "")).strip() or uuid.uuid4().hex,
                        "icon": icon_value,
                        "category": name,
                        "background": str(data.get("background", "transparent")),
                        "foreground": str(data.get("foreground", "#111111")),
                        "deletable": bool(data.get("deletable", True)),
                    }
                )

            duplicate_icons = {icon: names for icon, names in icon_usage.items() if len(names) > 1}
            if duplicate_icons:
                details = []
                for icon, names in duplicate_icons.items():
                    icon_label = "(blank)" if icon == "" else icon
                    details.append(f"{icon_label}: {', '.join(names)}")
                QMessageBox.warning(
                    dialog,
                    "Duplicate Icons",
                    "Each category must use a unique icon before saving.\n\n" + "\n".join(details),
                )
                return

            duplicate_names = {norm_name: names for norm_name, names in name_usage.items() if len(names) > 1}
            if duplicate_names:
                details = []
                for names in duplicate_names.values():
                    details.append(", ".join(names))
                QMessageBox.warning(
                    dialog,
                    "Duplicate Category Names",
                    "Each category must use a unique name before saving.\n\n" + "\n".join(details),
                )
                return

            defaults = list(getattr(self, "editor_categories_default", list(self.DEFAULT_EDITOR_CATEGORIES)))
            defaults_by_id = {str(d.get("id", "")).strip(): d for d in defaults if str(d.get("id", "")).strip()}
            defaults_by_name = {str(d.get("category", "")).strip(): d for d in defaults}

            merged = []
            seen_default_names = set()
            for c in cats:
                cid = str(c.get("id", "")).strip()
                name = str(c.get("category", "")).strip()
                default_entry = defaults_by_id.get(cid) or defaults_by_name.get(name)
                if default_entry:
                    default_name = str(default_entry.get("category", "")).strip()
                    if default_name in seen_default_names:
                        continue
                    default_id = str(default_entry.get("id", "")).strip()
                    merged.append(
                        {
                            "id": default_id or cid or uuid.uuid4().hex,
                            "icon": str(c.get("icon", default_entry.get("icon", ""))),
                            "category": default_name,
                            "background": str(c.get("background", default_entry.get("background", "transparent"))),
                            "foreground": str(c.get("foreground", default_entry.get("foreground", "#111111"))),
                            "deletable": False,
                        }
                    )
                    seen_default_names.add(default_name)
                    continue

                merged.append(
                    {
                        "id": cid or uuid.uuid4().hex,
                        "icon": str(c.get("icon", "")),
                        "category": name,
                        "background": str(c.get("background", "transparent")),
                        "foreground": str(c.get("foreground", "#111111")),
                        "deletable": True,
                    }
                )

            for d in defaults:
                default_name = str(d.get("category", "")).strip()
                if default_name in seen_default_names:
                    continue
                dd = dict(d)
                dd["deletable"] = False
                if not str(dd.get("id", "")).strip():
                    dd["id"] = uuid.uuid4().hex
                merged.append(dd)

            self.editor_categories = merged
            self.save_user_config()
            self.refresh_category_selector()
            self.normalize_logs_to_categories_and_rebuild_counters(previous_categories=previous_categories)
            if hasattr(self, "logs_viewer") and self.logs_viewer:
                self.logs_viewer.refresh_logs()
            dialog.accept()

        def reset_defaults():
            defaults = list(getattr(self, "editor_categories_default", list(self.DEFAULT_EDITOR_CATEGORIES)))
            defaults_by_name = {str(d.get("category", "")).strip(): dict(d) for d in defaults}

            used_custom_icons = set()
            for _container, data in row_widgets:
                name = str(data.get("category", "")).strip()
                if name in defaults_by_name:
                    continue
                icon_value = str(data.get("icon", "")).strip()
                if icon_value:
                    used_custom_icons.add(icon_value)

            for _container, data in row_widgets:
                name = str(data.get("category", "")).strip()
                if name not in defaults_by_name:
                    continue
                default_entry = defaults_by_name[name]
                reset_icon = str(default_entry.get("icon", "")).strip()
                if reset_icon and reset_icon in used_custom_icons:
                    reset_icon = ""
                data["icon"] = reset_icon
                data["background"] = str(default_entry.get("background", "transparent"))
                data["foreground"] = str(default_entry.get("foreground", "#111111"))

                icon_widget = data.get("_icon_widget")
                if icon_widget is not None:
                    icon_widget.blockSignals(True)
                    icon_widget.setCurrentText(data["icon"])
                    icon_widget.blockSignals(False)

                bg_btn = data.get("_bg_button")
                if bg_btn is not None:
                    self._set_preview_button_color(bg_btn, str(data["background"]))

                fg_btn = data.get("_fg_button")
                if fg_btn is not None:
                    self._set_preview_button_color(fg_btn, str(data["foreground"]))

            enforce_unique_icons()
            refresh_icon_choices()

        reset_btn.clicked.connect(reset_defaults)
        save_btn.clicked.connect(save_categories)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()

    def apply_editor_theme(self):
        dark_mode = bool(getattr(self, "editor_dark_mode", self.DEFAULT_EDITOR_PREFERENCES["editor_dark_mode"]))
        preset = self.DEFAULT_EDITOR_DARK_PRESET if dark_mode else self.DEFAULT_EDITOR_PREFERENCES

        editor_background = getattr(self, "editor_background_color", preset["editor_background_color"])
        body_background = getattr(self, "editor_body_background_color", preset["editor_body_background_color"])
        button_foreground = getattr(self, "editor_button_foreground_color", preset["editor_button_foreground_color"])
        button_background = getattr(self, "editor_button_background_color", preset["editor_button_background_color"])
        hover_color = getattr(self, "editor_hover_color", preset.get("editor_hover_color", self.DEFAULT_EDITOR_PREFERENCES["editor_hover_color"]))

        editor_text = "#f4f4f4" if dark_mode else "#111111"
        border_color = "#5c6673" if dark_mode else "#b8b8b8"
        selection_background = hover_color

        self.setStyleSheet(f"""
            QWidget#LogAppRoot {{
                background-color: {body_background};
                color: {editor_text};
            }}
            QWidget#LogAppRoot QLabel,
            QWidget#LogAppRoot QCheckBox,
            QWidget#LogAppRoot QComboBox {{
                color: {editor_text};
            }}
            QWidget#LogAppRoot QMenuBar {{
                background-color: {body_background};
                color: {editor_text};
            }}
            QWidget#LogAppRoot QMenuBar::item:hover {{
                background-color: {hover_color};
                color: {button_foreground};
            }}
            QWidget#LogAppRoot QMenuBar::item:selected {{
                background-color: {hover_color};
                color: {button_foreground};
            }}
            QWidget#LogAppRoot QMenu {{
                background-color: {body_background};
                color: {editor_text};
                border: 1px solid {border_color};
            }}
            QWidget#LogAppRoot QMenu::item:hover {{
                background-color: {hover_color};
                color: {button_foreground};
            }}
            QWidget#LogAppRoot QMenu::item:selected {{
                background-color: {hover_color};
                color: {button_foreground};
            }}
            QWidget#LogAppRoot QTextEdit,
            QWidget#LogAppRoot QListWidget {{
                background-color: {editor_background};
                color: {editor_text};
                border: 1px solid {border_color};
                selection-background-color: {selection_background};
                outline: none;
            }}
            QWidget#LogAppRoot QListWidget::item:hover {{
                background-color: {hover_color};
            }}
            QWidget#LogAppRoot QListWidget::item:selected {{
                background-color: {hover_color};
            }}
            QWidget#LogAppRoot QComboBox,
            QWidget#LogAppRoot QPushButton {{
                background-color: {button_background};
                color: {button_foreground};
                border: 1px solid {border_color};
                padding: 4px;
            }}
            QWidget#LogAppRoot QPushButton:hover {{
                background-color: {hover_color};
            }}
            QWidget#LogAppRoot QPushButton:pressed {{
                background-color: {hover_color};
            }}
        """)
        self.apply_editor_selected_log_highlight()

    def create_menu_bar(self, layout):
        menu_bar = QMenuBar(self)
        layout.setMenuBar(menu_bar)  # Attach menu bar to layout

        # Recent Files Menu
        self.recent_menu = QMenu("Recent", self)
        menu_bar.addMenu(self.recent_menu)
        self.update_recent_files_menu()

        # View Menu
        view_menu = QMenu("View", self)
        self.menu_bar = menu_bar  
        self.view_menu_action = self.menu_bar.addMenu(view_menu)
        
        # create overlay badge for the View menu
        importance_count = int(getattr(self, "log_counters", {}).get("Importance", 0))
        self.view_badge = QLabel(str(importance_count) if importance_count > 0 else "", self.menu_bar)
        self.view_badge.setObjectName("ViewBadge")
        self.view_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_badge.setStyleSheet(
            "QLabel#ViewBadge { background-color: #d32f2f; color: white; "
            "border-radius: 8px; min-width: 16px; max-height: 16px; "
            "font-size: 10px; font-weight: bold; padding: 0px 4px; }"
        )
        if importance_count <= 0:
            self.view_badge.hide()
        else:
            self.view_badge.show()
        self.view_badge.adjustSize()
        QTimer.singleShot(0, self.position_view_badge)
        
        self.important_action = QAction(f"Important ({importance_count})", self)
        self.important_action.setCheckable(True)
        self.important_action.triggered.connect(self.toggle_view_important)
        view_menu.addAction(self.important_action)

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
        dialog.setFixedSize(360, 380)
        # Keep this dialog readable regardless of the viewer theme.
        dialog.setStyleSheet("""
            QDialog { background-color: #f5f5f5; color: #111111; }
            QLabel, QCheckBox { color: #111111; }
            QPushButton { padding: 6px; }
        """)

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
        
        initial_preset = self.DEFAULT_VIEWER_DARK_PRESET if dark_mode_input.isChecked() else self.DEFAULT_VIEWER_PREFERENCES
        background_color = {"value": getattr(self, "viewer_background_color", initial_preset["viewer_background_color"])}
        background_button = QPushButton("Background Color")
        self._set_preview_button_color(background_button, background_color["value"])
        background_button.setEnabled(not dark_mode_input.isChecked())
        layout.addWidget(background_button)

        selected_color = {"value": getattr(self, "viewer_colored_selection_color", "#d6eaff")}
        color_button = QPushButton("Selected Highlight Color")
        color_button.setEnabled(selection_mode_input.currentText() == "Choose Color")
        self._set_preview_button_color(color_button, selected_color["value"])
        layout.addWidget(color_button)

        accent_color = {"value": getattr(self, "viewer_selection_accent_color", initial_preset.get("viewer_selection_accent_color", "#2196F3"))}
        accent_button = QPushButton("Selection Border Accent Color")
        self._set_preview_button_color(accent_button, accent_color["value"])
        layout.addWidget(accent_button)
        
        hover_color = {"value": getattr(self, "viewer_hover_color", initial_preset["viewer_hover_color"])}
        hover_button = QPushButton("Hover Color")
        self._set_preview_button_color(hover_button, hover_color["value"])
        layout.addWidget(hover_button)

        def choose_selection_color():
            color = QColorDialog.getColor(QColor(selected_color["value"]), dialog)
            if color.isValid():
                selected_color["value"] = color.name()
                self._set_preview_button_color(color_button, selected_color["value"])

        def choose_accent_color():
            color = QColorDialog.getColor(QColor(accent_color["value"]), dialog)
            if color.isValid():
                accent_color["value"] = color.name()
                self._set_preview_button_color(accent_button, accent_color["value"])
        
        def choose_background_color():
            color = QColorDialog.getColor(QColor(background_color["value"]), dialog)
            if color.isValid():
                background_color["value"] = color.name()
                self._set_preview_button_color(background_button, background_color["value"])

        def choose_hover_color():
            color = QColorDialog.getColor(QColor(hover_color["value"]), dialog)
            if color.isValid():
                hover_color["value"] = color.name()
                self._set_preview_button_color(hover_button, hover_color["value"])
        def update_selection_color_enabled(text):
            color_button.setEnabled(text == "Choose Color")

        def set_background_button_enabled():
            background_button.setEnabled(not dark_mode_input.isChecked())

        def reset_colors_to_mode_preset(checked):
            # Treat the checkbox toggle as a reset-to-preset switch.
            preset = self.DEFAULT_VIEWER_DARK_PRESET if checked else self.DEFAULT_VIEWER_PREFERENCES
            background_color["value"] = preset["viewer_background_color"]
            hover_color["value"] = preset["viewer_hover_color"]
            accent_color["value"] = preset.get("viewer_selection_accent_color", accent_color["value"])

            # Only reset selection highlight when user is in custom mode (it's the most visible impact)
            if selection_mode_input.currentText() == "Choose Color":
                selected_color["value"] = preset.get("viewer_colored_selection_color", selected_color["value"])

            self._set_preview_button_color(background_button, background_color["value"])
            self._set_preview_button_color(hover_button, hover_color["value"])
            self._set_preview_button_color(accent_button, accent_color["value"])
            self._set_preview_button_color(color_button, selected_color["value"])
            set_background_button_enabled()

        selection_mode_input.currentTextChanged.connect(update_selection_color_enabled)
        dark_mode_input.stateChanged.connect(reset_colors_to_mode_preset)
        set_background_button_enabled()
        background_button.clicked.connect(choose_background_color)
        color_button.clicked.connect(choose_selection_color)
        accent_button.clicked.connect(choose_accent_color)
        hover_button.clicked.connect(choose_hover_color)
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
            self.viewer_background_color = background_color["value"]
            self.viewer_hover_color = hover_color["value"]
            self.save_user_config()
            if hasattr(self, "logs_viewer") and self.logs_viewer:
                self.logs_viewer.apply_viewer_theme()
                self.logs_viewer.refresh_logs()
            dialog.accept()

        save_button.clicked.connect(save_preferences)
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec()

    def open_editor_playground(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Editor's Playground")
        dialog.setFixedSize(360, 320)
        # Keep this dialog readable regardless of the main UI theme.
        dialog.setStyleSheet("""
            QDialog { background-color: #f5f5f5; color: #111111; }
            QLabel, QCheckBox { color: #111111; }
            QPushButton { padding: 6px; }
        """)

        layout = QVBoxLayout(dialog)

        dark_mode_input = QCheckBox("Dark mode")
        dark_mode_input.setChecked(bool(getattr(self, "editor_dark_mode", False)))
        layout.addWidget(dark_mode_input)

        initial_preset = self.DEFAULT_EDITOR_DARK_PRESET if dark_mode_input.isChecked() else self.DEFAULT_EDITOR_PREFERENCES

        editor_background = {"value": getattr(self, "editor_background_color", initial_preset["editor_background_color"])}
        editor_background_button = QPushButton("Custom background (editor)")
        self._set_preview_button_color(editor_background_button, editor_background["value"])
        editor_background_button.setEnabled(True)
        layout.addWidget(editor_background_button)

        body_background = {"value": getattr(self, "editor_body_background_color", initial_preset["editor_body_background_color"])}
        body_background_button = QPushButton("Custom background (body)")
        self._set_preview_button_color(body_background_button, body_background["value"])
        body_background_button.setEnabled(not dark_mode_input.isChecked())
        layout.addWidget(body_background_button)

        button_foreground = {"value": getattr(self, "editor_button_foreground_color", initial_preset["editor_button_foreground_color"])}
        button_foreground_button = QPushButton("Buttons foreground")
        self._set_preview_button_color(button_foreground_button, button_foreground["value"])
        button_foreground_button.setEnabled(True)
        layout.addWidget(button_foreground_button)

        button_background = {"value": getattr(self, "editor_button_background_color", initial_preset["editor_button_background_color"])}
        button_background_button = QPushButton("Buttons background")
        self._set_preview_button_color(button_background_button, button_background["value"])
        button_background_button.setEnabled(True)
        layout.addWidget(button_background_button)

        hover_color = {"value": getattr(self, "editor_hover_color", initial_preset.get("editor_hover_color", self.DEFAULT_EDITOR_PREFERENCES["editor_hover_color"]))}
        hover_button = QPushButton("Hover")
        self._set_preview_button_color(hover_button, hover_color["value"])
        hover_button.setEnabled(True)
        layout.addWidget(hover_button)

        importance_color = {"value": getattr(self, "important_accent_color", self.DEFAULT_LOG_THEME_COLORS["important_accent_color"])}
        importance_button = QPushButton("Importance color")
        self._set_preview_button_color(importance_button, importance_color["value"])
        importance_button.setEnabled(True)
        layout.addWidget(importance_button)

        categories_button = QPushButton("Categories")
        layout.addWidget(categories_button)

        def choose_editor_background():
            color = QColorDialog.getColor(QColor(editor_background["value"]), dialog)
            if color.isValid():
                editor_background["value"] = color.name()
                self._set_preview_button_color(editor_background_button, editor_background["value"])

        def choose_body_background():
            color = QColorDialog.getColor(QColor(body_background["value"]), dialog)
            if color.isValid():
                body_background["value"] = color.name()
                self._set_preview_button_color(body_background_button, body_background["value"])

        def choose_button_foreground():
            color = QColorDialog.getColor(QColor(button_foreground["value"]), dialog)
            if color.isValid():
                button_foreground["value"] = color.name()
                self._set_preview_button_color(button_foreground_button, button_foreground["value"])

        def choose_button_background():
            color = QColorDialog.getColor(QColor(button_background["value"]), dialog)
            if color.isValid():
                button_background["value"] = color.name()
                self._set_preview_button_color(button_background_button, button_background["value"])

        def choose_hover_color():
            color = QColorDialog.getColor(QColor(hover_color["value"]), dialog)
            if color.isValid():
                hover_color["value"] = color.name()
                self._set_preview_button_color(hover_button, hover_color["value"])

        def choose_importance_color():
            color = QColorDialog.getColor(QColor(importance_color["value"]), dialog)
            if color.isValid():
                importance_color["value"] = color.name()
                self._set_preview_button_color(importance_button, importance_color["value"])

        def set_body_button_enabled():
            body_background_button.setEnabled(not dark_mode_input.isChecked())

        def reset_colors_to_mode_preset(checked):
            # Treat the checkbox toggle as a reset-to-preset switch.
            preset = self.DEFAULT_EDITOR_DARK_PRESET if checked else self.DEFAULT_EDITOR_PREFERENCES
            editor_background["value"] = preset["editor_background_color"]
            body_background["value"] = preset["editor_body_background_color"]
            button_foreground["value"] = preset["editor_button_foreground_color"]
            button_background["value"] = preset["editor_button_background_color"]
            hover_color["value"] = preset.get("editor_hover_color", self.DEFAULT_EDITOR_PREFERENCES["editor_hover_color"])

            self._set_preview_button_color(editor_background_button, editor_background["value"])
            self._set_preview_button_color(body_background_button, body_background["value"])
            self._set_preview_button_color(button_foreground_button, button_foreground["value"])
            self._set_preview_button_color(button_background_button, button_background["value"])
            self._set_preview_button_color(hover_button, hover_color["value"])
            set_body_button_enabled()

        dark_mode_input.stateChanged.connect(reset_colors_to_mode_preset)
        set_body_button_enabled()
        editor_background_button.clicked.connect(choose_editor_background)
        body_background_button.clicked.connect(choose_body_background)
        button_foreground_button.clicked.connect(choose_button_foreground)
        button_background_button.clicked.connect(choose_button_background)
        hover_button.clicked.connect(choose_hover_color)
        importance_button.clicked.connect(choose_importance_color)
        categories_button.clicked.connect(self.open_editor_categories)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def save_editor_preferences():
            self.editor_dark_mode = dark_mode_input.isChecked()
            self.editor_background_color = editor_background["value"]
            self.editor_body_background_color = body_background["value"]
            self.editor_button_foreground_color = button_foreground["value"]
            self.editor_button_background_color = button_background["value"]
            self.editor_hover_color = hover_color["value"]
            self.important_accent_color = importance_color["value"]
            self.save_user_config()
            self.apply_editor_theme()
            self.refresh_log_label_styles()
            dialog.accept()

        save_button.clicked.connect(save_editor_preferences)
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec()

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
        self.setObjectName("LogAppRoot")
        # set window title to current file
        self.setWindowTitle(self.fileName)
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
        self.refresh_category_selector()

        layout.addLayout(combo_layout)

        button_layout = QHBoxLayout()

        self.add_log_button = QPushButton("Add Log", self)
        self.add_log_button.clicked.connect(self.add_log)
        button_layout.addWidget(self.add_log_button)

        self.clear_logs_button = QPushButton("Clear Logs", self)
        self.clear_logs_button.clicked.connect(self.clear_logs)
        button_layout.addWidget(self.clear_logs_button)

        layout.addLayout(button_layout)

        self.log_list = LogListWidget(self)
        self.editor_selected_log_label = None
        # allow this widget to forward events to LogApp.eventFilter
        self.log_list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.log_list.installEventFilter(self)
        self.log_list.viewport().installEventFilter(self)
        # allow horizontal scrollbar when needed
        self.log_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.log_list.itemDoubleClicked.connect(self.edit_log)
        self.log_list.currentItemChanged.connect(self.on_editor_log_selection_changed)

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
        self.apply_editor_theme()

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

            cat_cfg = self._current_category_config() or {}
            category_id = str(cat_cfg.get("id", "")).strip() or "unknown"
            category_icon = str(cat_cfg.get("icon", "")).strip()
            category_bg = str(cat_cfg.get("background", "transparent"))
            category_fg = str(cat_cfg.get("foreground", "#111111"))
            icon_color = category_fg

            # Auto-increment counter for the selected category.
            # Ensure missing keys from older counter files are created on the fly.
            if category_id not in self.log_counters:
                self.log_counters[category_id] = 0
            self.log_counters[category_id] += 1
            log_number = f" #{self.log_counters[category_id]}"

            if self.log_type == "Debugging":
                memory_usage = self.get_system_info()
                cpu_usage = self.cpu_usage
                gpu_usage = self.gpu_usage
                additional_info = f" - {memory_usage}, {cpu_usage}, {gpu_usage}"
            elif self.log_type == "General" and self.user_name:
                additional_info = f" - User: {self.user_name}"

            # Category foreground drives the log entry foreground (viewer/editor will still render rich text).
            main_text_color = category_fg

            # Format the log text using format_text
            formatted_log_text = self.format_text(log_text)

            # Create the log entry with HTML formatting
            style_marker = self._category_style_marker(category_id, category_bg, category_fg)
            log_entry = (
                f"{style_marker}"
                f'<span style="color:{icon_color};">{category_icon}</span> '
                f'<span style="color:{main_text_color};">{timestamp} [{self.log_type}] {formatted_log_text}{additional_info}{log_number}</span>'
            )

            # Create a QLabel to render the rich text
            label = EditorLogLabel()
            self.configure_log_label(label, log_entry, word_wrap=False)
            label.setSizePolicy(label.sizePolicy().horizontalPolicy(), label.sizePolicy().verticalPolicy())

            # Add the QLabel to the QListWidget
            item = QListWidgetItem()
            # Set the item background from the category so hover/selection shows through
            try:
                if category_bg and str(category_bg).strip().lower() != "transparent":
                    item.setBackground(QBrush(QColor(category_bg)))
                else:
                    item.setBackground(QBrush())
            except Exception:
                pass
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
            self.reapply_active_filter()

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
            prefix_match = re.match(r"^\s*(\S*)\s*(\[[^\]]+\]\s*\[[^\]]+\])\s*", current_text)
            prefix_text = ""
            editable_text = current_text.strip()
            if prefix_match:
                icon_text = (prefix_match.group(1) or "").strip()
                header_text = (prefix_match.group(2) or "").strip()
                prefix_text = f"{icon_text} {header_text}".strip()
                editable_text = current_text[prefix_match.end():].strip()
            editable_text = re.sub(r"\s+\|\s+\[[^\]]+\].*$", "", editable_text).strip()
            editable_text = re.sub(r"\s*-\s*User:.*?(#\d+\s*)?$", "", editable_text).strip()
            editable_text = re.sub(r"\s+#\d+\s*$", "", editable_text).strip()

            # Open a dialog pre-filled with the current log text
            plain_text, ok = prompt_log_content_input(self, "Edit Log", prefix_text or "Log header", text=editable_text)
            if ok and plain_text.strip():
                status_date = datetime.now().strftime("[%Y-%m-%d %H:%M:%SH]")
                existing_html = label.text()
                marker = self._parse_category_style_marker(existing_html) or {}
                marker_category_id = str(marker.get("id", "")).strip()
                cat_cfg = self._category_config_by_id(marker_category_id) if marker_category_id else None
                if not cat_cfg:
                    cat_cfg = self._current_category_config() or {}
                category_id = str(cat_cfg.get("id", "")).strip() or marker_category_id or "unknown"
                category_icon = str(cat_cfg.get("icon", "")).strip()
                category_bg = str(cat_cfg.get("background", "transparent"))
                category_fg = str(cat_cfg.get("foreground", "#111111"))
                icon_color = category_fg
                main_text_color = category_fg

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

                style_marker = self._category_style_marker(category_id, category_bg, category_fg)
                preserved_prefix = prefix_text or f"{category_icon} [{datetime.now().strftime('%Y-%m-%d %H:%M:%SH')}] [{self.log_type}]"
                updated_text = (
                    f"{style_marker}"
                    f'<span style="color:{icon_color};">{category_icon}</span> '
                    f'<span style="color:{main_text_color};">{preserved_prefix[len(category_icon):].strip()} {plain_text}{status_suffix}</span>'
                )
                # Update the existing label with the new rich text
                updated_text = self.set_importance_marker(updated_text, self.is_important_log(existing_html))
                self.configure_log_label(label, updated_text, word_wrap=False)
                # update the corresponding item's background to match new content
                try:
                    row = self.log_list.row(item)
                    list_item = self.log_list.item(row)
                    if list_item:
                        bg = self.get_log_background_color(updated_text)
                        if isinstance(bg, str) and bg.strip() and bg.strip().lower() != "transparent":
                            list_item.setBackground(QBrush(QColor(bg)))
                        else:
                            list_item.setBackground(QBrush())
                except Exception:
                    pass
                row = self.log_list.row(item)
                self.logEdited.emit(row)
                self.reapply_active_filter()
                # No need to re-add the widget or duplicate it; this updates the current item.
            elif not plain_text.strip():
                show_neutral_message_box(
                    self,
                    QMessageBox.Icon.Warning,
                    "Invalid Input",
                    "Log entry cannot be empty.",
                    QMessageBox.StandardButton.Ok,
                )

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

        self.setWindowTitle(f"{self.fileName} - File saved")  # Update title
        QTimer.singleShot(2000, lambda: self.setWindowTitle(f"{self.fileName}"))   # Reset after 2 seconds

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
        self.apply_editor_theme()

        # Use project folder and config subfolder
        project_folder = os.path.dirname(file_path)
        config_folder = os.path.join(project_folder, "config")

        # Load log counters
        counters_path = os.path.join(config_folder, "counters.json")
        if os.path.exists(counters_path):
            try:
                with open(counters_path, "r", encoding="utf-8") as f:
                    loaded_counters = json.load(f)
                    # New format: ordered list of {id, count, ...}
                    if isinstance(loaded_counters, list):
                        self.log_counters = {}
                        for item in loaded_counters:
                            if not isinstance(item, dict):
                                continue
                            cid = str(item.get("id", "")).strip()
                            if not cid:
                                continue
                            try:
                                self.log_counters[cid] = int(item.get("count", 0))
                            except Exception:
                                self.log_counters[cid] = 0
                    # Old format: dict keyed by display name
                    elif isinstance(loaded_counters, dict):
                        self.log_counters = {}
                        # migrate by matching category name (ignoring icon changes)
                        self._ensure_editor_categories()
                        by_name = {str(c.get("category", "")).strip(): str(c.get("id", "")).strip() for c in getattr(self, "editor_categories", [])}
                        for k, v in loaded_counters.items():
                            name = str(k).strip()
                            # if key looks like "Name ICON", strip icon part
                            if name and len(name) >= 2 and name[-2] == " ":
                                name = name[:-2]
                            cid = by_name.get(name)
                            if not cid:
                                continue
                            try:
                                self.log_counters[cid] = int(v)
                            except Exception:
                                self.log_counters[cid] = 0
                    else:
                        self.log_counters = {}
            except Exception as e:
                print(f"Error loading log counters: {e}")
                self.log_counters = {}
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
            apply_neutral_dialog_style(progress_dialog)
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
                    self._load_was_canceled = True
                    # cleanup partially-loaded state
                    self.log_list.clear()
                    self.current_file = None
                    progress_dialog.close()
                    box = QMessageBox(self)
                    box.setIcon(QMessageBox.Icon.Information)
                    box.setWindowTitle("Loading Cancelled")
                    box.setText("The loading process has been cancelled.")
                    box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    apply_neutral_dialog_style(box)
                    box.exec()
                    print("Loading canceled by user.")

                    # close auxiliary viewers if open
                    try:
                        if hasattr(self, "logs_viewer") and self.logs_viewer:
                            self.logs_viewer.close()
                    except Exception:
                        pass
                    
                    return
                
                line = line.strip()

                if line:  # Ensure the line is not empty

                    # Create a QLabel and set the saved HTML content
                    label = EditorLogLabel()
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
            self.normalize_logs_to_categories_and_rebuild_counters()
            self.reapply_active_filter()
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
        # Wheel events on the list viewport -> horizontal if Shift held, otherwise vertical
        if getattr(self, "log_list", None) and source is self.log_list.viewport() and event.type() == QEvent.Type.Wheel:
            dx = event.angleDelta().x()
            dy = event.angleDelta().y()
            delta = dx if dx != 0 else dy
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                h = self.log_list.horizontalScrollBar()
                h.setValue(h.value() - (delta // 8))
            else:
                v = self.log_list.verticalScrollBar()
                v.setValue(v.value() - (dy // 8))
            event.accept()
            return True
    
        # Left/Right arrow keys when the list has focus -> scroll horizontally
        if getattr(self, "log_list", None) and source is self.log_list and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Left:
                h = self.log_list.horizontalScrollBar()
                h.setValue(h.value() - (h.singleStep() or 20))
                event.accept()
                return True
            if event.key() == Qt.Key.Key_Right:
                h = self.log_list.horizontalScrollBar()
                h.setValue(h.value() + (h.singleStep() or 20))
                event.accept()
                return True
                
        if source == self.log_input and event.type() == QEvent.Type.KeyPress:
            # Debug: print key code and modifiers
            print("Key pressed in log_input:", event.key(), event.modifiers())
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                print("Shift+Enter detected via eventFilter")
                self.add_log()
                return True  # Consume the event
        return super().eventFilter(source, event)

    def show_context_menu(self, pos: QPoint):
        self.show_context_menu_at_global_pos(self.log_list.viewport().mapToGlobal(pos))

    def show_context_menu_at_global_pos(self, global_pos: QPoint):
        scroll_state = self._capture_log_list_scroll()
        try:
            item = self.log_list.itemAt(self.log_list.viewport().mapFromGlobal(global_pos))
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
                
                action = menu.exec(global_pos)
                
                if action is None:
                    return  # Exit function without doing anything

                if action == delete_action:
                    row = self.log_list.row(item)
                    self.log_list.takeItem(row)
                    self.logDeleted.emit(row)  # Emit signal
                    self.reapply_active_filter()
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
        finally:
            self._restore_log_list_scroll(scroll_state)
            QTimer.singleShot(0, lambda state=scroll_state: self._restore_log_list_scroll(state))

    def _should_preserve_log_scroll(self):
        return bool(getattr(self, "active_filter", None) or getattr(self, "important_filter_active", False))

    def _begin_log_scroll_guard(self, delay_ms=250):
        if not hasattr(self, "log_list") or not self.log_list:
            return
        if not self._should_preserve_log_scroll():
            return
        self.log_list._suppress_auto_scroll = True
        guard_token = getattr(self, "_log_scroll_guard_token", 0) + 1
        self._log_scroll_guard_token = guard_token

        def clear_guard(token=guard_token):
            if getattr(self, "_log_scroll_guard_token", 0) == token and hasattr(self, "log_list") and self.log_list:
                self.log_list._suppress_auto_scroll = False

        QTimer.singleShot(delay_ms, clear_guard)

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
        self.reapply_active_filter()

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
                solution_text, ok = prompt_text_input(self, "Add Solution", f"Enter solution for Problem #{problem_number}:")
                if ok and solution_text.strip():
                    # Add the solution log
                    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%SH]")
                    solution_entry = (
                        f'<span style="color:yellow;">■</span> '
                        f'<span style="color:black;">{timestamp} [General] {solution_text.strip()} - Solution #{problem_number}</span>'
                    )
                    solution_label = EditorLogLabel()
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
                    self.reapply_active_filter()

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
            self.unsaved_changes = False
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
            self.setWindowTitle(f"{self.fileName} - Auto-saved")  # Update title
            QTimer.singleShot(8000, lambda: self.setWindowTitle(f"{self.fileName}"))  # Reset after 2 seconds
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
                "viewer_background_color": getattr(self, "viewer_background_color", self.DEFAULT_VIEWER_PREFERENCES["viewer_background_color"]),
                "viewer_hover_color": getattr(self, "viewer_hover_color", self.DEFAULT_VIEWER_PREFERENCES["viewer_hover_color"]),
                "editor_dark_mode": getattr(self, "editor_dark_mode", self.DEFAULT_EDITOR_PREFERENCES["editor_dark_mode"]),
                "editor_background_color": getattr(self, "editor_background_color", self.DEFAULT_EDITOR_PREFERENCES["editor_background_color"]),
                "editor_body_background_color": getattr(self, "editor_body_background_color", self.DEFAULT_EDITOR_PREFERENCES["editor_body_background_color"]),
                "editor_button_foreground_color": getattr(self, "editor_button_foreground_color", self.DEFAULT_EDITOR_PREFERENCES["editor_button_foreground_color"]),
                "editor_button_background_color": getattr(self, "editor_button_background_color", self.DEFAULT_EDITOR_PREFERENCES["editor_button_background_color"]),
                "editor_hover_color": getattr(self, "editor_hover_color", self.DEFAULT_EDITOR_PREFERENCES["editor_hover_color"]),
                "editor_categories": getattr(self, "editor_categories", list(self.DEFAULT_EDITOR_CATEGORIES)),
                "editor_categories_default": getattr(self, "editor_categories_default", list(self.DEFAULT_EDITOR_CATEGORIES)),
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
            for key, default_value in self.DEFAULT_EDITOR_PREFERENCES.items():
                settings.setValue(key, getattr(self, key, default_value))
            settings.setValue("editor_categories", getattr(self, "editor_categories", list(self.DEFAULT_EDITOR_CATEGORIES)))
            settings.setValue("editor_categories_default", getattr(self, "editor_categories_default", list(self.DEFAULT_EDITOR_CATEGORIES)))
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
                    for key, default_value in self.DEFAULT_EDITOR_PREFERENCES.items():
                        setattr(self, key, data.get(key, default_value))
                    self.editor_categories_default = data.get("editor_categories_default", list(self.DEFAULT_EDITOR_CATEGORIES))
                    self.editor_categories = data.get("editor_categories", list(self.editor_categories_default))
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
        for key, default_value in self.DEFAULT_EDITOR_PREFERENCES.items():
            value = settings.value(key, default_value)
            if isinstance(default_value, bool):
                value = value in (True, "true", "True", "1", 1)
            setattr(self, key, value)
        categories_value = settings.value("editor_categories", None)
        if categories_value is None:
            self.editor_categories = list(self.DEFAULT_EDITOR_CATEGORIES)
        else:
            # QSettings may store as string; keep it resilient.
            if isinstance(categories_value, str):
                try:
                    self.editor_categories = json.loads(categories_value)
                except Exception:
                    self.editor_categories = list(self.DEFAULT_EDITOR_CATEGORIES)
            else:
                self.editor_categories = categories_value

        categories_default_value = settings.value("editor_categories_default", None)
        if categories_default_value is None:
            self.editor_categories_default = list(self.DEFAULT_EDITOR_CATEGORIES)
        else:
            if isinstance(categories_default_value, str):
                try:
                    self.editor_categories_default = json.loads(categories_default_value)
                except Exception:
                    self.editor_categories_default = list(self.DEFAULT_EDITOR_CATEGORIES)
            else:
                self.editor_categories_default = categories_default_value

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
            self.reapply_active_filter()

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
            label = EditorLogLabel()
            self.configure_log_label(label, log, word_wrap=False)

            item = QListWidgetItem()
            self.log_list.addItem(item)
            self.log_list.setItemWidget(item, label)

    def create_restore_point(self):
        """Save the current logs as a restore point with a timestamped name."""
        version_name, ok = prompt_text_input(self, "Create Restore Point", "Enter a version name:")

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
            label = EditorLogLabel()
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
        # Open the DictionaryDialog and update keyword definitions
        if self.current_file:
            project_folder = os.path.dirname(self.current_file)
            config_folder = get_config_dir(project_folder)
        else:
            config_folder = get_config_dir()

        self.dictionary_dialog = DictionaryDialog(self, config_folder=config_folder)
        # Sync LogApp's keyword data with what was loaded from disk
        self.keyword_definitions = self.dictionary_dialog.dictionary
        self.keyword_images = self.dictionary_dialog.keyword_images

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
        dialog = FilterDialog(self, self.get_filterable_category_options())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            start_date, end_date, log_types = dialog.get_filters()
            self.filter_logs(start_date, end_date, log_types)

    def filter_logs(self, start_date, end_date, log_types):
        """Store filter settings.

        Args:
            start_date: Start date string (yyyy-MM-dd)
            end_date: End date string (yyyy-MM-dd)
            log_types: List of selected category names (e.g., ["Problem ★", "Bug ▲"])
        """
        self.active_filter = {
            "start_date": start_date,
            "end_date": end_date,
            "categories": log_types,  # Store as list
        }
        self.reapply_all_filters()

    def clear_filter_preferences(self):
        # Clear saved filter preferences from config
        try:
            settings = QSettings("LDS", "LogApp")
            settings.remove("filter/checked_categories")
        except Exception:
            pass
    
    def clear_filters(self):
        # Reset filtering to show all logs
        self.active_filter = None

        # Also reset filter preferences if a FilterDialog instance exists
        # This ensures next time the dialog opens, it shows defaults
        try:
            settings = QSettings("LDS", "LogApp")
            settings.remove("filter/checked_categories")
        except Exception:
            pass
        
        self.reapply_all_filters()
    
    def load_and_apply_saved_filters(self):
        # Load and apply saved filter preferences on app initialization
        try:
            settings = QSettings("LDS", "LogApp")
            checked_categories = settings.value("filter/checked_categories", [])

            # Only apply filters if categories were previously saved
            if checked_categories:
                # Use default date range (all time)
                start_date = QDate.currentDate().addDays(-70000).toString("yyyy-MM-dd")
                end_date = QDate.currentDate().toString("yyyy-MM-dd")

                # Apply the saved filters
                self.filter_logs(start_date, end_date, checked_categories)
        except Exception:
            # If anything fails, just continue without filters
            pass

    def reapply_active_filter(self):
        self.reapply_all_filters()

    def reapply_all_filters(self):
        # Reapply all active filters (date range, categories, importance)
        if not hasattr(self, "log_list") or not self.log_list:
            return

        if not self._should_preserve_log_scroll():
            self.editor_selected_log_label = None

        vertical_scrollbar = self.log_list.verticalScrollBar()
        horizontal_scrollbar = self.log_list.horizontalScrollBar()
        previous_vertical = vertical_scrollbar.value() if vertical_scrollbar else None
        previous_horizontal = horizontal_scrollbar.value() if horizontal_scrollbar else None

        start_date = None
        end_date = None
        category_filters = []  # Now a list

        if self.active_filter:
            start_date = QDate.fromString(self.active_filter.get("start_date", ""), "yyyy-MM-dd")
            end_date = QDate.fromString(self.active_filter.get("end_date", ""), "yyyy-MM-dd")
            category_filters = self.active_filter.get("categories", [])  # Get as list
            if not start_date.isValid():
                start_date = None
            if not end_date.isValid():
                end_date = None

        for i in range(self.log_list.count()):
            item = self.log_list.item(i)
            label = self.log_list.itemWidget(item)
            if not isinstance(label, QLabel):
                continue

            visible = True
            plain_text = self.strip_html(label.text())

            # Date range filter
            if start_date and end_date:
                date_match = re.search(r"\[(\d{4}-\d{2}-\d{2})", plain_text)
                if date_match:
                    log_date = QDate.fromString(date_match.group(1), "yyyy-MM-dd")
                    visible = start_date <= log_date <= end_date
                else:
                    visible = False

            # Category filter (check if log's category is in the selected list)
            if visible and category_filters:  # If any categories are selected
                marker = self._parse_category_style_marker(label.text()) or {}
                marker_category_id = str(marker.get("id", "")).strip()
                cfg = self._category_config_by_id(marker_category_id) if marker_category_id else None
                if cfg:
                    category_name = str(cfg.get("category", "")).strip()
                    icon = str(cfg.get("icon", "")).strip()
                    current_label = f"{category_name} {icon}".strip()
                    # Check if current log category is in the selected categories
                    visible = current_label in category_filters
                else:
                    visible = False

            # Importance filter
            if visible and self.important_filter_active:
                visible = self.is_important_log(label.text())

            item.setHidden(not visible)

        if vertical_scrollbar and previous_vertical is not None:
            vertical_scrollbar.setValue(previous_vertical)
        if horizontal_scrollbar and previous_horizontal is not None:
            horizontal_scrollbar.setValue(previous_horizontal)
        self.filterChanged.emit()

    def strip_html(self, html_text):
        doc = QTextDocument()
        doc.setHtml(html_text)
        return doc.toPlainText()

    def save_log_counters(self):
        """Save the log counters to a JSON file in the config folder."""
        if self.current_file:
            self._ensure_editor_categories()
            project_folder = os.path.dirname(self.current_file)
            config_folder = os.path.join(project_folder, "config")
            os.makedirs(config_folder, exist_ok=True)
            json_file = os.path.join(config_folder, "counters.json")
            try:
                # Keep counters 1:1 and ordered like categories.
                ordered = []
                for c in getattr(self, "editor_categories", []):
                    cid = str(c.get("id", "")).strip()
                    if not cid:
                        continue
                    ordered.append(
                        {
                            "id": cid,
                            "category": str(c.get("category", "")),
                            "icon": str(c.get("icon", "")),
                            "count": int(self.log_counters.get(cid, 0)),
                        }
                    )
                with open(json_file, "w", encoding="utf-8") as json_out:
                    json.dump(ordered, json_out, indent=4)
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




