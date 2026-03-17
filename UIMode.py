import os
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"

from functools import partial

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QSizePolicy, QApplication, QScrollArea, QStackedLayout,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QColorDialog,
    QToolButton, QMenu, QDialog, QSlider, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QLineEdit,
)
from PyQt6.QtCore import (
    Qt, QSize, QPropertyAnimation, QRect,
    QPoint, QEasingCurve, QTimer, pyqtSignal, QEvent,
    QParallelAnimationGroup, QEventLoop, QRectF, QPointF
    )

from PyQt6.QtCore import pyqtProperty

from PyQt6.QtGui import (
    QIcon, QPainter, QPen, QColor, QMouseEvent,
    QCursor, QFont, QColor, QPixmap, QClipboard, QAction, QBrush, QImage
    )
import sys
import math
import json
import base64, json
from io import BytesIO
from datetime import datetime
from pathlib import Path


TOOL_MENU = [
    {
        "type": "category", "name": "shapes", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-shapes.png", "children": [
            {"type": "tool", "name": "circle", "icon": "◯"},
            {"type": "tool", "name": "rect", "icon": "▭"},
            {"type": "tool", "name": "triangle", "icon": "△"},
            {"type": "tool", "name": "line", "icon": "—"},
            {"type": "tool", "name": "cross", "icon": "✕"},
            {"type": "tool", "name": "roundrect", "icon": "⬭"},
        ]
    },
    {
        "type": "category", "name": "colors", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-colors.png", "children": [
            {"type": "tool", "name": "fill", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-colors-fill.png", "icon_size": 66},
            {"type": "tool", "name": "crop", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-colors-crop.png", "icon_size": 66},
            {"type": "tool", "name": "eraser", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-colors-eraser.png", "icon_size": 66},
            {"type": "tool", "name": "draw", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-colors-paint.png", "icon_size": 66},
        ]
    },
    {
        "type": "category", "name": "label", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-label.png", "icon_size": 250, "children": [
            {"type": "tool", "name": "label", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-label-label.png", "icon_size": 96},
            {"type": "tool", "name": "arrow", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-label-arrows.png", "icon_size": 96},
            {"type": "tool", "name": "framewithlabel", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-label-rectwithlabel.png", "icon_size": 90},
            {"type": "tool", "name": "roundframewithlabel", "icon": r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-label-roundedrectwithlabel.png", "icon_size": 90},
        ]
    },
]

CUSTOM_BORDER_COLOR = "#ffffff"
CUSTOM_OBJECT_COLOR = "#ffffff"


class SideMenuPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: white; border-left: 1px solid #ddd;")
        self.setFixedWidth(275)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab bar
        tab_row = QHBoxLayout()
        tab_row.setContentsMargins(0, 0, 0, 0)
        tab_row.setSpacing(0)
        self._tabs = {}
        self._tab_contents = {}
        for name in ["File", "Pages", "History"]:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            tab_row.addWidget(btn)
            self._tabs[name] = btn

        tab_widget = QWidget()
        tab_widget.setLayout(tab_row)
        layout.addWidget(tab_widget)

        # Stacked content
        from PyQt6.QtWidgets import QStackedWidget
        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        # File page
        file_page = QWidget()
        file_layout = QVBoxLayout(file_page)
        file_layout.setContentsMargins(0, 8, 0, 8)
        file_layout.setSpacing(0)
        self.file_actions = {}
        for item in ["Open", "Save", "Save As", "Export", "Settings", "Hotkeys", "Exit"]:
            lbl = QPushButton(item)
            lbl.setFlat(True)
            lbl.setFixedHeight(38)
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            file_layout.addWidget(lbl)
            self.file_actions[item] = lbl
        file_layout.addStretch()
        self._stack.addWidget(file_page)

        # Pages page (placeholder)
        pages_page = QWidget()
        pages_layout = QVBoxLayout(pages_page)
        pages_layout.addWidget(QLabel("Pages coming soon"))
        pages_layout.addStretch()
        self._stack.addWidget(pages_page)

        # History page with accordion-style toggle
        history_page = QWidget()
        history_layout = QVBoxLayout(history_page)
        history_layout.setContentsMargins(0, 8, 0, 0)
        history_layout.setSpacing(8)

        # Create Checkpoint button (always visible)
        create_btn = QPushButton("Create Checkpoint")
        create_btn.setFixedHeight(40)
        create_btn.setStyleSheet("""
            QPushButton {
                background: #ff6600; color: white; border: none;
                font-weight: bold; border-radius: 4px; font-size: 11pt; margin: 0 8px;
            }
            QPushButton:hover { background: #e55a00; }
        """)
        self.create_checkpoint_btn = create_btn
        history_layout.addWidget(create_btn)

        # File History header button (always visible, toggles expansion)
        file_history_btn = QPushButton("File History ▶")
        file_history_btn.setFlat(True)
        file_history_btn.setFixedHeight(32)
        file_history_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #222; border: none;
                font-weight: bold; font-size: 12pt; text-align: left; padding-left: 8px;
            }
            QPushButton:hover { color: #ff6600; }
        """)
        file_history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.file_history_btn = file_history_btn
        self._history_expanded = False
        history_layout.addWidget(file_history_btn)

        # Scroll area for checkpoints (collapsible)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; margin: 0 8px; }")
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setMaximumHeight(200)

        self.checkpoint_list_widget = QWidget()
        self.checkpoint_list_layout = QVBoxLayout(self.checkpoint_list_widget)
        self.checkpoint_list_layout.setContentsMargins(4, 4, 4, 4)
        self.checkpoint_list_layout.setSpacing(6)

        empty_label = QLabel("No checkpoints yet")
        empty_label.setStyleSheet("color: #999; font-size: 9pt; text-align: center;")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkpoint_list_layout.addWidget(empty_label)
        self.checkpoint_list_layout.addStretch()

        scroll_area.setWidget(self.checkpoint_list_widget)

        # Hide scroll area by default
        scroll_area.setVisible(False)
        self.checkpoint_scroll_area = scroll_area
        history_layout.addWidget(scroll_area)

        history_layout.addStretch()
        self._stack.addWidget(history_page)

        # Connect File History button to toggle
        def toggle_history_list():
            is_visible = self.checkpoint_scroll_area.isVisible()
            self.checkpoint_scroll_area.setVisible(not is_visible)
            arrow = "-" if not is_visible else "▶"
            self.file_history_btn.setText(f"File History {arrow}")
            self._history_expanded = not is_visible

        file_history_btn.clicked.connect(toggle_history_list)

        # Wire tabs
        for i, name in enumerate(["File", "Pages", "History"]):
            self._tabs[name].clicked.connect(partial(self._switch_tab, i, name))
        self._switch_tab(0, "File")

    def _switch_tab(self, idx, name):
        self._stack.setCurrentIndex(idx)
        for n, btn in self._tabs.items():
            btn.setChecked(n == name)
    
    def set_accent_color(self, color: QColor):
        hex_color = color.name()
        tab_ss = f"""
            QPushButton {{ border: none; border-bottom: 4px solid #ddd;
                          background: white; font-size: 13pt; }}
            QPushButton:checked {{ border-bottom: 4px solid {hex_color};
                                   font-weight: bold; }}
            QPushButton:hover {{ background: {hex_color}; opacity: 0.1; color: white;}}
        """
        for btn in self._tabs.values():
            btn.setStyleSheet(tab_ss)

        action_ss = f"""
            QPushButton {{ text-align: left; padding: 0 18px;
                          border: none; font-size: 11pt; background: white; }}
            QPushButton:hover {{ background: {hex_color}; color: white; }}
        """
        for btn in self.file_actions.values():
            btn.setStyleSheet(action_ss)
            
    def _toggle_history_view(self):
        pass

# Context Menu - Properties

class ColorButton(QPushButton):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.setFixedSize(28, 28)
        self.setCheckable(True)
        self.setStyleSheet(
            f"border-radius: 14px; background: {self.color.name()}; border: 2px solid #222;"
        )
        self._hovered = False
    
    def enterEvent(self, event):
        self._hovered = True
        self.setStyleSheet(
            f"border-radius: 14px; background: {self.color.name()}; border: 2px solid #ff6600;"
        )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update()

    def leaveEvent(self, a0):
        self._hovered = False
        self.setStyleSheet(
            f"border-radius: 14px; background: {self.color.name()}; border: 2px solid #222;"
        )
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def paintEvent(self, a0):
        super().paintEvent(a0)
        if self.isChecked():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            # Draw orange indicator circle
            painter.setPen(QPen(QColor("#ff6600"), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(3, 3, self.width() - 6, self.height() - 6)


# Draggable Bar - Properties

class DraggableBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(18)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._dragging = False
        self._drag_pos = None

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Draw a simple horizontal line (centered)
        w = self.width()
        y = self.height() // 2
        line_length = int(w * 0.2)  # 20% of widget width
        x1 = (w - line_length) // 2
        x2 = x1 + line_length
        painter.setPen(QPen(QColor(0, 0, 0, 80), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(x1, y, x2, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_pos = event.globalPosition().toPoint()
            self._dialog_pos = self.parentWidget().pos()

    def mouseMoveEvent(self, event):
        if self._dragging:
            delta = event.globalPosition().toPoint() - self._drag_pos
            new_pos = self._dialog_pos + delta
            self.parentWidget().move(new_pos)

    def mouseReleaseEvent(self, a0):
        self._dragging = False

class SlidingTextRow(QWidget):
    row_clicked = pyqtSignal(int)

    def __init__(self, text, idx, parent=None):
        super().__init__(parent)
        self.idx = idx
        self._selected = False
        self.setFixedHeight(34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.label = QLabel(text, self)
        self.label.setStyleSheet(
            "color: #000000; background: transparent; padding: 0 6px; border: none; font-size: 9pt;"
        )
        self.label.setFixedHeight(34)
        self.label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.label.move(0, 0)

        self._anim = QPropertyAnimation(self.label, b"pos")
        self._anim.setDuration(3000)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def resizeEvent(self, event):
        fm = self.label.fontMetrics()
        text_w = fm.horizontalAdvance(self.label.text()) + 16
        self.label.setFixedWidth(max(text_w, self.width()))
        super().resizeEvent(event)

    def set_selected(self, val):
        self._selected = val
        color = "white" if val else "#000000"
        self.label.setStyleSheet(
            f"color: {color}; background: transparent; padding: 0 6px; border: none; font-size: 9pt;"
        )
        self.update()

    def enterEvent(self, event):
        self.update()
        text_w = self.label.width()
        if text_w > self.width():
            self._anim.stop()
            self._anim.setStartValue(self.label.pos())
            self._anim.setEndValue(QPoint(self.width() - text_w, 0))
            self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        self._anim.stop()
        self._anim.setStartValue(self.label.pos())
        self._anim.setEndValue(QPoint(0, 0))
        self._anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.row_clicked.emit(self.idx)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._selected:
            painter.fillRect(self.rect(), QColor("#ff6600"))
        elif self.underMouse():
            painter.fillRect(self.rect(), QColor("#ffe0cc"))
        painter.end()
    

class VerticalScrollBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._scroll_bar = None
        self._dragging = False
        self._drag_start_y = 0
        self._drag_start_val = 0

    def connect_to(self, scroll_bar):
        self._scroll_bar = scroll_bar
        scroll_bar.valueChanged.connect(self.update)
        scroll_bar.rangeChanged.connect(self.update)

    def _handle_y(self):
        margin = 20
        if self._scroll_bar is None:
            return margin
        total = self._scroll_bar.maximum() - self._scroll_bar.minimum()
        if total == 0:
            return margin
        ratio = (self._scroll_bar.value() - self._scroll_bar.minimum()) / total
        return int(margin + ratio * (self.height() - 2 * margin))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        margin = 20
        x = self.width() // 2
        painter.setPen(QPen(QColor(0, 0, 0, 60), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(x, margin, x, self.height() - margin)
        hy = self._handle_y()
        handle_radius = 12
        painter.setBrush(QColor("#fff"))
        painter.setPen(QPen(QColor("#222"), 2))
        painter.drawEllipse(QPointF(x, hy), handle_radius, handle_radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start_y = event.position().toPoint().y()
            if self._scroll_bar:
                self._drag_start_val = self._scroll_bar.value()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self._scroll_bar:
            margin = 20
            track_h = self.height() - 2 * margin
            dy = event.position().toPoint().y() - self._drag_start_y
            total = self._scroll_bar.maximum() - self._scroll_bar.minimum()
            if track_h > 0 and total > 0:
                delta = int(dy / track_h * total)
                new_val = max(self._scroll_bar.minimum(),
                              min(self._scroll_bar.maximum(),
                                  self._drag_start_val + delta))
                self._scroll_bar.setValue(new_val)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        super().mouseReleaseEvent(event)


class RestorePointsDialog(QDialog):
    # Dialog showing the last 5 undo states for restoration
    restore_selected = pyqtSignal(int)
    dialog_closed = pyqtSignal() 
    
    def __init__(self, parent=None, drawing_area=None, shape_idx=None):
        super().__init__(parent)
        self.drawing_area = drawing_area
        self.properties_dialog = parent
        self.shape_idx = shape_idx
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(False)
        self.setFixedSize(300, 460)
        self.setStyleSheet(
            "background: white; border-radius: 12px; border: 2px solid #222;"
        )
    
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
    
        self.draggable_bar = DraggableBar(self)
        layout.addWidget(self.draggable_bar)
    
        title = QLabel("Restore Points")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)
    
        # Collect entries for this shape only, most recent first
        self._entries = []
        if drawing_area and hasattr(drawing_area, "shape_history") and shape_idx is not None:
            matching = [
                e for e in drawing_area.shape_history
                if e["shape_idx"] == shape_idx
            ]
            self._entries = list(reversed(matching))

        self._selected_row = -1
        self._row_widgets = []

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        list_container = QWidget()
        list_container.setStyleSheet("background: transparent; border: none;")
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(2)

        if self._entries:
            for i, entry in enumerate(self._entries):
                text = f"[{entry['timestamp']}][{entry['shape_label']}] {entry['action']}"
                row = SlidingTextRow(text, i)
                def make_select(ri):
                    def on_click(idx):
                        self._selected_row = idx
                        for j, rw in enumerate(self._row_widgets):
                            rw.set_selected(j == idx)
                    return on_click
                row.row_clicked.connect(make_select(i))
                list_layout.addWidget(row)
                self._row_widgets.append(row)
        else:
            no_entry = QLabel("No restore points yet.")
            no_entry.setStyleSheet("color: #999; padding: 8px; border: none;")
            list_layout.addWidget(no_entry)

        list_layout.addStretch()
        scroll_area.setWidget(list_container)

        custom_vsb = VerticalScrollBar()
        custom_vsb.connect_to(scroll_area.verticalScrollBar())

        scroll_row = QHBoxLayout()
        scroll_row.setContentsMargins(0, 0, 0, 0)
        scroll_row.setSpacing(0)
        scroll_row.addWidget(scroll_area)
        scroll_row.addWidget(custom_vsb)
        layout.addLayout(scroll_row)
    
        restore_btn = QPushButton("Restore to Point")
        restore_btn.setFixedWidth(130)
        restore_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #222;
                padding: 8px;
                border-radius: 6px;
                background: #f0f0f0;
            }
            QPushButton:hover {
                background: #ff6600;
                color: white;
            }
        """)
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        def on_restore():
            list_idx = self._selected_row
            if list_idx < 0 or list_idx >= len(self._entries):
                return
            entry = self._entries[list_idx]
            target_idx = self.shape_idx
            if (
                self.drawing_area is None
                or target_idx is None
                or target_idx >= len(self.drawing_area.shapes)
            ):
                return
            self.drawing_area.push_undo()
            self.drawing_area.shapes[target_idx] = entry["shape_data"]
            self.drawing_area.selected_shape_index = None
            self.drawing_area.preview_shape = None
            self.drawing_area.preview_start = None
            self.drawing_area.preview_end = None
            self.drawing_area.preview_pixmap = None
            self.drawing_area._dragging_handle = None
            self.drawing_area._dragging_box = False
            self.drawing_area.shape_layers_overlay.setVisible(False)
            self.drawing_area.update()
            self.close()

        restore_btn.clicked.connect(on_restore)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #222;
                padding: 8px;
                border-radius: 6px;
                background: #f0f0f0;
            }
            QPushButton:hover {
                background: #ddd;
            }
        """)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.on_cancel)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(restore_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
            
    def on_cancel(self):
        self.close()

    def closeEvent(self, a0):
        if self.properties_dialog and isinstance(self.properties_dialog, PropertiesDialog):
            self.properties_dialog.show()
            self.properties_dialog.raise_()
            self.properties_dialog.activateWindow()
        self.dialog_closed.emit()
        super().closeEvent(a0)


class PropertiesDialog(QDialog):
    # Add a signal to emit updated properties
    from PyQt6.QtCore import pyqtSignal
    properties_applied = pyqtSignal(dict)

    def __init__(
        self,
        parent=None,
        shape_type=None,
        border_radius=0,
        border_weight=2,
        border_color="#000000",
        fill_color="#ffffff",
        drawing_area=None,
        shape_idx=None
    ):
        super().__init__(parent)
        self.drawing_area = drawing_area
        self.shape_idx = shape_idx
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(False)
        self.setFixedSize(300, 460)
        self.setStyleSheet(
            "background: white; border-radius: 12px; border: 2px solid #222;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        self.draggable_bar = DraggableBar(self)   
        layout.addWidget(self.draggable_bar)

        # Title
        title = QLabel("Properties")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)

        # Border Radius
        layout.addSpacing(4)
        border_radius_label = QLabel("Border Radius")
        border_radius_label.setStyleSheet("border: none;")
        layout.addWidget(border_radius_label)
        # Only show border radius for rect/roundrect
        border_radius_label.setVisible(shape_type in ("rect", "roundrect"))
        self.radius_slider = CustomSlider(0, 40, 10, self)
        layout.addWidget(self.radius_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        # Only show border radius for rect/roundrect
        self.radius_slider.setVisible(shape_type in ("rect", "roundrect"))
        # Set initial values
        self.radius_slider.setValue(border_radius)

        # Border Weight
        layout.addSpacing(4)
        border_weight_label = QLabel("Border Weight")
        border_weight_label.setStyleSheet("border: none;")
        layout.addWidget(border_weight_label)
        self.weight_slider = CustomSlider(1, 20, 2, self)
        layout.addWidget(self.weight_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        self.weight_slider.setValue(border_weight)
        
        global CUSTOM_BORDER_COLOR, CUSTOM_OBJECT_COLOR

        # Border Color
        border_color_label = QLabel("Border Color")
        border_color_label.setStyleSheet("border: none;")
        layout.addWidget(border_color_label)
        border_color_row = QHBoxLayout()
        self.border_color_buttons = []
        self.selected_border_color = QColor(border_color)
        border_colors = ["#000000", "#ffb366", "#ffe066", "#b3ff66", "#66ffd9", CUSTOM_BORDER_COLOR]
        for i, color in enumerate(border_colors):
            btn = ColorButton(color)
            if i == len(border_colors) - 1:
                # Last button: show quick properties color picker
                btn.clicked.connect(lambda _, b=btn: self._pick_custom_border_color(b))
            else:
                btn.clicked.connect(partial(self._on_border_color_selected, color, btn))
            border_color_row.addWidget(btn)
            self.border_color_buttons.append(btn)
            if color.lower() == border_color.lower():
                btn.setChecked(True)
        layout.addLayout(border_color_row)

        # Object Color
        object_color_label = QLabel("Object Color")
        object_color_label.setStyleSheet("border: none;")
        layout.addWidget(object_color_label)
        object_color_row = QHBoxLayout()
        self.object_color_buttons = []
        self.selected_object_color = QColor(fill_color)
        object_colors = ["#000000", "#ffb366", "#ffe066", "#b3ff66", "#66ffd9", CUSTOM_OBJECT_COLOR]
        for i, color in enumerate(object_colors):
            btn = ColorButton(color)
            if i == len(object_colors) - 1:
                btn.clicked.connect(lambda _, b=btn: self._pick_custom_object_color(b))
            else:
                btn.clicked.connect(partial(self._on_object_color_selected, color, btn))
            object_color_row.addWidget(btn)
            self.object_color_buttons.append(btn)
            if color.lower() == fill_color.lower():
                btn.setChecked(True)
        layout.addLayout(object_color_row)

        # Restore Point
        restore = ClickableLabel()
        restore.setText("Restore Point")
        restore.setAlignment(Qt.AlignmentFlag.AlignLeft)
        restore.setStyleSheet("""
            margin-top: 8px;
            border: none;
            color: #222;
        """)
        restore.setCursor(Qt.CursorShape.PointingHandCursor)
        restore.setOpenExternalLinks(False)
        layout.addWidget(restore)

        # Change color on hover
        def on_enter(event):
            restore.setStyleSheet("""
            margin-top: 8px;
            border: none;
            color: #ff6600;
            """)
        def on_leave(a0):
            restore.setStyleSheet("""
            margin-top: 8px;
            border: none;
            color: #222;
            """)
        restore.enterEvent = on_enter
        restore.leaveEvent = on_leave
        
        def open_restore_points():    
            if self.drawing_area:
                # Create and show restore points dialog modlessly (no exec())
                restore_dlg = RestorePointsDialog(self, self.drawing_area, shape_idx=self.shape_idx)
                restore_dlg.properties_dialog = self  # Ensure parent reference is set
        
                # Connect close signal to show properties again
                restore_dlg.dialog_closed.connect(lambda: self.show())
        
                # Hide this dialog temporarily (will be shown when restore_dlg closes)
                self.hide()
        
                # Position restore dialog next to properties dialog
                if self.isVisible():
                    pos = self.pos()
                    restore_dlg.move(pos.x() + 320, pos.y())
        
                # Show restore dialog modlessly
                restore_dlg.show()
                restore_dlg.raise_()
                restore_dlg.activateWindow()
    
        restore.clicked = open_restore_points

        # Close button (optional)
        close_btn = QPushButton("Close")
        def on_accept():
            props = {
                "border_radius": self.radius_slider.getValue(),
                "border_weight": self.weight_slider.getValue(),
                "border_color": self.selected_border_color,
                "object_color": self.selected_object_color,
            }
            self.properties_applied.emit(props)
            self.accept()

        close_btn.clicked.connect(on_accept)
        close_btn.setStyleSheet("""
            QPushButton{
                margin-top: 10px;
                border: none;    
                color: #222;
            }
            
            QPushButton:hover {
                color: #ff6600;
            }
            """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _on_border_color_selected(self, color_hex, button):
        """Handle border color selection"""
        # Deselect all border color buttons
        for btn in self.border_color_buttons:
            btn.blockSignals(True)
            btn.setChecked(False)
            btn.blockSignals(False)
        # Select the clicked button
        button.blockSignals(True)
        button.setChecked(True)
        button.blockSignals(False)
        self.selected_border_color = QColor(color_hex)
        button.update()

    def _on_object_color_selected(self, color_hex, button):
        """Handle object color selection"""
        # Deselect all object color buttons
        for btn in self.object_color_buttons:
            btn.blockSignals(True)
            btn.setChecked(False)
            btn.blockSignals(False)
        # Select the clicked button
        button.blockSignals(True)
        button.setChecked(True)
        button.blockSignals(False)
        self.selected_object_color = QColor(color_hex)
        button.update()
    
    def _pick_custom_border_color(self, button):
        global CUSTOM_BORDER_COLOR
        color = QColorDialog.getColor(self.selected_border_color, self, "Pick Border Color")
        if color.isValid():
            button.color = color
            button.setStyleSheet(
                f"border-radius: 14px; background: {color.name()}; border: 2px solid #222;"
            )
            CUSTOM_BORDER_COLOR = color.name()
            self._on_border_color_selected(color.name(), button)

    def _pick_custom_object_color(self, button):
        global CUSTOM_OBJECT_COLOR
        color = QColorDialog.getColor(self.selected_object_color, self, "Pick Object Color")
        if color.isValid():
            button.color = color
            button.setStyleSheet(
                f"border-radius: 14px; background: {color.name()}; border: 2px solid #222;"
            )
            CUSTOM_OBJECT_COLOR = color.name()
            self._on_object_color_selected(color.name(), button)


class ArcToolMenu(QWidget):
    category_selected = pyqtSignal(dict)  # Emits the category dict
    tool_selected = pyqtSignal(str)       # Emits the tool name

    def __init__(self, parent=None, items=None, border_color="#ff6600"):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setVisible(False)
        self.radius = 120
        self.icon_size = 74
        self.items = items or []
        self.buttons = []
        self.anim_group = None
        self.border_color = border_color
        self.active_category = None  # Track active category
        self.active_tool = None
    
    def set_active_category(self, category_name):
        self.active_category = category_name
        self._setup_ui()
    
    def set_active_tool(self, tool_name):
        self.active_tool = tool_name
        self._setup_ui()

    def _setup_ui(self):
        for btn in self.buttons:
            btn.setParent(None)
        self.buttons = []
        for idx, item in enumerate(self.items):
            btn = QToolButton(self)
            if item["icon"].endswith(".png") or item["icon"].endswith(".svg"):
                btn.setIcon(QIcon(item["icon"]))
                size = item.get("icon_size", self.icon_size)
                btn.setIconSize(QSize(size, size))
                btn.setFixedSize(size, size)
                btn.setText("")
            else:
                btn.setText(item["icon"])
            btn.setFixedSize(self.icon_size, self.icon_size)
            # Highlight if active category
            if item["type"] == "category" and item["name"] == self.active_category:
                bg = "#fff7ef"
            # Highlight if active tool
            elif item["type"] == "tool" and item["name"] == self.active_tool:
                bg = "#ffe6b3"
            else:
                bg = "#0078d7"
            btn.setStyleSheet(f"""
                QToolButton {{
                    border-radius: 37px;
                    background: {bg};
                    border: 2px solid {self.border_color};
                    font-size: 28pt;
                    color: #222;
                }}
                QToolButton:hover {{
                    background: #fff7ef;
                }}
            """)
            # ...existing code...
            if item["type"] == "tool":
                btn.clicked.connect(lambda checked, t=item["name"]: self._on_tool_selected(t))
            elif item["type"] == "category":
                btn.clicked.connect(lambda checked, cat=item: self._on_category_selected(cat))
            btn.move(0, 0)
            btn.setVisible(False)
            self.buttons.append(btn)
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    
    def update_tool_btn_border_2(self):
        color_hex = self.border_color
        pass

    def show_arc(self, origin):
        self._setup_ui()
        # Get the parent widget's global position and size
        parent = self.parentWidget()
        if parent is not None:
            global_pos = parent.mapToGlobal(QPoint(0, 0))
            self.setGeometry(global_pos.x(), global_pos.y(), parent.width(), parent.height())
            # Map the origin from parent coordinates to self (global) coordinates
            mapped_origin = origin
        else:
            self.setGeometry(0, 0, 800, 600)
            mapped_origin = origin
        for btn in self.buttons:
            btn.setVisible(True)
            btn.raise_()
        self.animate_buttons(mapped_origin)
        self.setVisible(True)
    

    def animate_buttons(self, origin):
        count = len(self.buttons)
        if count == 0:
            return
        # Change arc orientation: e.g., from 45 degrees (down-right) to 135 degrees (up-right)
        start_angle = math.radians(180)  # Start at 45 degrees (down-right)
        end_angle = math.radians(270)   # End at 135 degrees (up-right)
        angle_step = (end_angle - start_angle) / max(1, count - 1)
        self.anim_group = QParallelAnimationGroup(self)
        for i, btn in enumerate(self.buttons):
            angle = start_angle + angle_step * i
            dx = int(self.radius * math.cos(angle))
            dy = int(self.radius * math.sin(angle))
            end_pos = QPoint(origin.x() + dx - self.icon_size//2, origin.y() + dy - self.icon_size//2)
            anim = QPropertyAnimation(btn, b"pos", self)
            anim.setDuration(350)
            anim.setStartValue(origin)
            anim.setEndValue(end_pos)
            anim.setEasingCurve(QEasingCurve.Type.OutBack)
            btn.move(origin)
            self.anim_group.addAnimation(anim)
        self.anim_group.start()

    def hide_arc(self):
        if not self.buttons or not self.isVisible():
            self.setVisible(False)
            return
        origin = self.buttons[0].pos() + QPoint(self.icon_size // 2, self.icon_size // 2)
        group = QParallelAnimationGroup(self)
        for btn in self.buttons:
            anim = QPropertyAnimation(btn, b"pos", self)
            anim.setDuration(250)
            anim.setStartValue(btn.pos())
            anim.setEndValue(origin - QPoint(self.icon_size // 2, self.icon_size // 2))
            anim.setEasingCurve(QEasingCurve.Type.InBack)
            group.addAnimation(anim)
        def after():
            for btn in self.buttons:
                btn.setVisible(False)
            self.setVisible(False)
        group.finished.connect(after)
        group.start()

    def _on_tool_selected(self, tool_name):
        self.hide_arc()
        self.tool_selected.emit(tool_name)

    def _on_category_selected(self, category):
        self.hide_arc()
        self.category_selected.emit(category)

    def mousePressEvent(self, event):
        # Hide arc if click is outside any button
        if not any(btn.geometry().contains(event.position().toPoint()) for btn in self.buttons):
            self.hide_arc()
            event.accept()
            return
        super().mousePressEvent(event)


class RotatingToolButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rotation = 0
        self._icon = None

    def setIcon(self, icon):
        self._icon = icon
        super().setIcon(icon)

    def getRotation(self):
        return self._rotation

    def setRotation(self, value):
        self._rotation = value
        self.update()

    rotation = pyqtProperty(float, getRotation, setRotation)

    def paintEvent(self, event):
        if self._icon:
            painter = QPainter(self)
            try:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                rect = self.rect()
                rectf = QRectF(rect)
                # Draw border
                style = self.styleSheet()
                bg_cplor = "white"
                import re
                m_bg = re.search(r"background(?:-color)?:\s*([^;]+);", style)
                if m_bg:
                    bg_color = m_bg.group(1).strip()
                painter.setBrush(QColor(bg_color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(rectf.adjusted(1, 1, -1, -1))
                # Draw border
                color = "#222"
                m = re.search(r"border:\s*\d+px\s+solid\s+([^;]+);", style)
                if m:
                    color = m.group(1).strip()
                pen = QPen(QColor(color), 2)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(rectf.adjusted(1, 1, -1, -1))
                # Draw icon rotated around center with floating point precision
                painter.save()
                center = rectf.center()
                painter.translate(center)
                painter.rotate(self._rotation)
                painter.translate(-center)
                self._icon.paint(painter, rect, Qt.AlignmentFlag.AlignCenter)
                painter.restore()
            finally:
                painter.end()
        else:
            super().paintEvent(event)


class ClickableLabel(QLabel):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked = None  # Assign a callback
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.clicked:
            self.clicked()


class ToolButton(QPushButton):
    doubleClicked = pyqtSignal()
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self.setFixedSize(64, 64)
        self.setStyleSheet("""
            border: none; 
            margin: 0; 
            font-size: 18pt;
            font-weight: bold; 
            background: white;
            color: black;
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


class CustomToolTip(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            background: rgba(0,0,0,200);
            color: white;
            border-radius: 8px;
            padding: 8px 24px;
            font-size: 14pt;
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setVisible(False)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_tooltip(self, text, duration=2000):
        self.setText(text)
        self.adjustSize()
        parent = self.parentWidget()
        if parent:
            x = (parent.width() - self.width()) // 2
            y = parent.height() - self.height() - 40
            self.move(x, y)
        self.setVisible(True)
        self.raise_()
        self._timer.start(duration)


def _serialize_qpoint(p):
    return [p.x(), p.y()]

def _serialize_qcolor(c):
    return c.name()  # "#rrggbb"

def _serialize_pixmap(px: QPixmap) -> str:
    from PyQt6.QtCore import QBuffer, QIODevice
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    px.save(buf, "PNG")
    data = bytes(buf.data())
    return base64.b64encode(data).decode("utf-8")

def _deserialize_pixmap(s: str) -> QPixmap:
    data = base64.b64decode(s)
    px = QPixmap()
    px.loadFromData(data, "PNG")
    return px

def _serialize_shape(shape: tuple) -> dict:
    tool = shape[0]
    if tool == "image":
        return {
                "tool": "image",
                "start": _serialize_qpoint(shape[1]),
                "end": _serialize_qpoint(shape[2]),
                "pixmap": _serialize_pixmap(shape[3]),
        }
    elif tool == "draw":
        points = shape[1]
        color = shape[3]
        d = {
                "tool": "draw",
                "points": [_serialize_qpoint(p) for p in points],
                "color": _serialize_qcolor(color),
                "extras": []
        }
        for item in shape[4:]:
            d["extras"].append(_serialize_extra(item))
        return d
    else:
        d = {
                "tool": tool,
                "start": _serialize_qpoint(shape[1]),
                "end": _serialize_qpoint(shape[2]),
                "color": _serialize_qcolor(shape[3]),
                "extras": []
        }
        for item in shape[4:]:
            d["extras"].append(_serialize_extra(item))
        return d

def _serialize_extra(item):
    if isinstance(item, QColor):
        return {"type": "color", "value": item.name()}
    elif isinstance(item, dict):
        # border_weight dict — values may include color strings, keep as-is
        return {"type": "dict", "value": item}
    elif isinstance(item, (int, float, bool, str)) or item is None:
        return {"type": "primitive", "value": item}
    return {"type": "primitive", "value": None}

def _deserialize_extra(d):
    if d["type"] == "color":
        return QColor(d["value"])
    elif d["type"] == "dict":
        return d["value"]
    else:
        return d["value"]

def _deserialize_shape(d: dict) -> tuple:
    tool = d["tool"]
    if tool == "image":
        return (
                "image",
            QPoint(*d["start"]),
            QPoint(*d["end"]),
            _deserialize_pixmap(d["pixmap"]),
        )
    elif tool == "draw":
        pts = [QPoint(*p) for p in d["points"]]
        color = QColor(d["color"])
        extras = [_deserialize_extra(e) for e in d.get("extras", [])]
        return tuple(["draw", pts, None, color] + extras)
    else:
        start = QPoint(*d["start"])
        end = QPoint(*d["end"])
        color = QColor(d["color"])
        extras = [_deserialize_extra(e) for e in d.get("extras", [])]
        return tuple([tool, start, end, color] + extras)


class DrawingArea(QFrame):
    HANDLE_SIZE = 6
    shape_selected_for_edit = pyqtSignal() 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #e5e5e5; border: none;")
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.current_tool = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.shape_color = QColor("#000000")

        self.preview_shape = None
        self.preview_start = None
        self.preview_end = None

        self._dragging_handle = None
        self._dragging_box = False
        self._drag_offset = QPoint()
        self.shapes = []  # Store drawn shapes

        self._copied_shape = None  # Store copied shape

        self.undo_stack = []
        self.redo_stack = []
        self.shape_history = []
        self._pending_shape_action = None

        self._free_rotating = False
        self._rotation_start_angle = 0
        self._rotation_center = None
        self._rotation_initial = 0

        self.a4_size = QSize(1123, 794)

        self.eraser_strokes = []  # List of lists of QPoint
        self._erasing = False
        self._current_eraser_points = []

        self.eraser_mask = QPixmap(self.a4_size)
        self.eraser_mask.fill(Qt.GlobalColor.transparent)

        self.eraser_radius = 12

        self.draw_radius = 6

        # cache for in-progress image erasing to avoid repeated conversions
        self._image_erase_cache = {}

        # Zoom state
        self.scale_factor = 1.0
        self.zoom_percent = 0  # Relative to 100%
        self.pan_offset = QPoint(0, 0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # To receive wheel events

        # Overlay label for zoom info (hidden by default)
        self.zoom_overlay = QLabel(self)
        self.zoom_overlay.setStyleSheet("background: rgba(0,0,0,120); color: white; padding: 2px 8px; border-radius: 8px;")
        self.zoom_overlay.move(10, 10)
        self.zoom_overlay.resize(120, 28)
        self.zoom_overlay.hide()
        self._zoom_overlay_timer = QTimer(self)
        self._zoom_overlay_timer.setSingleShot(True)
        self._zoom_overlay_timer.timeout.connect(self.zoom_overlay.hide)

        self.shape_layers_overlay = ShapeLayersOverlay(self)
        self.shape_layers_overlay.shape_selected.connect(self.select_shape_by_index)
        # self.shape_layers_overlay.setVisible(False)
        self.selected_shape_index = None  # Track which shape is selected

        self._edit_locked_color = None

        self._show_rotation_indicator = False
        self._rotation_indicator_timer = QTimer(self)
        self._rotation_indicator_timer.setSingleShot(True)
        self._rotation_indicator_timer.timeout.connect(self.hide_rotation_indicator)

        self.cropping = False
        self.crop_preview_mode = False
        self.crop_start = None
        self.crop_end = None
        self._crop_dragging_handle = None

        self.tool_last_sizes = {
            'draw': 6,
            'eraser': 12,
            'shapes': 2,  # Default border width for shapes
            'line': 2     # Default line width
        }

        # Initialize tool sizes from last used sizes
        self.tool_sizes = self.tool_last_sizes.copy()
        
    def _to_local(self, pt, rotation, center):
        import math
        rad = math.radians(-rotation)
        dx = pt.x() - center.x()
        dy = pt.y() - center.y()
        nx = math.cos(rad) * dx - math.sin(rad) * dy + center.x()
        ny = math.sin(rad) * dx + math.cos(rad) * dy + center.y()
        return QPoint(int(round(nx)), int(round(ny)))
    
    def _from_local(self, pt, rotation, center):
        import math
        rad = math.radians(rotation)
        dx = pt.x() - center.x()
        dy = pt.y() - center.y()
        nx = math.cos(rad) * dx - math.sin(rad) * dy + center.x()
        ny = math.sin(rad) * dx + math.cos(rad) * dy + center.y()
        return QPoint(int(round(nx)), int(round(ny)))    

    def set_tool_size(self, tool_name, size):
        """Store tool size and update cursor if needed"""
        self.tool_sizes[tool_name] = size

        # Update cursor immediately if this is the current tool
        if self.current_tool == tool_name:
            if tool_name == 'eraser':
                pixmap = QPixmap(r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-colors-eraser.png")
                if not pixmap.isNull():
                    cursor_size = size * 2
                    cursor_pix = pixmap.scaled(cursor_size, cursor_size)
                    self.setCursor(QCursor(cursor_pix, cursor_size // 2, cursor_size // 2))
            elif tool_name == 'draw':
                cursor_size = max(size * 2, 8)
                pixmap = QPixmap(cursor_size, cursor_size)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                pen_width = max(size, 2)
                pen = QPen(self.shape_color, pen_width)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                margin = pen_width // 2 + 1
                painter.drawEllipse(margin, margin, cursor_size - 2 * margin, cursor_size - 2 * margin)
                painter.end()
                self._draw_cursor = QCursor(pixmap, cursor_size // 2, cursor_size // 2)
                self.setCursor(self._draw_cursor)

    def hide_rotation_indicator(self):
        self._show_rotation_indicator = False
        self.update()

    def set_shape_color(self, color):
        self.shape_color = color
        self._edit_locked_color = color

        self.update()

    def get_canvas_center(self):
        widget_rect = self.rect()
        return widget_rect.center()

    def wheelEvent(self, event):
        modifiers = event.modifiers()
        delta = event.angleDelta().y()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Zoom
            if delta > 0:
                self.zoom_by(10)
            else:
                self.zoom_by(-10)
            self.show_zoom_overlay()
            event.accept()
        elif modifiers & Qt.KeyboardModifier.ShiftModifier:
            # Pan horizontally
            self.pan_offset += QPoint(delta // 2, 0)
            self.clamp_pan_offset()  # Ensure panning doesn't go out of bounds
            self.update()
            event.accept()
        else:
            # Pan vertically
            self.pan_offset += QPoint(0, delta // 2)
            self.clamp_pan_offset() # Ensure panning doesn't go out of bounds
            self.update()
            event.accept()

    def zoom_by(self, delta_percent):
        self.zoom_percent += delta_percent
        self.zoom_percent = max(-90, min(400, self.zoom_percent))  # Clamp between 10% and 500%
        self.scale_factor = 1.0 + self.zoom_percent / 100.0
        self.clamp_pan_offset()
        self.update()

    def show_zoom_overlay(self):
        percent = int(self.scale_factor * 100)
        self.show_status_overlay(f"Zoom: {percent}%", 1200)
        
    def show_status_overlay(self, text, duration=1200):
        self.zoom_overlay.setText(text)
        self.zoom_overlay.adjustSize()
        self.zoom_overlay.show()
        self._zoom_overlay_timer.start(duration)    

    def set_tool(self, tool):
        self.current_tool = tool

        if self.selected_shape_index is not None:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            return

        if tool == "eraser":
            # Use the last stored size for eraser
            size = self.tool_last_sizes.get('eraser', 12)
            # Load eraser icon and set as cursor
            pixmap = QPixmap(r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-colors-eraser.png")
            if not pixmap.isNull():
                cursor_size = size * 2  # Use the last stored size
                cursor_pix = pixmap.scaled(cursor_size, cursor_size)
                self.setCursor(QCursor(cursor_pix, cursor_size // 2, cursor_size // 2))
            else:
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        elif tool == "draw" or (self.selected_shape_index is not None and self.shapes[self.selected_shape_index][0] == "draw"):
            # Show a circular cursor for draw tool
            size = max(self.draw_radius * 2, 8)
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            # Use at least 2px pen width for visibility
            pen_width = max(self.draw_radius, 2)
            pen = QPen(self.shape_color, pen_width)  # Use the current shape color
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            # Draw ellipse centered, with margin for pen width
            margin = pen_width // 2 + 1
            painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
            painter.end()
            self._draw_cursor = QCursor(pixmap, size // 2, size // 2)
            self.setCursor(self._draw_cursor)

        elif tool:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mousePressEvent(self, event):
        pt = self.widget_to_canvas(event.position().toPoint())

        # PREVENT ANY INTERACTION WITH LOCKED SHAPES
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on a locked shape
            for idx in reversed(range(len(self.shapes))):
                shape = self.shapes[idx]
                if self.is_shape_locked(idx):
                    # Get shape bounds to see if click is on it
                    if len(shape) >= 3:
                        tool = shape[0]
                        start, end = shape[1], shape[2]
                        if tool == "draw" and isinstance(start, list) and len(start) > 0:
                            min_x = min(p.x() for p in start)
                            min_y = min(p.y() for p in start)
                            max_x = max(p.x() for p in start)
                            max_y = max(p.y() for p in start)
                            rect = QRect(QPoint(min_x, min_y), QPoint(max_x, max_y)).normalized()
                        else:
                            rect = QRect(start, end).normalized()
                        if rect.contains(pt):
                            # Clicking on locked shape - do nothing
                            return

        # Deselect a locked shape if user clicks elsewhere
        if (event.button() == Qt.MouseButton.LeftButton
                and self.selected_shape_index is not None
                and self.preview_shape is None
                and self.is_shape_locked(self.selected_shape_index)):
            self.selected_shape_index = None
            self._edit_locked_color = None
            self.update()

        margin = 8

        # Add handling for crop preview adjustment
        if self.crop_preview_mode and self.crop_start is not None and self.crop_end is not None:
            crop_rect = QRect(self.crop_start, self.crop_end).normalized()
            # Check handles for resizing crop area
            for idx, handle in enumerate(self.handle_points(crop_rect)):
                if (handle - pt).manhattanLength() < self.HANDLE_SIZE:
                    self._crop_dragging_handle = idx
                    self.set_resize_cursor(idx)
                    return

            # Check for moving crop area
            if crop_rect.contains(pt):
                self._dragging_box = True
                self._drag_offset = pt - crop_rect.topLeft()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                return

        if self._free_rotating and self.selected_shape_index is not None:
            idx = self.selected_shape_index
            shape = self.shapes[idx]
            rotation = 0
            # Use preview coordinates if available (edit mode)
            start = self.preview_start if self.preview_start is not None else shape[1]
            end = self.preview_end if self.preview_end is not None else shape[2]
            if shape[0] == "draw" and isinstance(start, list):
                # For draw shapes, use bounding box center
                points = start
                min_x = min(p.x() for p in points)
                min_y = min(p.y() for p in points)
                max_x = max(p.x() for p in points)
                max_y = max(p.y() for p in points)
                self._rotation_center = QPoint((min_x + max_x) // 2, (min_y + max_y) // 2)
            else:
                rect = QRect(start, end).normalized()
                self._rotation_center = rect.center()
                self.preview_start = start
                self.preview_end = end
                # Extract rotation value robustly
                if len(shape) > 5 and isinstance(shape[5], (int, float)):
                    rotation = shape[5]
                elif len(shape) > 4 and isinstance(shape[4], (int, float)) and not isinstance(shape[4], bool):
                    rotation = shape[4]
                self.preview_rotation = rotation
            dx = pt.x() - self._rotation_center.x()
            dy = pt.y() - self._rotation_center.y()
            self._rotation_start_angle = math.degrees(math.atan2(dy, dx))
            self._rotation_initial = rotation
            return

        if self.preview_shape == "draw" and isinstance(self.preview_start, list):
            # Compute bounding box
            points = self.preview_start
            if points and len(points) > 1:
                min_x = min(p.x() for p in points)
                min_y = min(p.y() for p in points)
                max_x = max(p.x() for p in points)
                max_y = max(p.y() for p in points)
                rect = QRect(QPoint(min_x, min_y), QPoint(max_x, max_y)).normalized()
                draw_margin = max(self.draw_radius, margin)
                box_rect = rect.adjusted(-draw_margin, -draw_margin, draw_margin, draw_margin)
                # Check handles for resizing
                for idx, handle in enumerate(self.handle_points(box_rect)):
                    hit_size = max(64, self.HANDLE_SIZE * 2)
                    handle_rect = QRect(
                        handle.x() - hit_size // 2,
                        handle.y() - hit_size // 2,
                        hit_size,
                        hit_size
                    )
                    if handle_rect.contains(pt):
                        self._dragging_handle = idx
                        self._orig_points = [QPoint(p) for p in points]
                        self._orig_bbox = QRect(rect)
                        self.set_resize_cursor(idx)
                        self._pending_shape_action = "Resize"
                        return
                # Check for moving
                if box_rect.contains(pt):
                    self._dragging_box = True
                    self._orig_points = [QPoint(p) for p in points]
                    self._orig_bbox = QRect(rect)
                    self._drag_offset = pt - box_rect.topLeft()
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    self._pending_shape_action = "Move"
                    return

                if not self._dragging_handle and not self._dragging_box:
                    self.preview_shape = None
                    self.preview_start = None
                    self.preview_end = None
                    self.selected_shape_index = None
                    self.update()
                return

        # EDITING EXISTING SHAPE OR IMAGE
        if self.preview_shape and self.preview_start is not None and self.preview_end is not None:
            rect = QRect(self.preview_start, self.preview_end).normalized()
            box_rect = rect.adjusted(-margin, -margin, margin, margin)
            rotation = getattr(self, 'preview_rotation', 0)
            # Transform click into the shape's local (unrotated) coordinate space
            pt_local = self._to_local(pt, rotation, rect.center()) if rotation else pt
            hit_size = max(20, self.HANDLE_SIZE * 3)  # increase from 6px to at least 20px
            for idx, handle in enumerate(self.handle_points(box_rect)):
                handle_rect = QRect(handle.x() - hit_size//2, handle.y() - hit_size//2, hit_size, hit_size)
                if handle_rect.contains(pt_local):
                    self._dragging_handle = idx
                    self._drag_origin_center = rect.center()
                    self.set_resize_cursor(idx)
                    self._pending_shape_action = "Resize"
                    # Store the anchor corner's world position so resize won't move the shape
                    if rotation:
                        r = rect  # already normalized
                        x1, y1, x2, y2 = r.left(), r.top(), r.right(), r.bottom()
                        xm, ym = (x1+x2)//2, (y1+y2)//2
                        _anchor_map = {
                            0: QPoint(x2, y2), 1: QPoint(xm, y2), 2: QPoint(x1, y2),
                            3: QPoint(x1, ym), 4: QPoint(x1, y1), 5: QPoint(xm, y1),
                            6: QPoint(x2, y1), 7: QPoint(x2, ym)
                        }
                        ac = _anchor_map.get(idx)
                        self._drag_anchor_world = self._from_local(ac, rotation, r.center()) if ac else None
                    else:
                        self._drag_anchor_world = None
                    return
                
            # Check for moving
            if box_rect.contains(pt_local):
                self._dragging_box = True
                self._drag_offset = pt - box_rect.topLeft()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self._pending_shape_action = "Move"
                return
            
            # Commit edit if click outside (only if editing an existing shape)
            if self.selected_shape_index is not None:
                self.push_shape_restore(self.selected_shape_index, self._pending_shape_action or "Edit")
                self._pending_shape_action = None
                self.push_undo()
                old_shape = self.shapes[self.selected_shape_index]
                tool, start, end, border_color = old_shape[:4]

                # Robustly extract all extra properties from old_shape by type
                fill_color = None
                rotation = getattr(self, "preview_rotation", 0)
                extra_dicts = []
                lock_flag = None

                for item in old_shape[4:]:
                    if isinstance(item, QColor):
                        fill_color = item
                    elif isinstance(item, bool):
                        lock_flag = item
                    elif isinstance(item, (int, float)):
                        rotation = item
                    elif isinstance(item, dict):
                        extra_dicts.append(item)

                # preview_rotation reflects any free-rotate done during this edit session
                rotation = getattr(self, "preview_rotation", rotation)

                locked_color = self._edit_locked_color if self._edit_locked_color is not None else self.shape_color

                if self.preview_shape == "image":
                    if len(old_shape) > 4 and isinstance(old_shape[4], (int, float)) and not isinstance(old_shape[4], bool):
                        self.shapes[self.selected_shape_index] = (
                            "image", self.preview_start, self.preview_end,
                            self.preview_pixmap, rotation
                        )
                    else:
                        self.shapes[self.selected_shape_index] = (
                            "image", self.preview_start, self.preview_end,
                            self.preview_pixmap
                        )
                else:
                    # Rebuild shape preserving fill, rotation, dicts (border_radius/border_weight), and lock
                    new_shape = [self.preview_shape, self.preview_start, self.preview_end, border_color]
                    if fill_color is not None:
                        new_shape.append(fill_color)
                    if rotation != 0:
                        new_shape.append(rotation)
                    for d in extra_dicts:
                        new_shape.append(d)
                    if lock_flag is not None:
                        new_shape.append(lock_flag)
                    self.shapes[self.selected_shape_index] = tuple(new_shape)

            else:
                self.push_undo()
                # Placing a new/pasted shape
                if self.preview_shape == "image":
                    self.shapes.append((
                        "image",
                        self.preview_start,
                        self.preview_end,
                        self.preview_pixmap
                    ))
                else:
                    # Use fill color and rotation if present.
                    border_color = getattr(self, "preview_color", self.shape_color)
                    fill_color = getattr(self, "preview_fill_color", None)
                    rotation = getattr(self, "preview_rotation", 0)
                    shape_tuple = [
                        self.preview_shape,
                        self.preview_start,
                        self.preview_end,
                        border_color
                    ]
                    if fill_color is not None:
                        shape_tuple.append(fill_color)
                    if rotation != 0:
                        shape_tuple.append(rotation)
                    self.shapes.append(tuple(shape_tuple))

            self.preview_shape = None
            self.preview_start = None
            self.preview_end = None
            self.preview_pixmap = None
            # self.preview_color = None
            self.preview_fill_color = None
            self.preview_rotation = 0
            self.selected_shape_index = None

            self._edit_locked_color = None
            self.update()
            return

        if self.current_tool == "draw" and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.freehand_points = [pt]
            self.setCursor(self._draw_cursor)  # Keep the circle cursor
            self.update()
            return

        if self.current_tool == "eraser" and event.button() == Qt.MouseButton.LeftButton:
            self.push_undo()
            self._erasing = True
            self._current_eraser_points = [pt]
            self.update()
            return

        if self.current_tool == "fill" and event.button() == Qt.MouseButton.LeftButton:
            self.push_undo()
            self.fill_at_point(pt)
            self.update()
            return

        if self.current_tool == "crop" and event.button() == Qt.MouseButton.LeftButton:
            if not self.crop_preview_mode:
                self.cropping = True
                self.crop_start = pt
                self.crop_end = pt
            self.update()
            return

        # PLACING NEW SHAPE OR IMAGE
        if (self.current_tool or (self.preview_shape == "image" and hasattr(self, "preview_pixmap"))) and event.button() == Qt.MouseButton.LeftButton:
            if self.preview_start is not None and self.preview_end is not None:
                rect = QRect(self.preview_start, self.preview_end).normalized()
                box_rect = rect.adjusted(-margin, -margin, margin, margin)
                for idx, handle in enumerate(self.handle_points(box_rect)):
                    if (handle - pt).manhattanLength() < self.HANDLE_SIZE:
                        self._dragging_handle = idx
                        self.set_resize_cursor(idx)
                        return
                if box_rect.contains(pt):
                    self._dragging_box = True
                    self._drag_offset = pt - box_rect.topLeft()
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    return
            if self.canvas_contains(pt):
                if self.preview_shape is None:
                    self.preview_shape = self.current_tool
                    self.preview_start = pt
                    self.preview_end = pt
                    self.preview_rotation = 0
                    self.selected_shape_index = None
                else:
                    self.push_undo()
                    # Place the shape or image
                    if self.preview_shape == "image":
                        self.shapes.append(("image", self.preview_start, self.preview_end, self.preview_pixmap))
                        self.preview_shape = None
                        self.preview_start = None
                        self.preview_end = None
                        self.preview_pixmap = None
                    else:
                        # Use preview color if available (from paste), otherwise use current shape color
                        border_color = getattr(self, "preview_color", self.shape_color)
                        fill_color = getattr(self, "preview_fill_color", None)
                        rotation = getattr(self, "preview_rotation", 0)

                        shape_tuple = [self.preview_shape, self.preview_start, self.preview_end, border_color]
                        if fill_color is not None:
                            shape_tuple.append(fill_color)
                        if rotation != 0:
                            shape_tuple.append(rotation)
                        self.shapes.append(tuple(shape_tuple))

                        # Clear preview attributes after placing
                        self.preview_color = None
                        self.preview_fill_color = None
                        self.preview_rotation = 0
                        self.preview_shape = None
                        self.preview_start = None
                        self.preview_end = None
                self.update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pt = self.widget_to_canvas(event.position().toPoint())

        if self.crop_preview_mode and self._crop_dragging_handle is not None:
            self.set_resize_cursor(self._crop_dragging_handle)
            rect = QRect(self.crop_start, self.crop_end).normalized()
            x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()

            # Update according to handle index
            if self._crop_dragging_handle == 0:  # Top-left
                self.crop_start = pt
                self.crop_end = QPoint(x2, y2)
            elif self._crop_dragging_handle == 1:  # Top-middle
                self.crop_start = QPoint(x1, pt.y())
                self.crop_end = QPoint(x2, y2)
            elif self._crop_dragging_handle == 2:  # Top-right
                self.crop_start = QPoint(x1, pt.y())
                self.crop_end = QPoint(pt.x(), y2)
            elif self._crop_dragging_handle == 3:  # Right-middle
                self.crop_start = QPoint(x1, y1)
                self.crop_end = QPoint(pt.x(), y2)
            elif self._crop_dragging_handle == 4:  # Bottom-right
                self.crop_start = QPoint(x1, y1)
                self.crop_end = pt
            elif self._crop_dragging_handle == 5:  # Bottom-middle
                self.crop_start = QPoint(x1, y1)
                self.crop_end = QPoint(x2, pt.y())
            elif self._crop_dragging_handle == 6:  # Bottom-left
                self.crop_start = QPoint(pt.x(), y1)
                self.crop_end = QPoint(x2, pt.y())
            elif self._crop_dragging_handle == 7:  # Left-middle
                self.crop_start = QPoint(pt.x(), y1)
                self.crop_end = QPoint(x2, y2)

            self.update()
            return
        elif self.crop_preview_mode and self._dragging_box:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            delta = pt - self._drag_offset
            if not hasattr(self, '_original_crop_rect'):
                # Store original rectangle dimensions on first move
                self._original_crop_rect = QRect(self.crop_start, self.crop_end).normalized()
                self._start_drag_point = pt

            # Calculate how far we've moved from the start position
            total_delta = pt - self._start_drag_point

            # Move the original rectangle by that amount
            new_rect = QRect(
                self._original_crop_rect.topLeft() + total_delta,
                self._original_crop_rect.bottomRight() + total_delta
            )

            # Update crop coordinates while preserving exact dimensions
            self.crop_start = new_rect.topLeft()
            self.crop_end = new_rect.bottomRight()
            self.update()
            return

        # Hide rotation indicator if user moves/resizes
        if self._show_rotation_indicator:
            self.hide_rotation_indicator()
        pt = self.widget_to_canvas(event.position().toPoint())
        margin = 8

        if self._dragging_handle is not None and self.preview_shape == "draw" and isinstance(self.preview_start, list):
            # Resize freehand: scale all points according to bbox change
            points = self._orig_points
            orig_bbox = self._orig_bbox
            # Get new bbox from handle drag
            pt = self.widget_to_canvas(event.position().toPoint())
            x1, y1, x2, y2 = orig_bbox.left(), orig_bbox.top(), orig_bbox.right(), orig_bbox.bottom()
            idx = self._dragging_handle
            # Update bbox corners/edges
            if idx == 0:  # Top-left
                new_bbox = QRect(pt, QPoint(x2, y2)).normalized()
            elif idx == 1:  # Top-middle
                new_bbox = QRect(QPoint(x1, pt.y()), QPoint(x2, y2)).normalized()
            elif idx == 2:  # Top-right
                new_bbox = QRect(QPoint(x1, pt.y()), QPoint(pt.x(), y2)).normalized()
            elif idx == 3:  # Right-middle
                new_bbox = QRect(QPoint(x1, y1), QPoint(pt.x(), y2)).normalized()
            elif idx == 4:  # Bottom-right
                new_bbox = QRect(QPoint(x1, y1), pt).normalized()
            elif idx == 5:  # Bottom-middle
                new_bbox = QRect(QPoint(x1, y1), QPoint(x2, pt.y())).normalized()
            elif idx == 6:  # Bottom-left
                new_bbox = QRect(QPoint(pt.x(), y1), QPoint(x2, pt.y())).normalized()
            elif idx == 7:  # Left-middle
                new_bbox = QRect(QPoint(pt.x(), y1), QPoint(x2, y2)).normalized()
            else:
                new_bbox = QRect(orig_bbox)
            # Scale all points from orig_bbox to new_bbox
            def scale_point(p):
                ox, oy = orig_bbox.left(), orig_bbox.top()
                ow = orig_bbox.width() or 1
                oh = orig_bbox.height() or 1
                nx, ny = new_bbox.left(), new_bbox.top()
                nw = new_bbox.width() or 1
                nh = new_bbox.height() or 1
                rx = (p.x() - ox) / ow
                ry = (p.y() - oy) / oh
                return QPoint(int(nx + rx * nw), int(ny + ry * nh))
            self.preview_start = [scale_point(p) for p in points]
            self.preview_bbox = QRect(new_bbox)
            self.update()
            return

        elif self._dragging_box and self.preview_shape == "draw" and isinstance(self.preview_start, list):
            # Move freehand: offset all points by mouse delta
            points = self._orig_points
            orig_bbox = self._orig_bbox
            pt = self.widget_to_canvas(event.position().toPoint())
            margin = 8
            draw_margin = max(self.draw_radius, margin)
            box_rect = orig_bbox.adjusted(-draw_margin, -draw_margin, draw_margin, draw_margin)
            offset = pt - self._drag_offset
            delta = offset - box_rect.topLeft()
            self.preview_start = [p + delta for p in points]
            self.preview_bbox = orig_bbox.translated(delta)
            self.update()
            return

        if self._dragging_handle is not None:
            rotation = getattr(self, 'preview_rotation', 0)
            handle = self._dragging_handle

            if rotation and getattr(self, '_drag_anchor_world', None) is not None:
                if handle in (0, 2, 4, 6):
                    # Corner handles: C = midpoint of anchor-world and mouse gives exact fix
                    new_center = QPoint(
                        (self._drag_anchor_world.x() + pt.x()) // 2,
                        (self._drag_anchor_world.y() + pt.y()) // 2
                    )
                    anchor_local = self._to_local(self._drag_anchor_world, rotation, new_center)
                    dragged_local = self._to_local(pt, rotation, new_center)
                    if handle == 0:    # TL dragged, BR anchor
                        self.preview_start = dragged_local
                        self.preview_end = anchor_local
                    elif handle == 2:  # TR dragged, BL anchor
                        self.preview_start = QPoint(anchor_local.x(), dragged_local.y())
                        self.preview_end = QPoint(dragged_local.x(), anchor_local.y())
                    elif handle == 4:  # BR dragged, TL anchor
                        self.preview_start = anchor_local
                        self.preview_end = dragged_local
                    elif handle == 6:  # BL dragged, TR anchor
                        self.preview_start = QPoint(dragged_local.x(), anchor_local.y())
                        self.preview_end = QPoint(anchor_local.x(), dragged_local.y())
                else:
                    # Middle handles: constrain to one axis, then correct anchor drift
                    origin = getattr(self, '_drag_origin_center', None)
                    rect = QRect(self.preview_start, self.preview_end)
                    if origin is None:
                        origin = rect.center()
                    pt_local = self._to_local(pt, rotation, origin)
                    x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
                    if handle == 1:
                        self.preview_start = QPoint(x1, pt_local.y())
                        self.preview_end = QPoint(x2, y2)
                    elif handle == 3:
                        self.preview_start = QPoint(x1, y1)
                        self.preview_end = QPoint(pt_local.x(), y2)
                    elif handle == 5:
                        self.preview_start = QPoint(x1, y1)
                        self.preview_end = QPoint(x2, pt_local.y())
                    elif handle == 7:
                        self.preview_start = QPoint(pt_local.x(), y1)
                        self.preview_end = QPoint(x2, y2)
                    # Anchor correction: prevent the opposite edge from drifting in world space
                    ps, pe = self.preview_start, self.preview_end
                    xm = (ps.x() + pe.x()) // 2
                    ym = (ps.y() + pe.y()) // 2
                    _amap = {1: QPoint(xm, pe.y()), 3: QPoint(ps.x(), ym),
                             5: QPoint(xm, ps.y()), 7: QPoint(pe.x(), ym)}
                    ac = _amap.get(handle)
                    if ac:
                        cur_w = self._from_local(ac, rotation, QRect(ps, pe).center())
                        dx = self._drag_anchor_world.x() - cur_w.x()
                        dy = self._drag_anchor_world.y() - cur_w.y()
                        self.preview_start = QPoint(ps.x() + dx, ps.y() + dy)
                        self.preview_end   = QPoint(pe.x() + dx, pe.y() + dy)
            else:
                # Non-rotated: original logic unchanged
                self.set_resize_cursor(handle)
                rect = QRect(self.preview_start, self.preview_end)
                x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
                if handle == 0:
                    self.preview_start = pt;          self.preview_end = QPoint(x2, y2)
                elif handle == 1:
                    self.preview_start = QPoint(x1, pt.y()); self.preview_end = QPoint(x2, y2)
                elif handle == 2:
                    self.preview_start = QPoint(x1, pt.y()); self.preview_end = QPoint(pt.x(), y2)
                elif handle == 3:
                    self.preview_start = QPoint(x1, y1);     self.preview_end = QPoint(pt.x(), y2)
                elif handle == 4:
                    self.preview_start = QPoint(x1, y1);     self.preview_end = pt
                elif handle == 5:
                    self.preview_start = QPoint(x1, y1);     self.preview_end = QPoint(x2, pt.y())
                elif handle == 6:
                    self.preview_start = QPoint(pt.x(), y1); self.preview_end = QPoint(x2, pt.y())
                elif handle == 7:
                    self.preview_start = QPoint(pt.x(), y1); self.preview_end = QPoint(x2, y2)
            self.update()
            return

        if self._free_rotating and self.selected_shape_index is not None:
            idx = self.selected_shape_index
            shape = self.shapes[idx]
            if shape[0] == "draw" and isinstance(shape[1], list):
                points = self._orig_points if hasattr(self, "_orig_points") and self._orig_points else shape[1]
                min_x = min(p.x() for p in points)
                min_y = min(p.y() for p in points)
                max_x = max(p.x() for p in points)
                max_y = max(p.y() for p in points)
                center = QPoint((min_x + max_x) // 2, (min_y + max_y) // 2)
                dx = pt.x() - center.x()
                dy = pt.y() - center.y()
                angle = math.degrees(math.atan2(dy, dx))
                delta_angle = angle - self._rotation_start_angle
                new_rotation = (self._rotation_initial + delta_angle) % 180
                # Rotate points for preview
                rotated_points = self.rotate_points(points, new_rotation, center)
                self.preview_start = [QPoint(p) for p in rotated_points]
                # Update bounding box for handles
                min_x = min(p.x() for p in rotated_points)
                min_y = min(p.y() for p in rotated_points)
                max_x = max(p.x() for p in rotated_points)
                max_y = max(p.y() for p in rotated_points)
                self.preview_bbox = QRect(QPoint(min_x, min_y), QPoint(max_x, max_y)).normalized()
                self.preview_rotation = new_rotation
                self.update()
            else:
                # Free rotate for other shapes
                # For non-draw shapes, only update preview_rotation
                orig_start = getattr(self, "_orig_start", shape[1])
                orig_end = getattr(self, "_orig_end", shape[2])
                rect = QRect(orig_start, orig_end).normalized()
                center = rect.center()
                dx = pt.x() - center.x()
                dy = pt.y() - center.y()
                angle = math.degrees(math.atan2(dy, dx))
                delta_angle = angle - self._rotation_start_angle
                new_rotation = (self._rotation_initial + delta_angle) % 360
                self.preview_rotation = new_rotation

                # Do NOT rotate preview_start/end!
                self.preview_start = orig_start
                self.preview_end = orig_end
                self.update()
                return

        elif self._dragging_box:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            pt = self.widget_to_canvas(event.position().toPoint())
            margin = 8
            # Only do this for non-draw shapes
            if self.preview_shape != "draw" and self.preview_start is not None and self.preview_end is not None:
                rect = QRect(self.preview_start, self.preview_end).normalized()
                box_rect = rect.adjusted(-margin, -margin, margin, margin)
                offset = pt - self._drag_offset
                size = box_rect.size()
                # Move the box, but update preview_start/end to match the new box_rect minus margin
                new_box_rect = QRect(offset, size)
                new_shape_rect = new_box_rect.adjusted(margin, margin, -margin, -margin)
                self.preview_start = new_shape_rect.topLeft()
                self.preview_end = new_shape_rect.bottomRight()
                self.update()
                return

        else:
            # Only run this if not drawing or editing a "draw" shape
            if self.current_tool != "draw" and self.preview_shape != "draw":
                if self.preview_start is not None and self.preview_end is not None:
                    rect = QRect(self.preview_start, self.preview_end).normalized()
                    box_rect = rect.adjusted(-margin, -margin, margin, margin)
                    for idx, handle in enumerate(self.handle_points(box_rect)):
                        hit_size = max(64, self.HANDLE_SIZE * 2)
                        handle_rect = QRect(
                            handle.x() - hit_size // 2,
                            handle.y() - hit_size // 2,
                            hit_size,
                            hit_size
                        )
                        if handle_rect.contains(pt):
                            self.set_resize_cursor(idx)
                            break
                    else:
                        if box_rect.contains(pt):
                            self.setCursor(Qt.CursorShape.OpenHandCursor)
                        elif self.current_tool:
                            self.setCursor(Qt.CursorShape.CrossCursor)
                        else:
                            self.setCursor(Qt.CursorShape.ArrowCursor)

        if self.current_tool == "draw" and getattr(self, "drawing", False):
            self.freehand_points.append(pt)
            self.setCursor(self._draw_cursor)
            self.update()
            return

        if self.current_tool == "eraser" and self._erasing:
            self._current_eraser_points.append(pt)
            self.erase_at_point(pt)
            self.update()
            return

        if self.current_tool == "crop" and self.cropping:
            self.crop_end = pt
            self.update()
            return

        if self.preview_shape:
            pt = self.widget_to_canvas(event.position().toPoint())
            self.preview_end = pt
            self.update()

    def mouseReleaseEvent(self, event):

        if self._free_rotating:
            if event.button() != Qt.MouseButton.LeftButton:
                return
            self._free_rotating = False
            idx = self.selected_shape_index
            if idx is not None and 0 <= idx < len(self.shapes):
                self.push_shape_restore(idx, "Free Rotate")
                self.push_undo()
                shape = self.shapes[idx]
                if self.preview_shape == "draw" and isinstance(self.preview_start, list):
                    old_shape = self.shapes[idx]
                    draw_radius = old_shape[4] if len(old_shape) > 4 and isinstance(old_shape[4], (int, float)) else self.draw_radius
                    draw_color = old_shape[3] if len(old_shape) > 3 and isinstance(old_shape[3], QColor) else self.shape_color
                    self.shapes[idx] = (
                        "draw",
                        [QPoint(p) for p in self.preview_start],
                        None,
                        draw_color,
                        draw_radius,
                    )
                else:
                    # Save rotation for other shapes, preserve all properties
                    tool, start, end, border_color = shape[:4]
                    fill_color = None
                    extra_dicts = []
                    lock_flag = None
                    for item in shape[4:]:
                        if isinstance(item, QColor):
                            fill_color = item
                        elif isinstance(item, bool):
                            lock_flag = item
                        elif isinstance(item, dict):
                            extra_dicts.append(item)
                    rotation = getattr(self, 'preview_rotation', 0)
                    new_shape = [tool, start, end, border_color]
                    if fill_color is not None:
                        new_shape.append(fill_color)
                    new_shape.append(rotation)
                    for d in extra_dicts:
                        new_shape.append(d)
                    if lock_flag is not None:
                        new_shape.append(lock_flag)
                    self.shapes[idx] = tuple(new_shape)

            self.update()
            return

        self._dragging_handle = None

        if self.preview_shape == "draw" and isinstance(self.preview_start, list):
            # Commit edit if handle/box drag finished
            if self.selected_shape_index is not None:
                self.push_shape_restore(self.selected_shape_index, self._pending_shape_action or "Edit")
                self._pending_shape_action = None
                self.push_undo()
                old_shape = self.shapes[self.selected_shape_index]
                draw_radius = old_shape[4] if len(old_shape) > 4 and isinstance(old_shape[4], (int, float)) else self.draw_radius
                draw_color  = old_shape[3] if len(old_shape) > 3 and isinstance(old_shape[3], QColor) else self.shape_color
                rotation    = old_shape[5] if len(old_shape) > 5 and isinstance(old_shape[5], (int, float)) else 0
                shape_tuple = ["draw", [QPoint(p) for p in self.preview_start], None, draw_color, draw_radius]
                if rotation != 0:
                    shape_tuple.append(rotation)
                self.shapes[self.selected_shape_index] = tuple(shape_tuple)
            else:
                # Commit new/pasted freehand shape
                if self.preview_start and len(self.preview_start) > 1:
                    self.push_undo()
                    border_color = getattr(self, "preview_color", self.shape_color)
                    draw_radius = getattr(self, "preview_draw_radius", self.draw_radius)
                    rotation = getattr(self, "preview_rotation", 0)

                    shape_tuple = [
                        "draw",
                        [QPoint(p) for p in self.preview_start],
                        None,
                        border_color,
                        draw_radius
                    ]
                    if rotation != 0:
                        shape_tuple.append(rotation)
                    self.shapes.append(tuple(shape_tuple))

            self._dragging_handle = None
            self._dragging_box = False
            self._orig_bbox = None
            self._orig_points = None

            # Clean up temporary tracking variables
            if hasattr(self, '_original_crop_rect'):
                delattr(self, '_original_crop_rect')
            if hasattr(self, '_start_drag_point'):
                delattr(self, '_start_drag_point')

            if self.selected_shape_index is not None:
                # After editing an existing shape, use Arrow cursor for further editing
                self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                # After placing a new freehand, keep draw cursor if tool is still active
                if self.current_tool == "draw":
                    self.setCursor(self._draw_cursor)
                else:
                    self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()
            return

        self._dragging_box = False
        if self.current_tool == "eraser":
            pixmap = QPixmap(r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-colors-eraser.png")
            if not pixmap.isNull():
                size = self.eraser_radius * 2
                cursor_pix = pixmap.scaled(size, size)
                self.setCursor(QCursor(cursor_pix, size // 2, size // 2))
            else:
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        elif self.current_tool:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        if self.current_tool == "draw" and getattr(self, "drawing", False):
            self.drawing = False
            if hasattr(self, "freehand_points") and len(self.freehand_points) > 1:
                self.push_undo()
                self.shapes.append(("draw", self.freehand_points[:], None, self.shape_color, self.draw_radius))

            self.freehand_points = []
            self.setCursor(self._draw_cursor)
            self.update()
            return

        if self.current_tool == "crop" and self.cropping:
            self.cropping = False
            self.crop_preview_mode = True
            self._crop_dragging_handle = None
            self._dragging_box = False
            self.update()
            return

        if self._crop_dragging_handle is not None:
            self._crop_dragging_handle = None
            if hasattr(self, '_original_crop_rect'):
                delattr(self, '_original_crop_rect')
            if hasattr(self, '_start_drag_point'):
                delattr(self, '_start_drag_point')
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()
            return

        # Clean up crop box dragging
        if self.crop_preview_mode and self._dragging_box:
            self._dragging_box = False
            if hasattr(self, '_original_crop_rect'):
                delattr(self, '_original_crop_rect')
            if hasattr(self, '_start_drag_point'):
                delattr(self, '_start_drag_point')
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()
            return

        if self.current_tool == "eraser" and self._erasing:
            if len(self._current_eraser_points) > 1:
                self.eraser_strokes.append(list(self._current_eraser_points))
            self._erasing = False
            self._current_eraser_points = []
            # clear any per-image erase cache (we updated pixmaps while erasing)
            self._image_erase_cache.clear()
            self.update()
            return

        if self.drawing:
            pt = self.widget_to_canvas(event.position().toPoint())
            self.end_point = pt
            self.shapes.append((self.current_tool, self.start_point, self.end_point))
            self.drawing = False
            self.start_point = None
            self.end_point = None
            self.update()

    def set_resize_cursor(self, idx):
        # idx: 0-7 for 8 handles (corners and edges)
        # Map to appropriate resize cursors
        cursors = [
            Qt.CursorShape.SizeFDiagCursor,   # Top-left
            Qt.CursorShape.SizeVerCursor,     # Top-middle
            Qt.CursorShape.SizeBDiagCursor,   # Top-right
            Qt.CursorShape.SizeHorCursor,     # Right-middle
            Qt.CursorShape.SizeFDiagCursor,   # Bottom-right
            Qt.CursorShape.SizeVerCursor,     # Bottom-middle
            Qt.CursorShape.SizeBDiagCursor,   # Bottom-left
            Qt.CursorShape.SizeHorCursor,     # Left-middle
        ]
        if 0 <= idx < len(cursors):
            self.setCursor(cursors[idx])

    def paintEvent(self, event):
        super().paintEvent(event)
        # print("Current shapes:", self.shapes)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.save()

        # Center and zoom everything (canvas and shapes)
        center = self.get_canvas_center()
        painter.translate(center + self.pan_offset)
        painter.scale(self.scale_factor, self.scale_factor)
        painter.translate(-self.a4_size.width() // 2, -self.a4_size.height() // 2)

        # Draw the A4 canvas (white paper)
        painter.setBrush(QColor("white"))
        painter.setPen(QPen(QColor("#bbbbbb"), 3))
        painter.drawRect(0, 0, self.a4_size.width(), self.a4_size.height())

        # Draw shapes, but skip the one being edited (if any)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Draw all shapes (including images)
        for idx, shape in enumerate(self.shapes):
            tool, start, end, data = shape[:4]
            rotation = 0
            draw_width = 3
            if tool == "draw":
                if len(shape) > 4 and isinstance(shape[4], (int, float)):
                    draw_width = shape[4]
                if len(shape) > 5 and isinstance(shape[5], (int, float)):
                    rotation = shape[5]
            else:
                for item in shape[4:]:
                    if isinstance(item, (int, float)) and not isinstance(item, bool):
                        rotation = item

                # Extract per-shape border weight from dict element
                border_weight = 2
                border_radius = None
                for item in shape[4:]:
                    if isinstance(item, dict) and "border_weight" in item:
                        border_weight = item["border_weight"]
                    if isinstance(item, dict) and "border_radius" in item:
                        border_radius = item["border_radius"]

            if self.selected_shape_index is not None and idx == self.selected_shape_index and self.preview_shape:
                continue  # Skip the one being edited
            painter.save()

            if tool == "image" and isinstance(data, QPixmap):
                rect = QRect(start, end).normalized()
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                if rotation and rect is not None:
                    painter.translate(rect.center())
                    painter.rotate(rotation)
                    painter.translate(-rect.center())
                painter.drawPixmap(rect, data)
            else:
                color = data if isinstance(data, QColor) else QColor("#000000")
                fill_color = None
                if len(shape) > 4 and isinstance(shape[4], QColor):
                    fill_color = shape[4]
                if tool == "draw":
                    points = start
                    if not isinstance(points, list) or len(points) < 2:
                        painter.restore()
                        continue
                    painter.setPen(QPen(color, draw_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                    painter.drawPolyline(*points)
                else:
                    rect = QRect(start, end).normalized()
                    if rotation and rect is not None:
                        painter.translate(rect.center())
                        painter.rotate(rotation)
                        painter.translate(-rect.center())
                    # Draw fill first if present
                    if fill_color:
                        painter.setBrush(QBrush(fill_color))
                        painter.setPen(Qt.PenStyle.NoPen)
                        self.draw_shape(painter, tool, rect.topLeft(), rect.bottomRight(), border_radius=border_radius)
                    # Draw border
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.setPen(QPen(color, border_weight if border_weight is not None else 3))
                    self.draw_shape(painter, tool, rect.topLeft(), rect.bottomRight(), line_width=border_weight, border_radius=border_radius)
            painter.restore()

        if self.current_tool == "draw" and getattr(self, "drawing", False):
            if hasattr(self, "freehand_points") and len(self.freehand_points) > 1:
                painter.setPen(QPen(self.shape_color, self.draw_radius, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                painter.drawPolyline(*self.freehand_points)

        # Draw crop selection
        if (self.current_tool == "crop" and self.crop_start is not None and 
            self.crop_end is not None and (self.cropping or self.crop_preview_mode)):
            crop_rect = QRect(self.crop_start, self.crop_end).normalized()

            # Draw dashed selection rectangle
            crop_pen = QPen(QColor("#000"), 1, Qt.PenStyle.DashLine)
            painter.setPen(crop_pen)
            painter.drawRect(crop_rect)

            # Draw handles if in preview mode
            if self.crop_preview_mode:
                for pt in self.handle_points(crop_rect):
                    painter.setBrush(QColor("white"))
                    painter.setPen(QPen(QColor("#000"), 1))
                    painter.drawRect(pt.x() - self.HANDLE_SIZE//2, 
                                    pt.y() - self.HANDLE_SIZE//2, 
                                    self.HANDLE_SIZE, 
                                    self.HANDLE_SIZE)

        # Draw preview shape or image
        elif self.preview_shape and self.preview_start is not None:
            margin = 8
            # For draw tool, preview_start is a list of points
            if self.preview_shape == "draw" and isinstance(self.preview_start, list):
                # Compute bounding rect of points
                points = self.preview_start
                if points and len(points) > 1:
                    min_x = min(p.x() for p in points)
                    min_y = min(p.y() for p in points)
                    max_x = max(p.x() for p in points)
                    max_y = max(p.y() for p in points)
                    rect = QRect(QPoint(min_x, min_y), QPoint(max_x, max_y)).normalized()
                    draw_margin = max(self.draw_radius, margin)
                    box_rect = rect.adjusted(-draw_margin, -draw_margin, draw_margin, draw_margin)
                else:
                    rect = None
                    box_rect = None
            else:
                rect = QRect(self.preview_start, self.preview_end).normalized()
                box_rect = rect.adjusted(-margin, -margin, margin, margin)
            painter.save()
            rotation = getattr(self, 'preview_rotation', 0)
            if isinstance(rotation, (int, float)) and rotation and rect is not None:
                painter.translate(rect.center())
                painter.rotate(rotation)
                painter.translate(-rect.center())
            # Draw bounding box/handles for draw
            if self.preview_shape == "draw" and box_rect:
                box_pen = QPen(QColor("#0078d7"), 2, Qt.PenStyle.DashLine)
                painter.setPen(box_pen)
                painter.drawRect(box_rect)
                # Draw handles
                for pt in self.handle_points(box_rect):
                    painter.setBrush(QColor("white"))
                    painter.setPen(QPen(QColor("#0078d7"), 2))
                    painter.drawRect(pt.x() - self.HANDLE_SIZE//2, pt.y() - self.HANDLE_SIZE//2, self.HANDLE_SIZE, self.HANDLE_SIZE)
            # Only show bounding box/handles if NOT freehand draw
            elif self.preview_shape != "draw" and not self._free_rotating:
                box_pen = QPen(QColor("#0078d7"), 2, Qt.PenStyle.DashLine)
                painter.setPen(box_pen)
                self.draw_bounding_box_and_handles(painter, box_rect)
            if self.preview_shape == "draw" and not self._free_rotating and box_rect:
                # Draw bounding box for freehand
                box_pen = QPen(QColor("#0078d7"), 2, Qt.PenStyle.DashLine)
                painter.setPen(box_pen)
                painter.drawRect(box_rect)
            # Draw preview
            if self.preview_shape == "draw" and isinstance(self.preview_start, list) and len(self.preview_start) > 1:
                preview_pen = QPen(QColor("#ff6600"), 3, Qt.PenStyle.DashLine)
                painter.setPen(preview_pen)
                points = self.preview_start

                painter.drawPolyline(*points)
            elif self.preview_shape == "image" and hasattr(self, "preview_pixmap") and isinstance(self.preview_pixmap, QPixmap):
                painter.drawPixmap(rect, self.preview_pixmap)
            elif self.preview_shape is not None and rect is not None:
                preview_pen = QPen(QColor("#ff6600"), 3, Qt.PenStyle.DashLine)
                painter.setPen(preview_pen)
                self.draw_shape(painter, self.preview_shape, rect.topLeft(), rect.bottomRight())
            painter.restore()

        # Optionally, highlight selected shape if not editing
        if self.selected_shape_index is not None and self.preview_shape is None and 0 <= self.selected_shape_index < len(self.shapes):
            tool, start, end, data = self.shapes[self.selected_shape_index][:4]
            _shape = self.shapes[self.selected_shape_index]
            rotation = 0
            for item in _shape[4:]:
                if isinstance(item, (int, float)) and not isinstance(item, bool):
                    rotation = item

            painter.save()
            highlight_pen = QPen(QColor("#ff6600"), 4, Qt.PenStyle.DashLine)
            painter.setPen(highlight_pen)
            if tool == "draw" and isinstance(start, list) and len(start) > 1:
                # Draw the polyline directly
                painter.drawPolyline(*start)
            else:
                rect = QRect(start, end).normalized()
                if rotation:
                    painter.translate(rect.center())
                    painter.rotate(rotation)
                    painter.translate(-rect.center())
                if tool == "image":
                    painter.drawRect(rect)
                else:
                    self.draw_shape(painter, tool, rect.topLeft(), rect.bottomRight())
            painter.restore()

        painter.restore()

        # Degree indicator during free rotate
        if (getattr(self, "_free_rotating", False) and hasattr(self, "preview_rotation")) or self._show_rotation_indicator:
            painter.save()
            # Find a good spot: near the shape center or mouse
            if self.selected_shape_index is not None:
                shape = self.shapes[self.selected_shape_index]
                if shape[0] == "draw" and isinstance(self.preview_start, list) and self.preview_start:
                    min_x = min(p.x() for p in self.preview_start)
                    min_y = min(p.y() for p in self.preview_start)
                    max_x = max(p.x() for p in self.preview_start)
                    max_y = max(p.y() for p in self.preview_start)
                    center = QPoint((min_x + max_x) // 2, (min_y + max_y) // 2)
                else:
                    rect = QRect(self.preview_start, self.preview_end).normalized()
                    center = rect.center()
                # Draw the angle text
                angle = int(round(self.preview_rotation)) if hasattr(self, "preview_rotation") else 0
                painter.setPen(QPen(QColor("#ff6600"), 2))
                painter.setFont(QFont("Arial", 18, QFont.Weight.Bold))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                text = f"{angle}°"
                text_rect = painter.fontMetrics().boundingRect(text)
                pos = center + QPoint(0, -40)
                painter.drawText(pos.x() - text_rect.width() // 2, pos.y(), text)
            painter.restore()

    def draw_bounding_box_and_handles(self, painter, rect):
        # Draw bounding box
        painter.setPen(QPen(QColor("#0078d7"), 1, Qt.PenStyle.DotLine))
        painter.drawRect(rect)
        # Draw 8 handles (corners + edges)
        for pt in self.handle_points(rect):
            painter.setBrush(QColor("white"))
            painter.setPen(QPen(QColor("#0078d7"), 2))
            painter.drawRect(pt.x() - self.HANDLE_SIZE//2, pt.y() - self.HANDLE_SIZE//2, self.HANDLE_SIZE, self.HANDLE_SIZE)

    # Add method to confirm crop
    def confirm_crop(self):
        if self.crop_preview_mode and self.crop_start is not None and self.crop_end is not None:
            crop_rect = QRect(self.crop_start, self.crop_end).normalized()
            self.crop_to_rect(crop_rect)
            self.cancel_crop()

    # Add method to cancel crop
    def cancel_crop(self):
        self.crop_preview_mode = False
        self.cropping = False
        self.crop_start = None
        self.crop_end = None
        self._crop_dragging_handle = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def handle_points(self, rect):
        x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
        xm, ym = (x1 + x2)//2, (y1 + y2)//2
        return [
            QPoint(x1, y1), QPoint(xm, y1), QPoint(x2, y1),  # Top: left, mid, right
            QPoint(x2, ym),                                 # Right mid
            QPoint(x2, y2), QPoint(xm, y2), QPoint(x1, y2), # Bottom: right, mid, left
            QPoint(x1, ym),                                 # Left mid
        ][:8]  # Only 8 handles!

    def draw_shape(self, painter, tool, start, end, line_width=None, border_radius=None):
        if line_width is None:
            line_width = self.tool_sizes.get('shapes' if tool not in ['line'] else 'line', 2)
        painter.setPen(QPen(painter.pen().color(), line_width))
        if tool == "draw":
            # Polyline drawing
            if isinstance(start, list) and len(start) > 1:
                painter.drawPolyline(*start)
            return  # Don't try to create a QRect for draw

        rect = QRect(start, end).normalized()
        if tool == "circle":
            painter.drawEllipse(rect)
        elif tool == "rect":
            if border_radius:
                painter.drawRoundedRect(rect, border_radius, border_radius)
            else:
                painter.drawRect(rect)
        elif tool == "line":
            painter.drawLine(start, end)
        elif tool == "triangle":
            x1, y1 = rect.left(), rect.top()
            x2, y2 = rect.right(), rect.bottom()
            points = [
                QPoint((x1 + x2) // 2, y1),  # Top center
                QPoint(x1, y2),              # Bottom left
                QPoint(x2, y2)               # Bottom right
            ]
            painter.drawPolygon(*points)
        elif tool == "cross":
            painter.drawLine(rect.topLeft(), rect.bottomRight())
            painter.drawLine(rect.bottomLeft(), rect.topRight())
        elif tool == "roundrect":
            r = border_radius if border_radius is not None else 18
            painter.drawRoundedRect(rect, r, r)

    def widget_to_canvas(self, pos):
        """Convert widget coordinates to canvas coordinates, considering zoom and centering."""
        center = self.get_canvas_center()
        # Subtract pan_offset here!
        x = (pos.x() - center.x() - self.pan_offset.x()) / self.scale_factor + self.a4_size.width() / 2
        y = (pos.y() - center.y() - self.pan_offset.y()) / self.scale_factor + self.a4_size.height() / 2
        return QPoint(int(x), int(y))

    def canvas_contains(self, pt):
        """Check if a canvas point is inside the A4 canvas."""
        return QRect(0, 0, self.a4_size.width(), self.a4_size.height()).contains(pt)

    def clamp_pan_offset(self):
        """Ensure the canvas cannot be panned completely out of view."""
        widget_w, widget_h = self.width(), self.height()
        canvas_w = self.a4_size.width() * self.scale_factor
        canvas_h = self.a4_size.height() * self.scale_factor

        # If canvas is smaller than widget, center it (no panning allowed)
        if canvas_w <= widget_w:
            px = 0
        else:
            max_pan_x = (canvas_w - widget_w) // 2
            px = max(-max_pan_x, min(self.pan_offset.x(), max_pan_x))

        if canvas_h <= widget_h:
            py = 0
        else:
            max_pan_y = (canvas_h - widget_h) // 2
            py = max(-max_pan_y, min(self.pan_offset.y(), max_pan_y))

        self.pan_offset = QPoint(int(px), int(py))

    def keyPressEvent(self, event):

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_C:
            if (
                self.selected_shape_index is not None
                and 0 <= self.selected_shape_index < len(self.shapes)
            ):
                self.copy_selected_shape_to_clipboard()
            return

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            clipboard = QApplication.clipboard()
            mime = clipboard.mimeData()
            text = clipboard.text()
            if mime.hasImage():
                self.paste_image_from_clipboard()
            elif self._is_shape_json(text):
                self.paste_shape_from_clipboard()
            return

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_E:
            if self.shape_layers_overlay.isVisible():
                self.shape_layers_overlay.setVisible(False)
            else:
                self.show_shape_layers_overlay()
            return

        # Delete key: Delete selected shape
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_shape()
            return

        if event.key() == Qt.Key.Key_Escape:
            if self.crop_preview_mode:
                self.cancel_crop()
                return
            # Deselect locked shape on Escape
            if self.selected_shape_index is not None and self.preview_shape is None:
                self.selected_shape_index = None
                self._edit_locked_color = None
                self.update()
                return

        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.crop_preview_mode:
                self.confirm_crop()
                return

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Z:
                self.undo()
                return
            elif event.key() == Qt.Key.Key_Y:
                self.redo()
                return

        super().keyPressEvent(event)

    def show_shape_layers_overlay(self):
        self.shape_layers_overlay.update_shapes(self.shapes)
        self.shape_layers_overlay.selected_idx = None
        self.shape_layers_overlay.refresh()
        self.shape_layers_overlay.setVisible(True)
        self.shape_layers_overlay.raise_()
        self.shape_layers_overlay.setEnabled(True)

    def select_shape_by_index(self, idx):
        if idx is None or idx < 0 or idx >= len(self.shapes):
            # deselect
            self.selected_shape_index = None
            self.preview_shape = None
            self.preview_start = None
            self.preview_end = None
            self.shape_layers_overlay.setVisible(False)
            self.current_tool = None
            self._edit_locked_color = None
            self.update()
            return

        # PREVENT SELECTION OF LOCKED SHAPES
        if self.is_shape_locked(idx):
            self.selected_shape_index = idx
            self.preview_shape = None
            self.preview_start = None
            self.preview_end = None
            self.preview_rotation = 0
            self.shape_layers_overlay.setVisible(False)
            self.current_tool = None
            self._edit_locked_color = None
            self.update()
            return
        self.selected_shape_index = idx
        self.shape_layers_overlay.setVisible(False)
        self.current_tool = None
        shape = self.shapes[idx]
        tool, start, end, data = shape[:4]

        # Extract fill_color and rotation robustly
        fill_color = None
        rotation = 0
        if tool == "draw":
            if len(shape) > 5 and isinstance(shape[5], (int, float)):
                rotation = shape[5]
            if len(shape) > 4 and isinstance(shape[4], QColor):
                fill_color = shape[4]
            self.preview_shape = "draw"
            self.preview_start = [QPoint(p) for p in start]
            self.preview_end = None
            self.preview_bbox = QRect(QPoint(min(p.x() for p in start), min(p.y() for p in start)),
                                     QPoint(max(p.x() for p in start), max(p.y() for p in start))).normalized()
            self.preview_rotation = rotation
            self._edit_locked_color = data if isinstance(data, QColor) else QColor("#000000")

        else:
            # For non-draw shapes
            if len(shape) > 4 and isinstance(shape[4], QColor):
                fill_color = shape[4]
            if len(shape) > 5 and isinstance(shape[5], (int, float)):
                rotation = shape[5]
            elif len(shape) > 4 and isinstance(shape[4], (int, float)) and not isinstance(shape[4], bool):
                rotation = shape[4]
            self.preview_shape = tool
            self.preview_start = start
            self.preview_end = end
            self.preview_rotation = rotation
            self.preview_pixmap = data if tool == "image" else None
            self._edit_locked_color = data if isinstance(data, QColor) else QColor("#000000")

        # --- PATCH END ---
        self.shape_selected_for_edit.emit()
        self.update()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        text = clipboard.text()

        # Lock/Unlock
        lock_action = QAction("", self)
        can_lock = (
            self.selected_shape_index is not None
            and 0 <= self.selected_shape_index < len(self.shapes)
        )
        is_locked = self.is_shape_locked(self.selected_shape_index) if can_lock else False
        lock_action.setText("Unlock" if is_locked else "Lock")
        lock_action.setEnabled(can_lock)
        if can_lock:
            if is_locked:
                lock_action.triggered.connect(self.unlock_selected_shape)
            else:
                lock_action.triggered.connect(self.lock_selected_shape)
        menu.addAction(lock_action)
        menu.addSeparator()

        # Undo/Redo
        undo_action = QAction("Undo", self)
        undo_action.setEnabled(bool(self.undo_stack))
        def do_undo():
            self.undo()
            self.update()  
        undo_action.triggered.connect(do_undo)
        menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setEnabled(bool(self.redo_stack))
        def do_redo():
            self.redo()
            self.update()  
        redo_action.triggered.connect(do_redo)
        menu.addAction(redo_action)

        menu.addSeparator()

        # Paste
        paste_action = QAction("Paste", self)
        can_paste = mime.hasImage() or self._is_shape_json(text)
        paste_action.setEnabled(can_paste)
        if mime.hasImage():
            paste_action.triggered.connect(self.paste_image_from_clipboard)
        elif self._is_shape_json(text):
            paste_action.triggered.connect(self.paste_shape_from_clipboard)
        menu.addAction(paste_action)

        # Copy
        copy_action = QAction("Copy", self)
        can_copy = (
            self.selected_shape_index is not None
            and 0 <= self.selected_shape_index < len(self.shapes)
        )
        copy_action.setEnabled(can_copy)
        if can_copy:
            if self.shapes[self.selected_shape_index][0] == "image":
                copy_action.triggered.connect(self.copy_selected_image_to_clipboard)
            else:
                copy_action.triggered.connect(self.copy_selected_shape_to_clipboard)
        menu.addAction(copy_action)

        # Rotate
        rotate_action = QAction("Rotate 90°", self)
        can_rotate = (
            self.selected_shape_index is not None
            and 0 <= self.selected_shape_index < len(self.shapes)
            and self.shapes[self.selected_shape_index][0] not in ["image", "draw"]
            and not self.is_shape_locked(self.selected_shape_index)
        )
        rotate_action.setEnabled(can_rotate)
        if can_rotate:
            rotate_action.triggered.connect(self.rotate_selected_shape)
        menu.addAction(rotate_action)

        # Free Rotate
        free_rotate_action = QAction("Free Rotate", self)
        can_rotate = (
            self.selected_shape_index is not None
            and 0 <= self.selected_shape_index < len(self.shapes)
            and not self.is_shape_locked(self.selected_shape_index)
        )
        free_rotate_action.setEnabled(can_rotate)
        if can_rotate:
            free_rotate_action.triggered.connect(self.start_free_rotate)
        menu.addAction(free_rotate_action)

        # Delete
        delete_action = QAction("Delete", self)
        can_delete = (
            self.selected_shape_index is not None
            and 0 <= self.selected_shape_index < len(self.shapes)
            and not self.is_shape_locked(self.selected_shape_index)
        )
        delete_action.setEnabled(can_delete)
        if can_delete:
            delete_action.triggered.connect(self.delete_selected_shape)
        menu.addAction(delete_action)

        menu.addSeparator()

        # Properties
        properties_action = QAction("Properties", self)
        can_properties = (
            self.selected_shape_index is not None
            and 0 <= self.selected_shape_index < len(self.shapes)
            and self.shapes[self.selected_shape_index][0] not in ["image", "draw"]
            and not self.is_shape_locked(self.selected_shape_index)
        )
        properties_action.setEnabled(can_properties)
        menu.addAction(properties_action)

        def show_properties():
            idx = self.selected_shape_index
            if idx is None:
                return

            shape = self.shapes[idx]
            tool = shape[0]

            # Extract current properties
            border_color = "#000000"
            fill_color = "#ffffff"
            # Read border weight from shape's stored dict
            border_weight = 2
            for item in shape[4:]:
                if isinstance(item, dict) and "border_weight" in item:
                    border_weight = item["border_weight"]
                    break

            # Safely extract border color (always at index 3)
            if len(shape) > 3 and isinstance(shape[3], QColor):
                border_color = shape[3].name()

            # Extract fill color and rotation from remaining elements
            fill_color_obj = None
            rotation = 0
            for item in shape[4:]:
                if isinstance(item, QColor):
                    fill_color_obj = item
                elif isinstance(item, (int, float)):
                    rotation = item

            if fill_color_obj:
                fill_color = fill_color_obj.name()

            border_radius = 0
            for item in shape[4:]:
                if isinstance(item, dict) and "border_radius" in item:
                    border_radius = item["border_radius"]
                    break
            if tool == "roundrect" and border_radius == 0:
                border_radius = 18

            dlg = PropertiesDialog(
                self,
                shape_type=tool,
                border_radius=border_radius,
                border_weight=border_weight,
                border_color=border_color,
                fill_color=fill_color,
                drawing_area=self,
                shape_idx=idx,
            )

            def apply_props(props):
                idx = self.selected_shape_index
                if idx is None or idx >= len(self.shapes):
                    return

                old_shape = self.shapes[idx]
                tool, start, end = old_shape[0], old_shape[1], old_shape[2]

                new_border_color = props["border_color"]
                new_object_color = props["object_color"]
                new_border_weight = props["border_weight"]
                new_border_radius = props.get("border_radius", 0)

                if not isinstance(new_border_color, QColor):
                    new_border_color = QColor(new_border_color)

                # Detect what changed for the restore point label
                changed_parts = []
                old_bc = QColor(border_color) if isinstance(border_color, str) else border_color
                if new_border_color.name() != old_bc.name():
                    changed_parts.append("Border Color")

                old_fc_name = fill_color_obj.name() if fill_color_obj else "#ffffff"
                new_oc_name = new_object_color.name() if isinstance(new_object_color, QColor) else "#ffffff"
                if new_oc_name != old_fc_name:
                    changed_parts.append("Object Color")

                if new_border_weight != border_weight:
                    changed_parts.append("Border Weight")

                if new_border_radius != border_radius:
                    changed_parts.append("Border Radius")

                action_label = ("Change " + " & ".join(changed_parts)) if changed_parts else "Properties Applied"

                # Record per-shape restore point (before the change)
                self.push_shape_restore(idx, action_label)
                # Record global undo snapshot
                self.push_undo()

                existing_fill_color = None
                existing_rotation = 0
                for item in old_shape[4:]:
                    if isinstance(item, QColor):
                        existing_fill_color = item
                    elif isinstance(item, (int, float)):
                        existing_rotation = item

                new_shape = [tool, start, end, new_border_color]

                if (
                    isinstance(new_object_color, QColor)
                    and new_object_color.name() != "#ffffff"
                ):
                    new_shape.append(new_object_color)
                elif existing_fill_color is not None:
                    new_shape.append(existing_fill_color)

                if existing_rotation != 0:
                    new_shape.append(existing_rotation)

                if new_border_radius:
                    new_shape.append({"border_radius": new_border_radius})

                new_shape.append({"border_weight": new_border_weight})

                if isinstance(old_shape[-1], bool):
                    new_shape.append(old_shape[-1])

                self.shapes[idx] = tuple(new_shape)

                self.preview_shape = None
                self.preview_start = None
                self.preview_end = None
                self.selected_shape_index = None

                self.shape_layers_overlay.update_shapes(self.shapes)
                self.shape_layers_overlay.selected_idx = None
                self.shape_layers_overlay.refresh()
                self.update()

            dlg.properties_applied.connect(apply_props)
            dlg.exec()

        properties_action.triggered.connect(show_properties)

        menu.exec(event.globalPos())
        self.repaint()

    def start_free_rotate(self):
        if self.is_shape_locked(self.selected_shape_index):
            return
        self._free_rotating = True
        idx = self.selected_shape_index
        if idx is not None and 0 <= idx < len(self.shapes):
            shape = self.shapes[idx]
            # Ensure rotation value exists
            if len(shape) == 4:
                self.shapes[idx] = (*shape, 0)
            rotation = 0
            if len(shape) > 5 and isinstance(shape[5], (int, float)):
                rotation = shape[5]
            elif shape[0] != "draw" and len(shape) > 4 and isinstance(shape[4], (int, float)) and not isinstance(shape[4], bool):
                rotation = shape[4]
            self.preview_rotation = rotation
            # For "draw" shapes, rotate preview points if rotation is not zero
            if shape[0] == "draw":
                # Use preview points if available
                points = [QPoint(p) for p in self.preview_start] if self.preview_start is not None else [QPoint(p) for p in shape[1]]
                if rotation:
                    min_x = min(p.x() for p in points)
                    min_y = min(p.y() for p in points)
                    max_x = max(p.x() for p in points)
                    max_y = max(p.y() for p in points)
                    center = QPoint((min_x + max_x) // 2, (min_y + max_y) // 2)
                    rotated_points = self.rotate_points(points, rotation, center)
                    self.preview_start = [QPoint(p) for p in rotated_points]
                    self._orig_points = [QPoint(p) for p in rotated_points]
                else:
                    self.preview_start = [QPoint(p) for p in points]
                    self._orig_points = [QPoint(p) for p in points]
            else:
                # For non-draw shapes, use preview coords if available
                self.preview_start = self.preview_start if self.preview_start is not None else shape[1]
                self.preview_end = self.preview_end if self.preview_end is not None else shape[2]
                self._orig_start = self.preview_start
                self._orig_end = self.preview_end
                self.preview_rotation = rotation
        self.update()

        self.shape_layers_overlay.selected_idx = idx
        self.shape_layers_overlay.refresh()

    def rotate_selected_shape(self):
        if self.is_shape_locked(self.selected_shape_index):
            return
        idx = self.selected_shape_index
        if idx is None or idx < 0 or idx >= len(self.shapes):
            return
        self.push_shape_restore(idx, "Rotate 90°")
        self.push_undo()
        shape = self.shapes[idx]
        tool, start, end, color = self.shapes[idx][:4]

        preview_start = self.preview_start if self.preview_start is not None else start
        preview_end = self.preview_end if self.preview_end is not None else end

        if tool == "draw" and isinstance(start, list) and len(start) > 1:
            # For freehand, rotate points for preview
            min_x = min(p.x() for p in start)
            min_y = min(p.y() for p in start)
            max_x = max(p.x() for p in start)
            max_y = max(p.y() for p in start)
            center = QPoint((min_x + max_x) // 2, (min_y + max_y) // 2)
            angle = 90
            cos_a = math.cos(math.radians(angle))
            sin_a = math.sin(math.radians(angle))
            rotated_points = []
            for p in start:
                x, y = p.x() - center.x(), p.y() - center.y()
                rx = x * cos_a - y * sin_a + center.x()
                ry = x * sin_a + y * cos_a + center.y()
                rotated_points.append(QPoint(int(rx), int(ry)))
            # Set preview
            self.preview_shape = tool
            self.preview_start = [QPoint(p) for p in rotated_points]
            self.preview_end = None
            self.preview_rotation = 0
            self._pending_rotation_commit = 90
        else:
            # For regular shapes, just update preview_rotation
            rect = QRect(preview_start, preview_end).normalized()
            center = rect.center()
            # Extract current rotation
            rotation = 0
            if len(shape) > 5 and isinstance(shape[5], (int, float)):
                rotation = shape[5]
            elif len(shape) > 4 and isinstance(shape[4], (int, float)) and not isinstance(shape[4], bool):
                rotation = shape[4]
            self.preview_shape = tool
            self.preview_start = preview_start
            self.preview_end = preview_end
            self.preview_rotation = (rotation + 90) % 360
            self._pending_rotation_commit = 90

            # Swap width/height for 90-degree rotation
            new_rect = QRect(center.x() - rect.height() // 2, center.y() - rect.width() // 2, rect.height(), rect.width())
            old_shape = self.shapes[idx]
            tool, _, _, color = old_shape[:4]

            # Robustly extract all extra properties by type
            fill_color = None
            rotation = 0
            extra_dicts = []
            lock_flag = None
            for item in old_shape[4:]:
                if isinstance(item, QColor):
                    fill_color = item
                elif isinstance(item, bool):
                    lock_flag = item
                elif isinstance(item, (int, float)):
                    rotation = item
                elif isinstance(item, dict):
                    extra_dicts.append(item)

            new_shape = [tool, new_rect.topLeft(), new_rect.bottomRight(), color]
            if fill_color is not None:
                new_shape.append(fill_color)
            new_shape.append((rotation + 90) % 360)
            for d in extra_dicts:
                new_shape.append(d)
            if lock_flag is not None:
                new_shape.append(lock_flag)
            self.shapes[idx] = tuple(new_shape)

        self.shape_layers_overlay.update_shapes(self.shapes)
        self.shape_layers_overlay.selected_idx = idx
        self.shape_layers_overlay.refresh()
        self._show_rotation_indicator = True
        self._rotation_indicator_timer.start(1800)
        self.update()

        # Hide the indicator and commit the rotation after the timer
        def commit_rotation():
            self._show_rotation_indicator = False
            self.update()
        self._rotation_indicator_timer.timeout.disconnect()
        self._rotation_indicator_timer.timeout.connect(commit_rotation)

    def paste_shape_from_clipboard(self, adjust_mode=False):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        self.push_undo()
        try:
            shape_dict = json.loads(text)
            tool = shape_dict.get("tool")

            # Use the copied shape's original color
            color = QColor(shape_dict.get("color", "#000000"))

            # Get fill color and rotation from copied shape
            fill_color = None
            if "fill_color" in shape_dict:
                fill_color = QColor(shape_dict["fill_color"])

            rotation = shape_dict.get("rotation", 0)
            offset = QPoint(20, 20)

            if tool == "draw" and "points" in shape_dict:
                points = [QPoint(x, y) for x, y in shape_dict["points"]]
                points = [p + offset for p in points]
                self.preview_shape = tool
                self.preview_start = points
                self.preview_end = None
                # Store the copied properties for when we place the shape
                self.preview_color = color
                self.preview_fill_color = fill_color
                self.preview_rotation = rotation
                self.selected_shape_index = None
                self.set_tool("draw")
                if points and len(points) > 1:
                    min_x = min(p.x() for p in points)
                    min_y = min(p.y() for p in points)
                    max_x = max(p.x() for p in points)
                    max_y = max(p.y() for p in points)
                    self.preview_bbox = QRect(QPoint(min_x, min_y), QPoint(max_x, max_y)).normalized()
                else:
                    self.preview_bbox = None
                self.update()
                return
            elif "start" in shape_dict and "end" in shape_dict:
                start = QPoint(*shape_dict["start"]) + offset
                end = QPoint(*shape_dict["end"]) + offset
                self.preview_shape = tool
                self.preview_start = start
                self.preview_end = end
                # Store the copied properties for when we place the shape
                self.preview_color = color
                self.preview_fill_color = fill_color
                self.preview_rotation = rotation
                self.selected_shape_index = None
                self.update()
                return
            else:
                return  # Not a recognized shape
        except Exception:
            pass  # Not a shape, ignore

    def paste_image_from_clipboard(self):
        """Paste image from clipboard without adjust_mode parameter"""
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        if mime.hasImage():
            pixmap = clipboard.pixmap()
            if not pixmap.isNull():
                self.push_undo()
                # Set up preview for placing the image
                self.preview_shape = "image"
                self.preview_pixmap = pixmap
                # Default size for pasted image
                size = QSize(200, 150)
                center = QPoint(400, 300)  # Default center position
                self.preview_start = QPoint(center.x() - size.width()//2, center.y() - size.height()//2)
                self.preview_end = QPoint(center.x() + size.width()//2, center.y() + size.height()//2)
                self.selected_shape_index = None
                self.update()

    def copy_selected_image_to_clipboard(self):
        if self.selected_shape_index is not None:
            tool, start, end, data = self.shapes[self.selected_shape_index][:4]
            if tool == "image":
                clipboard = QApplication.clipboard()
                clipboard.setPixmap(data)

    def _is_shape_json(self, text):
        try:
            shape = json.loads(text)
            if not isinstance(shape, dict) or "tool" not in shape or "color" not in shape:
                return False
            # Accept either start/end or points for freehand
            if ("start" in shape and "end" in shape) or ("points" in shape):
                return True
            return False
        except Exception:
            return False

    def copy_selected_shape_to_clipboard(self):
        if self.selected_shape_index is not None and 0 <= self.selected_shape_index < len(self.shapes):
            shape = self.shapes[self.selected_shape_index]
            tool, start, end, data = shape[:4]

            shape_dict = {
                "tool": tool,
                "color": data.name() if isinstance(data, QColor) else "#000000"  # Use the shape's actual color
            }

            # Handle freehand
            if tool == "draw" and isinstance(start, list):
                shape_dict["points"] = [(p.x(), p.y()) for p in start]
            else:
                shape_dict["start"] = (start.x(), start.y())
                shape_dict["end"] = (end.x(), end.y())

            # Extract ALL properties from the shape tuple
            fill_color = None
            rotation = None

            # Parse the rest of the shape tuple to find fill_color and rotation
            for v in shape[4:]:
                if isinstance(v, QColor):
                    fill_color = v
                elif isinstance(v, (int, float)):
                    rotation = v

            # Store fill color if it exists
            if fill_color is not None:
                shape_dict["fill_color"] = fill_color.name()

            # Store rotation if it exists
            if rotation is not None:
                shape_dict["rotation"] = rotation

            clipboard = QApplication.clipboard()
            clipboard.setText(json.dumps(shape_dict))

    def delete_selected_shape(self):
        if self.selected_shape_index is not None and 0 <= self.selected_shape_index < len(self.shapes):
            if self.is_shape_locked(self.selected_shape_index):
                return  # Cannot delete locked shapes
            self.push_undo()
            self.shapes.pop(self.selected_shape_index)
            self.selected_shape_index = None
            self.preview_shape = None
            self.preview_start = None
            self.preview_end = None
            self.shape_layers_overlay.update_shapes(self.shapes)
            self.update()

    def push_undo(self):
        # Custom copy to avoid deepcopying QPixmap
        new_shapes = []
        for shape in self.shapes:
            tool, start, end, data = shape[:4]
            if tool == "image":
                # QPixmap: shallow copy reference
                new_shapes.append((tool, QPoint(start), QPoint(end), data))
            elif tool == "draw":
                # Copy the list of points
                points_copy = [QPoint(p) for p in start] if isinstance(start, list) else []
                # Copy rotation if present
                if len(shape) > 4:
                    color = QColor(data) if isinstance(data, (QColor, str)) else QColor("#000000")
                    new_shapes.append((tool, points_copy, None, color, shape[4]))
                else:
                    color = QColor(data) if isinstance(data, (QColor, str)) else QColor("#000000")
                    new_shapes.append((tool, points_copy, None, color))
            else:
                # QColor: can be copied; preserve all extra elements (fill_color, rotation, border_weight dict, lock flag)
                color = QColor(data) if isinstance(data, (QColor, str)) else QColor("#000000")
                new_shape = [tool, QPoint(start), QPoint(end), color]
                for item in shape[4:]:
                    if isinstance(item, QColor):
                        new_shape.append(QColor(item))
                    elif isinstance(item, dict):
                        new_shape.append(dict(item))
                    else:
                        new_shape.append(item)
                new_shapes.append(tuple(new_shape))

        eraser_mask_copy = self.eraser_mask.copy()
        eraser_strokes_copy = [list(stroke) for stroke in self.eraser_strokes]

        self.undo_stack.append((new_shapes, eraser_mask_copy, eraser_strokes_copy))
        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append((self.shapes, self.eraser_mask.copy(), [list(s) for s in self.eraser_strokes]))
            shapes, eraser_mask, eraser_strokes = self.undo_stack.pop()
            self.shapes = shapes
            self.eraser_mask = eraser_mask
            self.eraser_strokes = [list(s) for s in eraser_strokes]

            self.selected_shape_index = None
            self.preview_shape = None
            self.preview_start = None
            self.preview_end = None
            self.preview_pixmap = None
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append((self.shapes, self.eraser_mask.copy(), [list(s) for s in self.eraser_strokes]))
            shapes, eraser_mask, eraser_strokes = self.redo_stack.pop()
            self.shapes = shapes
            self.eraser_mask = eraser_mask
            self.eraser_strokes = [list(s) for s in eraser_strokes]
            self.selected_shape_index = None
            self.preview_shape = None
            self.preview_start = None
            self.preview_end = None
            self.preview_pixmap = None
            self.update()
            
    def _copy_single_shape(self, shape):
        tool = shape[0]
        start, end, data = shape[1], shape[2], shape[3]
        if tool == "image":
            return (tool, QPoint(start), QPoint(end), data)  # pixmap is ref-copied
        elif tool == "draw":
            points_copy = [QPoint(p) for p in start] if isinstance(start, list) else []
            color = QColor(data) if isinstance(data, (QColor, str)) else QColor("#000000")
            result = [tool, points_copy, None, color]
            for item in shape[4:]:
                result.append(item)
            return tuple(result)
        else:
            color = QColor(data) if isinstance(data, (QColor, str)) else QColor("#000000")
            new_shape = [tool, QPoint(start), QPoint(end), color]
            for item in shape[4:]:
                if isinstance(item, QColor):
                    new_shape.append(QColor(item))
                elif isinstance(item, dict):
                    new_shape.append(dict(item))
                else:
                    new_shape.append(item)
            return tuple(new_shape)

    def push_shape_restore(self, idx, action_label):
        # Record a per-shape restore point before a properties change
        if idx is None or idx < 0 or idx >= len(self.shapes):
            return
        shape = self.shapes[idx]    
        shape_label = f"{"Object"}{idx + 1}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%SH")
        self.shape_history.append({
            "timestamp": timestamp,
            "shape_idx": idx,
            "shape_label": shape_label,
            "action": action_label,
            "shape_data": self._copy_single_shape(shape),
        })
        if len(self.shape_history) > 100:
            self.shape_history.pop(0)

    def erase_at_point(self, pt):

        radius = self.eraser_radius

        def circle_intersects_rect(center, r, rect):
            cx, cy = center.x(), center.y()
            left, top, right, bottom = rect.left(), rect.top(), rect.right(), rect.bottom()
            closest_x = max(left, min(cx, right))
            closest_y = max(top, min(cy, bottom))
            dx = cx - closest_x
            dy = cy - closest_y
            return (dx*dx + dy*dy) <= (r*r)

        def dist2(a, b):
            dx = a.x() - b.x()
            dy = a.y() - b.y()
            return dx*dx + dy*dy

        erased_any = False
        r2 = radius * radius

        # Iterate reversed so topmost shapes are processed first
        for idx in reversed(range(len(self.shapes))):
            # SKIP LOCKED SHAPES
            if self.is_shape_locked(idx):
                continue
            shape = self.shapes[idx]
            tool = shape[0]

            # FREEHAND polyline: same splitting logic (preserve behavior)
            if tool == "draw" and isinstance(shape[1], list):
                pts = shape[1]
                if not pts:
                    continue
                segments = []
                current_segment = []
                for p in pts:
                    if dist2(p, pt) > r2:
                        current_segment.append(QPoint(p))
                    else:
                        if len(current_segment) >= 2:
                            segments.append(current_segment)
                        current_segment = []
                if len(current_segment) >= 2:
                    segments.append(current_segment)

                if not segments:
                    del self.shapes[idx]
                    erased_any = True
                else:
                    metadata = list(shape[3:]) if len(shape) > 3 else []
                    if len(segments) == 1:
                        new_shape = ("draw", [QPoint(p) for p in segments[0]], None) + tuple(metadata)
                        self.shapes[idx] = new_shape
                        erased_any = True
                    else:
                        del self.shapes[idx]
                        for seg in reversed(segments):
                            new_shape = ("draw", [QPoint(p) for p in seg], None) + tuple(metadata)
                            self.shapes.insert(idx, new_shape)
                        erased_any = True

            # IMAGE: erase into the image (rotation + rect scaling aware)
            elif tool == "image" and isinstance(shape[3], QPixmap):
                start, end = shape[1], shape[2]
                rect = QRect(start, end).normalized()

                # extract rotation if present (image tuple may be ("image", start, end, pixmap, rotation))
                rotation = 0
                if len(shape) > 4 and isinstance(shape[4], (int, float)):
                    rotation = shape[4]

                # Use cached QImage while erasing to avoid repeated convertToFormat cost
                img = self._image_erase_cache.get(idx)
                if img is None:
                    img = shape[3].toImage().convertToFormat(QImage.Format.Format_ARGB32)
                    self._image_erase_cache[idx] = img

                # compute scale from displayed rect -> image pixels
                disp_w = max(1, rect.width())
                disp_h = max(1, rect.height())
                img_w = max(1, img.width())
                img_h = max(1, img.height())
                sx = img_w / disp_w
                sy = img_h / disp_h
                # average scale for radius
                scale_avg = (sx + sy) / 2.0
                radius_px = max(1, int(round(radius * scale_avg)))

                # If rotated, map the canvas point back into image-local coords by inverse rotation
                if rotation:
                    center = rect.center()
                    angle = math.radians(-rotation)  # inverse rotation
                    cos_a = math.cos(angle)
                    sin_a = math.sin(angle)
                    dx = pt.x() - center.x()
                    dy = pt.y() - center.y()
                    ux = dx * cos_a - dy * sin_a + center.x()
                    uy = dx * sin_a + dy * cos_a + center.y()
                    intersects = circle_intersects_rect(QPoint(int(ux), int(uy)), radius, rect)
                    local_fx = (ux - rect.left()) * sx
                    local_fy = (uy - rect.top()) * sy
                else:
                    intersects = circle_intersects_rect(pt, radius, rect)
                    local_fx = (pt.x() - rect.left()) * sx
                    local_fy = (pt.y() - rect.top()) * sy

                if intersects:
                    # clamp to image bounds
                    lx = max(0, min(int(round(local_fx)), img_w - 1))
                    ly = max(0, min(int(round(local_fy)), img_h - 1))

                    # Apply eraser (clear) into the image
                    img_painter = QPainter(img)
                    img_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    img_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                    img_painter.setPen(Qt.PenStyle.NoPen)
                    img_painter.setBrush(QColor(0, 0, 0, 0))
                    img_painter.drawEllipse(QPoint(lx, ly), radius_px, radius_px)
                    img_painter.end()

                    # Keep the edited QImage in the cache (future erases use it)
                    self._image_erase_cache[idx] = img

                    # Replace the pixmap in the shape with the updated image (preserve rotation if present)
                    new_pix = QPixmap.fromImage(img)
                    new_shape = list(shape)
                    new_shape[3] = new_pix
                    # ensure rotation stays in tuple (if originally present)
                    if rotation and (len(shape) <= 4 or not isinstance(shape[4], (int, float))):
                        # append rotation if it wasn't already part of tuple
                        new_shape.append(rotation)
                    self.shapes[idx] = tuple(new_shape)
                    erased_any = True

            # GEOMETRIC shapes: remove if eraser intersects bounding rect
            else:
                start = shape[1]
                end = shape[2]
                rect = QRect(start, end).normalized()
                # Skip if eraser doesn't touch the bounding rect
                if not circle_intersects_rect(pt, radius, rect):
                    continue

                # Extract properties: border color, optional fill and rotation
                rest = list(shape[3:]) if len(shape) > 3 else []
                border_color = QColor("#000000")
                fill_color = None
                rotation = 0
                border_weight = 2
                border_radius = None
                # Robust parsing: collect QColor entries (first = border, second = fill if present)
                qcolors = [v for v in rest if isinstance(v, QColor)]
                nums = [v for v in rest if isinstance(v, (int, float))]
                if qcolors:
                    border_color = qcolors[0]
                    if len(qcolors) > 1:
                        fill_color = qcolors[1]
                # rotation is taken from any numeric value (prefer the last numeric entry)
                if nums:
                    rotation = nums[-1]
                # per-shape border weight and border radius stored in dict element
                for item in rest:
                    if isinstance(item, dict):
                        if "border_weight" in item:
                            border_weight = item["border_weight"]
                        if "border_radius" in item:
                            border_radius = item["border_radius"]

                # HIGH-QUALITY RASTERIZATION (supersampled)
                disp_h = max(1, rect.height())
                disp_w = max(1, rect.width())
                # supersample factor (2x by default) for smoother result; increase to 3 for even higher quality
                ss = 1

                # Border width in display coords (use per-shape weight, fall back to global default)
                border_width_disp = border_weight

                # Scaled pen width in image pixels
                pen_w_px = max(1, int(round(border_width_disp * ss)))

                # Padding (in image pixels) to avoid clipping of stroke/antialiasing
                aa_margin = 1 * ss   # extra antialias margin
                raw_pad = (pen_w_px // 2) + aa_margin
                pad = ((raw_pad + ss - 1) // ss) * ss  # round up to nearest multiple of ss

                img_w = max(1, int(disp_w * ss) + 2 * pad)
                img_h = max(1, int(disp_h * ss) + 2 * pad)

                # Use premultiplied format for nicer alpha compositing
                img = QImage(img_w, img_h, QImage.Format.Format_ARGB32_Premultiplied)
                img.fill(0)  # fully transparent

                painter_img = QPainter(img)
                painter_img.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter_img.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

                # Translate by pad (in device coords) then scale so we can draw using display coords.
                # We translate by pad/ss in "display" coords because we'll scale by ss next.
                painter_img.translate(pad / ss, pad / ss)
                painter_img.scale(ss, ss)

                local_rect = QRect(0, 0, disp_w, disp_h)

                # Draw fill only if the original shape actually had a fill_color
                if fill_color is not None:
                    painter_img.setBrush(QBrush(fill_color))
                    painter_img.setPen(Qt.PenStyle.NoPen)
                    self.draw_shape(painter_img, tool, local_rect.topLeft(), local_rect.bottomRight(), border_radius=border_radius)
                else:
                    painter_img.setBrush(Qt.BrushStyle.NoBrush)

                # Draw border (scale pen width by supersample factor so stroke thickness is preserved)
                pen = QPen(border_color, border_width_disp * 1.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                # Because we already scaled the painter, set pen width in display units (painter.scale handles pixel density)
                pen.setWidthF(border_width_disp)
                painter_img.setPen(pen)
                self.draw_shape(painter_img, tool, local_rect.topLeft(), local_rect.bottomRight(), border_radius=border_radius, line_width=border_weight)
                painter_img.end()

                # Cache the QImage for in-progress erasing so repeated erase calls paint into the same high-res image
                self._image_erase_cache[idx] = img

                # Map canvas eraser point into high-res image pixels (account for pad)
                sx = ss
                sy = ss
                scale_avg = (sx + sy) / 2.0
                radius_px = max(1, int(round(radius * scale_avg)))

                if rotation:
                    center = rect.center()
                    angle = math.radians(-rotation)  # inverse rotation mapping
                    cos_a = math.cos(angle)
                    sin_a = math.sin(angle)
                    dx = pt.x() - center.x()
                    dy = pt.y() - center.y()
                    ux = dx * cos_a - dy * sin_a + center.x()
                    uy = dx * sin_a + dy * cos_a + center.y()
                    local_fx = (ux - rect.left()) * sx + pad
                    local_fy = (uy - rect.top()) * sy + pad
                    intersects = circle_intersects_rect(QPoint(int(ux), int(uy)), radius, rect)
                else:
                    local_fx = (pt.x() - rect.left()) * sx + pad
                    local_fy = (pt.y() - rect.top()) * sy + pad
                    intersects = circle_intersects_rect(pt, radius, rect)

                if intersects:
                    lx = max(0, min(int(round(local_fx)), img_w - 1))
                    ly = max(0, min(int(round(local_fy)), img_h - 1))

                    # Apply eraser (clear) into the high-res image
                    img_painter = QPainter(img)
                    img_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    img_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                    img_painter.setPen(Qt.PenStyle.NoPen)
                    img_painter.setBrush(QColor(0, 0, 0, 0))
                    img_painter.drawEllipse(QPoint(lx, ly), radius_px, radius_px)
                    img_painter.end()

                    # Keep the full high-res image (includes pad on all sides)
                    highres_img = img  # full image (disp_w*ss + 2*pad)
                    self._image_erase_cache[idx] = highres_img

                    # Create pixmap from the high-res image and mark devicePixelRatio so Qt scales correctly
                    new_pix = QPixmap.fromImage(highres_img)
                    try:
                        new_pix.setDevicePixelRatio(float(ss))
                    except Exception:
                        pass

                    # pad is an integer multiple of ss, so display padding is exact integer
                    pad_disp = pad // ss
                    if pad_disp < 0:
                        pad_disp = 0

                    # Expand the original shape rect by the exact pad_disp so the pixmap logical size
                    # and the shape rect align 1:1 (avoids sub-pixel shift / top-left offset).
                    new_start = QPoint(max(0, rect.left() - pad_disp), max(0, rect.top() - pad_disp))
                    new_end = QPoint(
                        min(self.a4_size.width(), rect.right() + pad_disp),
                        min(self.a4_size.height(), rect.bottom() + pad_disp)
                    )

                    # Replace the vector shape by an image shape (preserve rotation flag so future draws/erases remain correct)
                    new_shape = ("image", new_start, new_end, new_pix, rotation)
                    self.shapes[idx] = new_shape
                    erased_any = True

        if erased_any:
            # update layer overlay / UI state
            self.shape_layers_overlay.update_shapes(self.shapes)

        self.update()

    def fill_at_point(self, pt):

        def rotate_point(p, angle, center):
            # Rotate point p by -angle degrees around center
            angle_rad = math.radians(-angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            x, y = p.x() - center.x(), p.y() - center.y()
            rx = x * cos_a - y * sin_a + center.x()
            ry = x * sin_a + y * cos_a + center.y()
            return QPoint(int(rx), int(ry))

        def is_on_border(tool, start, end, pt, tolerance=8, rotation=0):
            # If start/end are not QPoint, it's not a geometric shape border
            if not isinstance(start, QPoint) or not isinstance(end, QPoint):
                return False
            rect = QRect(start, end).normalized()
            # If rotated, test against inverse-rotated point
            test_pt = pt
            if rotation:
                center = rect.center()
                test_pt = rotate_point(pt, rotation, center)
            if tool == "rect" or tool == "roundrect":
                left = abs(test_pt.x() - rect.left()) < tolerance and rect.top() <= test_pt.y() <= rect.bottom()
                right = abs(test_pt.x() - rect.right()) < tolerance and rect.top() <= test_pt.y() <= rect.bottom()
                top = abs(test_pt.y() - rect.top()) < tolerance and rect.left() <= test_pt.x() <= rect.right()
                bottom = abs(test_pt.y() - rect.bottom()) < tolerance and rect.left() <= test_pt.x() <= rect.right()
                return left or right or top or bottom
            elif tool == "circle":
                center = rect.center()
                rx = rect.width() / 2
                ry = rect.height() / 2
                if rx == 0 or ry == 0:
                    return False
                dx = (test_pt.x() - center.x()) / rx
                dy = (test_pt.y() - center.y()) / ry
                dist = math.hypot(dx, dy)
                return abs(dist - 1) < (tolerance / max(rx, ry))
            elif tool == "triangle":
                x1, y1 = rect.left(), rect.top()
                x2, y2 = rect.right(), rect.bottom()
                tri = [
                    QPoint((x1 + x2) // 2, y1),
                    QPoint(x1, y2),
                    QPoint(x2, y2)
                ]
                def point_near_line(p1, p2):
                    px, py = test_pt.x(), test_pt.y()
                    x0, y0 = p1.x(), p1.y()
                    x1_, y1_ = p2.x(), p2.y()
                    dx, dy = x1_ - x0, y1_ - y0
                    if dx == dy == 0:
                        return math.hypot(px - x0, py - y0) < tolerance
                    t = max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)))
                    proj_x = x0 + t * dx
                    proj_y = y0 + t * dy
                    return math.hypot(px - proj_x, py - proj_y) < tolerance
                return (
                    point_near_line(tri[0], tri[1]) or
                    point_near_line(tri[1], tri[2]) or
                    point_near_line(tri[2], tri[0])
                )
            elif tool == "line":
                x0, y0 = start.x(), start.y()
                x1_, y1_ = end.x(), end.y()
                dx, dy = x1_ - x0, y1_ - y0
                if dx == dy == 0:
                    return math.hypot(test_pt.x() - x0, test_pt.y() - y0) < tolerance
                t = max(0, min(1, ((test_pt.x() - x0) * dx + (test_pt.y() - y0) * dy) / (dx * dx + dy * dy)))
                proj_x = x0 + t * dx
                proj_y = y0 + t * dy
                return math.hypot(test_pt.x() - proj_x, test_pt.y() - proj_y) < tolerance
            elif tool == "cross":
                rect = QRect(start, end).normalized()
                def near_line(p1, p2):
                    x0, y0 = p1.x(), p1.y()
                    x1_, y1_ = p2.x(), p2.y()
                    dx, dy = x1_ - x0, y1_ - y0
                    if dx == dy == 0:
                        return math.hypot(test_pt.x() - x0, test_pt.y() - y0) < tolerance
                    t = max(0, min(1, ((test_pt.x() - x0) * dx + (test_pt.y() - y0) * dy) / (dx * dx + dy * dy)))
                    proj_x = x0 + t * dx
                    proj_y = y0 + t * dy
                    return math.hypot(test_pt.x() - proj_x, test_pt.y() - proj_y) < tolerance
                return (
                    near_line(rect.topLeft(), rect.bottomRight()) or
                    near_line(rect.bottomLeft(), rect.topRight())
                )
            return False

        # Iterate top-down
        for idx in reversed(range(len(self.shapes))):
            if self.is_shape_locked(idx):
                continue
            shape = self.shapes[idx]
            tool = shape[0]
            start, end = shape[1], shape[2]

            # Parse existing properties robustly: border_color, optional fill_color, optional rotation
            rest = list(shape[3:]) if len(shape) > 3 else []
            border_color = QColor("#000000")
            fill_color = None
            rotation = 0
            # collect QColor and numeric props
            qcols = [v for v in rest if isinstance(v, QColor)]
            nums = [v for v in rest if isinstance(v, (int, float)) and not isinstance(v, bool)]
            dicts = [v for v in rest if isinstance(v, dict)]  
            bools = [v for v in rest if isinstance(v, bool)] 
            if qcols:
                border_color = qcols[0]
                if len(qcols) > 1:
                    fill_color = qcols[1]
            if nums:
                rotation = nums[-1]

            if tool == "image":
                rect = QRect(start, end).normalized()
                if rect.contains(pt):
                    # Do nothing for images
                    return

            # FREEHAND (draw) shapes: change stroke color only when clicked near the stroke
            if tool == "draw" and isinstance(start, list):
                points = start
                touched = any((p - pt).manhattanLength() < 10 for p in points)
                if touched:
                    self.push_undo()
                    # preserve draw radius and rotation if present
                    draw_radius = None
                    draw_rotation = 0
                    if len(shape) > 4 and isinstance(shape[4], (int, float)):
                        draw_radius = shape[4]
                    if len(shape) > 5 and isinstance(shape[5], (int, float)):
                        draw_rotation = shape[5]
                    # Build tuple: ("draw", points, None, border_color, draw_radius?, rotation?)
                    new_shape = ["draw", [QPoint(p) for p in points], None, self.shape_color]
                    if draw_radius is not None:
                        new_shape.append(draw_radius)
                    if draw_rotation:
                        new_shape.append(draw_rotation)
                    self.shapes[idx] = tuple(new_shape)
                    self.shape_layers_overlay.update_shapes(self.shapes)
                continue

            # For non-draw shapes ensure start/end are QPoint before creating rect/hit-tests
            rect_ok = isinstance(start, QPoint) and isinstance(end, QPoint)
            # If click is on border -> update border only
            if rect_ok and is_on_border(tool, start, end, pt, tolerance=8, rotation=rotation):
                self.push_undo()
                new_shape = [tool, start, end, self.shape_color]
                # preserve existing fill if any
                if fill_color is not None:
                    new_shape.append(fill_color)
                # preserve rotation if non-zero
                if rotation:
                    new_shape.append(rotation)
                for d in dicts:         
                    new_shape.append(d)
                for b in bools:          
                    new_shape.append(b)
                self.shapes[idx] = tuple(new_shape)
                self.shape_layers_overlay.update_shapes(self.shapes)
                continue

            # If click is inside the shape rect -> update fill only
            if rect_ok:
                rect = QRect(start, end).normalized()
                if rect.contains(pt):
                    self.push_undo()
                    # preserve existing border_color
                    new_shape = [tool, start, end, border_color, self.shape_color]
                    if rotation:
                        new_shape.append(rotation)
                    for d in dicts:          
                        new_shape.append(d)
                    for b in bools:          
                        new_shape.append(b)
                    self.shapes[idx] = tuple(new_shape)
                    self.shape_layers_overlay.update_shapes(self.shapes)
                    continue

    def crop_to_rect(self, crop_rect):
        self.push_undo()

        # Create a composite pixmap of the cropped area
        cropped_pixmap = QPixmap(crop_rect.size())
        cropped_pixmap.fill(Qt.GlobalColor.white)  # White background like the canvas

        painter = QPainter(cropped_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Translate painter to draw shapes in the correct position relative to crop area
        painter.translate(-crop_rect.topLeft())

        # Draw all shapes that intersect with the crop area
        for shape in self.shapes:
            tool, start, end, *rest = shape

            if tool == "draw" and isinstance(start, list):
                # Check if any points are in the crop area
                clipped_points = [p for p in start if crop_rect.contains(p)]
                if clipped_points:
                    color = rest[0] if rest else QColor("#000000")
                    draw_width = rest[1] if len(rest) > 1 and isinstance(rest[1], (int, float)) else self.draw_radius
                    painter.setPen(QPen(color, draw_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                    painter.drawPolyline(*start)  # Draw full polyline for better appearance

            elif tool == "image" and len(rest) > 0 and isinstance(rest[0], QPixmap):
                rect = QRect(start, end).normalized()
                if crop_rect.intersects(rect):
                    rotation = rest[1] if len(rest) > 1 and isinstance(rest[1], (int, float)) else 0
                    painter.save()
                    if rotation:
                        painter.translate(rect.center())
                        painter.rotate(rotation)
                        painter.translate(-rect.center())
                    painter.drawPixmap(rect, rest[0])
                    painter.restore()

            else:
                # Handle geometric shapes
                rect = QRect(start, end).normalized()
                if crop_rect.intersects(rect):
                    color = rest[0] if rest else QColor("#000000")
                    fill_color = None
                    rotation = 0

                    # Extract properties
                    for prop in rest[1:]:
                        if isinstance(prop, QColor):
                            fill_color = prop
                        elif isinstance(prop, (int, float)):
                            rotation = prop

                    painter.save()
                    if rotation:
                        painter.translate(rect.center())
                        painter.rotate(rotation)
                        painter.translate(-rect.center())

                    # Draw fill first if present
                    if fill_color:
                        painter.setBrush(QBrush(fill_color))
                        painter.setPen(Qt.PenStyle.NoPen)
                        self.draw_shape(painter, tool, rect.topLeft(), rect.bottomRight())

                    # Draw border
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.setPen(QPen(color, 3))
                    self.draw_shape(painter, tool, rect.topLeft(), rect.bottomRight())
                    painter.restore()

        # Draw eraser strokes that intersect with the crop area
        painter.setPen(QPen(QColor("white"), 22, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        for stroke in self.eraser_strokes:
            if len(stroke) > 1:
                # Check if stroke intersects crop area
                stroke_intersects = any(crop_rect.contains(p) for p in stroke)
                if stroke_intersects:
                    painter.drawPolyline(*stroke)

        painter.end()

        # Instead of clearing everything, keep shapes/strokes that are OUTSIDE the crop area
        shapes_to_keep = []
        for shape in self.shapes:
            tool, start, end, *rest = shape

            if tool == "draw" and isinstance(start, list):
                # Keep if no points are in the crop area
                if not any(crop_rect.contains(p) for p in start):
                    shapes_to_keep.append(shape)
            elif tool == "image" and len(rest) > 0:
                rect = QRect(start, end).normalized()
                # Keep if doesn't intersect crop area
                if not crop_rect.intersects(rect):
                    shapes_to_keep.append(shape)
            else:
                rect = QRect(start, end).normalized()
                # Keep if doesn't intersect crop area
                if not crop_rect.intersects(rect):
                    shapes_to_keep.append(shape)

        # Keep eraser strokes that don't intersect with crop area
        eraser_strokes_to_keep = []
        for stroke in self.eraser_strokes:
            if len(stroke) > 1:
                # Keep if stroke doesn't intersect crop area
                if not any(crop_rect.contains(p) for p in stroke):
                    eraser_strokes_to_keep.append(stroke)

        # Update shapes and eraser strokes to only keep those outside crop area
        self.shapes = shapes_to_keep
        self.eraser_strokes = eraser_strokes_to_keep

        # Clear only the eraser mask area that was cropped
        new_eraser_mask = QPixmap(self.a4_size)
        new_eraser_mask.fill(Qt.GlobalColor.transparent)

        # Redraw eraser mask for remaining strokes
        if self.eraser_strokes:
            mask_painter = QPainter(new_eraser_mask)
            mask_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            mask_painter.setPen(Qt.PenStyle.NoPen)
            mask_painter.setBrush(QColor("white"))
            for stroke in self.eraser_strokes:
                if len(stroke) > 1:
                    for pt in stroke:
                        mask_painter.drawEllipse(pt, self.eraser_radius, self.eraser_radius)
            mask_painter.end()

        self.eraser_mask = new_eraser_mask

        # Create the moveable selection as an image
        self.preview_shape = "image"
        self.preview_pixmap = cropped_pixmap
        self.preview_start = crop_rect.topLeft()
        self.preview_end = crop_rect.bottomRight()
        self.selected_shape_index = None

        # Clear crop state
        self.crop_preview_mode = False
        self.cropping = False
        self.crop_start = None
        self.crop_end = None
        self._crop_dragging_handle = None

        self.update()

    def rotate_points(self, points, angle_degrees, center):
        angle = math.radians(angle_degrees)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        cx, cy = center.x(), center.y()
        rotated = []
        for p in points:
            x, y = p.x() - cx, p.y() - cy
            rx = x * cos_a - y * sin_a + cx
            ry = x * sin_a + y * cos_a + cy
            rotated.append(QPoint(int(rx), int(ry)))
        return rotated

    def clip_polyline_to_rect(self, points, clip_rect):
        """Clip a polyline to a rectangle - simplified version"""
        if not points:
            return []

        clipped_points = []

        for point in points:
            if clip_rect.contains(point):
                clipped_points.append(point)
            else:
                # For points outside, we could implement line-rectangle intersection
                # For now, just skip points outside the rectangle
                pass

        return clipped_points if len(clipped_points) > 1 else []

    def clip_line_to_rect(self, p1, p2, rect):
        """Clip a line segment to a rectangle using Cohen-Sutherland algorithm"""
        def compute_outcode(x, y):
            code = 0
            if x < rect.left():
                code |= 1  # LEFT
            elif x > rect.right():
                code |= 2  # RIGHT
            if y < rect.top():
                code |= 4  # TOP
            elif y > rect.bottom():
                code |= 8  # BOTTOM
            return code

        x1, y1 = p1.x(), p1.y()
        x2, y2 = p2.x(), p2.y()

        outcode1 = compute_outcode(x1, y1)
        outcode2 = compute_outcode(x2, y2)

        while True:
            if not (outcode1 | outcode2):  # Both inside
                return [QPoint(int(x1), int(y1)), QPoint(int(x2), int(y2))]
            elif outcode1 & outcode2:  # Both outside same region
                return None
            else:
                # Calculate intersection
                outcode = outcode1 if outcode1 else outcode2

                if outcode & 8:  # BOTTOM
                    x = x1 + (x2 - x1) * (rect.bottom() - y1) / (y2 - y1)
                    y = rect.bottom()
                elif outcode & 4:  # TOP
                    x = x1 + (x2 - x1) * (rect.top() - y1) / (y2 - y1)
                    y = rect.top()
                elif outcode & 2:  # RIGHT
                    y = y1 + (y2 - y1) * (rect.right() - x1) / (x2 - x1)
                    x = rect.right()
                elif outcode & 1:  # LEFT
                    y = y1 + (y2 - y1) * (rect.left() - x1) / (x2 - x1)
                    x = rect.left()

                if outcode == outcode1:
                    x1, y1 = x, y
                    outcode1 = compute_outcode(x1, y1)
                else:
                    x2, y2 = x, y
                    outcode2 = compute_outcode(x2, y2)

    def clip_shape_to_rect(self, tool, shape_rect, clip_rect, rest):
        """Clip geometric shapes to rectangle"""
        if not clip_rect.intersects(shape_rect):
            return None

        # Extract properties
        color = rest[0] if rest else QColor("#000000")
        fill_color = None
        rotation = 0

        for prop in rest[1:]:
            if isinstance(prop, QColor):
                fill_color = prop
            elif isinstance(prop, (int, float)):
                rotation = prop

        # Create intersection for all geometric shapes
        intersect = shape_rect.intersected(clip_rect)
        if intersect.isEmpty():
            return None

        adjusted_rect = QRect(
            intersect.left() - offset.x(),
            intersect.top() - offset.y(),
            intersect.width(),
            intersect.height()
        )

        # For geometric shapes, convert to rectangle if clipped
        if tool in ["circle", "triangle", "cross"]:
            # Convert complex shapes to rectangles when clipped
            tool = "rect"

        shape_data = [tool, adjusted_rect.topLeft(), adjusted_rect.bottomRight(), color]
        if fill_color:
            shape_data.append(fill_color)
        if rotation:
            shape_data.append(rotation)

        return tuple(shape_data)

    def is_shape_locked(self, idx):
        if idx is None or idx < 0 or idx >= len(self.shapes):
            return False
        shape = self.shapes[idx]
        # Check if last element is a boolean (lock flag)
        if len(shape) > 0 and isinstance(shape[-1], bool):
            return shape[-1]
        # No explicit lock flag present -> treat as unlocked
        return False

    def lock_selected_shape(self):
        idx = self.selected_shape_index
        if idx is not None and 0 <= idx < len(self.shapes):
            self.push_undo()
            old_shape = self.shapes[idx]
            tool = old_shape[0]
            # If shape was being dragged/edited, commit preview position first
            if self.preview_shape and self.preview_start is not None and self.preview_end is not None:
                border_color = old_shape[3]
                fill_color = None
                rotation = getattr(self, 'preview_rotation', 0)
                extra_dicts = []
                for item in old_shape[4:]:
                    if isinstance(item, QColor):
                        fill_color = item
                    elif isinstance(item, (int, float)) and not isinstance(item, bool):
                        rotation = item
                    elif isinstance(item, dict):
                        extra_dicts.append(item)
                shape = [tool, self.preview_start, self.preview_end, border_color]
                if fill_color is not None:
                    shape.append(fill_color)
                if rotation:
                    shape.append(rotation)
                for d in extra_dicts:
                    shape.append(d)
            else:
                shape = list(old_shape)
                if shape and isinstance(shape[-1], bool):
                    shape = shape[:-1]
            shape.append(True)
            self.shapes[idx] = tuple(shape)
            self.selected_shape_index = None
            self.preview_shape = None
            self.preview_start = None
            self.preview_end = None
            self.update()

    def unlock_selected_shape(self):
        idx = self.selected_shape_index
        if idx is not None and 0 <= idx < len(self.shapes):
            self.push_undo()
            shape = list(self.shapes[idx])
            # misread as rotation=0 by select_shape_by_index (bool is subclass of int)
            if shape and isinstance(shape[-1], bool):
                shape = shape[:-1]
            self.shapes[idx] = tuple(shape)
            self.selected_shape_index = None
            self.preview_shape = None
            self.preview_start = None
            self.preview_end = None
            self.update()

    def points_close(self, p1, p2, tolerance=5):
        return (p1 - p2).manhattanLength() < tolerance


class ShapeLayersOverlay(QWidget):
    shape_selected = pyqtSignal(int)

    class ShapeWidget(QWidget):
        def __init__(self, idx, parent=None):
            super().__init__(parent)
            self.idx = idx
            self.icon = QLabel(self)
            self.icon.setFixedSize(64, 128)
            self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label = QLabel(self)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox = QVBoxLayout(self)
            vbox.addWidget(self.icon)
            vbox.addWidget(self.label)
            vbox.setContentsMargins(18, 18, 18, 18)
            vbox.setSpacing(0)
            self.setLayout(vbox)
            self.setAcceptDrops(True)
            self._drag_pixmap = None
            self._dragging = False
            self._mouse_pressed = False

        def paintEvent(self, event):
            super().paintEvent(event)
            # Draw border if selected
            if getattr(self.parent(), "selected_idx", None) == self.idx:
                painter = QPainter(self)
                pen = QPen(QColor("#ff6600"), 4, Qt.PenStyle.DashLine)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 16, 16)

        def mouseDoubleClickEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.parent().selected_idx = self.idx
                self.parent().refresh()
                self.parent().shape_selected.emit(self.idx)
                self.parent().update_shapes(self.parent().shapes)
                self.parent().setVisible(False)
                
            super().mouseDoubleClickEvent(event)
        
        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.parent().selected_idx = self.idx
                self.parent().refresh()
                self._mouse_pressed = True
                self._press_pos = event.position().toPoint()
            super().mousePressEvent(event)
        
        def mouseMoveEvent(self, event):
            if self._mouse_pressed:
                # Start drag only if moved enough (avoid drag on double-click)
                if (event.position().toPoint() - self._press_pos).manhattanLength() > QApplication.startDragDistance():
                    from PyQt6.QtGui import QDrag
                    from PyQt6.QtCore import QMimeData
                    drag = QDrag(self)
                    mime = QMimeData()
                    mime.setText(str(self.idx))
                    drag.setMimeData(mime)
                    if not self.icon.pixmap().isNull():
                        drag.setPixmap(self.icon.pixmap())
                        drag.setHotSpot(event.position().toPoint() - self.icon.pos())
                    self._dragging = True
                    self.parent()._start_auto_scroll(event.globalPosition().toPoint())
                    drag.exec()
                    self._dragging = False
                    self.parent()._stop_auto_scroll()
                    self._mouse_pressed = False
            super().mouseMoveEvent(event)
        
        def mouseReleaseEvent(self, event):
            self._mouse_pressed = False
            super().mouseReleaseEvent(event)
        
        def dragEnterEvent(self, event):
            if event.mimeData().hasText():
                event.acceptProposedAction()

        def dragMoveEvent(self, event):
            if event.mimeData().hasText():
                event.acceptProposedAction()
                self.parent()._auto_scroll_if_needed(event.position().toPoint())

        def dropEvent(self, event):
            if event.mimeData().hasText():
                from_idx = int(event.mimeData().text())
                to_idx = self.idx
                self.parent().reorder_shape(from_idx, to_idx)
                event.acceptProposedAction()


    def __init__(self, drawing_area):
        super().__init__(drawing_area)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: none;")
        self.setVisible(False)
        self.drawing_area = drawing_area
        self.current_index = 0
        self.selected_idx = None
        self._auto_scroll_timer = QTimer(self)
        self._auto_scroll_timer.setInterval(50)
        self._auto_scroll_timer.timeout.connect(self._do_auto_scroll)
        self._scroll_direction = 0

        self.main_layout = QHBoxLayout(self)
        self.left_arrow = QPushButton("◀")
        self.right_arrow = QPushButton("▶")
        self.left_arrow.setFixedWidth(28)
        self.right_arrow.setFixedWidth(28)
        self.left_arrow.clicked.connect(self.prev_shape)
        self.right_arrow.clicked.connect(self.next_shape)
        self.main_layout.addWidget(self.left_arrow)

        self.shape_widgets = []
        for i in range(3):
            shape_widget = self.ShapeWidget(i, self)
            self.main_layout.addWidget(shape_widget)
            self.shape_widgets.append(shape_widget)

        self.main_layout.addWidget(self.right_arrow)
        self.installEventFilter(self)



    def update_shapes(self, shapes):
        self.shapes = shapes
        self.current_index = max(0, len(shapes) - 3)  # Show most recent at left
        self.selected_idx = None
        self.refresh()

    def refresh(self):
        total = len(self.shapes)
        print("Shapes:", self.shapes)
        for i, shape_widget in enumerate(self.shape_widgets):
            idx = self.current_index + i
            if idx < total:
                tool, start, end, data = self.shapes[idx][:4]
                pix = QPixmap(64, 64)
                pix.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pix)
                if self.selected_idx == idx:
                    shape_widget.setStyleSheet("background: none; border: 2px dashed orange; border-radius: 16px;")
                else:
                    shape_widget.setStyleSheet("background: none; border: none;")
                shape_widget.update()
                try:
                    if tool == "image" and isinstance(data, QPixmap):
                        thumb = data.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        x = (64 - thumb.width()) // 2
                        y = (64 - thumb.height()) // 2
                        painter.drawPixmap(x, y, thumb)
                    else:
                        painter.setPen(QPen(Qt.GlobalColor.black, 3))
                        rect = pix.rect().adjusted(8, 8, -8, -8)
                        if tool == "rect":
                            painter.drawRect(rect)
                        elif tool == "circle":
                            painter.drawEllipse(rect)
                        elif tool == "triangle":
                            points = [
                                QPoint(rect.center().x(), rect.top()),
                                QPoint(rect.left(), rect.bottom()),
                                QPoint(rect.right(), rect.bottom())
                            ]
                            painter.drawPolygon(*points)
                        elif tool == "line":
                            painter.drawLine(rect.bottomLeft(), rect.topRight())
                        elif tool == "cross":
                            painter.drawLine(rect.topLeft(), rect.bottomRight())
                            painter.drawLine(rect.bottomLeft(), rect.topRight())
                        elif tool == "roundrect":
                            painter.drawRoundedRect(rect, 18, 18)
                        elif tool == "draw":
                            # Draw a scaled polyline preview
                            if isinstance(start, list) and len(start) > 1:
                                # Scale points to fit the rect
                                min_x = min(p.x() for p in start)
                                min_y = min(p.y() for p in start)
                                max_x = max(p.x() for p in start)
                                max_y = max(p.y() for p in start)
                                src_w = max_x - min_x or 1
                                src_h = max_y - min_y or 1
                                dst_w = rect.width()
                                dst_h = rect.height()
                                scaled_points = [
                                QPoint(
                                    rect.left() + int((p.x() - min_x) / src_w * dst_w),
                                    rect.top() + int((p.y() - min_y) / src_h * dst_h)
                                )
                                for p in start
                            ]
                            painter.drawPolyline(*scaled_points)
                finally:
                    painter.end()
                shape_widget.icon.setPixmap(pix)
                shape_widget.label.setText(f"Object {idx+1}")
                shape_widget.idx = idx
                shape_widget.setEnabled(True)
                shape_widget.setStyleSheet("background: none;")
            else:
                shape_widget.icon.clear()
                shape_widget.label.clear()
                shape_widget.setEnabled(False)
                shape_widget.setStyleSheet("background: none;")
                shape_widget.update()
        # Arrow enable/disable
        self.left_arrow.setEnabled(self.current_index > 0)
        self.right_arrow.setEnabled(self.current_index + 3 < len(self.shapes))

    def prev_shape(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.refresh()

    def next_shape(self):
        if self.current_index + 3 < len(self.shapes):
            self.current_index += 1
            self.refresh()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.prev_shape()
        else:
            self.next_shape()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = 22
        # Draw white background with rounded corners
        painter.setBrush(QColor("white"))
        painter.setPen(QPen(QColor("#222"), 3))
        painter.drawRoundedRect(rect, radius, radius)
        super().paintEvent(event)   
    
    def setVisible(self, visible):
        super().setVisible(visible)
        app = QApplication.instance()
        if visible:
            app.installEventFilter(self)
            
        else:
            app.removeEventFilter(self)
            

    
    
    def reorder_shape(self, from_idx, to_idx):
        self.drawing_area.push_undo()
        # Move shape in drawing_area.shapes and refresh everything
        if from_idx == to_idx or from_idx >= len(self.shapes) or to_idx >= len(self.shapes):
            return
        shape = self.shapes.pop(from_idx)
        self.shapes.insert(to_idx, shape)
        self.drawing_area.shapes = self.shapes
        self.drawing_area.selected_shape_index = None  # Deselect after reorder
        self.drawing_area.preview_shape = None
        self.drawing_area.preview_start = None
        self.drawing_area.preview_end = None
        self.drawing_area.preview_pixmap = None
        self.drawing_area.update()
        self.update_shapes(self.shapes)
        self.selected_idx = None
        self.refresh()
        # Deselect tool in parent UI if needed
        if hasattr(self.drawing_area.parent(), "deselect_tool"):
            self.drawing_area.parent().deselect_tool()

    # --- Auto-scroll logic for drag ---
    def _start_auto_scroll(self, global_pos):
        self._scroll_direction = 0
        self._auto_scroll_timer.start()

    def _stop_auto_scroll(self):
        self._auto_scroll_timer.stop()
        self._scroll_direction = 0

    def _auto_scroll_if_needed(self, local_pos):
        margin = 32
        if local_pos.x() < margin:
            self._scroll_direction = -1
        elif local_pos.x() > self.width() - margin:
            self._scroll_direction = 1
        else:
            self._scroll_direction = 0

    def _do_auto_scroll(self):
        if self._scroll_direction == -1:
            self.prev_shape()
        elif self._scroll_direction == 1:
            self.next_shape()


class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self._angle = 0
        self._text = "Loading..."
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def show_with_text(self, text):
        self._text = text
        self._angle = 0
        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.show()
        self._timer.start(25)
        QApplication.processEvents()

    def hide_overlay(self):
        self._timer.stop()
        self.hide()

    def _tick(self):
        self._angle = (self._angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 140))

        cx = self.width() // 2
        cy = self.height() // 2
        r = 32

        # Background circle
        painter.setPen(QPen(QColor(255, 255, 255, 40), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawEllipse(QPointF(cx, cy), r, r)

        # Spinning arc
        painter.setPen(QPen(QColor("#ff6600"), 5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        arc_rect = QRectF(cx - r, cy - r, r * 2, r * 2)
        painter.drawArc(arc_rect, -self._angle * 16, 100 * 16)

        # Label
        painter.setPen(QColor("white"))
        font = painter.font()
        font.setPointSize(13)
        painter.setFont(font)
        text_rect = self.rect().adjusted(0, cy + r + 14, 0, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self._text)


class UIMode(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        screen = QApplication.primaryScreen()
        if screen:
            rect = screen.geometry()
            w = int(rect.width() * 0.7)
            h = int(rect.height() * 0.7)
            self.resize(w, h)
            self.move(
                rect.left() + (rect.width() - w) // 2,
                rect.top() + (rect.height() - h) // 2
            )
        
        self.checkpoints_dir = None  # Will be set when a file is opened
        self.current_canvas_file = None  # Track the current file path
        
        self.selected_tool = None
        self._first_ribbon_init = True
        
        self.setWindowTitle("Log Documentation System - Log Mode")
        self.setStyleSheet("font-family: Arial; font-size: 12pt;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        #self.resize(1100, 700)
        self.init_ui()
        self._show_controls = False
        
        
        self.custom_tooltip = CustomToolTip(self)
        self.drawing_area.shape_selected_for_edit.connect(self.deselect_tool)
        self._tool_btn_anim = None  # Initialize attribute to avoid assignment error
        self._last_category_index = 0
        self.drawing_area.shape_selected_for_edit.connect(self.sync_color_with_selected_shape)
        #self._was_maximized = False
        
        

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background: white; font-family: Arial; font-size: 12pt;")  # Set window bg to white

        # Tool Ribbon (with scroll for more tools)
        ribbon_widget = QWidget()
        ribbon_layout = QVBoxLayout(ribbon_widget)
        ribbon_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        ribbon_layout.setContentsMargins(0, 0, 0, 0)
        ribbon_layout.setSpacing(20)
        ribbon_widget.setStyleSheet("""
            background: white;
            border: none;
        } QWidget:Hover {
            background: #f0f0f0;
        } QScrollArea {
            border: none;
        } QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 0px;
        } QScrollBar:horizontal {
            border: none;
            background: transparent;
            height: 0px;
        } QScrollBar::handle {
            background: #ff6600;
        } QScrollBar::add-line, QScrollBar::sub-line
        {
        
        """)  # Blend with drawing area
        
        self.ribbon_tools_container = QWidget()
        self.ribbon_tools_layout = QVBoxLayout(self.ribbon_tools_container)
        self.ribbon_tools_layout.setContentsMargins(0, 0, 0, 0)
        self.ribbon_tools_layout.setSpacing(44)
        ribbon_layout.addWidget(self.ribbon_tools_container, alignment=Qt.AlignmentFlag.AlignTop)
    
        self.quick_prop = ClickableLabel()
        self.quick_prop.setFixedSize(62, 78)
        self.quick_prop.setStyleSheet("""
            background: none;
            border: 2px solid #222;       
            border-radius: 22px;          
            margin-top: 25px;
            margin-bottom: 25px;
        """)
        self.quick_prop.setMinimumHeight(110)
        self.quick_prop.setMaximumHeight(110)
        self.current_shape_color = QColor("#000000")
        
        def update_quick_prop_icon():
            pixmap = QPixmap(r"C:\Users\Mathew\Documents\log-documentation-system\assets\paintprop1.png").scaled(58, 58, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            # Tint the pixmap with the current color
            colored = QPixmap(pixmap.size())
            colored.fill(Qt.GlobalColor.transparent)
            painter = QPainter(colored)
            try:
                painter.drawPixmap(0, 0, pixmap)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                painter.fillRect(colored.rect(), self.current_shape_color)
            finally:
                painter.end()
            self.quick_prop.setPixmap(colored)
        
        update_quick_prop_icon()
        
        def pick_color():
            if self.drawing_area.selected_shape_index is not None:
                self.custom_tooltip.show_tooltip("Cannot change color while editing a shape", 2500)
                return
        
            color = QColorDialog.getColor(self.current_shape_color, self, "Pick Shape Color")
            if color.isValid():
                self.current_shape_color = color
                update_quick_prop_icon()
                self.drawing_area.set_shape_color(color)  # Pass color to drawing area
                self.update_tool_btn_border()
                self._side_menu.set_accent_color(color)
                # Update selected tool button color
                if self.selected_tool:
                    self.select_tool(self.selected_tool)
                # Update ribbon shadow color if visible
                effect = self.ribbon_widget.graphicsEffect()
                if isinstance(effect, QGraphicsDropShadowEffect):
                    effect.setColor(self.current_shape_color)

        self.quick_prop.clicked = pick_color
        
        ribbon_layout.insertWidget(0, self.quick_prop, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Add a divider below the quick_prop with adjustable thickness
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("color: black; background: black; height: 3px; margin: 3px 0; margin-left: 10px; margin-right: 10px;")
        ribbon_layout.insertWidget(1, divider)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(ribbon_widget)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedWidth(80)
        scroll.setStyleSheet("background: white; border: none;")  # Blend scroll area too

        
        self.ribbon_shadow = QGraphicsDropShadowEffect(scroll)
        self.ribbon_shadow.setBlurRadius(24)
        self.ribbon_shadow.setOffset(0, 0)
        self.ribbon_shadow.setColor(Qt.GlobalColor.blue)
        scroll.setGraphicsEffect(None)  # No shadow by default
        
        self._ribbon_scroll_hint_shown = False
        self._ribbon_scroll_restore_value = None
        self._ribbon_scroll_timer = QTimer(self)
        self._ribbon_scroll_timer.setSingleShot(True)
        self._ribbon_scroll_anim = None  # Keep a reference to avoid garbage collection

        def auto_scroll_ribbon():
            if self._ribbon_scroll_hint_shown:
                return
            bar = scroll.verticalScrollBar()
            if bar is not None and bar.maximum() > 0:
                self._ribbon_scroll_hint_shown = True  # Mark as shown
                self._ribbon_scroll_restore_value = bar.value()
                target = min(bar.value() + 60, bar.maximum())
                # Animate scroll
                if self._ribbon_scroll_anim is not None:
                    self._ribbon_scroll_anim.stop()
                self._ribbon_scroll_anim = QPropertyAnimation(bar, b"value", self)
                self._ribbon_scroll_anim.setDuration(350)
                self._ribbon_scroll_anim.setStartValue(bar.value())
                self._ribbon_scroll_anim.setEndValue(target)
                self._ribbon_scroll_anim.start()
                self._ribbon_scroll_timer.start(900)  # Restore after 900ms

        def restore_ribbon_scroll():
            bar = scroll.verticalScrollBar()
            if bar is not None and self._ribbon_scroll_restore_value is not None:
                # Animate back
                if self._ribbon_scroll_anim is not None:
                    self._ribbon_scroll_anim.stop()
                from PyQt6.QtCore import QPropertyAnimation
                self._ribbon_scroll_anim = QPropertyAnimation(bar, b"value", self)
                self._ribbon_scroll_anim.setDuration(350)
                self._ribbon_scroll_anim.setStartValue(bar.value())
                self._ribbon_scroll_anim.setEndValue(self._ribbon_scroll_restore_value)
                self._ribbon_scroll_anim.start()
                self._ribbon_scroll_restore_value = None

        self._ribbon_scroll_timer.timeout.connect(restore_ribbon_scroll)

        # Subclass QScrollArea to override enterEvent
        class CustomScrollArea(QScrollArea):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._auto_scroll_callback = None

            def set_auto_scroll_callback(self, callback):
                self._auto_scroll_callback = callback

            def enterEvent(self, event):
                if self._auto_scroll_callback:
                    self._auto_scroll_callback()
                super().enterEvent(event)

        custom_scroll = CustomScrollArea()
        custom_scroll.setWidgetResizable(True)
        custom_scroll.setWidget(ribbon_widget)
        custom_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        custom_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        custom_scroll.setFixedWidth(80)
        custom_scroll.setStyleSheet("background: white; border: none;")
        custom_scroll.set_auto_scroll_callback(auto_scroll_ribbon)
        scroll = custom_scroll  # Use the custom scroll area
        
        # Drawing Area
        self.drawing_area = DrawingArea()
        self.drawing_area.installEventFilter(self)

        # Top bar (custom, only shows controls on hover)
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(48)
        self.top_bar.setStyleSheet("background: white;")
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)

        # Stacked layout for label/controls
        self.stacked = QStackedLayout()
        self.title_label = QLabel("Log Documentation System")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16pt; padding: 8px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_opacity = QGraphicsOpacityEffect(self.title_label)
        self.title_label.setGraphicsEffect(self.title_opacity)
        self.title_opacity.setOpacity(1.0)

        # Controls widget (centered)
        self.controls_widget = QWidget()
        controls_layout = QHBoxLayout(self.controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.setSpacing(155)
        self.quick_save_btn = QPushButton("Quick Save")
        self.min_btn = QPushButton("Minimize")
        self.max_btn = QPushButton("Maximize")
        self.close_btn = QPushButton("Close")
        for btn in [self.quick_save_btn, self.min_btn, self.max_btn, self.close_btn]:
            btn.setFixedHeight(52)
            btn.setStyleSheet("background: none; border: none; font-size: 14pt; margin: 0 8px;")
            controls_layout.addWidget(btn)
        self.controls_widget.setVisible(False)

        self.stacked.addWidget(self.title_label)
        self.stacked.addWidget(self.controls_widget)
        top_bar_layout.addLayout(self.stacked, stretch=1)
        
        # Top bar quick save
        self.quick_save_btn.clicked.connect(self.save_canvas)

        # Hamburger menu — floating overlay button (top-right corner)
        self.menu_btn = QPushButton("≡")
        self.menu_btn.setFixedSize(42, 42)
        self.menu_btn.setParent(self)
        self.menu_btn.setStyleSheet("background: none; border: none; font-size: 42pt;")
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.clicked.connect(self.toggle_side_menu)
        self.menu_btn.show()

        # Connect window control buttons
        self.close_btn.clicked.connect(self.close)
        self.min_btn.clicked.connect(self.handle_minimize)
        self.max_btn.clicked.connect(self.toggle_max_restore)

        # Mouse tracking for hover event
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.title_label.installEventFilter(self)
        self.controls_widget.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.controls_widget.installEventFilter(self)
        # Install event filter for hover
        scroll.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        scroll.installEventFilter(self)
        
        self.ribbon_widget = scroll  # Save for eventFilter

        # Layout assembly
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.top_bar)
        content_layout.addWidget(self.drawing_area)
        main_layout.addWidget(scroll)
        main_layout.addLayout(content_layout)
        
        # Side menu panel (overlay, starts hidden off-screen right)
        self._side_menu = SideMenuPanel(self)
        self._side_menu_open = False
        self._side_menu.raise_()
        self._side_menu.hide()
        # Sync initial accent color
        self._side_menu.set_accent_color(self.current_shape_color)
        # Side panel file actions
        self._side_menu.file_actions["Save"].clicked.connect(self.save_canvas)
        self._side_menu.file_actions["Save As"].clicked.connect(
            lambda: (setattr(self, "current_canvas_file", None), self.save_canvas())
        )
        self._side_menu.file_actions["Open"].clicked.connect(self.open_canvas)
        # Connect Exit action
        self._side_menu.file_actions["Exit"].clicked.connect(self.close)
        
        # History Tab
        self._side_menu.create_checkpoint_btn.clicked.connect(self.create_file_checkpoint)
        self.menu_btn.raise_()
        
        self.ribbon_layout = ribbon_layout
        self.divider = divider  
        
        # Tool button (bottom right, floating)
        self.tool_btn = RotatingToolButton()
        self._rotated = False
        self.tool_btn.setFixedSize(68, 68)
        self.tool_btn.setParent(self)
        self.tool_btn.setIcon(QIcon(r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool.png"))
        
        self.tool_btn.setIconSize(QSize(68, 68)) 
        self.update_tool_btn_border()
        self.tool_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Add shadow effect
        
        self.tool_btn.show()
    
        def on_tool_btn_clicked():
            target = 180 if not self._rotated else 0
            anim = QPropertyAnimation(self.tool_btn, b"rotation")
            anim.setDuration(400)
            anim.setStartValue(self.tool_btn.getRotation())
            anim.setEndValue(target)
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            anim.start()
            self._tool_btn_anim = anim  # Prevent garbage collection
            self._rotated = not self._rotated
            self.update_tool_btn_border()
            anim.finished.connect(self.show_arc_menu)
        
        
        try:
            self.tool_btn.clicked.disconnect()
        except TypeError:
            pass
        self.tool_btn.clicked.connect(on_tool_btn_clicked)
        self.set_tool_category(TOOL_MENU[0])
        
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.timeout.connect(self._auto_save_tick)
        self._auto_save_timer.start(30000)  # Auto-save every 30 seconds
        
    def toggle_side_menu(self):
        h = self.height()
        panel_w = self._side_menu.width()

        if not self._side_menu_open:
            self._side_menu.setGeometry(self.width(), 0, panel_w, h)
            self._side_menu.show()
            self._side_menu.raise_()
            self.menu_btn.hide()          
            end_x = self.width() - panel_w
        else:
            end_x = self.width()

        self._side_menu_anim = QPropertyAnimation(self._side_menu, b"pos")
        self._side_menu_anim.setDuration(250)
        self._side_menu_anim.setStartValue(self._side_menu.pos())
        self._side_menu_anim.setEndValue(QPoint(end_x, 0))
        self._side_menu_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        if self._side_menu_open:
            def _on_close_done():
                self._side_menu.hide()
                self.menu_btn.show()      
                self.menu_btn.raise_()
            self._side_menu_anim.finished.connect(_on_close_done)
        self._side_menu_anim.start()
        self._side_menu_open = not self._side_menu_open  
        
        
    def rotate_tool_btn_back(self, *args):
        if self._rotated:
            anim = QPropertyAnimation(self.tool_btn, b"rotation")
            anim.setDuration(400)
            anim.setStartValue(self.tool_btn.getRotation())
            anim.setEndValue(0)
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            anim.start()
            self._tool_btn_anim = anim
            self._rotated = False
            self.update_tool_btn_border()
    
        
    def update_tool_btn_border(self):
        color_hex = self.current_shape_color.name()
        bg = "#ffe6b3" if self._rotated else "white"
        self.tool_btn.setStyleSheet(
            f"""
            border: 2px solid {color_hex};
            border-radius: 34px;
            background-color: {bg};
            """
        ) 
        
    def show_arc_menu(self):
        # Toggle arc menu: if already shown, hide it
        if hasattr(self, "arc_menu") and self.arc_menu.isVisible():
            self.arc_menu.hide_arc()
            QApplication.instance().removeEventFilter(self)
            self.drawing_area.setFocus()
            return
        btn = self.tool_btn
        origin = QPoint(btn.x() + btn.width()//2, btn.y() + btn.height()//2)
        color_hex = self.current_shape_color.name()
        self.arc_menu = ArcToolMenu(self, items=TOOL_MENU, border_color=color_hex)
        if hasattr(self, "selected_category") and self.selected_category:
            self.arc_menu.set_active_category(self.selected_category)
        else:
            self.arc_menu.set_active_category(TOOL_MENU[0]["name"])
        if self.selected_tool:
            self.arc_menu.set_active_tool(self.selected_tool)
        else:
            self.arc_menu.set_active_tool(None)
        self.arc_menu.category_selected.connect(self.set_tool_category)
        self.arc_menu.tool_selected.connect(self.select_tool)
        self.arc_menu.category_selected.connect(self.rotate_tool_btn_back)
        self.arc_menu.tool_selected.connect(self.rotate_tool_btn_back)
        self.arc_menu.show_arc(origin)
        # Install event filter to close arc menu on outside click
        QApplication.instance().installEventFilter(self)
    

    def set_tool_category(self, category):
        # Accept either a dict or a string (category name)
        if isinstance(category, str):
            # Find the category dict by name
            category = next((c for c in TOOL_MENU if c["name"] == category), TOOL_MENU[0])
        

        new_index = next((i for i, c in enumerate(TOOL_MENU) if c["name"] == category["name"]), 0)
        direction = "right" if new_index > getattr(self, "_last_category_index", 0) else "left"
        self._last_category_index = new_index

        # --- Create new container with tool buttons ---
        new_container = QWidget()
        new_layout = QVBoxLayout(new_container)
        new_layout.setContentsMargins(0, 0, 0, 0)
        new_layout.setSpacing(44)
        new_container.setStyleSheet("background: Transparent")
        category_tool_buttons = {}
        style_map = {
            "circle": "font-size: 30pt; color: #222; border: none; background: transparent; font-weight: bold;",
            "rect": "font-size: 58pt; color: #222; border: none; background: transparent;",
            "triangle": "font-size: 30pt; color: #222; border: none; background: transparent;",
            "line": "font-size: 28pt; color: #222; border: none; background: transparent;",
            "cross": "font-size: 28pt; color: #222; border: none; background: transparent;",
            "roundrect": "font-size: 38pt; color: #222; border: none; background: transparent;",
            "fill": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "crop": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "eraser": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "draw": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "label": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "arrow": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "framewithlabel": "font-size: 52pt; color: #222; border: none; background: transparent;",
            "roundframewithlabel": "font-size: 32pt; color: #222; border: none; background: transparent;",
        }
        pretty_names = {
            "circle": "Circle",
            "rect": "Rectangle",
            "triangle": "Triangle",
            "line": "Line",
            "cross": "Cross",
            "roundrect": "Rounded Rectangle",
            "fill": "Fill",
            "crop": "Crop",
            "eraser": "Eraser",
            "draw": "Draw",
            "label": "Label",
            "arrow": "Arrow",
            "framewithlabel": "Frame with Label",
            "roundframewithlabel": "Clock",
        }
        for tool in category["children"]:
            btn = ToolButton("")
            if tool["icon"].endswith(".png") or tool["icon"].endswith(".svg"):
                btn.setIcon(QIcon(tool["icon"]))
                size = tool.get("icon_size", 48)
                btn.setIconSize(QSize(size, size))
            else:
                btn.setText(tool["icon"])
            btn.setStyleSheet(style_map.get(tool["name"], "font-size: 28pt; color: #222; border: none; background: transparent; font-weight: bold;"))
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=tool["name"]: self.select_tool(t))
            btn.clicked.connect(lambda checked, t=tool["name"]: self.show_tool_tooltip(pretty_names.get(t, t.title())))
            btn.doubleClicked.connect(lambda t=tool["name"]: self.handle_tool_double_click(t))
            new_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
            category_tool_buttons[tool["name"]] = btn
        new_layout.addStretch()

        old_container = self.ribbon_tools_container
        self.ribbon_tools_container = new_container
        self.ribbon_tools_layout = new_layout
        self.category_tool_buttons = category_tool_buttons
        self.selected_category = category["name"]

        # Place new container off-screen and add to layout
        width = old_container.width() if old_container and old_container.width() > 0 else 80
        offset = width + 20
        if direction == "right":
            new_x = offset
            old_end_x = -offset
        else:
            new_x = -offset
            old_end_x = offset

        parent_widget = old_container.parentWidget() if old_container else None
        parent_layout = parent_widget.layout() if parent_widget else None
        if parent_layout:
            parent_layout.addWidget(new_container)
            new_container.move(new_x, old_container.y() if old_container else 0)
            new_container.show()

            anim_old = QPropertyAnimation(old_container, b"pos")
            anim_old.setDuration(350)
            anim_old.setStartValue(old_container.pos())
            anim_old.setEndValue(QPoint(old_end_x, old_container.y() if old_container else 0))
            anim_old.setEasingCurve(QEasingCurve.Type.OutCubic)

            anim_new = QPropertyAnimation(new_container, b"pos")
            anim_new.setDuration(350)
            anim_new.setStartValue(QPoint(new_x, old_container.y() if old_container else 0))
            anim_new.setEndValue(QPoint(0, old_container.y() if old_container else 0))
            anim_new.setEasingCurve(QEasingCurve.Type.OutCubic)

            group = QParallelAnimationGroup(self)
            group.addAnimation(anim_old)
            group.addAnimation(anim_new)

            def finish():
                if old_container:
                    old_container.hide()
                    parent_layout.removeWidget(old_container)
                    old_container.setParent(None)
                    old_container.deleteLater()
                # Highlight selected tool if needed
                if self.selected_tool in self.category_tool_buttons:
                    self.select_tool(self.selected_tool)
                else:
                    self.deselect_tool()
                self._ribbon_anim_group = None 

            group.finished.connect(finish)
            group.start()
            self._ribbon_anim_group = group
        else:
            # Fallback: just show new container if layout is missing
            new_container.move(0, 0)
            new_container.show()
            if self.selected_tool in self.category_tool_buttons:
                self.select_tool(self.selected_tool)
            else:
                self.deselect_tool()
    
    def animate_ribbon_tools(self, direction):
        start_x = -120 if direction == "right" else 120
        self.ribbon_tools_container.move(start_x, self.ribbon_tools_container.y())
        anim = QPropertyAnimation(self.ribbon_tools_container, b"pos")
        anim.setDuration(1000)
        anim.setStartValue(QPoint(start_x, self.ribbon_tools_container.y()))
        anim.setEndValue(QPoint(0, self.ribbon_tools_container.y()))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._ribbon_anim = anim  # Prevent garbage collection
        return anim
    
    def select_tool(self, tool):
        
        # Find the category containing this tool
        found_category = None
        for category in TOOL_MENU:
            for child in category["children"]:
                if child["name"] == tool:
                    found_category = category
                    break
            if found_category:
                break

        
        # If the tool is not in the current category, switch the ribbon to that category
        if found_category and (not hasattr(self, "selected_category") or self.selected_category != found_category["name"]):
            # set_tool_category will call select_tool again, so avoid recursion
            self.selected_tool = tool  # Set before switching category to avoid recursion issues
            self.set_tool_category(found_category)
        
        self.selected_tool = tool
        color_hex = self.current_shape_color.name()
        # Use the same style_map as in set_tool_category
        style_map = {
            "circle": "font-size: 30pt; color: #222; border: none; background: transparent; font-weight: bold;",
            "rect": "font-size: 58pt; color: #222; border: none; background: transparent;",
            "triangle": "font-size: 30pt; color: #222; border: none; background: transparent;",
            "line": "font-size: 28pt; color: #222; border: none; background: transparent;",
            "cross": "font-size: 28pt; color: #222; border: none; background: transparent;",
            "roundrect": "font-size: 38pt; color: #222; border: none; background: transparent;",
            "fill": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "crop": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "eraser": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "draw": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "label": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "arrow": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "framewithlabel": "font-size: 52pt; color: #222; border: none; background: transparent;",
            "roundframewithlabel": "font-size: 32pt; color: #222; border: none; background: transparent;",
        }
        # Deselect all
        for name, btn in getattr(self, "category_tool_buttons", {}).items():
            btn.setChecked(False)
            btn.setStyleSheet(style_map.get(name, "font-size: 28pt; color: #222; border: none; background: transparent; font-weight: bold;"))
        # Highlight selected
        if tool in self.category_tool_buttons:
            btn = self.category_tool_buttons[tool]
            btn.setChecked(True)
            # Compose selected style with correct font-size
            base_style = style_map.get(tool, "font-size: 28pt; color: #222; border: none; background: transparent; font-weight: bold;")
            selected_style = (
                base_style +
                f"border: 3px solid {color_hex}; border-radius: 12px; background: #fff7ef;"
            )
            btn.setStyleSheet(selected_style)
        # Pass the tool to the drawing area
        self.drawing_area.set_tool(tool)

    def deselect_tool(self):
        self.selected_tool = None
        style_map = {
            "circle": "font-size: 30pt; color: #222; border: none; background: transparent; font-weight: bold;",
            "rect": "font-size: 58pt; color: #222; border: none; background: transparent;",
            "triangle": "font-size: 30pt; color: #222; border: none; background: transparent;",
            "line": "font-size: 28pt; color: #222; border: none; background: transparent;",
            "cross": "font-size: 28pt; color: #222; border: none; background: transparent;",
            "roundrect": "font-size: 38pt; color: #222; border: none; background: transparent;",
            "fill": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "crop": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "eraser": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "draw": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "label": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "arrow": "font-size: 32pt; color: #222; border: none; background: transparent;",
            "framewithlabel": "font-size: 52pt; color: #222; border: none; background: transparent;",
            "roundframewithlabel": "font-size: 32pt; color: #222; border: none; background: transparent;",
        }
        for name, btn in getattr(self, "category_tool_buttons", {}).items():
            btn.setChecked(False)
            btn.setStyleSheet(style_map.get(name, "font-size: 28pt; color: #222; border: none; background: transparent; font-weight: bold;"))
        if self.drawing_area.selected_shape_index is None:
            self.drawing_area.set_tool(None)
        

    def eventFilter(self, obj, event):
        # Close side menu when clicking on drawing area
        if (obj == self.drawing_area 
                and event.type() == QEvent.Type.MouseButtonPress
                and self._side_menu_open):
            self.toggle_side_menu()
            
        if obj in (self.title_label, self.controls_widget):
            if event.type() == event.Type.Enter:
                self.fade_out_title_and_show_controls()
            elif event.type() == event.Type.Leave:
                # Only fade back if the mouse is not over either widget
                if not self.title_label.underMouse() and not self.controls_widget.underMouse():
                    self.fade_in_title_and_hide_controls()
        
        if hasattr(self, "ribbon_widget") and obj is self.ribbon_widget:
            if event.type() == event.Type.Enter:
                shadow = QGraphicsDropShadowEffect(self.ribbon_widget)
                shadow.setBlurRadius(0)
                shadow.setOffset(0, 0)
                shadow.setColor(self.current_shape_color)
                self.ribbon_widget.setGraphicsEffect(shadow)
                # Animate the blur radius
                self.shadow_anim = QPropertyAnimation(shadow, b"blurRadius")
                self.shadow_anim.setDuration(300)
                self.shadow_anim.setStartValue(0)
                self.shadow_anim.setEndValue(24)
                self.shadow_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
                self.shadow_anim.start()
            elif event.type() == event.Type.Leave:
                self.ribbon_widget.setGraphicsEffect(None)
        
        if hasattr(self, "arc_menu") and self.arc_menu.isVisible():
            if event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease):
                if hasattr(event, "globalPosition"):
                    pos = event.globalPosition().toPoint()
                else:
                    pos = event.globalPos()
                # Check if click is inside any visible arc menu button
                for btn in self.arc_menu.buttons:
                    if not btn.isVisible():
                        continue
                    btn_rect = btn.rect()
                    btn_top_left = btn.mapToGlobal(btn_rect.topLeft())
                    btn_rect_global = QRect(btn_top_left, btn_rect.size())
                    if btn_rect_global.contains(pos):
                        return super().eventFilter(obj, event)
                # If not inside any button, close the menu
                self.arc_menu.hide_arc()
                QApplication.instance().removeEventFilter(self)
                #QApplication.instance().removeEventFilter(self)
                self.rotate_tool_btn_back()
                self.drawing_area.setFocus()
                return True
        
        return super().eventFilter(obj, event)

    def fade_out_title_and_show_controls(self):
        if self.stacked.currentWidget() != self.title_label or getattr(self, "_animating", False):
            return
        self._animating = True
        self.anim = QPropertyAnimation(self.title_opacity, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.finished.connect(self._show_controls_widget)
        self.anim.start()

    def _show_controls_widget(self):
        self.stacked.setCurrentWidget(self.controls_widget)
        self.title_opacity.setOpacity(1.0)  # Reset opacity for next time
        self._animating = False

    def fade_in_title_and_hide_controls(self):
        if self.stacked.currentWidget() != self.controls_widget or getattr(self, "_animating", False):
            return
        self._animating = True
        self.stacked.setCurrentWidget(self.title_label)
        self.title_opacity.setOpacity(0.0)
        self.anim = QPropertyAnimation(self.title_opacity, b"opacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.finished.connect(self._finish_fade_in_title)
        self.anim.start()
    
    def _finish_fade_in_title(self):
        self._animating = False

    def resizeEvent(self, event):
        if self._side_menu_open:
            panel_w = self._side_menu.width()
            self._side_menu.setGeometry(self.width() - panel_w, 0,
                                         panel_w, self.height())
        # Floating tool button (bottom right)
        btn_margin = 24
        self.tool_btn.move(self.width() - self.tool_btn.width() - btn_margin,
                           self.height() - self.tool_btn.height() - btn_margin)
        # Floating hamburger (top right)
        self.menu_btn.move(self.width() - self.menu_btn.width() - 8, 4)
        super().resizeEvent(event)

    def handle_minimize(self):
        self._was_fullscreen = self.isFullScreen()
        self._was_maximized = self.isMaximized()
        self.showMinimized()
    
    def toggle_max_restore(self):
        if self.isFullScreen() or self.isMaximized():
            self.showNormal()
            self.max_btn.setText("Maximize")
        else:
            self.showFullScreen()
            self.max_btn.setText("Restore")
    

    # Optional: override mousePressEvent for dragging the window
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.top_bar.underMouse():
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if hasattr(self, '_drag_pos') and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if hasattr(self, '_drag_pos'):
            del self._drag_pos
        super().mouseReleaseEvent(event)
    
    def show_tool_tooltip(self, text):
        self.custom_tooltip.show_tooltip(text)
    
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            # Cancel placing shape if in progress
            if self.drawing_area.preview_shape is not None:
                self.drawing_area.preview_shape = None
                self.drawing_area.preview_start = None
                self.drawing_area.preview_end = None
                self.drawing_area.selected_shape_index = None
                self.drawing_area.update()
            # Deselect tool if one is selected
            if self.selected_tool is not None:
                self.deselect_tool()
            # Optionally, close arc menu if open
            if hasattr(self, "arc_menu") and self.arc_menu.isVisible():
                self.arc_menu.hide_arc()
                QApplication.instance().removeEventFilter(self)
                self.rotate_tool_btn_back()
            

            # Hide shape layers overlay if visible
            if self.drawing_area.shape_layers_overlay.isVisible():
                self.drawing_area.shape_layers_overlay.setVisible(False)
            return
            
        # Existing Ctrl+E for shape layers overlay
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_E:
            if self.drawing_area.shape_layers_overlay.isVisible():
                self.drawing_area.shape_layers_overlay.setVisible(False)
            else:
                self.drawing_area.show_shape_layers_overlay()
        
        else:
            super().keyPressEvent(event)
    
    
    def show_eraser_size_dialog(self, event=None):
        dlg = EraserSizeDialog(self, self.drawing_area.eraser_radius)
        dlg.move(self.geometry().center() - dlg.rect().center())
        dlg.slider.valueChanged.connect(lambda v: None)  # No-op, but you can update live preview if wanted
        if dlg.exec():
            self.drawing_area.eraser_radius = dlg.getValue()
            # Update eraser cursor immediately if needed
            if self.drawing_area.current_tool == "eraser":
                pixmap = QPixmap(r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-colors-eraser.png")
                if not pixmap.isNull():
                    size = self.drawing_area.eraser_radius * 2
                    cursor_pix = pixmap.scaled(size, size)
                    self.drawing_area.setCursor(QCursor(cursor_pix, size // 2, size // 2))


    def show_draw_size_dialog(self, event=None):
        dlg = DrawSizeDialog(self, self.drawing_area.draw_radius)
        dlg.move(self.geometry().center() - dlg.rect().center())
        dlg.slider.valueChanged.connect(lambda v: None)
        if dlg.exec():
            self.drawing_area.draw_radius = dlg.getValue()
            # Update draw cursor immediately if needed
            if self.drawing_area.current_tool == "draw":
                min_cursor_size = 8
                size = max(self.drawing_area.draw_radius * 2, min_cursor_size)
                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                pen_width = max(self.drawing_area.draw_radius, 2)
                pen = QPen(self.current_shape_color, pen_width)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                margin = pen_width // 2 + 1
                painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
                painter.end()
                self.drawing_area._draw_cursor = QCursor(pixmap, size // 2, size // 2)
                self.drawing_area.setCursor(self.drawing_area._draw_cursor)
                
    def sync_color_with_selected_shape(self):
        idx = self.drawing_area.selected_shape_index
        if idx is not None and 0 <= idx < len(self.drawing_area.shapes):
            
            
            # Update quick_prop icon and tool button border
            if hasattr(self, "quick_prop"):
                # Redraw the color icon
                pixmap = QPixmap(r"C:\Users\Mathew\Documents\log-documentation-system\assets\paintprop1.png").scaled(58, 58, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                colored = QPixmap(pixmap.size())
                colored.fill(Qt.GlobalColor.transparent)
                painter = QPainter(colored)
                try:
                    painter.drawPixmap(0, 0, pixmap)
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                    painter.fillRect(colored.rect(), self.current_shape_color)
                finally:
                    painter.end()
                self.quick_prop.setPixmap(colored)
            self.update_tool_btn_border()
            
    
    def show_tool_size_dialog(self, tool_name, current_size, min_size=1, max_size=64):
        dialog = GenericSizeDialog(
            self, 
            current_size,
            min_size,
            max_size,
            f"Adjust {tool_name.title()} Size"
        )

        # Center dialog on screen
        screen_geometry = QApplication.primaryScreen().geometry()
        dialog_geometry = dialog.geometry()
        center_point = screen_geometry.center()
        dialog.move(
            center_point.x() - dialog_geometry.width()//2,
            center_point.y() - dialog_geometry.height()//2
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_size = dialog.getValue()
            if tool_name == "draw":
                self.drawing_area.draw_radius = new_size  # Set draw radius
                self.drawing_area.tool_last_sizes['draw'] = new_size  # Store last used size
                # Update cursor immediately
                size = max(new_size * 2, 8)
                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                pen_width = max(new_size, 2)
                pen = QPen(self.current_shape_color, pen_width)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                margin = pen_width // 2 + 1
                painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
                painter.end()
                self.drawing_area._draw_cursor = QCursor(pixmap, size // 2, size // 2)
                if self.drawing_area.current_tool == "draw":
                    self.drawing_area.setCursor(self.drawing_area._draw_cursor)
            elif tool_name == "eraser":
                self.drawing_area.eraser_radius = new_size  # Set eraser radius
                self.drawing_area.tool_last_sizes['eraser'] = new_size  # Store last used size
                # Update cursor immediately
                if self.drawing_area.current_tool == "eraser":
                    pixmap = QPixmap(r"C:\Users\Mathew\Documents\log-documentation-system\assets\tool-colors-eraser.png")
                    if not pixmap.isNull():
                        size = new_size * 2
                        cursor_pix = pixmap.scaled(size, size)
                        self.drawing_area.setCursor(QCursor(cursor_pix, size // 2, size // 2))
                        
            elif tool_name in ['shapes', 'line']:
                self.drawing_area.tool_sizes[tool_name] = new_size  # Set current size
                self.drawing_area.tool_last_sizes[tool_name] = new_size  # Store last used size

    def handle_tool_double_click(self, tool_name):
        if tool_name == 'eraser':
            current_size = self.drawing_area.tool_last_sizes.get('eraser', 12)
            self.show_tool_size_dialog(tool_name, current_size, 4, 64)
        elif tool_name == 'draw':
            current_size = self.drawing_area.tool_last_sizes.get('draw', 6)
            self.show_tool_size_dialog(tool_name, current_size, 1, 32)
        elif tool_name in ['shapes', 'line']:
            current_size = self.drawing_area.tool_last_sizes.get(tool_name, 2)
            self.show_tool_size_dialog(tool_name, current_size, 1, 20)
    
    def _core_save_canvas(self, file_path):
        #Core save logic - handles actual serialization and file writing
        da = self.drawing_area
        project_folder = os.path.dirname(file_path)
        config_folder = os.path.join(project_folder, "config")
        os.makedirs(config_folder, exist_ok=True)

        # Serialize shapes
        shapes_data = [_serialize_shape(s) for s in da.shapes]

        # Serialize eraser mask
        eraser_mask_b64 = _serialize_pixmap(da.eraser_mask)

        # Serialize eraser strokes
        strokes_data = [[_serialize_qpoint(p) for p in stroke]
                        for stroke in da.eraser_strokes]

        payload = {
            "version": 1,
            "shapes": shapes_data,
            "eraser_mask": eraser_mask_b64,
            "eraser_strokes": strokes_data,
            "scale_factor": da.scale_factor,
            "zoom_percent": da.zoom_percent,
            "pan_offset": [da.pan_offset.x(), da.pan_offset.y()],
            "tool_sizes": da.tool_sizes,
            "current_shape_color": self.current_shape_color.name(),
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        # Save shape history (restore points) to config
        def _serialize_history_entry(entry):
            e = dict(entry)
            e["shape_data"] = _serialize_shape(entry["shape_data"])
            return e

        history_data = [_serialize_history_entry(e) for e in da.shape_history]
        with open(os.path.join(config_folder, "shape_history.json"), "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2)

        self.current_canvas_file = file_path

    def save_canvas(self):
        # Manual save with file dialog and LoadingOverlay
        if self.current_canvas_file:
            file_path = self.current_canvas_file
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Canvas", "", "UI Canvas (*.ldsu)"
            )
            if not file_path:
                return
            if not file_path.endswith(".ldsu"):
                file_path += ".ldsu"
            self.current_canvas_file = file_path
        
        # Show overlay AFTER dialog closes
        if not hasattr(self, '_loading_overlay'):
            self._loading_overlay = LoadingOverlay(self)
        self._loading_overlay.setGeometry(self.rect())
        self._loading_overlay.show_with_text("Saving...")    

        # Brief title feedback
        self.setWindowTitle("Log Documentation System - Saved")
        QTimer.singleShot(50, lambda: self.setWindowTitle("Log Documentation System - Log Mode"))
        QTimer.singleShot(50, self._do_save_canvas)
        
    def _do_save_canvas(self):        
        try:
            file_path = self.current_canvas_file
            self._core_save_canvas(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save canvas:\n{e}")
        finally:
            try:
                size_bytes = os.path.getsize(self.current_canvas_file)
            except OSError:
                size_bytes = 0
            delay_ms = int(size_bytes / 1000 + 5000)
            QTimer.singleShot(delay_ms, self._loading_overlay.hide_overlay)

    def _auto_save_tick(self):
        # Called every 30 seconds to auto-save
        if hasattr(self, "current_canvas_file") and self.current_canvas_file:
            self._perform_auto_save()

    def _perform_auto_save(self):
        # Perform auto-save and display status on zoom overlay
        try:
            file_path = self.current_canvas_file
            self._core_save_canvas(file_path)
            
            # Show success message on status overlay
            self.drawing_area.show_status_overlay("Auto-saved ✓", duration=2000)
        except Exception as e:
            # Show error briefly
            self.drawing_area.show_status_overlay(f"Auto-save failed: {str(e)[:30]}", duration=3000)
            print(f"Auto-save error: {e}")
                    
                
                
    def open_canvas(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Canvas", "", "UI Canvas (*.ldsu)"
            )
        if not file_path:
            return

        if not hasattr(self, '_loading_overlay'):
            self._loading_overlay = LoadingOverlay(self)
        self._loading_overlay.setGeometry(self.rect())
        self._loading_overlay.show_with_text("Opening...")
        
        # Open immediately (do not delay opening itself)
        QTimer.singleShot(50, lambda: self._do_open_canvas(file_path))

    def _do_open_canvas(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            da = self.drawing_area
            da.shapes = [_deserialize_shape(s) for s in payload["shapes"]]
            da.eraser_mask = _deserialize_pixmap(payload["eraser_mask"])
            da.eraser_strokes = [
                [QPoint(*p) for p in stroke]
                for stroke in payload["eraser_strokes"]
            ]
            da.scale_factor = payload.get("scale_factor", 1.0)
            da.zoom_percent = payload.get("zoom_percent", 0)
            pan = payload.get("pan_offset", [0, 0])
            da.pan_offset = QPoint(pan[0], pan[1])
            da.tool_sizes = payload.get("tool_sizes", da.tool_sizes)
            da.selected_shape_index = None

            color_hex = payload.get("current_shape_color", "#000000")
            self.current_shape_color = QColor(color_hex)
            self.drawing_area.set_shape_color(self.current_shape_color)
            self._side_menu.set_accent_color(self.current_shape_color)

            project_folder = os.path.dirname(file_path)
            history_path = os.path.join(project_folder, "config", "shape_history.json")
            if os.path.exists(history_path):
                with open(history_path, "r", encoding="utf-8") as f:
                    history_raw = json.load(f)
                da.shape_history = []
                for entry in history_raw:
                    e = dict(entry)
                    e["shape_data"] = _deserialize_shape(entry["shape_data"])
                    da.shape_history.append(e)
            else:
                da.shape_history = []

            self.current_canvas_file = file_path
            da.undo_stack.clear()
            da.redo_stack.clear()
            da.update()
            self.refresh_history_list()
        
        except Exception as e:
            print(f"Error opening canvas: {e}")
            # Optionally show a message box here to inform the user
            QMessageBox.critical(self, "Error", f"Failed to open canvas:\n{e}")
        finally:
            try:
                size_bytes = os.path.getsize(file_path)
            except OSError:
                size_bytes = 0
            delay_ms = int(size_bytes / 1000 + 5000)
            if hasattr(self, '_loading_overlay') and self._loading_overlay:
                QTimer.singleShot(delay_ms, self._loading_overlay.hide_overlay)
            

    def create_file_checkpoint(self):
        if not self.current_canvas_file:
            QMessageBox.warning(self, "No File", "Please save a file first before creating checkpoints.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Create Checkpoint")
        dialog.setFixedSize(300, 150)

        layout = QVBoxLayout(dialog)
        label = QLabel("Checkpoint Name:")
        input_field = QLineEdit()
        input_field.setPlaceholderText("e.g., First Draft")

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Create")
        cancel_btn = QPushButton("Cancel")

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addWidget(label)
        layout.addWidget(input_field)
        layout.addLayout(btn_layout)

        def on_create():
            name = input_field.text().strip()
            if not name:
                QMessageBox.warning(dialog, "Invalid", "Checkpoint name cannot be empty.")
                return
            dialog.accept()
            self._save_checkpoint(name)

        ok_btn.clicked.connect(on_create)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec()
    
    def _save_checkpoint(self, checkpoint_name):
        try:
            # Ensure checkpoints directory exists
            history_dir = os.path.join(os.path.dirname(self.current_canvas_file), "history")
            os.makedirs(history_dir, exist_ok=True)

            # Find next checkpoint number
            existing = [f for f in os.listdir(history_dir) if f.startswith("checkpoint_") and f.endswith(".json")]
            next_num = len(existing) + 1

            checkpoint_name_file = f"checkpoint_{next_num}"
            config_path = os.path.join(history_dir, f"{checkpoint_name_file}.json")
            meta_path = os.path.join(history_dir, f"{checkpoint_name_file}.meta")
            png_path = os.path.join(history_dir, f"{checkpoint_name_file}.png")

            # Save canvas state
            self._core_save_canvas(config_path)

            # Save metadata
            meta_data = {
                "name": checkpoint_name,
                "timestamp": datetime.now().isoformat(),
                "source_file": os.path.basename(self.current_canvas_file)
            }
            with open(meta_path, "w") as f:
                json.dump(meta_data, f)

            # Save thumbnail
            pixmap = self._capture_drawing_area_snapshot()
            if pixmap:
                pixmap.save(png_path, "PNG")

            self.refresh_history_list()
            QMessageBox.information(self, "Success", f"Checkpoint '{checkpoint_name}' created.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create checkpoint: {str(e)}")
    
    def _load_checkpoint(self, checkpoint_name):
        try:
            history_dir = os.path.join(os.path.dirname(self.current_canvas_file), "history")
            config_path = os.path.join(history_dir, f"{checkpoint_name}.json")

            if not os.path.exists(config_path):
                QMessageBox.critical(self, "Error", f"Checkpoint file not found: {config_path}")
                return

            self._do_open_canvas(config_path)
            QMessageBox.information(self, "Loaded", f"Checkpoint '{checkpoint_name}' loaded.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load checkpoint: {str(e)}")
    
    def _delete_checkpoint(self, checkpoint_name):
        try:
            history_dir = os.path.join(os.path.dirname(self.current_canvas_file), "history")
            config_path = os.path.join(history_dir, f"{checkpoint_name}.json")
            meta_path = os.path.join(history_dir, f"{checkpoint_name}.meta")
            png_path = os.path.join(history_dir, f"{checkpoint_name}.png")

            for path in [config_path, meta_path, png_path]:
                if os.path.exists(path):
                    os.remove(path)

            self.refresh_history_list()
            QMessageBox.information(self, "Deleted", f"Checkpoint '{checkpoint_name}' deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete checkpoint: {str(e)}")
        
    def _capture_drawing_area_snapshot(self):
        try:
            pixmap = QPixmap(self.drawing_area.size())
            pixmap.fill(QColor("white"))
            painter = QPainter(pixmap)
            self.drawing_area.render(painter)
            painter.end()
            return pixmap
        except Exception:
            return None   

    def refresh_history_list(self):
        if not self.current_canvas_file:
            return

        history_dir = os.path.join(os.path.dirname(self.current_canvas_file), "history")

        # Clear existing items
        while self._side_menu.checkpoint_list_layout.count() > 1:
            self._side_menu.checkpoint_list_layout.takeAt(0)

        if not os.path.exists(history_dir):
            return

        # Get all checkpoints
        meta_files = sorted([f for f in os.listdir(history_dir) if f.endswith(".meta")])

        if not meta_files:
            return

        for meta_file in meta_files:
            checkpoint_name = meta_file.replace(".meta", "")
            meta_path = os.path.join(history_dir, meta_file)

            try:
                with open(meta_path, "r") as f:
                    meta = json.load(f)
                    display_name = meta.get("name", checkpoint_name)
                    timestamp = meta.get("timestamp", "")
            except:
                display_name = checkpoint_name
                timestamp = ""

            # Create checkpoint item
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(4, 4, 4, 4)

            label = QLabel(f"{display_name}\n{timestamp[:10]}")
            label.setStyleSheet("font-size: 9pt;")

            load_btn = QPushButton("Load")
            load_btn.setFixedWidth(50)
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedWidth(60)

            load_btn.clicked.connect(lambda checked, cp=checkpoint_name: self._load_checkpoint(cp))
            delete_btn.clicked.connect(lambda checked, cp=checkpoint_name: self._delete_checkpoint(cp))

            item_layout.addWidget(label)
            item_layout.addStretch()
            item_layout.addWidget(load_btn)
            item_layout.addWidget(delete_btn)

            self._side_menu.checkpoint_list_layout.insertWidget(self._side_menu.checkpoint_list_layout.count() - 1, item_widget)            


class DrawSizeDialog(QDialog):
    def __init__(self, parent, current_value):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(340, 170)
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        self.bg_widget = QWidget(self)
        self.bg_widget.setStyleSheet("""
            background: white;
            border-radius: 22px;
            border: 2px solid #222;
        """)
        self.bg_widget.setGeometry(0, 0, 340, 170)
        self.bg_widget.lower()
        label = QLabel("Draw Size", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #222; background: none;")
        layout.addWidget(label)
        self.slider = CustomSlider(2, 32, current_value, self)
        layout.addWidget(self.slider, alignment=Qt.AlignmentFlag.AlignCenter)
        ok_btn = QPushButton("OK", self)
        ok_btn.setFixedHeight(36)
        ok_btn.setStyleSheet("""
            background: Transparent;
            border-radius: 12px;
            border: Transparent;
            font-size: 12pt;
            font-weight: bold;
        """)
        layout.addWidget(ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        ok_btn.clicked.connect(self.accept)

    def getValue(self):
        return self.slider.getValue()
    
    


class EraserSizeDialog(QDialog):
    def __init__(self, parent, current_value):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(340, 170)
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        self.bg_widget = QWidget(self)
        self.bg_widget.setStyleSheet("""
            background: white;
            border-radius: 22px;
            border: 2px solid #222;
        """)
        self.bg_widget.setGeometry(0, 0, 340, 170)
        self.bg_widget.lower()
        label = QLabel("Eraser Size", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #222; background: none;")
        layout.addWidget(label)
        self.slider = CustomSlider(4, 64, current_value, self)
        layout.addWidget(self.slider, alignment=Qt.AlignmentFlag.AlignCenter)
        ok_btn = QPushButton("OK", self)
        ok_btn.setFixedHeight(36)
        ok_btn.setStyleSheet("""
            background: Transparent;
            border-radius: 12px;
            border: Transparent;
            font-size: 12pt;
            font-weight: bold;
        """)
        layout.addWidget(ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        ok_btn.clicked.connect(self.accept)

    def getValue(self):
        return self.slider.getValue()

    def paintEvent(self, event):
        # Draw rounded background (optional, since bg_widget covers it)
        pass


class CustomSlider(QWidget):
    def __init__(self, min_value=4, max_value=64, value=12, parent=None):
        super().__init__(parent)
        self.setFixedHeight(54)
        self.setMinimumWidth(260)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self._dragging = False

    def setValue(self, v):
        v = max(self.min_value, min(self.max_value, v))
        if self.value != v:
            self.value = v
            self.valueChanged.emit(v)
            self.update()

    def getValue(self):
        return self.value

    def mousePressEvent(self, event):
        self._dragging = True
        self._set_value_from_pos(event.position().x())

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._set_value_from_pos(event.position().x())

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def _set_value_from_pos(self, x):
        margin = 28
        w = self.width() - 2 * margin
        ratio = (x - margin) / w
        v = int(self.min_value + ratio * (self.max_value - self.min_value))
        self.setValue(v)

    # Custom signal
    from PyQt6.QtCore import pyqtSignal
    valueChanged = pyqtSignal(int)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        margin = 28
        y = self.height() // 2
        w = self.width() - 2 * margin
        # Draw background line (faded)
        bg_color = QColor(0, 0, 0, 60)
        painter.setPen(QPen(bg_color, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(margin, y, self.width() - margin, y)
        # Draw filled line (opaque)
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        filled_x = int(margin + ratio * w)
        painter.setPen(QPen(QColor("#222"), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(margin, y, filled_x, y)
        # Draw handle (circle)
        handle_radius = 16
        painter.setBrush(QColor("#fff"))
        painter.setPen(QPen(QColor("#222"), 2))
        painter.drawEllipse(QPointF(filled_x, y), handle_radius, handle_radius)
        # Draw current value inside handle
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor("#222"))
        painter.drawText(QRectF(filled_x-handle_radius, y-handle_radius, handle_radius*2, handle_radius*2),
                         Qt.AlignmentFlag.AlignCenter, str(self.value))


class GenericSizeDialog(QDialog):
    def __init__(self, parent, current_value, min_value=1, max_value=64, title="Adjust Draw Size"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Container widget with white background
        container = QWidget()
        container.setStyleSheet("""
            background: white;
            border: 2px solid #222;
            border-radius: 12px;
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14pt; color: #222; background: transparent; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title_label)
        
        # Slider
        self.slider = CustomSlider(min_value, max_value, current_value)
        self.slider.setFixedWidth(200)
        container_layout.addWidget(self.slider, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # OK Button
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #222;
                font-size: 12pt;
                padding: 5px 15px;
            }
            QPushButton:hover {
                color: #666;
                border: 2px solid #222;
                padding: 3px 13px;
            }
        """)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        container_layout.addWidget(ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(container)

    def getValue(self):
        return self.slider.getValue()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = UIMode()
    win.show()
    sys.exit(app.exec())
