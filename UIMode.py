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
    QFileDialog, QMessageBox, QFontComboBox, QLineEdit, QTextEdit
)
from PyQt6.QtCore import (
    Qt, QSize, QPropertyAnimation, QRect,
    QPoint, QEasingCurve, QTimer, pyqtSignal, QEvent,
    QParallelAnimationGroup, QEventLoop, QRectF, QPointF, QObject,
    pyqtProperty, QThread, pyqtSlot, QRegularExpression
    )


from PyQt6.QtGui import (
    QIcon, QPainter, QPen, QColor, QMouseEvent,
    QCursor, QFont, QColor, QPixmap, QClipboard, QAction, QBrush, 
    QImage, QRegularExpressionValidator
    )
import sys
import math
import json
import base64, json
from io import BytesIO
from datetime import datetime
from pathlib import Path

_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

TOOL_MENU = [
    {
        "type": "category", "name": "shapes", "icon": os.path.join(_ASSETS_DIR, "tool-shapes.png"), "children": [
            {"type": "tool", "name": "circle", "icon": "◯"},
            {"type": "tool", "name": "rect", "icon": "▭"},
            {"type": "tool", "name": "triangle", "icon": "△"},
            {"type": "tool", "name": "line", "icon": "—"},
            {"type": "tool", "name": "cross", "icon": "✕"},
            {"type": "tool", "name": "roundrect", "icon": "⬭"},
        ]
    },
    {
        "type": "category", "name": "colors", "icon": os.path.join(_ASSETS_DIR, "tool-colors.png"), "children": [
            {"type": "tool", "name": "fill", "icon": os.path.join(_ASSETS_DIR, "tool-colors-fill.png"), "icon_size": 66},
            {"type": "tool", "name": "crop", "icon": os.path.join(_ASSETS_DIR, "tool-colors-crop.png"), "icon_size": 66},
            {"type": "tool", "name": "eraser", "icon": os.path.join(_ASSETS_DIR, "tool-colors-eraser.png"), "icon_size": 66},
            {"type": "tool", "name": "draw", "icon": os.path.join(_ASSETS_DIR, "tool-colors-paint.png"), "icon_size": 66},
        ]
    },
    {
        "type": "category", "name": "label", "icon": os.path.join(_ASSETS_DIR, "tool-label.png"), "icon_size": 250, "children": [
            {"type": "tool", "name": "label", "icon": os.path.join(_ASSETS_DIR, "tool-label-label.png"), "icon_size": 96},
            {"type": "tool", "name": "arrow", "icon": os.path.join(_ASSETS_DIR, "tool-label-arrows.png"), "icon_size": 96},
            {"type": "tool", "name": "framewithlabel", "icon": os.path.join(_ASSETS_DIR, "tool-label-rectwithlabel.png"), "icon_size": 90},
            {"type": "tool", "name": "roundframewithlabel", "icon": os.path.join(_ASSETS_DIR, "tool-label-roundedrectwithlabel.png"), "icon_size": 90},
        ]
    },
]

CUSTOM_BORDER_COLOR = "#ffffff"
CUSTOM_OBJECT_COLOR = "#ffffff"
_RECENT_FILES_PATH = Path.home() / ".lds-project" / "recent_files.json"


class SideMenuPanel(QWidget):
    space_added   = pyqtSignal()
    space_selected = pyqtSignal(int)
    
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
        tab_row.setContentsMargins(2, 0, 0, 0)
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
        tab_widget.setStyleSheet("background: white; border-left: 1px solid #ddd;")
        tab_widget.setLayout(tab_row)
        layout.addWidget(tab_widget)

        # Stacked content
        from PyQt6.QtWidgets import QStackedWidget
        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        # File page
        file_page = QWidget()
        file_layout = QVBoxLayout(file_page)
        file_layout.setContentsMargins(2, 8, 0, 8)
        file_layout.setSpacing(0)
        self.file_actions = {}
        self._recent_file_buttons = []

        # Top group
        for item in ["Open", "Recent"]:
            lbl = QPushButton(item)
            lbl.setFlat(True)
            lbl.setFixedHeight(38)
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            file_layout.addWidget(lbl)
            self.file_actions[item] = lbl

        # Collapsible recent files list (sits below "Recent" button)
        recent_scroll = QScrollArea()
        recent_scroll.setWidgetResizable(True)
        recent_scroll.setStyleSheet("QScrollArea { border: 1px; background: transparent; margin: 0 8px; }")
        recent_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        recent_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.recent_list_widget = QWidget()
        self.recent_list_layout = QVBoxLayout(self.recent_list_widget)
        self.recent_list_layout.setContentsMargins(2, 2, 4, 2)
        self.recent_list_layout.setSpacing(2)
        self.recent_list_widget.setStyleSheet("background: transparent; border: 1px;")
        _empty_lbl = QLabel("No recent files")
        _empty_lbl.setStyleSheet("color: #999; font-size: 9pt;")
        _empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recent_list_layout.addWidget(_empty_lbl)

        recent_scroll.setWidget(self.recent_list_widget)
        recent_scroll.setMaximumHeight(0)
        self.recent_scroll_area = recent_scroll
        file_layout.addWidget(recent_scroll)

        self._recent_expanded = False
        self._recent_anim = QPropertyAnimation(recent_scroll, b"maximumHeight")
        self._recent_anim.setDuration(300)
        self._recent_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        def toggle_recent_list():
            expanding = not self._recent_expanded
            self._recent_anim.stop()
            self._recent_anim.setStartValue(recent_scroll.maximumHeight())
            self._recent_anim.setEndValue(190 if expanding else 0)
            self._recent_expanded = expanding
            self._recent_anim.start()

        self.file_actions["Recent"].clicked.connect(toggle_recent_list)

        # Bottom group
        for item in ["Save", "Save As", "Export", "Settings", "Hotkeys", "Exit"]:
            lbl = QPushButton(item)
            lbl.setFlat(True)
            lbl.setFixedHeight(38)
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            lbl.setStyleSheet("border: 1px;")
            file_layout.addWidget(lbl)
            self.file_actions[item] = lbl
        file_layout.addStretch()
        self._stack.addWidget(file_page)

        # Pages page
        pages_page = QWidget()
        pages_layout = QVBoxLayout(pages_page)
        pages_layout.setContentsMargins(0, 8, 0, 8)
        pages_layout.setSpacing(8)

        # Create Space button
        self.create_space_btn = QPushButton("+ Create Space")
        self.create_space_btn.setFixedHeight(40)
        self.create_space_btn.setStyleSheet("""
            QPushButton {
                background: #ff6600; color: white; border: none;
                font-weight: bold; border-radius: 4px; font-size: 11pt; margin: 0 8px;
            }
            QPushButton:hover { background: #e55a00; }
        """)
        self.create_space_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.create_space_btn.clicked.connect(self.space_added.emit)
        pages_layout.addWidget(self.create_space_btn)

        # Spaces header
        spaces_header = QLabel("Spaces")
        spaces_header.setStyleSheet(
            "font-weight: bold; font-size: 12pt; padding-left: 8px; color: #222;"
        )
        spaces_header.setFixedHeight(32)
        pages_layout.addWidget(spaces_header)

        # Spaces scroll (always visible, no toggle)
        spaces_scroll = QScrollArea()
        spaces_scroll.setWidgetResizable(True)
        spaces_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; margin: 0 8px; }"
        )
        spaces_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        spaces_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.spaces_list_widget = QWidget()
        self.spaces_list_widget.setStyleSheet("background: transparent; border: none;")
        self.spaces_list_layout = QVBoxLayout(self.spaces_list_widget)
        self.spaces_list_layout.setContentsMargins(4, 4, 4, 4)
        self.spaces_list_layout.setSpacing(4)
        _no_spaces_lbl = QLabel("No spaces yet")
        _no_spaces_lbl.setStyleSheet("color: #999; font-size: 9pt;")
        _no_spaces_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spaces_list_layout.addWidget(_no_spaces_lbl)
        self.spaces_list_layout.addStretch()

        spaces_scroll.setWidget(self.spaces_list_widget)
        pages_layout.addWidget(spaces_scroll, stretch=1)
        self._space_item_filters = []
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
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(200)

        self.checkpoint_list_widget = QWidget()
        self.checkpoint_list_layout = QVBoxLayout(self.checkpoint_list_widget)
        self.checkpoint_list_layout.setContentsMargins(4, 4, 4, 4)
        self.checkpoint_list_layout.setSpacing(6)
        self.checkpoint_list_widget.setStyleSheet("background: transparent; border: none;")

        empty_label = QLabel("No checkpoints yet")
        empty_label.setStyleSheet("color: #999; font-size: 9pt; text-align: center;")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkpoint_list_layout.addWidget(empty_label)
        self.checkpoint_list_layout.addStretch()
        self._checkpoint_filters = []

        scroll_area.setWidget(self.checkpoint_list_widget)

        # Start collapsed via height=0 (stays in layout, animation controls size)
        scroll_area.setMaximumHeight(0)
        self.checkpoint_scroll_area = scroll_area
        history_layout.addWidget(scroll_area)

        history_layout.addStretch()
        self._stack.addWidget(history_page)

        # Slide animation
        self._history_anim = QPropertyAnimation(scroll_area, b"maximumHeight")
        self._history_anim.setDuration(500)
        self._history_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Connect File History button to toggle
        def toggle_history_list():
            expanding = not self._history_expanded
            self._history_anim.stop()
            self._history_anim.setStartValue(scroll_area.maximumHeight())
            self._history_anim.setEndValue(200 if expanding else 0)
            self.file_history_btn.setText(f"File History {'-' if expanding else '▶'}")
            self._history_expanded = expanding
            self._history_anim.start()

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
            
        # Store for use by refresh_recent_list
        self._accent_hex = hex_color

        # Recent file buttons follow accent
        for btn in getattr(self, '_recent_file_buttons', []):
            btn.setStyleSheet(f"""
                QPushButton {{ text-align: left; padding: 0 18px 0 28px;
                              border: none; font-size: 10pt; background: white; color: #555; }}
                QPushButton:hover {{ background: {hex_color}; color: white; }}
            """)
        
        # Create Checkpoint button follows accent color
        darker = color.darker(120).name()
        self.create_checkpoint_btn.setStyleSheet(f"""
            QPushButton {{
                background: {hex_color}; color: white; border: none;
                font-weight: bold; border-radius: 4px; font-size: 11pt; margin: 0 8px;
            }}
            QPushButton:hover {{ background: {darker}; }}
        """)
        
        # Create Space button follows accent color
        if hasattr(self, 'create_space_btn'):
            self.create_space_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {hex_color}; color: white; border: none;
                    font-weight: bold; border-radius: 4px; font-size: 11pt; margin: 0 8px;
                }}
                QPushButton:hover {{ background: {darker}; }}
            """)

        # File History toggle button hover follows accent
        self.file_history_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: #222; border: none;
                font-weight: bold; font-size: 12pt; text-align: left; padding-left: 8px;
            }}
            QPushButton:hover {{ color: {hex_color}; }}
        """)

        # Propagate to existing checkpoint item filters
        for f in self._checkpoint_filters:
            f.update_accent(hex_color)
            
    def _toggle_history_view(self):
        pass
    
    def refresh_recent_list(self, recent_files, on_open=None, tooltip_fn=None):
        while self.recent_list_layout.count():
            item = self.recent_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._recent_file_buttons = []

        accent = getattr(self, "_accent_hex", "#ff6600")

        if not recent_files:
            lbl = QLabel("No recent files")
            lbl.setStyleSheet("color: #999; font-size: 9pt;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.recent_list_layout.addWidget(lbl)
            return

        for fp in recent_files[:5]:
            import os as _os
            name = _os.path.basename(fp)
            btn = QPushButton(name)
            btn.setFlat(True)
            btn.setFixedHeight(34)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{ text-align: left; padding: 0 18px 0 28px;
                              border: none; font-size: 10pt; background: white; color: #555; }}
                QPushButton:hover {{ background: {accent}; color: white; }}
            """)
            if on_open:
                btn.clicked.connect(lambda checked, path=fp: on_open(path))
            if tooltip_fn:
                btn.enterEvent = lambda event, path=fp: tooltip_fn(path)
            self.recent_list_layout.addWidget(btn)
            self._recent_file_buttons.append(btn)
            
    def refresh_spaces(self, spaces: list, current_space_idx: int, current_page_idx: int,
               on_space_selected=None, on_page_selected=None, on_delete_page=None, on_rename_page=None, 
               tooltip_fn=None, on_rename_space=None, on_delete_space=None):
        while self.spaces_list_layout.count():
            item = self.spaces_list_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()
        
        self._space_item_filters.clear()
        accent = getattr(self, "_accent_hex", "#ff6600")

        if not spaces:
            lbl = QLabel("No spaces yet")
            lbl.setStyleSheet("color: #999; font-size: 9pt;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.spaces_list_layout.addWidget(lbl)
            self.spaces_list_layout.addStretch()
            return

        for si, space in enumerate(spaces):
            is_active = (si == current_space_idx)
            arrow = "▼" if is_active else "▶"

            header_btn = QPushButton(f"{arrow}  {space['name']}")
            header_btn.setFixedHeight(34)
            header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if is_active:
                darker = QColor(accent).darker(115).name()
                header_btn.setStyleSheet(f"""
                    QPushButton {{
                        text-align: left; padding: 0 10px; border: none;
                        background: {accent}; color: white;
                        border-radius: 4px; font-size: 10pt; font-weight: bold;
                    }}
                    QPushButton:hover {{ background: {darker}; }}
                """)
            else:
                header_btn.setStyleSheet("""
                    QPushButton {
                        text-align: left; padding: 0 10px; border: none;
                        background: #f0f0f0; color: #444;
                        border-radius: 4px; font-size: 10pt;
                    }
                    QPushButton:hover { background: #e4e4e4; }
                """)

            f_hdr = _SpaceHeaderFilter(
                header_btn,
                on_click=lambda _si=si: (
                    on_space_selected(_si) if on_space_selected else None,
                    tooltip_fn("Double-click to rename / delete", 1500) if tooltip_fn else None,
                ),
                on_dblclick=lambda _si=si: (
                    on_rename_space(_si) if on_rename_space else None
                ),
            )
            self._space_item_filters.append(f_hdr)
            self.spaces_list_layout.addWidget(header_btn)

            # Only show page list for the active space
            if not is_active:
                continue

            for pi, page in enumerate(space["pages"]):
                is_active_page = (pi == current_page_idx)

                item_widget = QWidget()
                item_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
                item_widget.setStyleSheet(
                    f"background: {'#edf4ff' if is_active_page else '#f9f9f9'}; border-radius: 4px;"
                )
                item_widget.setCursor(Qt.CursorShape.PointingHandCursor)
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(6, 6, 6, 6)
                item_layout.setSpacing(8)

                # Thumbnail
                thumb_label = QLabel()
                thumb_label.setFixedSize(64, 46)
                thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                thumb_label.setStyleSheet(
                    f"border: 2px solid {accent if is_active_page else '#e0e0e0'}; "
                    f"background: #e0e0e0; border-radius: 2px;"
                )
                if page.get("thumbnail"):
                    thumb_label.setPixmap(
                        page["thumbnail"].scaled(
                            60, 42,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                    )
                item_layout.addWidget(thumb_label)

                # Name + date
                info_layout = QVBoxLayout()
                info_layout.setContentsMargins(0, 0, 0, 0)
                info_layout.setSpacing(2)
                name_lbl = QLabel(page["name"])
                name_lbl.setStyleSheet(
                    f"border: none; background: transparent; font-size: 9pt; font-weight: bold; "
                    f"color: {accent if is_active_page else '#222'};"
                )
                date_lbl = QLabel(page.get("created", "")[:10])
                date_lbl.setStyleSheet(
                    "border: none; background: transparent; font-size: 8pt; color: #999;"
                )
                info_layout.addWidget(name_lbl)
                info_layout.addWidget(date_lbl)
                item_layout.addLayout(info_layout)
                item_layout.addStretch()

                # Delete (X) button
                del_btn = QPushButton("✕")
                del_btn.setFixedSize(22, 22)
                del_btn.setStyleSheet(
                    "QPushButton { border: none; color: #aaa; font-size: 11pt; background: transparent; }"
                    "QPushButton:hover { color: #ff3300; }"
                )
                if on_delete_page:
                    del_btn.clicked.connect(lambda _, _si=si, _pi=pi: on_delete_page(_si, _pi))
                item_layout.addWidget(del_btn)

                f = _CheckpointItemFilter(
                    item_widget, accent,
                    on_dblclick=lambda _si=si, _pi=pi: (
                        on_rename_page(_si, _pi) if on_rename_page else None
                    ),
                    on_click=lambda _si=si, _pi=pi: (
                        tooltip_fn("Double-click to rename", 1500) if tooltip_fn else None,
                        on_page_selected(_si, _pi) if on_page_selected else None,
                    ),
                )
                self._space_item_filters.append(f)

                self.spaces_list_layout.addWidget(item_widget)

        self.spaces_list_layout.addStretch()           

# Context Menu - Properties

class ColorButton(QPushButton):
    def __init__(self, color, parent=None, is_transparent=False):
        super().__init__(parent)
        self.is_transparent = is_transparent
        self.color = QColor(Qt.GlobalColor.transparent) if is_transparent else QColor(color)
        self.setFixedSize(28, 28)
        self.setCheckable(True)
        if is_transparent:
            self.setStyleSheet(
                "border-radius: 14px; background: white; border: 2px solid #222;"
            )
        else:
            self.setStyleSheet(
                f"border-radius: 14px; background: {self.color.name()}; border: 2px solid #222;"
            )
        self._hovered = False
    
    def enterEvent(self, event):
        self._hovered = True
        if self.is_transparent:
            self.setStyleSheet(
                "border-radius: 14px; background: white; border: 2px solid #ff6600;"
            )
        else:
            self.setStyleSheet(
                f"border-radius: 14px; background: {self.color.name()}; border: 2px solid #ff6600;"
            )
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update()

    def leaveEvent(self, a0):
        self._hovered = False
        if self.is_transparent:
            self.setStyleSheet(
                "border-radius: 14px; background: white; border: 2px solid #222;"
            )
        else:
            self.setStyleSheet(
                f"border-radius: 14px; background: {self.color.name()}; border: 2px solid #222;"
            )
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def paintEvent(self, a0):
        super().paintEvent(a0)
        if self.is_transparent:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor("#cc0000"), 2))
            painter.drawLine(6, self.height() - 6, self.width() - 6, 6)
            painter.end()
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
        # Parent the tooltip on UIMode (parent of DrawingArea), not on this dialog
        _ui_parent = parent.parent() if parent is not None and parent.parent() is not None else (parent or self)
        self.custom_tooltip = CustomToolTip(_ui_parent)
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
        self.weight_slider = CustomSlider(0, 20, 2, self)
        layout.addWidget(self.weight_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        self.weight_slider.setValue(border_weight)
        
        global CUSTOM_BORDER_COLOR, CUSTOM_OBJECT_COLOR

        # Border Color
        border_color_label = QLabel("Border Color")
        border_color_label.setStyleSheet("border: none;")
        layout.addWidget(border_color_label)
        border_color_row = QHBoxLayout()
        self.border_color_buttons = []
        self._initial_border_color = border_color
        self._initial_fill_color = fill_color
        self.selected_border_color = QColor(Qt.GlobalColor.transparent) if border_color == "transparent" else QColor(border_color)
        border_colors = ["#000000", "#ffb366", "#ffe066", "#b3ff66", "transparent", CUSTOM_BORDER_COLOR, ]
        for i, color in enumerate(border_colors):
            is_transp = (color == "transparent")
            btn = ColorButton(color, is_transparent=is_transp)
            if i == len(border_colors) - 1:
                # Last button: show quick properties color picker
                btn.clicked.connect(lambda _, b=btn: self._pick_custom_border_color(b))
            elif is_transp:
                btn.clicked.connect(partial(self._on_border_color_selected, "transparent", btn))
            else:
                btn.clicked.connect(partial(self._on_border_color_selected, color, btn))
            border_color_row.addWidget(btn)
            self.border_color_buttons.append(btn)
            if is_transp and border_color.lower() == "transparent":
                btn.setChecked(True)
            elif not is_transp and color.lower() == border_color.lower():
                btn.setChecked(True)
        layout.addLayout(border_color_row)

        # Sync weight slider with transparent border button (connected after buttons exist)
        def _on_weight_changed(val):
            if val == 0:
                # Auto-select transparent border button
                for btn in self.border_color_buttons:
                    btn.blockSignals(True)
                    btn.setChecked(False)
                    btn.blockSignals(False)
                # The transparent button is at index 4
                if len(self.border_color_buttons) > 4:
                    self.border_color_buttons[4].blockSignals(True)
                    self.border_color_buttons[4].setChecked(True)
                    self.border_color_buttons[4].blockSignals(False)
                self.selected_border_color = QColor(Qt.GlobalColor.transparent)
            else:
                # If border was transparent, restore to the shape's original border color
                if self.selected_border_color.alpha() == 0:
                    restore_color = QColor(self._initial_border_color) if self._initial_border_color and self._initial_border_color != "transparent" else QColor("#000000")
                    for btn in self.border_color_buttons:
                        btn.blockSignals(True)
                        btn.setChecked(False)
                        btn.blockSignals(False)
                    # Try to find a matching preset button, else fall back to first
                    matched = False
                    for btn in self.border_color_buttons:
                        if not btn.is_transparent and btn.color.name() == restore_color.name():
                            btn.blockSignals(True)
                            btn.setChecked(True)
                            btn.blockSignals(False)
                            matched = True
                            break
                    if not matched:
                        self.border_color_buttons[0].blockSignals(True)
                        self.border_color_buttons[0].setChecked(True)
                        self.border_color_buttons[0].blockSignals(False)
                        restore_color = QColor("#000000")
                    self.selected_border_color = restore_color
        self.weight_slider.valueChanged.connect(_on_weight_changed)

        # Object Color
        object_color_label = QLabel("Object Color")
        object_color_label.setStyleSheet("border: none;")
        layout.addWidget(object_color_label)
        object_color_label.setVisible(shape_type != "line")
        object_color_container = QWidget()
        object_color_container.setStyleSheet("border: none;")
        object_color_row = QHBoxLayout(object_color_container)
        object_color_row.setContentsMargins(0, 0, 0, 0)       
        object_color_row.setSpacing(10) 
        self.object_color_buttons = []
        self.selected_object_color = QColor(Qt.GlobalColor.transparent) if fill_color == "transparent" else QColor(fill_color)
        object_colors = ["#000000", "#ffb366", "#ffe066", "#b3ff66", "transparent", CUSTOM_OBJECT_COLOR, ]
        for i, color in enumerate(object_colors):
            is_transp = (color == "transparent")
            btn = ColorButton(color, is_transparent=is_transp)
            if i == len(object_colors) - 1:
                btn.clicked.connect(lambda _, b=btn: self._pick_custom_object_color(b))
            elif is_transp:
                btn.clicked.connect(partial(self._on_object_color_selected, "transparent", btn))
            else:
                btn.clicked.connect(partial(self._on_object_color_selected, color, btn))
            object_color_row.addWidget(btn)
            self.object_color_buttons.append(btn)
            if is_transp and fill_color.lower() == "transparent":
                btn.setChecked(True)
            elif not is_transp and color.lower() == fill_color.lower():
                btn.setChecked(True)
        object_color_container.setVisible(shape_type != "line")
        layout.addWidget(object_color_container)

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
        
        self._block_close = False

        # Close button (optional)
        close_btn = QPushButton("Close")
        def on_accept():
            border_weight = self.weight_slider.getValue()
            border_color_val = self.selected_border_color
            object_color_val = self.selected_object_color

            # Border weight 0 means transparent border
            if border_weight == 0:
                border_color_val = QColor(Qt.GlobalColor.transparent)

            border_is_transparent = border_color_val.alpha() == 0
            object_is_transparent = object_color_val.alpha() == 0

            if border_is_transparent and object_is_transparent and shape_type != "label":
                # Block ESC/other close attempts while tooltip is visible
                self._block_close = True
                self.custom_tooltip.show_tooltip("Both colors cannot be transparent", 2500)
                def _unblock():
                    self._block_close = False
                QTimer.singleShot(2500, _unblock)
                return
            
            else:
                props = {
                    "border_radius": self.radius_slider.getValue(),
                    "border_weight": border_weight,
                    "border_color": border_color_val,
                    "object_color": object_color_val,
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
        if color_hex == "transparent":
            self.selected_border_color = QColor(Qt.GlobalColor.transparent)
            # Auto-set weight to 0
            self.weight_slider.setValue(0)
        else:
            self.selected_border_color = QColor(color_hex)
            # If weight was 0, restore to 1 so the border is visible
            if self.weight_slider.getValue() == 0:
                self.weight_slider.setValue(1)
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
        if color_hex == "transparent":
            self.selected_object_color = QColor(Qt.GlobalColor.transparent)
        else:
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
    
    def closeEvent(self, event):
        if self._block_close:
            event.ignore()
            return
        super().closeEvent(event)


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
                bg_color = "white"
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
    if c.alpha() == 0:
        return "transparent"
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

def _pixmap_to_qimage(px: QPixmap) -> QImage:
    return px.toImage()

def _encode_qimage_b64(img: QImage) -> str:
    from PyQt6.QtCore import QBuffer, QIODevice
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    img.save(buf, "PNG")
    data = bytes(buf.data())
    return base64.b64encode(data).decode("utf-8")

def _serialize_shape_for_thread(shape: tuple) -> dict:
    tool = shape[0]
    if tool == "image":
        d = {
            "tool": "image",
            "start": _serialize_qpoint(shape[1]),
            "end": _serialize_qpoint(shape[2]),
            "qimage": _pixmap_to_qimage(shape[3]),
        }
        # Preserve rotation stored at shape[4]
        if len(shape) > 4 and isinstance(shape[4], (int, float)):
            d["rotation"] = shape[4]
        return d
    elif tool == "draw":
        d = {
            "tool": "draw",
            "points": [_serialize_qpoint(p) for p in shape[1]],
            "color": _serialize_qcolor(shape[3]),
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

def _serialize_page_state_for_thread(state) -> dict:
    return {
        "name": state["name"],
        "created": state.get("created", ""),
        "shapes": [_serialize_shape_for_thread(s) for s in state["shapes"]],
        "eraser_mask_img": _pixmap_to_qimage(state["eraser_mask"]),
        "eraser_strokes": [[_serialize_qpoint(p) for p in stroke]
                           for stroke in state["eraser_strokes"]],
        "scale_factor": state["scale_factor"],
        "zoom_percent": state["zoom_percent"],
        "pan_offset": [state["pan_offset"].x(), state["pan_offset"].y()],
        "tool_sizes": state["tool_sizes"],
    }

def _finalize_page_for_json(page_dict: dict) -> dict:
    page_dict["eraser_mask"] = _encode_qimage_b64(page_dict.pop("eraser_mask_img"))
    for shape in page_dict["shapes"]:
        if "qimage" in shape:
            shape["pixmap"] = _encode_qimage_b64(shape.pop("qimage"))
    return page_dict

def _serialize_shape(shape: tuple) -> dict:
    tool = shape[0]
    if tool == "image":
        d = {
                "tool": "image",
                "start": _serialize_qpoint(shape[1]),
                "end": _serialize_qpoint(shape[2]),
                "pixmap": _serialize_pixmap(shape[3]),
        }
        # Preserve rotation stored at shape[4]
        if len(shape) > 4 and isinstance(shape[4], (int, float)):
            d["rotation"] = shape[4]
        return d
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
        return {"type": "color", "value": "transparent" if item.alpha() == 0 else item.name()}
    elif isinstance(item, dict):
        # border_weight dict — values may include color strings, keep as-is
        return {"type": "dict", "value": item}
    elif isinstance(item, (int, float, bool, str)) or item is None:
        return {"type": "primitive", "value": item}
    return {"type": "primitive", "value": None}

def _deserialize_extra(d):
    if d["type"] == "color":
        if d["value"] == "transparent":
            return QColor(Qt.GlobalColor.transparent)
        return QColor(d["value"])
    elif d["type"] == "dict":
        return d["value"]
    else:
        return d["value"]

def _deserialize_shape(d: dict) -> tuple:
    tool = d["tool"]
    if tool == "image":
        shape = [
            "image",
            QPoint(*d["start"]),
            QPoint(*d["end"]),
            _deserialize_pixmap(d["pixmap"]),
        ]
        if "rotation" in d:
            shape.append(d["rotation"])
        return tuple(shape)
    elif tool == "draw":
        pts = [QPoint(*p) for p in d["points"]]
        color = QColor(Qt.GlobalColor.transparent) if d["color"] == "transparent" else QColor(d["color"])
        extras = [_deserialize_extra(e) for e in d.get("extras", [])]
        return tuple(["draw", pts, None, color] + extras)
    else:
        start = QPoint(*d["start"])
        end = QPoint(*d["end"])
        color = QColor(Qt.GlobalColor.transparent) if d["color"] == "transparent" else QColor(d["color"])
        extras = [_deserialize_extra(e) for e in d.get("extras", [])]
        return tuple([tool, start, end, color] + extras)
    

def _serialize_page_state(state) -> dict:
    return {
        "name": state["name"],
        "created": state.get("created", ""),
        "shapes":         [_serialize_shape(s) for s in state["shapes"]],
        "eraser_mask":    _serialize_pixmap(state["eraser_mask"]),
        "eraser_strokes": [[_serialize_qpoint(p) for p in stroke]
                           for stroke in state["eraser_strokes"]],
        "scale_factor":   state["scale_factor"],
        "zoom_percent":   state["zoom_percent"],
        "pan_offset":     [state["pan_offset"].x(), state["pan_offset"].y()],
        "tool_sizes":     state["tool_sizes"],
    }

def _deserialize_page_state(pd: dict, a4_size) -> dict:
    em = _deserialize_pixmap(pd["eraser_mask"])
    return {
        "name":           pd["name"],
        "shapes":         [_deserialize_shape(s) for s in pd["shapes"]],
        "eraser_mask":    em,
        "eraser_strokes": [[QPoint(*p) for p in stroke]
                           for stroke in pd["eraser_strokes"]],
        "scale_factor":   pd.get("scale_factor", 1.0),
        "zoom_percent":   pd.get("zoom_percent", 0),
        "pan_offset":     QPoint(*pd.get("pan_offset", [0, 0])),
        "tool_sizes":     pd.get("tool_sizes", {}),
        "created":        pd.get("created", ""),
        "shape_history":  [],
        "undo_stack":     [],
        "redo_stack":     [],
    }    


class _LabelTextOverlay(QWidget):
    # Movable, resizable text-box overlay for the label tool (MS Paint style).

    HANDLE_SIZE    = 8
    HANDLE_MARGIN  = 8    # Extra margin so handles are not clipped
    BORDER_HIT     = 12   # px from edge that triggers move cursor

    _RESIZE_CURSORS = [
        Qt.CursorShape.SizeFDiagCursor,  # 0 TL
        Qt.CursorShape.SizeVerCursor,    # 1 TM
        Qt.CursorShape.SizeBDiagCursor,  # 2 TR
        Qt.CursorShape.SizeHorCursor,    # 3 MR
        Qt.CursorShape.SizeFDiagCursor,  # 4 BR
        Qt.CursorShape.SizeVerCursor,    # 5 BM
        Qt.CursorShape.SizeBDiagCursor,  # 6 BL
        Qt.CursorShape.SizeHorCursor,    # 7 ML
    ]

    def __init__(self, drawing_area, canvas_rect, text_edit, toolbar):
        super().__init__(drawing_area)
        self._da              = drawing_area
        self._canvas_rect     = QRect(canvas_rect)
        self._te              = text_edit
        self._toolbar         = toolbar
        self._drag_mode       = None          # None | ('move',) | ('resize', idx)
        self._drag_start_global = None
        self._drag_start_rect   = None

        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: none;")

        layout = QVBoxLayout(self)
        hs = self.HANDLE_SIZE
        layout.setContentsMargins(hs, hs, hs, hs)
        layout.setSpacing(0)
        layout.addWidget(text_edit)
        self._te.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._te.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    # geometry helpers

    def handle_points_local(self):
        r  = self.rect()
        x1, y1, x2, y2 = r.left(), r.top(), r.right(), r.bottom()
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        return [
            QPoint(x1, y1), QPoint(cx, y1), QPoint(x2, y1),
            QPoint(x2, cy),
            QPoint(x2, y2), QPoint(cx, y2), QPoint(x1, y2),
            QPoint(x1, cy),
        ]

    def _hit_test(self, pos):
        hs = self.HANDLE_SIZE + 4
        for i, h in enumerate(self.handle_points_local()):
            if abs(pos.x() - h.x()) <= hs and abs(pos.y() - h.y()) <= hs:
                return ('resize', i)
        bh = self.BORDER_HIT
        if not self.rect().adjusted(bh, bh, -bh, -bh).contains(pos):
            return ('move',)
        return ('inside',)

    def _reposition(self):
        # Add margin for handles so they are not clipped
        margin = self.HANDLE_MARGIN
        tl = self._da.canvas_to_widget(self._canvas_rect.topLeft())
        br = self._da.canvas_to_widget(self._canvas_rect.bottomRight())
        widget_rect = QRect(tl, br).normalized()
        widget_rect = widget_rect.adjusted(-margin, -margin, margin, margin)
        self.setGeometry(widget_rect)
        if self._toolbar and self._toolbar.isVisible():
            toolbar_h = self._toolbar.height()
            tx = widget_rect.left()
            ty = max(0, widget_rect.top() - toolbar_h - 2)
            self._toolbar.move(tx, ty)
            min_w = getattr(self._da, '_label_toolbar_min_width', 310)
            self._toolbar.setFixedWidth(max(widget_rect.width(), min_w))

    # MouseEvents
    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        hit = self._hit_test(event.pos())
        if hit[0] in ('resize', 'move'):
            self._drag_mode         = hit
            self._drag_start_global = event.globalPosition().toPoint()
            self._drag_start_rect   = QRect(self._canvas_rect)
            self.grabMouse()
            event.accept()
        else:
            self._te.setFocus()
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_mode is None:
            hit = self._hit_test(event.pos())
            if hit[0] == 'resize':
                self.setCursor(self._RESIZE_CURSORS[hit[1]])
            elif hit[0] == 'move':
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.unsetCursor()
            super().mouseMoveEvent(event)
            return

        curr = event.globalPosition().toPoint()
        dw   = curr - self._drag_start_global
        dx   = int(round(dw.x() / self._da.scale_factor))
        dy   = int(round(dw.y() / self._da.scale_factor))

        orig = self._drag_start_rect
        x1, y1, x2, y2 = orig.left(), orig.top(), orig.right(), orig.bottom()

        if self._drag_mode[0] == 'move':
            new_rect = QRect(QPoint(x1 + dx, y1 + dy), QPoint(x2 + dx, y2 + dy))
            new_rect, guides = self._da._find_snap_guides(new_rect)
            self._da._active_guides = guides
        else:
            idx = self._drag_mode[1]
            if   idx == 0: new_rect = QRect(QPoint(x1+dx, y1+dy), QPoint(x2,    y2   ))
            elif idx == 1: new_rect = QRect(QPoint(x1,    y1+dy), QPoint(x2,    y2   ))
            elif idx == 2: new_rect = QRect(QPoint(x1,    y1+dy), QPoint(x2+dx, y2   ))
            elif idx == 3: new_rect = QRect(QPoint(x1,    y1   ), QPoint(x2+dx, y2   ))
            elif idx == 4: new_rect = QRect(QPoint(x1,    y1   ), QPoint(x2+dx, y2+dy))
            elif idx == 5: new_rect = QRect(QPoint(x1,    y1   ), QPoint(x2,    y2+dy))
            elif idx == 6: new_rect = QRect(QPoint(x1+dx, y1   ), QPoint(x2,    y2+dy))
            elif idx == 7: new_rect = QRect(QPoint(x1+dx, y1   ), QPoint(x2,    y2   ))
            else:          new_rect = QRect(orig)
            new_rect = new_rect.normalized()
            self._da._active_guides = []

        if new_rect.width() > 20 and new_rect.height() > 20:
            self._canvas_rect           = new_rect
            self._da._label_canvas_rect = new_rect
            self._reposition()
            # Force the text widget and canvas to repaint so the text
            # visibly moves live as the overlay is dragged.
            try:
                if self._te is not None:
                    self._te.update()
                    self._te.repaint()
            except Exception:
                pass
            try:
                self._da.update()
            except Exception:
                pass
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._drag_mode is not None:
            self.releaseMouse()
            self._drag_mode = None
            self.unsetCursor()
            self._da._active_guides = []
            # Sync logical canvas_rect to overlay geometry (minus margin)
            margin = self.HANDLE_MARGIN
            overlay_rect = self.geometry()
            logical_rect = overlay_rect.adjusted(margin, margin, -margin, -margin)
            da = self._da
            top_left = da.widget_to_canvas(logical_rect.topLeft())
            bottom_right = da.widget_to_canvas(logical_rect.bottomRight())
            self._canvas_rect = QRect(top_left, bottom_right).normalized()
            if hasattr(da, '_label_canvas_rect'):
                da._label_canvas_rect = QRect(self._canvas_rect)
            # Reposition overlay so the margin frame remains consistent after release
            self._reposition()
            # Ensure canvas is refreshed after commit
            try:
                da.update()
            except Exception:
                pass
        super().mouseReleaseEvent(event)

    # paint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Dotted blue border, matching DrawingArea
        pen = QPen(QColor("#0078d7"), 1, Qt.PenStyle.DotLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        margin = self.HANDLE_MARGIN
        r = self.rect().adjusted(margin, margin, -margin-1, -margin-1)
        painter.drawRect(r)
        # Handles (match DrawingArea)
        hs = self.HANDLE_SIZE // 2
        # Use same handle placement as DrawingArea
        x1, y1, x2, y2 = r.left(), r.top(), r.right(), r.bottom()
        xm, ym = (x1 + x2)//2, (y1 + y2)//2
        points = [
            QPoint(x1, y1), QPoint(xm, y1), QPoint(x2, y1),
            QPoint(x2, ym),
            QPoint(x2, y2), QPoint(xm, y2), QPoint(x1, y2),
            QPoint(x1, ym),
        ]
        for pt in points:
            painter.setBrush(QColor("white"))
            painter.setPen(QPen(QColor("#0078d7"), 2))
            painter.drawRect(pt.x() - hs, pt.y() - hs, self.HANDLE_SIZE, self.HANDLE_SIZE)
        painter.end()


class DrawingArea(QFrame):
    HANDLE_SIZE = 6
    shape_selected_for_edit = pyqtSignal()
    shape_deselected = pyqtSignal()
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
        
        self.open_file_callback = None
        self.save_file_callback = None
        self.tooltip_callback = None

        # Snap-to-grid state
        self.snap_to_grid = False
        self.grid_size = 20

        # Alignment guides state
        self._active_guides = []  # list of ("h"|"v", coordinate) tuples

        # Label / text-box tool state
        self._labeling = False
        self._label_start = None
        self._label_end = None
        self._text_edit_overlay = None
        self._text_edit_widget = None
        self._label_font_size = 14
        self._label_font_family = "Arial"
        self._label_font_underline = False
        self._label_text_align = "left"
        self._label_font_color = QColor("#000000")
        # Minimum width for the inline label toolbar (can be adjusted at runtime)
        self._label_toolbar_min_width = 310
        self._label_edit_index = None
        self._label_edit_rotation = 0
        
        self._draw_shift_anchor = None
        self._draw_freehand_base = None

    # Snap-to-grid helpers

    def _snap_to_grid(self, pt):
        g = self.grid_size
        return QPoint(round(pt.x() / g) * g, round(pt.y() / g) * g)

    def _snap_delta_to_grid(self, delta):
        g = self.grid_size
        return QPoint(round(delta.x() / g) * g, round(delta.y() / g) * g)

    # Alignment guide helpers

    def _get_alignment_edges(self, exclude_idx=None):
        """Collect horizontal and vertical alignment coordinates from all shapes + canvas edges."""
        vs = set()  # vertical lines (x coordinates)
        hs = set()  # horizontal lines (y coordinates)
        # Canvas edges and centers
        w, h = self.a4_size.width(), self.a4_size.height()
        vs.update([0, w // 2, w])
        hs.update([0, h // 2, h])
        for idx, shape in enumerate(self.shapes):
            if idx == exclude_idx:
                continue
            tool = shape[0]
            if tool == "draw" and isinstance(shape[1], list) and shape[1]:
                pts = shape[1]
                xs = [p.x() for p in pts]
                ys = [p.y() for p in pts]
                left, right = min(xs), max(xs)
                top, bottom = min(ys), max(ys)
            elif tool != "draw":
                r = QRect(shape[1], shape[2]).normalized()
                left, right = r.left(), r.right()
                top, bottom = r.top(), r.bottom()
            else:
                continue
            cx = (left + right) // 2
            cy = (top + bottom) // 2
            vs.update([left, cx, right])
            hs.update([top, cy, bottom])
        return vs, hs

    def _find_snap_guides(self, shape_rect, threshold=8):
        """Given the rect of the shape being moved, find alignment snaps.
        Returns (snapped_rect, guides) where guides is list of ("h"|"v", coord)."""
        vs, hs = self._get_alignment_edges(exclude_idx=self.selected_shape_index)
        guides = []
        dx = 0
        dy = 0
        # Shape edges
        sl, sr = shape_rect.left(), shape_rect.right()
        st, sb = shape_rect.top(), shape_rect.bottom()
        scx = (sl + sr) // 2
        scy = (st + sb) // 2
        # Check vertical alignment (x)
        best_vdist = threshold + 1
        for edge_x in vs:
            for sx in (sl, scx, sr):
                dist = abs(sx - edge_x)
                if dist < best_vdist:
                    best_vdist = dist
                    dx = edge_x - sx
                    best_vguide = edge_x
        if best_vdist <= threshold:
            guides.append(("v", best_vguide))
        else:
            dx = 0
        # Check horizontal alignment (y)
        best_hdist = threshold + 1
        for edge_y in hs:
            for sy in (st, scy, sb):
                dist = abs(sy - edge_y)
                if dist < best_hdist:
                    best_hdist = dist
                    dy = edge_y - sy
                    best_hguide = edge_y
        if best_hdist <= threshold:
            guides.append(("h", best_hguide))
        else:
            dy = 0
        snapped = shape_rect.translated(dx, dy)
        return snapped, guides

    def _find_resize_snap_guides(self, rect, handle_idx, threshold=8):
        """Find alignment snaps during resize, only adjusting the dragged edge(s)."""
        vs, hs = self._get_alignment_edges(exclude_idx=self.selected_shape_index)
        guides = []

        # Which edges are being dragged by this handle?
        drag_left   = handle_idx in (0, 6, 7)
        drag_right  = handle_idx in (2, 3, 4)
        drag_top    = handle_idx in (0, 1, 2)
        drag_bottom = handle_idx in (4, 5, 6)

        sl, sr = rect.left(), rect.right()
        st, sb = rect.top(), rect.bottom()

        # Vertical (x) snap — only the dragged left or right edge
        dx = 0
        check_xs = []
        if drag_left:
            check_xs.append(sl)
        if drag_right:
            check_xs.append(sr)

        best_vdist = threshold + 1
        best_vguide = None
        for edge_x in vs:
            for sx in check_xs:
                dist = abs(sx - edge_x)
                if dist < best_vdist:
                    best_vdist = dist
                    dx = edge_x - sx
                    best_vguide = edge_x
        if best_vdist <= threshold and best_vguide is not None:
            guides.append(("v", best_vguide))
        else:
            dx = 0

        # Horizontal (y) snap — only the dragged top or bottom edge
        dy = 0
        check_ys = []
        if drag_top:
            check_ys.append(st)
        if drag_bottom:
            check_ys.append(sb)

        best_hdist = threshold + 1
        best_hguide = None
        for edge_y in hs:
            for sy in check_ys:
                dist = abs(sy - edge_y)
                if dist < best_hdist:
                    best_hdist = dist
                    dy = edge_y - sy
                    best_hguide = edge_y
        if best_hdist <= threshold and best_hguide is not None:
            guides.append(("h", best_hguide))
        else:
            dy = 0

        # Only adjust the dragged edges, leaving the opposite edges in place
        snapped = QRect(rect)
        if drag_left:
            snapped.setLeft(rect.left() + dx)
        elif drag_right:
            snapped.setRight(rect.right() + dx)
        if drag_top:
            snapped.setTop(rect.top() + dy)
        elif drag_bottom:
            snapped.setBottom(rect.bottom() + dy)

        return snapped, guides

    def _apply_aspect_ratio_constraint(self, new_rect, orig_rect, handle_idx):
        """Constrain new_rect to orig_rect's aspect ratio during a corner handle resize.
        Only the dragged corner moves; the opposite corner stays fixed."""
        orig_w = orig_rect.width() or 1
        orig_h = orig_rect.height() or 1
        orig_aspect = orig_w / orig_h
        nw = new_rect.width()
        nh = new_rect.height()
        if nw == 0 or nh == 0:
            return new_rect
        # Drive by whichever axis changed proportionally more
        if abs(nw / orig_w) >= abs(nh / orig_h):
            nw_new = nw
            nh_new = max(1, int(round(nw / orig_aspect)))
        else:
            nh_new = nh
            nw_new = max(1, int(round(nh * orig_aspect)))
        # Re-anchor opposite corner for each corner handle
        if handle_idx == 0:    # TL dragged → BR fixed
            fixed = new_rect.bottomRight()
            return QRect(QPoint(fixed.x() - nw_new, fixed.y() - nh_new), fixed).normalized()
        elif handle_idx == 2:  # TR dragged → BL fixed
            fixed = new_rect.bottomLeft()
            return QRect(fixed, QPoint(fixed.x() + nw_new, fixed.y() - nh_new)).normalized()
        elif handle_idx == 4:  # BR dragged → TL fixed
            fixed = new_rect.topLeft()
            return QRect(fixed, QPoint(fixed.x() + nw_new, fixed.y() + nh_new)).normalized()
        elif handle_idx == 6:  # BL dragged → TR fixed
            fixed = new_rect.topRight()
            return QRect(QPoint(fixed.x() - nw_new, fixed.y()), QPoint(fixed.x(), fixed.y() + nh_new)).normalized()
        return new_rect

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
                pixmap = QPixmap(os.path.join(_ASSETS_DIR, "tool-colors-eraser.png"))
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
            # Block zoom while the inline text editor is open — font sizes
            # in the widget are tied to the current scale_factor and
            # rescaling mid-edit would desync editor vs committed text.
            if getattr(self, '_text_edit_overlay', None) is not None:
                event.accept()
                return
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
            pixmap = QPixmap(os.path.join(_ASSETS_DIR, "tool-colors-eraser.png"))
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
        # Commit text overlay if user clicks anywhere outside the overlay
        # Skip on right-click so contextMenuEvent can handle lock/unlock for labels
        if self._text_edit_overlay is not None and self._text_edit_overlay.isVisible():
            if event.button() == Qt.MouseButton.RightButton:
                return
            click_pos = event.position().toPoint()
            if not self._text_edit_overlay.geometry().contains(click_pos):
                self._commit_text_overlay()
            return

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
            # --- Line: endpoint-only editing (start/end handles, body move, commit) ---
            if self.preview_shape == "line":
                if self.selected_shape_index is not None:
                    hit_size = max(20, self.HANDLE_SIZE * 3)
                    for h_idx, h_pt in enumerate([self.preview_start, self.preview_end]):
                        hr = QRect(h_pt.x() - hit_size // 2, h_pt.y() - hit_size // 2, hit_size, hit_size)
                        if hr.contains(pt):
                            self._dragging_handle = h_idx  # 0 = start, 1 = end
                            self._pending_shape_action = "Resize"
                            return
                    ax, ay = self.preview_start.x(), self.preview_start.y()
                    bx, by = self.preview_end.x(), self.preview_end.y()
                    dx_l, dy_l = bx - ax, by - ay
                    lensq = dx_l * dx_l + dy_l * dy_l
                    if lensq > 0:
                        t_v = max(0.0, min(1.0, ((pt.x() - ax) * dx_l + (pt.y() - ay) * dy_l) / lensq))
                        dist_sq = (ax + t_v * dx_l - pt.x()) ** 2 + (ay + t_v * dy_l - pt.y()) ** 2
                    else:
                        dist_sq = (pt.x() - ax) ** 2 + (pt.y() - ay) ** 2
                    if dist_sq <= 100:
                        self._dragging_box = True
                        self._drag_offset = pt - self.preview_start
                        self.setCursor(Qt.CursorShape.ClosedHandCursor)
                        self._pending_shape_action = "Move"
                        return
                # Commit: save edited line or place new line
                if self.selected_shape_index is not None:
                    self.push_shape_restore(self.selected_shape_index, self._pending_shape_action or "Edit")
                    self._pending_shape_action = None
                    self.push_undo()
                    old_shape = self.shapes[self.selected_shape_index]
                    _tool, _start, _end, border_color = old_shape[:4]
                    fill_color = None
                    rotation = getattr(self, "preview_rotation", 0)
                    extra_dicts = []
                    label_text = None
                    lock_flag = None
                    for item in old_shape[4:]:
                        if isinstance(item, QColor):
                            fill_color = item
                        elif isinstance(item, bool):
                            lock_flag = item
                        elif isinstance(item, str):
                            label_text = item
                        elif isinstance(item, (int, float)):
                            rotation = item
                        elif isinstance(item, dict):
                            extra_dicts.append(item)
                    rotation = getattr(self, "preview_rotation", rotation)
                    new_shape = [self.preview_shape, self.preview_start, self.preview_end, border_color]
                    if fill_color is not None:
                        new_shape.append(fill_color)
                    if rotation != 0:
                        new_shape.append(rotation)
                    if label_text is not None:
                        new_shape.append(label_text)
                    for item in getattr(self, '_pending_shape_extras', []):
                        new_shape.append(item)
                    self._pending_shape_extras = []
                    for d in extra_dicts:
                        new_shape.append(d)
                    if lock_flag is not None:
                        new_shape.append(lock_flag)
                    self.shapes[self.selected_shape_index] = tuple(new_shape)
                else:
                    self.push_undo()
                    border_color = getattr(self, "preview_color", self.shape_color)
                    fill_color = getattr(self, "preview_fill_color", None)
                    rotation = getattr(self, "preview_rotation", 0)
                    shape_tuple = [self.preview_shape, self.preview_start, self.preview_end, border_color]
                    if fill_color is not None:
                        shape_tuple.append(fill_color)
                    if rotation != 0:
                        shape_tuple.append(rotation)
                    pending_label = getattr(self, '_pending_label_text', None)
                    if pending_label is not None:
                        shape_tuple.append(pending_label)
                        self._pending_label_text = None
                    for item in getattr(self, '_pending_shape_extras', []):
                        shape_tuple.append(item)
                    self._pending_shape_extras = []
                    self.shapes.append(tuple(shape_tuple))
                    self.preview_color = None
                    self.preview_fill_color = None
                    self.preview_rotation = 0
                self.preview_shape = None
                self.preview_start = None
                self.preview_end = None
                self.preview_pixmap = None
                self.preview_fill_color = None
                self.preview_rotation = 0
                self.selected_shape_index = None
                self._edit_locked_color = None
                self.update()
                return
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
                    # Store original rect for aspect-ratio constraint (Shift+resize)
                    self._resize_orig_rect = QRect(rect)
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
                label_text = None
                lock_flag = None

                for item in old_shape[4:]:
                    if isinstance(item, QColor):
                        fill_color = item
                    elif isinstance(item, bool):
                        lock_flag = item
                    elif isinstance(item, str):
                        label_text = item
                    elif isinstance(item, (int, float)):
                        rotation = item
                    elif isinstance(item, dict):
                        extra_dicts.append(item)

                # preview_rotation reflects any free-rotate done during this edit session
                rotation = getattr(self, "preview_rotation", rotation)

                locked_color = self._edit_locked_color if self._edit_locked_color is not None else self.shape_color

                if self.preview_shape == "image":
                    _edit_img_shape = ["image", self.preview_start, self.preview_end, self.preview_pixmap]
                    if rotation:
                        _edit_img_shape.append(rotation)
                    self.shapes[self.selected_shape_index] = tuple(_edit_img_shape)
                else:
                    # Rebuild shape preserving fill, rotation, label text, dicts, and lock
                    new_shape = [self.preview_shape, self.preview_start, self.preview_end, border_color]
                    if fill_color is not None:
                        new_shape.append(fill_color)
                    if rotation != 0:
                        new_shape.append(rotation)
                    # Preserve label text from the original shape
                    if label_text is not None:
                        new_shape.append(label_text)
                    for item in getattr(self, '_pending_shape_extras', []):
                        new_shape.append(item)
                    self._pending_shape_extras = []
                    for d in extra_dicts:
                        new_shape.append(d)
                    if lock_flag is not None:
                        new_shape.append(lock_flag)
                    self.shapes[self.selected_shape_index] = tuple(new_shape)

            else:
                self.push_undo()
                # Placing a new/pasted shape
                if self.preview_shape == "image":
                    _img_rotation = getattr(self, "preview_rotation", 0)
                    _img_shape = ["image", self.preview_start, self.preview_end, self.preview_pixmap]
                    if _img_rotation:
                        _img_shape.append(_img_rotation)
                    self.shapes.append(tuple(_img_shape))
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
                    # Preserve label text for pasted label shapes
                    pending_label = getattr(self, '_pending_label_text', None)
                    if pending_label is not None:
                        shape_tuple.append(pending_label)
                        self._pending_label_text = None
                    for item in getattr(self, '_pending_shape_extras', []):
                        shape_tuple.append(item)
                    self._pending_shape_extras = []
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
            self.shape_deselected.emit()
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

        if self.current_tool == "label" and event.button() == Qt.MouseButton.LeftButton:
            if self.canvas_contains(pt):
                self._labeling = True
                self._label_start = pt
                self._label_end = pt
                self.preview_shape = "label"
                self.preview_start = pt
                self.preview_end = pt
                self.preview_rotation = 0
                self.selected_shape_index = None
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
                        _img_rotation = getattr(self, "preview_rotation", 0)
                        _img_shape = ["image", self.preview_start, self.preview_end, self.preview_pixmap]
                        if _img_rotation:
                            _img_shape.append(_img_rotation)
                        self.shapes.append(tuple(_img_shape))
                        self.preview_shape = None
                        self.preview_start = None
                        self.preview_end = None
                        self.preview_pixmap = None
                        self.preview_rotation = 0
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
                        # Preserve label text for pasted label shapes
                        pending_label = getattr(self, '_pending_label_text', None)
                        if pending_label is not None:
                            shape_tuple.append(pending_label)
                            self._pending_label_text = None
                        for item in getattr(self, '_pending_shape_extras', []):
                            shape_tuple.append(item)
                        self._pending_shape_extras = []
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
            if self.snap_to_grid:
                pt = self._snap_to_grid(pt)
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
            # Alignment guides for freehand resize
            if not self.snap_to_grid:
                snapped, self._active_guides = self._find_resize_snap_guides(new_bbox, idx)
                new_bbox = snapped
            else:
                self._active_guides = []
            # Aspect ratio constraint: hold Shift on a corner handle to scale proportionally
            if (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) and idx in (0, 2, 4, 6):
                new_bbox = self._apply_aspect_ratio_constraint(new_bbox, self._orig_bbox, idx)
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
            # Apply snap-to-grid
            if self.snap_to_grid:
                delta = self._snap_delta_to_grid(delta)
            # Apply alignment guides (when grid is off)
            new_bbox = orig_bbox.translated(delta)
            if not self.snap_to_grid:
                new_bbox, self._active_guides = self._find_snap_guides(new_bbox)
                delta = QPoint(new_bbox.left() - orig_bbox.left(), new_bbox.top() - orig_bbox.top())
            else:
                self._active_guides = []
            self.preview_start = [p + delta for p in points]
            self.preview_bbox = new_bbox
            self.update()
            return

        if self._dragging_handle is not None:
            # --- Line: drag start (0) or end (1) endpoint directly ---
            if self.preview_shape == "line":
                if self.snap_to_grid:
                    pt = self._snap_to_grid(pt)
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    anchor = self.preview_end if self._dragging_handle == 0 else self.preview_start
                    pt = self._snap_line_angle(anchor, pt)
                if self._dragging_handle == 0:
                    self.preview_start = pt
                else:
                    self.preview_end = pt
                self.setCursor(Qt.CursorShape.CrossCursor)
                self.update()
                return
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
                # Non-rotated: snap point then compute new start/end
                self.set_resize_cursor(handle)
                if self.snap_to_grid:
                    pt = self._snap_to_grid(pt)
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
                # Alignment guides for non-rotated resize
                if not self.snap_to_grid:
                    new_rect = QRect(self.preview_start, self.preview_end).normalized()
                    snapped, self._active_guides = self._find_resize_snap_guides(new_rect, handle)
                    self.preview_start = snapped.topLeft()
                    self.preview_end = snapped.bottomRight()
                else:
                    self._active_guides = []
                # Aspect ratio constraint: hold Shift on a corner handle to scale proportionally
                if (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) and handle in (0, 2, 4, 6) and hasattr(self, '_resize_orig_rect'):
                    constrained = self._apply_aspect_ratio_constraint(
                        QRect(self.preview_start, self.preview_end).normalized(),
                        self._resize_orig_rect, handle
                    )
                    self.preview_start = constrained.topLeft()
                    self.preview_end = constrained.bottomRight()
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
            # --- Line: translate both endpoints preserving direction ---
            if self.preview_shape == "line" and self.preview_start is not None and self.preview_end is not None:
                new_start = pt - self._drag_offset
                if self.snap_to_grid:
                    new_start = self._snap_to_grid(new_start)
                delta = new_start - self.preview_start
                self.preview_start = new_start
                self.preview_end = self.preview_end + delta
                self.update()
                return
            # Only do this for non-draw shapes
            if self.preview_shape != "draw" and self.preview_start is not None and self.preview_end is not None:
                rect = QRect(self.preview_start, self.preview_end).normalized()
                box_rect = rect.adjusted(-margin, -margin, margin, margin)
                offset = pt - self._drag_offset
                size = box_rect.size()
                # Move the box, but update preview_start/end to match the new box_rect minus margin
                new_box_rect = QRect(offset, size)
                new_shape_rect = new_box_rect.adjusted(margin, margin, -margin, -margin)
                # Apply snap-to-grid
                if self.snap_to_grid:
                    snapped_tl = self._snap_to_grid(new_shape_rect.topLeft())
                    snap_delta = snapped_tl - new_shape_rect.topLeft()
                    new_shape_rect.translate(snap_delta)
                # Apply alignment guides (when grid is off)
                if not self.snap_to_grid:
                    new_shape_rect, self._active_guides = self._find_snap_guides(new_shape_rect)
                else:
                    self._active_guides = []
                self.preview_start = new_shape_rect.topLeft()
                self.preview_end = new_shape_rect.bottomRight()
                self.update()
                return

        else:
            # Only run this if not drawing or editing a "draw" shape
            if self.current_tool != "draw" and self.preview_shape != "draw":
                if self.preview_start is not None and self.preview_end is not None:
                    if self.preview_shape == "line":
                        # Show endpoint cross or body hand cursor for line
                        _hs2 = max(20, self.HANDLE_SIZE * 3)
                        _near_ep = any(
                            QRect(h.x() - _hs2 // 2, h.y() - _hs2 // 2, _hs2, _hs2).contains(pt)
                            for h in [self.preview_start, self.preview_end]
                        )
                        if _near_ep:
                            self.setCursor(Qt.CursorShape.CrossCursor)
                        else:
                            _ax, _ay = self.preview_start.x(), self.preview_start.y()
                            _bx, _by = self.preview_end.x(), self.preview_end.y()
                            _dx2, _dy2 = _bx - _ax, _by - _ay
                            _lsq = _dx2 * _dx2 + _dy2 * _dy2
                            if _lsq > 0:
                                _t2 = max(0.0, min(1.0, ((pt.x() - _ax) * _dx2 + (pt.y() - _ay) * _dy2) / _lsq))
                                _dsq = (_ax + _t2 * _dx2 - pt.x()) ** 2 + (_ay + _t2 * _dy2 - pt.y()) ** 2
                            else:
                                _dsq = (pt.x() - _ax) ** 2 + (pt.y() - _ay) ** 2
                            if _dsq <= 100 and self.selected_shape_index is not None:
                                self.setCursor(Qt.CursorShape.OpenHandCursor)
                            elif self.current_tool:
                                self.setCursor(Qt.CursorShape.CrossCursor)
                            else:
                                self.setCursor(Qt.CursorShape.ArrowCursor)
                    else:
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
            shift_held = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            if shift_held:
                if self._draw_shift_anchor is None:
                    # Shift just pressed — lock anchor at the last drawn point
                    self._draw_shift_anchor = self.freehand_points[-1] if self.freehand_points else pt
                    self._draw_freehand_base = self.freehand_points[:]
                snapped = self._snap_line_angle(self._draw_shift_anchor, pt)
                self.freehand_points = self._draw_freehand_base + [snapped]
            else:
                if self._draw_shift_anchor is not None:
                    self._draw_shift_anchor = None
                    self._draw_freehand_base = None
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

        if self.current_tool == "label" and self._labeling:
            self._label_end = pt
            self.preview_end = pt
            self.update()
            return

        # Only update placement preview for active tool drawing (not selected-shape editing)
        if self.preview_shape and self.current_tool is not None and self.selected_shape_index is None:
            pt = self.widget_to_canvas(event.position().toPoint())
            if self.snap_to_grid:
                pt = self._snap_to_grid(pt)
            if self.current_tool == "line" and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier) and self.preview_start is not None:
                pt = self._snap_line_angle(self.preview_start, pt)
            self.preview_end = pt
            self.update()

    def mouseReleaseEvent(self, event):

        if self.current_tool == "label" and self._labeling and event.button() == Qt.MouseButton.LeftButton:
            self._labeling = False
            if self.preview_start is not None and self.preview_end is not None:
                canvas_rect = QRect(self.preview_start, self.preview_end).normalized()
                if canvas_rect.width() > 5 and canvas_rect.height() > 5:
                    self.preview_shape = None  # hide the preview placeholder
                    self._show_text_overlay(canvas_rect)
                else:
                    self.preview_shape = None
                    self.preview_start = None
                    self.preview_end = None
            self.update()
            return

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
                    label_text = None
                    lock_flag = None
                    for item in shape[4:]:
                        if isinstance(item, QColor):
                            fill_color = item
                        elif isinstance(item, bool):
                            lock_flag = item
                        elif isinstance(item, str):
                            label_text = item
                        elif isinstance(item, dict):
                            extra_dicts.append(item)
                    rotation = getattr(self, 'preview_rotation', 0)
                    new_shape = [tool, start, end, border_color]
                    if fill_color is not None:
                        new_shape.append(fill_color)
                    new_shape.append(rotation)
                    if label_text is not None:
                        new_shape.append(label_text)
                    for d in extra_dicts:
                        new_shape.append(d)
                    if lock_flag is not None:
                        new_shape.append(lock_flag)
                    self.shapes[idx] = tuple(new_shape)

            self.update()
            return

        # Commit overset move/resize for non-draw shape edits so label stays in view after drag
        if (self._dragging_box or self._dragging_handle) and self.selected_shape_index is not None:
            idx = self.selected_shape_index
            if 0 <= idx < len(self.shapes) and self.preview_shape is not None and self.preview_start is not None and self.preview_end is not None:
                old_shape = self.shapes[idx]
                if old_shape[0] != "draw":
                    base = [old_shape[0], self.preview_start, self.preview_end]
                    if len(old_shape) > 3:
                        base.append(old_shape[3])
                    base.extend(old_shape[4:])
                    self.shapes[idx] = tuple(base)

        self._dragging_handle = None
        self._active_guides = []

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
            pixmap = QPixmap(os.path.join(_ASSETS_DIR, "tool-colors-eraser.png"))
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
            self._draw_shift_anchor = None  
            self._draw_freehand_base = None 
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

        # Draw snap grid overlay
        if self.snap_to_grid:
            grid_pen = QPen(QColor(180, 180, 180, 60), 1, Qt.PenStyle.SolidLine)
            painter.setPen(grid_pen)
            g = self.grid_size
            w, h = self.a4_size.width(), self.a4_size.height()
            x = g
            while x < w:
                painter.drawLine(x, 0, x, h)
                x += g
            y = g
            while y < h:
                painter.drawLine(0, y, w, y)
                y += g

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
            # Skip label shapes that are currently open for text editing
            if tool == "label" and idx == getattr(self, "_label_edit_index", None) and self._text_edit_overlay is not None:
                continue
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
                    if tool == "line":
                        # Draw line directly with original endpoints to preserve direction
                        if color.alpha() > 0 and border_weight and border_weight > 0:
                            painter.setBrush(Qt.BrushStyle.NoBrush)
                            painter.setPen(QPen(color, border_weight if border_weight is not None else 3))
                            painter.drawLine(start, end)
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
                        # Draw border (skip if transparent or weight is 0)
                        if color.alpha() > 0 and border_weight and border_weight > 0:
                            painter.setBrush(Qt.BrushStyle.NoBrush)
                            painter.setPen(QPen(color, border_weight if border_weight is not None else 3))
                            self.draw_shape(painter, tool, rect.topLeft(), rect.bottomRight(), line_width=border_weight, border_radius=border_radius)
                    # Draw text content for label shapes
                    if tool == "label":
                        lbl_text = ""
                        lbl_font_size = 14
                        lbl_bold = False
                        lbl_italic = False
                        lbl_underline = False
                        lbl_font_family = getattr(self, "_label_font_family", "Arial")
                        lbl_align = "left"
                        for _item in shape[4:]:
                            if isinstance(_item, str):
                                lbl_text = _item
                            elif isinstance(_item, dict) and "font_size" in _item:
                                lbl_font_size = _item.get("font_size", lbl_font_size)
                                lbl_bold = _item.get("font_bold", False)
                                lbl_italic = _item.get("font_italic", False)
                                lbl_underline = _item.get("font_underline", False)
                                lbl_font_family = _item.get("font_family", lbl_font_family)
                                lbl_align = _item.get("text_align", lbl_align)
                        if lbl_text:
                            # Prefer rendering rich text (HTML) so per-character styles like
                            # background highlight are preserved. Fall back to plain drawText
                            # if the rich-text render path fails.
                            try:
                                from PyQt6.QtGui import QTextDocument
                                text_draw_rect = rect.adjusted(4, 4, -4, -4)
                                lbl_font = QFont(lbl_font_family, lbl_font_size)
                                lbl_font.setBold(lbl_bold)
                                lbl_font.setItalic(lbl_italic)
                                lbl_font.setUnderline(lbl_underline)

                                doc = QTextDocument()
                                doc.setDefaultFont(lbl_font)

                                # Heuristic: treat the stored text as HTML if it contains tags
                                is_html = isinstance(lbl_text, str) and ("<" in lbl_text and ">" in lbl_text and any(k in lbl_text.lower() for k in ("<span", "<p", "<div", "<br", "<b", "<i", "<u", "style=", "<!doctype", "<html")))
                                if is_html:
                                    doc.setHtml(lbl_text)
                                else:
                                    # Escape plain text and wrap with styling for color/alignment
                                    safe_text = (lbl_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"))
                                    doc.setHtml(f'<div style="color:{color.name()}; font-family:{lbl_font_family}; font-size:{lbl_font_size}pt; text-align:{lbl_align};">{safe_text}</div>')

                                doc.setTextWidth(float(text_draw_rect.width()))
                                painter.save()
                                painter.translate(text_draw_rect.left(), text_draw_rect.top())
                                doc.drawContents(painter, QRectF(0, 0, text_draw_rect.width(), text_draw_rect.height()))
                                painter.restore()
                            except Exception:
                                painter.setPen(QPen(color))
                                lbl_font = QFont(lbl_font_family, lbl_font_size)
                                lbl_font.setBold(lbl_bold)
                                lbl_font.setItalic(lbl_italic)
                                lbl_font.setUnderline(lbl_underline)
                                painter.setFont(lbl_font)
                                text_draw_rect = rect.adjusted(4, 4, -4, -4)
                                # map stored alignment to a Qt flag
                                align_map = {
                                    "left": Qt.AlignmentFlag.AlignLeft,
                                    "center": Qt.AlignmentFlag.AlignHCenter,
                                    "right": Qt.AlignmentFlag.AlignRight,
                                }
                                a_flag = align_map.get(lbl_align, Qt.AlignmentFlag.AlignLeft)
                                painter.drawText(
                                    text_draw_rect,
                                    a_flag | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                                    lbl_text,
                                )
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
                if self.preview_shape != "line":
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
            elif self.preview_shape == "label" and self.selected_shape_index is not None:
                # Draw selected label's text + border (using live preview rect while moving)
                if 0 <= self.selected_shape_index < len(self.shapes):
                    lbl_shape = self.shapes[self.selected_shape_index]
                    if len(lbl_shape) >= 4 and lbl_shape[0] == "label":
                        _, s_start, s_end, s_data, *rest = lbl_shape
                        if self.preview_start is not None and self.preview_end is not None:
                            rect_show = QRect(self.preview_start, self.preview_end).normalized()
                        else:
                            rect_show = QRect(s_start, s_end).normalized()
                        # Fill / border for label shape if needed
                        color = s_data if isinstance(s_data, QColor) else QColor("#000000")
                        fill_color = None
                        lbl_text = ""
                        lbl_font_size = self._label_font_size
                        lbl_bold = False
                        lbl_italic = False
                        lbl_underline = False
                        lbl_font_family = getattr(self, "_label_font_family", "Arial")
                        lbl_align = getattr(self, "_label_text_align", "left")
                        for item in rest:
                            if isinstance(item, QColor):
                                fill_color = item
                            elif isinstance(item, str):
                                lbl_text = item
                            elif isinstance(item, dict):
                                lbl_font_size = item.get("font_size", lbl_font_size)
                                lbl_bold = item.get("font_bold", False)
                                lbl_italic = item.get("font_italic", False)
                                lbl_underline = item.get("font_underline", False)
                                lbl_font_family = item.get("font_family", lbl_font_family)
                                lbl_align = item.get("text_align", lbl_align)
                        if fill_color is not None:
                            painter.setBrush(QBrush(fill_color))
                            painter.setPen(Qt.PenStyle.NoPen)
                            self.draw_shape(painter, "label", rect_show.topLeft(), rect_show.bottomRight())
                        painter.setBrush(Qt.BrushStyle.NoBrush)
                        painter.setPen(QPen(color, 2))
                        self.draw_shape(painter, "label", rect_show.topLeft(), rect_show.bottomRight())
                        if lbl_text:
                            text_draw_rect = rect_show.adjusted(4, 4, -4, -4)
                            lbl_font = QFont(lbl_font_family, lbl_font_size)
                            lbl_font.setBold(lbl_bold)
                            lbl_font.setItalic(lbl_italic)
                            lbl_font.setUnderline(lbl_underline)
                            try:
                                from PyQt6.QtGui import QTextDocument
                                doc = QTextDocument()
                                doc.setDefaultFont(lbl_font)
                                is_html = isinstance(lbl_text, str) and ("<" in lbl_text and ">" in lbl_text and any(k in lbl_text.lower() for k in ("<span", "<p", "<div", "<br", "<b", "<i", "<u", "style=", "<!doctype", "<html")))
                                if is_html:
                                    doc.setHtml(lbl_text)
                                else:
                                    safe_text = (lbl_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"))
                                    doc.setHtml(f'<div style="color:{color.name()}; font-family:{lbl_font_family}; font-size:{lbl_font_size}pt; text-align:{lbl_align};">{safe_text}</div>')
                                doc.setTextWidth(float(text_draw_rect.width()))
                                painter.save()
                                painter.translate(text_draw_rect.left(), text_draw_rect.top())
                                doc.drawContents(painter, QRectF(0, 0, text_draw_rect.width(), text_draw_rect.height()))
                                painter.restore()
                            except Exception:
                                painter.setPen(QPen(color))
                                painter.setFont(lbl_font)
                                painter.drawText(
                                    text_draw_rect,
                                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                                    lbl_text,
                                )
            elif self.preview_shape == "line" and self.preview_start is not None and self.preview_end is not None:
                # Draw line using actual endpoints (not normalized rect corners)
                preview_pen = QPen(QColor("#ff6600"), 3, Qt.PenStyle.DashLine)
                painter.setPen(preview_pen)
                painter.drawLine(self.preview_start, self.preview_end)
                # Orange endpoint handles
                for endpt in [self.preview_start, self.preview_end]:
                    painter.setBrush(QBrush(QColor("#ff6600")))
                    painter.setPen(QPen(QColor("#ffffff"), 2))
                    painter.drawEllipse(QPointF(endpt), 6, 6)
            elif self.preview_shape is not None and self.preview_shape != "label" and rect is not None:
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

            # Do not draw the orange selection highlight while the inline
            # label editor overlay is active for this shape — the overlay
            # provides its own visual chrome.
            if getattr(self, '_text_edit_overlay', None) is not None and getattr(self, '_label_edit_index', None) == self.selected_shape_index:
                pass
            else:
                painter.save()
                highlight_pen = QPen(QColor("#ff6600"), 4, Qt.PenStyle.DashLine)
                painter.setPen(highlight_pen)
                if tool == "draw" and isinstance(start, list) and len(start) > 1:
                    # Draw the polyline directly
                    painter.drawPolyline(*start)
                else:
                    if tool == "line":
                        painter.drawLine(start, end)
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

        # Draw alignment guide lines
        if self._active_guides:
            guide_pen = QPen(QColor("#0078d7"), 1, Qt.PenStyle.DashLine)
            painter.setPen(guide_pen)
            w, h = self.a4_size.width(), self.a4_size.height()
            for direction, coord in self._active_guides:
                if direction == "v":
                    painter.drawLine(coord, 0, coord, h)
                else:
                    painter.drawLine(0, coord, w, coord)

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
            if painter.pen().style() == Qt.PenStyle.NoPen:
                pass  # Preserve NoPen for fill-only drawing
            else:
                line_width = self.tool_sizes.get('shapes' if tool not in ['line'] else 'line', 2)
                painter.setPen(QPen(painter.pen().color(), line_width))
        else:
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
        elif tool == "label":
            painter.drawRect(rect)

    def widget_to_canvas(self, pos):
        # Convert widget coordinates to canvas coordinates, considering zoom and centering
        center = self.get_canvas_center()
        # Subtract pan_offset here!
        x = (pos.x() - center.x() - self.pan_offset.x()) / self.scale_factor + self.a4_size.width() / 2
        y = (pos.y() - center.y() - self.pan_offset.y()) / self.scale_factor + self.a4_size.height() / 2
        return QPoint(int(round(x)), int(round(y)))

    def canvas_to_widget(self, pt):
        # Convert canvas coordinates to widget coordinates (inverse of widget_to_canvas)
        center = self.get_canvas_center()
        x = center.x() + self.pan_offset.x() + (pt.x() - self.a4_size.width() / 2) * self.scale_factor
        y = center.y() + self.pan_offset.y() + (pt.y() - self.a4_size.height() / 2) * self.scale_factor
        return QPoint(int(round(x)), int(round(y)))

    def _show_text_overlay(self, canvas_rect, existing_text=""):
        # Show an editable, movable/resizable text box overlaid on the canvas rectangle
        self._cancel_text_overlay()

        tl = self.canvas_to_widget(canvas_rect.topLeft())
        br = self.canvas_to_widget(canvas_rect.bottomRight())
        widget_rect = QRect(tl, br).normalized()
        widget_rect = widget_rect.intersected(self.rect())
        if widget_rect.width() < 10 or widget_rect.height() < 10:
            return

        # toolbar (font size + bold + italic) shown above the text box ──
        toolbar_h = 28
        toolbar_y = max(0, widget_rect.top() - toolbar_h - 2)
        toolbar = QWidget(self)
        toolbar.setFixedHeight(toolbar_h)
        toolbar.setGeometry(widget_rect.left(), toolbar_y, max(widget_rect.width(), 310), toolbar_h)
        # Derive colors from the current shape/app accent so the toolbar matches
        acc_qcolor = getattr(self, 'shape_color', None)
        if acc_qcolor is None:
            # fallback to a sensible accent used elsewhere
            acc_qcolor = getattr(self, 'current_shape_color', QColor("#ff6600"))
        accent = acc_qcolor if isinstance(acc_qcolor, QColor) else QColor(str(acc_qcolor))
        accent_hex = accent.name()

        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(4, 2, 4, 2)
        tb_layout.setSpacing(4)

        # Force toolbar to use the exact accent color
        toolbar.setStyleSheet(f"background: {accent_hex}; border-radius:4px;")

        size_lbl = QLabel("A", toolbar)
        size_lbl.setStyleSheet(f"color:white; font-size:11pt; border:none; background:transparent;")
        tb_layout.addWidget(size_lbl)

        font_size_input = QLineEdit(str(self._label_font_size), toolbar)
        font_size_input.setFixedWidth(38)
        font_size_input.setFixedHeight(23)
        font_size_input.setMaxLength(3)
        #font_size_input.setInputMask("000")  # Only allow 3 digits for font size
        regex = QRegularExpression(r'[1-9][0-9]{0,2}')  # 1-999
        validator = QRegularExpressionValidator(regex, font_size_input)
        font_size_input.setValidator(validator)
        # - background: white by default; becomes black if accent is white
        # - foreground: black by default; becomes white if accent is black
        accent_hex_lower = accent_hex.lower()
        control_bg = "#000000" if accent_hex_lower in ("#ffffff", "white") else "#ffffff"
        control_fg = "#ffffff" if accent_hex_lower in ("#000000", "black") else "#000000"
        # Safety: ensure contrast — if they accidentally match, invert the foreground
        if control_bg == control_fg:
            control_fg = "#ffffff" if control_bg == "#000000" else "#000000"

        border_col = accent.darker(120).name()
        font_size_input.setStyleSheet(
            f"background:{control_bg}; color:{control_fg}; border:1px solid {border_col}; border-radius:3px; font-size:10pt; margin-top:1px;"
        )
        tb_layout.addWidget(font_size_input)

        # Font family selector
        font_combo = QFontComboBox(toolbar)
        font_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        font_combo.setFixedHeight(23)
        font_combo.setFixedWidth(100)
        font_combo.setStyleSheet(
            f"background:{control_bg}; color:{control_fg}; border:1px solid {border_col}; border-radius:3px; font-size:10pt; margin-top:1px;"
        )
        # initialize to current selection if set
        current_family = getattr(self, "_label_font_family", "Arial")
        try:
            font_combo.setCurrentFont(QFont(current_family))
        except Exception:
            pass
        tb_layout.addWidget(font_combo)

        # Text color to use when a button is shown with the accent background
        checked_text_color = "#ffffff" if accent_hex_lower in ("#000000", "black") else "#000000"

        bold_btn = QPushButton("B", toolbar)
        bold_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bold_btn.setCheckable(True)
        bold_btn.setChecked(getattr(self, "_label_font_bold", False))
        bold_btn.setFixedSize(24, 22)
        bold_style = (
            f"QPushButton{{background:{control_bg};color:{control_fg};border:1px solid {border_col};border-radius:3px;font-weight:bold;font-size:10pt;}}"
            f"QPushButton:checked{{background:{accent_hex};border-color:{accent_hex};color:{checked_text_color};}}"
        )
        bold_btn.setStyleSheet(bold_style)
        tb_layout.addWidget(bold_btn)

        italic_btn = QPushButton("I", toolbar)
        italic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        italic_btn.setCheckable(True)
        italic_btn.setChecked(getattr(self, "_label_font_italic", False))
        italic_btn.setFixedSize(24, 22)
        italic_style = (
            f"QPushButton{{background:{control_bg};color:{control_fg};border:1px solid {border_col};border-radius:3px;font-style:italic;font-size:10pt;}}"
            f"QPushButton:checked{{background:{accent_hex};border-color:{accent_hex};color:{checked_text_color};}}"
        )
        italic_btn.setStyleSheet(italic_style)
        tb_layout.addWidget(italic_btn)
        
        # Underline button
        underline_btn = QPushButton("U", toolbar)
        underline_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        underline_btn.setCheckable(True)
        underline_btn.setChecked(getattr(self, "_label_font_underline", False))
        underline_btn.setFixedSize(24, 22)
        # give the button an underlined appearance
        ufont = QFont()
        ufont.setUnderline(True)
        ufont.setBold(True)
        underline_btn.setFont(ufont)
        underline_style = (
            f"QPushButton{{background:{control_bg};color:{control_fg};border:1px solid {border_col};border-radius:3px;font-size:10pt;}}"
            f"QPushButton:checked{{background:{accent_hex};border-color:{accent_hex};color:{checked_text_color};}}"
        )
        underline_btn.setStyleSheet(underline_style)
        tb_layout.addWidget(underline_btn)

        # Alignment toggle button (cycles: Left -> Center -> Right)
        align_btn = QPushButton("L", toolbar)
        align_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        align_btn.setFixedSize(24, 22)
        align_style = (
            f"QPushButton{{background:{control_bg};color:{control_fg};border:1px solid {border_col};border-radius:3px;font-size:10pt;}}"
            f"QPushButton:pressed{{background:{accent_hex};border-color:{accent_hex};color:{checked_text_color};}}"
        )
        align_btn.setStyleSheet(align_style)
        tb_layout.addWidget(align_btn)

        # helper to update the visible label on the align button
        def _update_align_btn_text():
            val = getattr(self, "_label_text_align", "left")
            if val == "left":
                align_btn.setText("L")
            elif val == "center":
                align_btn.setText("C")
            else:
                align_btn.setText("R")

        _update_align_btn_text()

        def _cycle_align():
            order = ["left", "center", "right"]
            cur = getattr(self, "_label_text_align", "left")
            nxt = order[(order.index(cur) + 1) % len(order)]
            setattr(self, "_label_text_align", nxt)
            _update_align_btn_text()
            # apply alignment: to selection if present, otherwise to whole document
            try:
                align_map = {
                    "left": Qt.AlignmentFlag.AlignLeft,
                    "center": Qt.AlignmentFlag.AlignHCenter,
                    "right": Qt.AlignmentFlag.AlignRight,
                }
                a = align_map.get(nxt, Qt.AlignmentFlag.AlignLeft)
                cursor = te.textCursor()
                from PyQt6.QtGui import QTextBlockFormat
                block_fmt = QTextBlockFormat()
                block_fmt.setAlignment(a)
                if cursor.hasSelection():
                    cursor.beginEditBlock()
                    cursor.mergeBlockFormat(block_fmt)
                    cursor.endEditBlock()
                else:
                    # apply to entire document
                    cursor.select(cursor.SelectionType.Document)
                    cursor.mergeBlockFormat(block_fmt)
                    try:
                        te.setAlignment(a)
                    except Exception:
                        pass
            except Exception:
                pass

        align_btn.clicked.connect(_cycle_align)
        
        
        # Text color button — shows a colored square, opens color picker on click
        color_btn = QPushButton(toolbar)
        color_btn.setFixedSize(24, 22)
        color_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        def _update_color_btn_appearance():
            c = getattr(self, "_label_font_color", QColor("#000000"))
            color_btn.setStyleSheet(
                f"QPushButton{{background:{c.name()};border:1px solid white;border-radius:3px;}}"
                f"QPushButton:hover{{border:2px solid {accent_hex};}}"
            )

        _update_color_btn_appearance()

        def _on_color_btn_clicked():
            current = getattr(self, "_label_font_color", QColor("#000000"))
            chosen = QColorDialog.getColor(current, self, "Text Color")
            if not chosen.isValid():
                return
            self._label_font_color = chosen
            _update_color_btn_appearance()
            # Apply only to selection; if no selection, set insertion-point format
            try:
                from PyQt6.QtGui import QTextCharFormat
                cursor = te.textCursor()
                fmt = QTextCharFormat()
                fmt.setForeground(QBrush(chosen))
                if cursor.hasSelection():
                    cursor.beginEditBlock()
                    cursor.mergeCharFormat(fmt)
                    cursor.endEditBlock()
                te.mergeCurrentCharFormat(fmt)
                te.update()
            except Exception:
                pass
            
        color_btn.clicked.connect(_on_color_btn_clicked)
        tb_layout.addWidget(color_btn)
        tb_layout.addStretch()
        
        toolbar.show()

        # Keep references to toolbar controls so eventFilter hotkeys
        # can update the UI (checked state / displayed values).
        self._label_bold_btn = bold_btn
        self._label_italic_btn = italic_btn
        self._label_underline_btn = underline_btn
        self._label_align_btn = align_btn
        self._label_font_size_input = font_size_input
        self._label_font_combo = font_combo
        self._label_color_btn = color_btn
        self._label_color_btn_update_fn = _update_color_btn_appearance

        # text edit
        te = QTextEdit()
        te.setFrameShape(QFrame.Shape.NoFrame)
        te.setStyleSheet("QTextEdit { border: none; background: transparent; }")
        # hide scrollbars for inline editor
        te.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        te.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        te.setWordWrapMode(te.wordWrapMode().WordWrap)
        # If existing_text contains HTML (from a previous rich-text edit), preserve it.
        try:
            if isinstance(existing_text, str) and ("<" in existing_text and ">" in existing_text and any(k in existing_text.lower() for k in ("<span", "<p", "<div", "<br", "<b", "<i", "<u", "style=", "<!doctype", "<html"))):
                # Preserve inline per-character styling (underline / font-size)
                # when present. Only strip absolute font-size declarations
                # when no inline sizes exist to avoid losing selection-specific
                # formatting. This prevents accidental application of underline
                # or size to the entire label when only part was edited.
                try:
                    import re
                    s = existing_text
                    has_inline_size = bool(re.search(r"font-size\s*:\s*[^;\"']+", s, flags=re.I) or re.search(r"<font[^>]*\s+size\s*=\s*[\"']", s, flags=re.I))
                    # If no inline sizes are present, it's safe to normalize
                    # by removing any stray absolute declarations. Otherwise,
                    # keep inline sizes intact so per-character sizes survive.
                    if not has_inline_size:
                        s = re.sub(r"font-size\s*:\s*[^;\"']+;?", "", s, flags=re.I)
                        s = re.sub(r'(<font[^>]*?)\s+size\s*=\s*"[^\"]*"([^>]*>)', r'\1\2', s, flags=re.I)
                        s = re.sub(r"(<font[^>]*?)\s+size\s*=\s*'[^']*'([^>]*>)", r'\1\2', s, flags=re.I)
                        s = re.sub(r'style\s*=\s*"\s*"', '', s, flags=re.I)
                    else:
                        # Stored HTML has unscaled (canvas-space) font sizes.
                        # Scale them up by scale_factor for WYSIWYG display in
                        # the editor widget.
                        sf = self.scale_factor or 1.0
                        if sf != 1.0:
                            def _scale_fs(m):
                                val = float(m.group(1))
                                unit = m.group(2) if m.group(2) else 'pt'
                                scaled = val * sf
                                if abs(scaled - round(scaled)) < 0.05:
                                    return f"font-size:{int(round(scaled))}{unit}"
                                return f"font-size:{scaled:.1f}{unit}"
                            s = re.sub(r'font-size\s*:\s*([0-9.]+)\s*(pt|px)?', _scale_fs, s, flags=re.I)
                except Exception:
                    s = existing_text
                te.setHtml(s)
            else:
                te.setPlainText(existing_text)
        except Exception:
            te.setPlainText(existing_text)

        # movable/resizable overlay 
        overlay = _LabelTextOverlay(self, canvas_rect, te, toolbar)
        overlay._reposition()  # ensure margin plus handles is applied immediately
        overlay.show()
        overlay.raise_()

        # Always scale the editor font by the current canvas zoom so the
        # text in the overlay matches the committed label visually (WYSIWYG).
        self._apply_label_font_to_editor(te, apply_style_flags=False, scale_font=True)

        # Set an explicit insertion char format so the very first typed text
        # has a well-defined fontPointSize.  Without this, text on the first
        # line uses the implicit document-default and charFormat().fontPointSize()
        # can return 0, causing mismatches with lines created after Enter
        # (which receive an explicit format via _reapply_format_after_enter).
        if not existing_text:
            try:
                from PyQt6.QtGui import QTextCharFormat
                _pt = max(1, int(self._label_font_size * (self.scale_factor or 1.0)))
                _init_fmt = QTextCharFormat()
                _init_fmt.setFontPointSize(float(_pt))
                _init_fmt.setFontFamily(getattr(self, "_label_font_family", "Arial"))
                _init_fmt.setFontWeight(QFont.Weight.Bold if getattr(self, "_label_font_bold", False) else QFont.Weight.Normal)
                _init_fmt.setFontItalic(getattr(self, "_label_font_italic", False))
                _init_fmt.setFontUnderline(getattr(self, "_label_font_underline", False))
                _init_fmt.setForeground(QBrush(getattr(self, "_label_font_color", QColor("#000000"))))
                te.mergeCurrentCharFormat(_init_fmt)
            except Exception:
                pass

        te.setFocus()
        if existing_text:
            cursor = te.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            te.setTextCursor(cursor)

        self._text_edit_overlay    = overlay
        self._text_edit_widget     = te
        self._label_toolbar_widget = toolbar
        self._label_canvas_rect    = canvas_rect

        # Wire toolbar controls (apply to selection if present, otherwise to whole document)
        def _on_font_size_changed(text):
            try:
                sz = int(text)
                if 1 <= sz <= 999: # limit font size to 999
                    self._label_font_size = sz
                    # If a selection exists, apply size only to selection
                    try:
                        cursor = te.textCursor()
                        from PyQt6.QtGui import QTextCharFormat
                        pt_size = max(1, int(sz * (self.scale_factor or 1.0)))
                        fmt = QTextCharFormat()
                        fmt.setFontPointSize(float(pt_size))
                        fmt.setFontFamily(getattr(self, "_label_font_family", "Arial"))
                        if cursor.hasSelection():
                            cursor.beginEditBlock()
                            cursor.mergeCharFormat(fmt)
                            cursor.endEditBlock()
                        te.mergeCurrentCharFormat(fmt)
                        # Update document default font so new paragraphs (Enter) use this size
                        try:
                            doc_font = te.document().defaultFont()
                            doc_font.setPointSize(pt_size)
                            doc_font.setFamily(getattr(self, "_label_font_family", "Arial"))
                            te.document().setDefaultFont(doc_font)
                        except Exception:
                            pass
                        te.update()
                    except Exception:
                        pass
            except ValueError:
                pass

        def _on_bold_toggled(checked: bool):
            self._label_font_bold = checked
            try:
                cursor = te.textCursor()
                from PyQt6.QtGui import QTextCharFormat
                fmt = QTextCharFormat()
                fmt.setFontWeight(QFont.Weight.Bold if checked else QFont.Weight.Normal)
                if cursor.hasSelection():
                    cursor.beginEditBlock()
                    cursor.mergeCharFormat(fmt)
                    cursor.endEditBlock()
                te.mergeCurrentCharFormat(fmt)
                te.update()
            except Exception:
                pass

        def _on_italic_toggled(checked: bool):
            self._label_font_italic = checked
            try:
                cursor = te.textCursor()
                from PyQt6.QtGui import QTextCharFormat
                fmt = QTextCharFormat()
                fmt.setFontItalic(bool(checked))
                if cursor.hasSelection():
                    cursor.beginEditBlock()
                    cursor.mergeCharFormat(fmt)
                    cursor.endEditBlock()
                te.mergeCurrentCharFormat(fmt)
                te.update()
            except Exception:
                pass

        def _on_underline_toggled(checked: bool):
            self._label_font_underline = checked
            try:
                cursor = te.textCursor()
                from PyQt6.QtGui import QTextCharFormat
                fmt = QTextCharFormat()
                fmt.setFontUnderline(bool(checked))
                if cursor.hasSelection():
                    cursor.beginEditBlock()
                    cursor.mergeCharFormat(fmt)
                    cursor.endEditBlock()
                te.mergeCurrentCharFormat(fmt)
                te.update()
            except Exception:
                pass

        def _on_font_changed(qf):
            try:
                family = qf.family()
            except Exception:
                # Some PyQt versions may emit no-arg signal; fall back
                self._apply_label_font_to_editor(te)
                return
            self._label_font_family = family
            try:
                cursor = te.textCursor()
                from PyQt6.QtGui import QTextCharFormat
                fmt = QTextCharFormat()
                fmt.setFontFamily(family)
                if cursor.hasSelection():
                    cursor.beginEditBlock()
                    cursor.mergeCharFormat(fmt)
                    cursor.endEditBlock()
                te.mergeCurrentCharFormat(fmt)
                te.update()
            except Exception:
                pass

        font_size_input.editingFinished.connect(lambda: _on_font_size_changed(font_size_input.text()))
        bold_btn.toggled.connect(_on_bold_toggled)
        italic_btn.toggled.connect(_on_italic_toggled)
        underline_btn.toggled.connect(_on_underline_toggled)
        try:
            font_combo.currentFontChanged.connect(_on_font_changed)
        except Exception:
            try:
                # Fallback: connect without args and re-apply whole document
                font_combo.currentFontChanged.connect(lambda: self._apply_label_font_to_editor(te))
            except Exception:
                pass

        # Sync toolbar with cursor format when cursor position changes (debounced)
        self._cursor_sync_timer = QTimer()
        self._cursor_sync_timer.setSingleShot(True)
        self._cursor_sync_timer.setInterval(250)

        def _do_sync_toolbar():
            try:
                _te = self._text_edit_widget
                if _te is None:
                    return
                cursor = _te.textCursor()
                fmt = cursor.charFormat()
                # Sync font size (lightweight — just setText on QLineEdit)
                pt_size = fmt.fontPointSize()
                if pt_size > 0:
                    sf = self.scale_factor or 1.0
                    logical_size = max(1, int(round(pt_size / sf))) if sf != 0 else int(pt_size)
                    if self._label_font_size != logical_size:
                        self._label_font_size = logical_size
                        _fi = getattr(self, '_label_font_size_input', None)
                        if _fi is not None:
                            _fi.blockSignals(True)
                            _fi.setText(str(logical_size))
                            _fi.blockSignals(False)
                # Sync bold
                try:
                    is_bold = fmt.fontWeight() == QFont.Weight.Bold
                except TypeError:
                    is_bold = False
                if self._label_font_bold != is_bold:
                    self._label_font_bold = is_bold
                    _bb = getattr(self, '_label_bold_btn', None)
                    if _bb is not None:
                        _bb.blockSignals(True)
                        _bb.setChecked(is_bold)
                        _bb.blockSignals(False)
                # Sync italic
                is_italic = fmt.fontItalic()
                if self._label_font_italic != is_italic:
                    self._label_font_italic = is_italic
                    _ib = getattr(self, '_label_italic_btn', None)
                    if _ib is not None:
                        _ib.blockSignals(True)
                        _ib.setChecked(is_italic)
                        _ib.blockSignals(False)
                # Sync underline
                is_underline = fmt.fontUnderline()
                if self._label_font_underline != is_underline:
                    self._label_font_underline = is_underline
                    _ub = getattr(self, '_label_underline_btn', None)
                    if _ub is not None:
                        _ub.blockSignals(True)
                        _ub.setChecked(is_underline)
                        _ub.blockSignals(False)
                # Sync font family — only update the internal var, skip
                # QFontComboBox.setCurrentFont which is very expensive
                family = fmt.fontFamily()
                if family and family != getattr(self, '_label_font_family', ''):
                    self._label_font_family = family
                    
                # Sync text color — update button appearance when cursor moves into colored text
                fg = fmt.foreground()
                if fg.style() != Qt.BrushStyle.NoBrush:
                    fg_color = fg.color()
                    current_color = getattr(self, '_label_font_color', QColor("#000000"))
                    if fg_color.isValid() and fg_color != current_color:
                        self._label_font_color = fg_color
                        _fn = getattr(self, '_label_color_btn_update_fn', None)
                        if _fn is not None:
                            _fn()
            except Exception:
                pass

        self._cursor_sync_timer.timeout.connect(_do_sync_toolbar)
        te.cursorPositionChanged.connect(lambda: self._cursor_sync_timer.start())
        
        def _on_text_changed():
            try:
                _te = self._text_edit_widget
                if _te is None:
                    return
                # characterCount() == 1 means only the trailing paragraph
                # separator remains — the document is effectively empty.
                if _te.document().characterCount() > 1:
                    return
                from PyQt6.QtGui import QTextCharFormat
                _pt = max(1, int(self._label_font_size * (self.scale_factor or 1.0)))
                _fmt = QTextCharFormat()
                _fmt.setFontPointSize(float(_pt))
                _fmt.setFontFamily(getattr(self, "_label_font_family", "Arial"))
                _fmt.setFontWeight(QFont.Weight.Bold if getattr(self, "_label_font_bold", False) else QFont.Weight.Normal)
                _fmt.setFontItalic(getattr(self, "_label_font_italic", False))
                _fmt.setFontUnderline(getattr(self, "_label_font_underline", False))
                _fmt.setForeground(QBrush(getattr(self, "_label_font_color", QColor("#000000"))))
                _te.mergeCurrentCharFormat(_fmt)
            except Exception:
                pass
            
        te.textChanged.connect(_on_text_changed)

        # Install event filter for Escape / Ctrl+Enter
        te.installEventFilter(self)

    def _apply_label_font_to_editor(self, te, apply_style_flags: bool = True, scale_font: bool = True):
        # Apply current label font settings to the QTextEdit overlay.

        # If apply_style_flags is False, only update font family and point-size
        # (used when scaling on zoom/pan) to avoid overwriting per-character
        # bold/italic/underline that may have been applied to a selection.
        
        if te is None:
            return
        # Compute point size. When `scale_font` is True, apply canvas zoom
        # so the widget matches the canvas rendering. When False, use the
        # logical label font size (useful for new labels where the user
        # expects the configured point-size regardless of current zoom).
        if scale_font:
            pt_size = max(1, int(self._label_font_size * (self.scale_factor or 1.0)))
        else:
            pt_size = max(1, int(self._label_font_size))

        family = getattr(self, "_label_font_family", "Arial")
        # Base font (do not force style flags here if only scaling)
        font = QFont(family, pt_size)
        if apply_style_flags:
            font.setBold(getattr(self, "_label_font_bold", False))
            font.setItalic(getattr(self, "_label_font_italic", False))
            font.setUnderline(getattr(self, "_label_font_underline", False))

        # Apply to the widget and update document default font
        te.setFont(font)
        try:
            te.document().setDefaultFont(font)

            # When apply_style_flags is False (used for zoom/pan rescaling)
            # avoid merging char/block formats across the whole document
            # because that would overwrite per-character selection styles.
            cursor = te.textCursor()
            if apply_style_flags:
                # Merge a char format across the document for family/size and
                # optionally style flags (bold/italic/underline).
                cursor.select(cursor.SelectionType.Document)
                from PyQt6.QtGui import QTextCharFormat
                fmt = QTextCharFormat()
                fmt.setFontPointSize(float(pt_size))
                fmt.setFontFamily(family)
                # Only set these if caller explicitly wants to apply style flags
                try:
                    fmt.setFontWeight(QFont.Weight.Bold if getattr(self, "_label_font_bold", False) else QFont.Weight.Normal)
                except Exception:
                    pass
                try:
                    fmt.setFontItalic(getattr(self, "_label_font_italic", False))
                except Exception:
                    pass
                try:
                    fmt.setFontUnderline(getattr(self, "_label_font_underline", False))
                except Exception:
                    pass
                cursor.mergeCharFormat(fmt)

                # Also merge block/paragraph alignment so existing paragraphs adopt
                # the chosen horizontal alignment (left/center/right).
                try:
                    from PyQt6.QtGui import QTextBlockFormat
                    align_map = {
                        "left": Qt.AlignmentFlag.AlignLeft,
                        "center": Qt.AlignmentFlag.AlignHCenter,
                        "right": Qt.AlignmentFlag.AlignRight,
                    }
                    a = align_map.get(getattr(self, "_label_text_align", "left"), Qt.AlignmentFlag.AlignLeft)
                    block_fmt = QTextBlockFormat()
                    block_fmt.setAlignment(a)
                    cursor.mergeBlockFormat(block_fmt)
                    te.setTextCursor(cursor)
                    try:
                        te.setAlignment(a)
                    except Exception:
                        pass
                except Exception:
                    te.setTextCursor(cursor)
            else:
                # Only update widget/document default fonts (no per-char merges)
                # so zoom/pan only affects on-screen sizing and does not change
                # stored character formatting.
                pass
        except Exception:
            pass
        te.update()
        te.repaint()

    def _commit_text_overlay(self):
        # Commit the text-box contents as a label shape on the canvas.
        if self._text_edit_widget is None:
            return
        # Preserve rich-text formatting (highlights, spans) by using HTML when available
        try:
            text = self._text_edit_widget.toHtml()
        except Exception:
            text = self._text_edit_widget.toPlainText()
        # Prefer to preserve per-character inline styles (underline / font-size)
        # when present. Only remove absolute font-size declarations when no
        # inline sizes exist to avoid losing selection-specific formatting.
        has_inline_size = False
        has_inline_underline = False
        try:
            import re
            if isinstance(text, str):
                has_inline_size = bool(re.search(r"font-size\s*:\s*[^;\"']+", text, flags=re.I) or re.search(r"<font[^>]*\s+size\s*=\s*[\"']", text, flags=re.I))
                has_inline_underline = bool(re.search(r'<u\b', text, flags=re.I) or re.search(r'text-decoration\s*:\s*underline', text, flags=re.I))
                # The editor uses scaled font sizes (logical_size × scale_factor)
                # for WYSIWYG display.  Convert inline font-sizes back to logical
                # (unscaled) canvas-space values before storing, so that
                # paintEvent's painter.scale() doesn't double-scale them.
                sf = self.scale_factor or 1.0
                if sf != 1.0 and has_inline_size:
                    def _unscale_fs(m):
                        val = float(m.group(1))
                        unit = m.group(2) if m.group(2) else 'pt'
                        unscaled = val / sf
                        if abs(unscaled - round(unscaled)) < 0.05:
                            return f"font-size:{int(round(unscaled))}{unit}"
                        return f"font-size:{unscaled:.1f}{unit}"
                    text = re.sub(r'font-size\s*:\s*([0-9.]+)\s*(pt|px)?', _unscale_fs, text, flags=re.I)
                    # Re-check after unscaling
                    has_inline_size = bool(re.search(r"font-size\s*:\s*[^;\"']+", text, flags=re.I) or re.search(r"<font[^>]*\s+size\s*=\s*[\"']", text, flags=re.I))
                if not has_inline_size:
                    text = re.sub(r"font-size\s*:\s*[^;\"']+;?", "", text, flags=re.I)
                    text = re.sub(r'(<font[^>]*?)\s+size\s*=\s*"[^\"]*"([^>]*>)', r'\1\2', text, flags=re.I)
                    text = re.sub(r"(<font[^>]*?)\s+size\s*=\s*'[^']*'([^>]*>)", r'\1\2', text, flags=re.I)
                    text = re.sub(r'style\s*=\s*"\s*"', '', text, flags=re.I)
                else:
                    # still remove empty style attributes
                    text = re.sub(r'style\s*=\s*"\s*"', '', text, flags=re.I)
        except Exception:
            pass
        canvas_rect = getattr(self, "_label_canvas_rect", None)
        color = self.shape_color
        font_size = self._label_font_size
        font_bold = getattr(self, "_label_font_bold", False)
        font_italic = getattr(self, "_label_font_italic", False)
        edit_idx = self._label_edit_index

        # When editing an existing label, preserve its stored border color
        # instead of overwriting it with the current tool color.
        if edit_idx is not None and 0 <= edit_idx < len(self.shapes):
            orig_border = self.shapes[edit_idx][3]
            if isinstance(orig_border, QColor):
                color = orig_border

        self._cancel_text_overlay()

        if canvas_rect is None:
            self.preview_shape = None
            self.preview_start = None
            self.preview_end = None
            self._label_edit_index = None
            self.update()
            return

        start = canvas_rect.topLeft()
        end = canvas_rect.bottomRight()

        if text.strip():
            self.push_undo()
            # If the saved HTML contains per-character font sizes or underlines,
            # prefer those inline styles and avoid forcing a global font_size or
            # font_underline flag that would apply to the whole label.
            font_dict = {
                "font_bold": font_bold,
                "font_italic": font_italic,
                "font_family": getattr(self, "_label_font_family", "Arial"),
                "text_align": getattr(self, "_label_text_align", "left"),
            }
            # Only include a global font_size when there are no inline sizes
            if not has_inline_size:
                font_dict["font_size"] = font_size
            # Only include a global underline flag when no inline underline
            # formatting is present; otherwise inline <u> spans will control
            # which characters are underlined.
            font_dict["font_underline"] = (getattr(self, "_label_font_underline", False) and not has_inline_underline)
            # Keep explicit bold/italic keys (already in dict)
            font_dict["font_bold"] = font_bold
            font_dict["font_italic"] = font_italic
            new_shape = ("label", start, end, color, text, font_dict)
            # Preserve rotation from the original shape being edited
            edit_rotation = getattr(self, '_label_edit_rotation', 0)
            if edit_rotation:
                new_shape = new_shape + (edit_rotation,)
            if edit_idx is not None and 0 <= edit_idx < len(self.shapes):
                # Re-attach fill_color (object color) and border property dicts
                # that were applied via Properties and must survive a re-edit.
                orig = self.shapes[edit_idx]
                orig_fill = None
                for item in orig[4:]:
                    if isinstance(item, QColor):
                        orig_fill = item
                        break
                if orig_fill is not None:
                    # Insert fill_color before text (at index 4, after border_color)
                    new_shape = new_shape[:4] + (orig_fill,) + new_shape[4:]
                for item in orig[4:]:
                    if isinstance(item, dict) and ("border_weight" in item or "border_radius" in item):
                        new_shape = new_shape + (item,)
                self.shapes[edit_idx] = new_shape
            else:
                self.shapes.append(new_shape)
                
        self.preview_shape = None
        self.preview_start = None
        self.preview_end = None
        self._label_edit_index = None
        self._label_edit_rotation = 0
        self.selected_shape_index = None
        self.shape_deselected.emit()
        self.update()

    def _cancel_text_overlay(self):
        # Dismiss the text-box overlay without committing
        if self._text_edit_overlay is not None:
            self._text_edit_overlay.hide()
            self._text_edit_overlay.setParent(None)
            self._text_edit_overlay.deleteLater()
            self._text_edit_overlay = None
        if self._text_edit_widget is not None:
            self._text_edit_widget = None
        if getattr(self, "_label_toolbar_widget", None) is not None:
            self._label_toolbar_widget.hide()
            self._label_toolbar_widget.setParent(None)
            self._label_toolbar_widget.deleteLater()
            self._label_toolbar_widget = None
        # Clear stored toolbar control references
        self._label_bold_btn = None
        self._label_italic_btn = None
        self._label_underline_btn = None
        self._label_align_btn = None
        self._label_font_size_input = None
        self._label_color_btn = None
        self._label_color_btn_update_fn = None
        # Stop cursor sync timer to avoid stale callbacks
        if hasattr(self, '_cursor_sync_timer') and self._cursor_sync_timer is not None:
            self._cursor_sync_timer.stop()
        self._label_font_combo = None

    def eventFilter(self, obj, event):
        """Intercept key events on the label text-edit overlay."""
        if self._text_edit_widget is not None and obj is self._text_edit_widget:
            if event.type() == QEvent.Type.KeyPress:
                key = event.key()
                mods = event.modifiers()

                # Cancel overlay
                if key == Qt.Key.Key_Escape:
                    self._cancel_text_overlay()
                    self.preview_shape = None
                    self.preview_start = None
                    self.preview_end = None
                    self._label_edit_index = None
                    self.update()
                    return True

                # Commit: Ctrl+Enter
                if (key in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                        and mods & Qt.KeyboardModifier.ControlModifier):
                    self._commit_text_overlay()
                    return True

                te = self._text_edit_widget

                # Plain Enter: let QTextEdit create the new paragraph, then
                # re-apply the current char format so the font size stays
                # consistent instead of reverting to the document default.
                if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (mods & Qt.KeyboardModifier.ControlModifier):
                    def _reapply_format_after_enter():
                        try:
                            from PyQt6.QtGui import QTextCharFormat
                            pt_size = max(1, int(self._label_font_size * (self.scale_factor or 1.0)))
                            fmt = QTextCharFormat()
                            fmt.setFontPointSize(float(pt_size))
                            fmt.setFontFamily(getattr(self, "_label_font_family", "Arial"))
                            fmt.setFontWeight(QFont.Weight.Bold if getattr(self, "_label_font_bold", False) else QFont.Weight.Normal)
                            fmt.setFontItalic(getattr(self, "_label_font_italic", False))
                            fmt.setFontUnderline(getattr(self, "_label_font_underline", False))
                            fmt.setForeground(QBrush(getattr(self, "_label_font_color", QColor("#000000"))))
                            te.mergeCurrentCharFormat(fmt)
                        except Exception:
                            pass
                    QTimer.singleShot(0, _reapply_format_after_enter)
                    # Don't return True — let Enter propagate to QTextEdit normally

                # Toggle Bold: Ctrl+B
                if key == Qt.Key.Key_B and mods & Qt.KeyboardModifier.ControlModifier:
                    btn = getattr(self, "_label_bold_btn", None)
                    if btn is not None:
                        try:
                            btn.setChecked(not btn.isChecked())
                        except Exception:
                            try:
                                new_bold = not getattr(self, "_label_font_bold", False)
                                self._label_font_bold = new_bold
                                cursor = te.textCursor()
                                from PyQt6.QtGui import QTextCharFormat
                                if cursor.hasSelection():
                                    fmt = QTextCharFormat()
                                    fmt.setFontWeight(QFont.Weight.Bold if new_bold else QFont.Weight.Normal)
                                    cursor.beginEditBlock()
                                    cursor.mergeCharFormat(fmt)
                                    cursor.endEditBlock()
                                    try:
                                        te.mergeCurrentCharFormat(fmt)
                                    except Exception:
                                        pass
                                    te.update()
                                else:
                                    self._apply_label_font_to_editor(te)
                            except Exception:
                                self._apply_label_font_to_editor(te)
                    else:
                        try:
                            new_bold = not getattr(self, "_label_font_bold", False)
                            self._label_font_bold = new_bold
                            cursor = te.textCursor()
                            from PyQt6.QtGui import QTextCharFormat
                            if cursor.hasSelection():
                                fmt = QTextCharFormat()
                                fmt.setFontWeight(QFont.Weight.Bold if new_bold else QFont.Weight.Normal)
                                cursor.beginEditBlock()
                                cursor.mergeCharFormat(fmt)
                                cursor.endEditBlock()
                                try:
                                    te.mergeCurrentCharFormat(fmt)
                                except Exception:
                                    pass
                                te.update()
                            else:
                                self._apply_label_font_to_editor(te)
                        except Exception:
                            self._apply_label_font_to_editor(te)
                    return True

                # Toggle Italic: Ctrl+I
                if key == Qt.Key.Key_I and mods & Qt.KeyboardModifier.ControlModifier:
                    btn = getattr(self, "_label_italic_btn", None)
                    if btn is not None:
                        try:
                            btn.setChecked(not btn.isChecked())
                        except Exception:
                            try:
                                new_italic = not getattr(self, "_label_font_italic", False)
                                self._label_font_italic = new_italic
                                cursor = te.textCursor()
                                from PyQt6.QtGui import QTextCharFormat
                                fmt = QTextCharFormat()
                                fmt.setFontItalic(bool(new_italic))
                                if cursor.hasSelection():
                                    cursor.beginEditBlock()
                                    cursor.mergeCharFormat(fmt)
                                    cursor.endEditBlock()
                                    try:
                                        te.mergeCurrentCharFormat(fmt)
                                    except Exception:
                                        pass
                                    te.update()
                                else:
                                    self._apply_label_font_to_editor(te)
                            except Exception:
                                self._apply_label_font_to_editor(te)
                    else:
                        try:
                            new_italic = not getattr(self, "_label_font_italic", False)
                            self._label_font_italic = new_italic
                            cursor = te.textCursor()
                            from PyQt6.QtGui import QTextCharFormat
                            fmt = QTextCharFormat()
                            fmt.setFontItalic(bool(new_italic))
                            if cursor.hasSelection():
                                cursor.beginEditBlock()
                                cursor.mergeCharFormat(fmt)
                                cursor.endEditBlock()
                                try:
                                    te.mergeCurrentCharFormat(fmt)
                                except Exception:
                                    pass
                                te.update()
                            else:
                                self._apply_label_font_to_editor(te)
                        except Exception:
                            self._apply_label_font_to_editor(te)
                    return True

                # Toggle Underline: Ctrl+U
                if key == Qt.Key.Key_U and mods & Qt.KeyboardModifier.ControlModifier:
                    btn = getattr(self, "_label_underline_btn", None)
                    if btn is not None:
                        try:
                            btn.setChecked(not btn.isChecked())
                        except Exception:
                            try:
                                new_underline = not getattr(self, "_label_font_underline", False)
                                self._label_font_underline = new_underline
                                cursor = te.textCursor()
                                from PyQt6.QtGui import QTextCharFormat
                                fmt = QTextCharFormat()
                                try:
                                    fmt.setFontUnderline(bool(new_underline))
                                except Exception:
                                    fmt.setFontUnderline(bool(new_underline))
                                if cursor.hasSelection():
                                    cursor.beginEditBlock()
                                    cursor.mergeCharFormat(fmt)
                                    cursor.endEditBlock()
                                    try:
                                        te.mergeCurrentCharFormat(fmt)
                                    except Exception:
                                        pass
                                    te.update()
                                else:
                                    self._apply_label_font_to_editor(te)
                            except Exception:
                                self._apply_label_font_to_editor(te)
                    else:
                        try:
                            new_underline = not getattr(self, "_label_font_underline", False)
                            self._label_font_underline = new_underline
                            cursor = te.textCursor()
                            from PyQt6.QtGui import QTextCharFormat
                            fmt = QTextCharFormat()
                            try:
                                fmt.setFontUnderline(bool(new_underline))
                            except Exception:
                                fmt.setFontUnderline(bool(new_underline))
                            if cursor.hasSelection():
                                cursor.beginEditBlock()
                                cursor.mergeCharFormat(fmt)
                                cursor.endEditBlock()
                                try:
                                    te.mergeCurrentCharFormat(fmt)
                                except Exception:
                                    pass
                                te.update()
                            else:
                                self._apply_label_font_to_editor(te)
                        except Exception:
                            self._apply_label_font_to_editor(te)
                    return True

                # Alignment: Ctrl+L (left), Ctrl+T (center), Ctrl+R (right)
                if key in (Qt.Key.Key_L, Qt.Key.Key_T, Qt.Key.Key_R) and mods & Qt.KeyboardModifier.ControlModifier:
                    try:
                        if key == Qt.Key.Key_L:
                            self._label_text_align = 'left'
                        elif key == Qt.Key.Key_T:
                            self._label_text_align = 'center'
                        else:
                            self._label_text_align = 'right'
                        cursor = te.textCursor()
                        from PyQt6.QtGui import QTextBlockFormat
                        align_map = {
                            'left': Qt.AlignmentFlag.AlignLeft,
                            'center': Qt.AlignmentFlag.AlignHCenter,
                            'right': Qt.AlignmentFlag.AlignRight,
                        }
                        a = align_map.get(self._label_text_align, Qt.AlignmentFlag.AlignLeft)
                        if cursor.hasSelection():
                            block_fmt = QTextBlockFormat()
                            block_fmt.setAlignment(a)
                            cursor.beginEditBlock()
                            cursor.mergeBlockFormat(block_fmt)
                            cursor.endEditBlock()
                        else:
                            # Apply to entire document
                            cursor.select(cursor.SelectionType.Document)
                            block_fmt = QTextBlockFormat()
                            block_fmt.setAlignment(a)
                            cursor.mergeBlockFormat(block_fmt)
                            try:
                                te.setAlignment(a)
                            except Exception:
                                pass
                        # Update align button text if toolbar present
                        ab = getattr(self, '_label_align_btn', None)
                        if ab is not None:
                            try:
                                ab.setText('L' if self._label_text_align == 'left' else ('C' if self._label_text_align == 'center' else 'R'))
                            except Exception:
                                pass
                    except Exception:
                        pass
                    return True

                # Font size increase/decrease: Ctrl + '+' / Ctrl + '-'
                if mods & Qt.KeyboardModifier.ControlModifier and (key == Qt.Key.Key_Plus or key == Qt.Key.Key_Equal):
                    try:
                        self._label_font_size = max(1, min(999, getattr(self, '_label_font_size', 14) + 1))
                        # Apply only to selection if present, otherwise update insertion-point format
                        try:
                            cursor = te.textCursor()
                            from PyQt6.QtGui import QTextCharFormat
                            pt_size = max(1, int(self._label_font_size * (self.scale_factor or 1.0)))
                            fmt = QTextCharFormat()
                            fmt.setFontPointSize(float(pt_size))
                            if cursor.hasSelection():
                                cursor.beginEditBlock()
                                cursor.mergeCharFormat(fmt)
                                cursor.endEditBlock()
                            te.mergeCurrentCharFormat(fmt)
                            # Update document default font so new paragraphs use this size
                            try:
                                doc_font = te.document().defaultFont()
                                doc_font.setPointSize(pt_size)
                                te.document().setDefaultFont(doc_font)
                            except Exception:
                                pass
                            te.update()
                        except Exception:
                            pass
                        # reflect in toolbar input if present
                        fi = getattr(self, '_label_font_size_input', None)
                        if fi is not None:
                            try:
                                fi.setText(str(self._label_font_size))
                            except Exception:
                                pass
                    except Exception:
                        pass
                    return True
                if mods & Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_Minus:
                    try:
                        self._label_font_size = max(1, getattr(self, '_label_font_size', 14) - 1)
                        # Apply only to selection if present, otherwise update insertion-point format
                        try:
                            cursor = te.textCursor()
                            from PyQt6.QtGui import QTextCharFormat
                            pt_size = max(1, int(self._label_font_size * (self.scale_factor or 1.0)))
                            fmt = QTextCharFormat()
                            fmt.setFontPointSize(float(pt_size))
                            if cursor.hasSelection():
                                cursor.beginEditBlock()
                                cursor.mergeCharFormat(fmt)
                                cursor.endEditBlock()
                            te.mergeCurrentCharFormat(fmt)
                            # Update document default font so new paragraphs use this size
                            try:
                                doc_font = te.document().defaultFont()
                                doc_font.setPointSize(pt_size)
                                te.document().setDefaultFont(doc_font)
                            except Exception:
                                pass
                            te.update()
                        except Exception:
                            pass
                        fi = getattr(self, '_label_font_size_input', None)
                        if fi is not None:
                            try:
                                fi.setText(str(self._label_font_size))
                            except Exception:
                                pass
                    except Exception:
                        pass
                    return True

                # Alt+Arrow: move the label shape while the text editor is open
                if mods & Qt.KeyboardModifier.AltModifier and key in (
                    Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down
                ):
                    _arrow_delta = {
                        Qt.Key.Key_Left:  QPoint(-1,  0),
                        Qt.Key.Key_Right: QPoint( 1,  0),
                        Qt.Key.Key_Up:    QPoint( 0, -1),
                        Qt.Key.Key_Down:  QPoint( 0,  1),
                    }
                    step = 10 if mods & Qt.KeyboardModifier.ShiftModifier else 1
                    delta = _arrow_delta[key] * step
                    edit_idx = getattr(self, '_label_edit_index', None)
                    if edit_idx is not None and 0 <= edit_idx < len(self.shapes):
                        self.push_undo()
                        shape = self.shapes[edit_idx]
                        new_start = shape[1] + delta
                        new_end   = shape[2] + delta
                        # Apply snap guidelines (same logic as regular arrow-key move)
                        if not self.snap_to_grid:
                            new_rect = QRect(new_start, new_end).normalized()
                            # Temporarily use edit_idx as selected_shape_index so
                            # _find_snap_guides excludes the label being moved.
                            _prev_sel = self.selected_shape_index
                            self.selected_shape_index = edit_idx
                            snapped, guides = self._find_snap_guides(new_rect)
                            self.selected_shape_index = _prev_sel
                            direction = _arrow_delta[key]
                            gd = snapped.topLeft() - new_rect.topLeft()
                            gx = gd.x() if direction.x() == 0 or direction.x() * gd.x() >= 0 else 0
                            gy = gd.y() if direction.y() == 0 or direction.y() * gd.y() >= 0 else 0
                            guide_delta = QPoint(gx, gy)
                            new_start += guide_delta
                            new_end   += guide_delta
                            self._active_guides = guides
                        else:
                            self._active_guides = []
                        self.shapes[edit_idx] = (shape[0], new_start, new_end) + shape[3:]
                        # Update the overlay's canvas rect and reposition it
                        overlay = getattr(self, '_text_edit_overlay', None)
                        if overlay is not None:
                            overlay._canvas_rect = QRect(new_start, new_end).normalized()
                            overlay._reposition()
                        self._label_canvas_rect = QRect(new_start, new_end).normalized()
                        self.update()
                    return True

        return super().eventFilter(obj, event)

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
        # If an inline label editor is active, reposition it so it remains
        # glued to the canvas after pan/zoom changes and refresh its font.
        overlay = getattr(self, '_text_edit_overlay', None)
        if overlay is not None:
            try:
                overlay._reposition()
                # Re-apply font sizing based on new scale_factor (preserve per-char styles)
                try:
                    self._apply_label_font_to_editor(getattr(self, '_text_edit_widget', None), apply_style_flags=False)
                except Exception:
                    pass
            except Exception:
                pass

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_C:
            if (
                self.selected_shape_index is not None
                and 0 <= self.selected_shape_index < len(self.shapes)
            ):
                tool = self.shapes[self.selected_shape_index][0]
                if tool == "image":
                    self.copy_selected_image_to_clipboard()
                else:
                    self.copy_selected_shape_to_clipboard()
                if callable(self.tooltip_callback):
                    self.tooltip_callback("Copied")
            return

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            clipboard = QApplication.clipboard()
            mime = clipboard.mimeData()
            text = clipboard.text()
            if mime.hasImage():
                self.paste_image_from_clipboard()
                if callable(self.tooltip_callback):
                    self.tooltip_callback("Pasted")
            elif self._is_shape_json(text):
                self.paste_shape_from_clipboard()
                if callable(self.tooltip_callback):
                    self.tooltip_callback("Pasted")
            return

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_E:
            if self.shape_layers_overlay.isVisible():
                self.shape_layers_overlay.setVisible(False)
            else:
                self.show_shape_layers_overlay()
            return

        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_G:
            self.snap_to_grid = not self.snap_to_grid
            if callable(self.tooltip_callback):
                self.tooltip_callback("Grid: On" if self.snap_to_grid else "Grid: Off")
            self.update()
            return
        
        # Open file
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_O:
            if callable(getattr(self, 'open_file_callback', None)):
                self.open_file_callback()
            return
        
        # Save file
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
            if callable(getattr(self, 'save_file_callback', None)):
                self.save_file_callback()
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
                if callable(self.tooltip_callback):
                    self.tooltip_callback("Undo")
                return
            elif event.key() == Qt.Key.Key_Y:
                self.redo()
                if callable(self.tooltip_callback):
                    self.tooltip_callback("Redo")
                return
            elif event.key() == Qt.Key.Key_D:
                self.duplicate_selected_object()
                if callable(self.tooltip_callback):
                    self.tooltip_callback("Duplicated")

                return
        
        # Arrow keys: move selected shape (1 px; 10 px with Shift)
        arrow_keys = {
            Qt.Key.Key_Left:  QPoint(-1,  0),
            Qt.Key.Key_Right: QPoint( 1,  0),
            Qt.Key.Key_Up:    QPoint( 0, -1),
            Qt.Key.Key_Down:  QPoint( 0,  1),
        }
        if event.key() in arrow_keys:
            step = 10 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1
            if self.snap_to_grid:
                step = self.grid_size
            direction = arrow_keys[event.key()]
            delta = direction * step

            def _arrow_guide_snap(rect):
                """Apply alignment guides but never pull back against the arrow direction."""
                snapped, guides = self._find_snap_guides(rect)
                gd = snapped.topLeft() - rect.topLeft()
                # Zero out any guide component opposing the arrow direction
                gx = gd.x() if direction.x() == 0 or direction.x() * gd.x() >= 0 else 0
                gy = gd.y() if direction.y() == 0 or direction.y() * gd.y() >= 0 else 0
                return QPoint(gx, gy), guides

            # Case 1: shape is selected and committed in self.shapes
            if self.selected_shape_index is not None:
                idx = self.selected_shape_index
                if 0 <= idx < len(self.shapes) and not self.is_shape_locked(idx):
                    self.push_undo()
                    shape = self.shapes[idx]
                    tool = shape[0]
                    if tool == "draw":
                        current_points = self.preview_start if isinstance(self.preview_start, list) else shape[1]
                        if not self.snap_to_grid:
                            xs = [p.x() for p in current_points]
                            ys = [p.y() for p in current_points]
                            cur_bbox = QRect(QPoint(min(xs), min(ys)), QPoint(max(xs), max(ys)))
                            new_bbox = cur_bbox.translated(delta)
                            guide_delta, self._active_guides = _arrow_guide_snap(new_bbox)
                            delta = delta + guide_delta
                        else:
                            self._active_guides = []
                        new_points = [p + delta for p in current_points]
                        self.shapes[idx] = tuple(["draw", new_points] + list(shape[2:]))
                        self.preview_start = [QPoint(p) for p in new_points]
                    else:
                        cur_start = self.preview_start if self.preview_start is not None else shape[1]
                        cur_end = self.preview_end if self.preview_end is not None else shape[2]
                        new_start = cur_start + delta
                        new_end = cur_end + delta
                        if not self.snap_to_grid:
                            new_rect = QRect(new_start, new_end).normalized()
                            guide_delta, self._active_guides = _arrow_guide_snap(new_rect)
                            new_start += guide_delta
                            new_end += guide_delta
                        else:
                            self._active_guides = []
                        self.shapes[idx] = tuple([tool, new_start, new_end] + list(shape[3:]))
                        self.preview_start = new_start
                        self.preview_end = new_end
                    self.update()
                    return

            # Case 2: shape is floating as a preview (after paste/duplicate)
            elif self.preview_shape is not None:
                if self.preview_shape == "draw" and isinstance(self.preview_start, list):
                    if not self.snap_to_grid:
                        xs = [p.x() for p in self.preview_start]
                        ys = [p.y() for p in self.preview_start]
                        cur_bbox = QRect(QPoint(min(xs), min(ys)), QPoint(max(xs), max(ys)))
                        new_bbox = cur_bbox.translated(delta)
                        guide_delta, self._active_guides = _arrow_guide_snap(new_bbox)
                        delta = delta + guide_delta
                    else:
                        self._active_guides = []
                    self.preview_start = [p + delta for p in self.preview_start]
                else:
                    if self.preview_start is not None and self.preview_end is not None:
                        new_start = self.preview_start + delta
                        new_end = self.preview_end + delta
                        if not self.snap_to_grid:
                            new_rect = QRect(new_start, new_end).normalized()
                            guide_delta, self._active_guides = _arrow_guide_snap(new_rect)
                            new_start += guide_delta
                            new_end += guide_delta
                        else:
                            self._active_guides = []
                        self.preview_start = new_start
                        self.preview_end = new_end
                    else:
                        self._active_guides = []
                        if self.preview_start is not None:
                            self.preview_start = self.preview_start + delta
                        if self.preview_end is not None:
                            self.preview_end = self.preview_end + delta
                self.update()
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
            self.shape_deselected.emit()
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
            if tool == "label":
                # Open inline text editor when selecting a label from the layers
                text = ""
                font_size = getattr(self, "_label_font_size", 14)
                font_bold = getattr(self, "_label_font_bold", False)
                font_italic = getattr(self, "_label_font_italic", False)
                font_underline = getattr(self, "_label_font_underline", False)
                font_family = getattr(self, "_label_font_family", "Arial")
                label_rotation = 0
                for item in shape[4:]:
                    if isinstance(item, str):
                        text = item
                    elif isinstance(item, dict) and "font_size" in item:
                        font_size = item.get("font_size", font_size)
                        font_bold = item.get("font_bold", False)
                        font_italic = item.get("font_italic", False)
                        font_underline = item.get("font_underline", False)
                        font_family = item.get("font_family", font_family)
                        font_align = item.get("text_align", getattr(self, "_label_text_align", "left"))
                    elif isinstance(item, (int, float)) and not isinstance(item, bool):
                        label_rotation = item
                self._label_font_size = font_size
                self._label_font_bold = font_bold
                self._label_font_italic = font_italic
                self._label_font_underline = font_underline
                self._label_font_family = font_family
                self._label_edit_rotation = label_rotation
                # restore alignment state for editing
                try:
                    self._label_text_align = font_align
                except Exception:
                    self._label_text_align = getattr(self, "_label_text_align", "left")
                self._label_edit_index = idx
                canvas_rect = QRect(start, end).normalized()
                # Hide preview and open overlay for direct editing
                self.preview_shape = None
                self.preview_start = None
                self.preview_end = None
                self._edit_locked_color = data if isinstance(data, QColor) else QColor("#000000")
                self._show_text_overlay(canvas_rect, existing_text=text)
            else:
                self.preview_shape = tool
                self.preview_start = start
                self.preview_end = end
                self.preview_rotation = rotation
                self.preview_pixmap = data if tool == "image" else None
                self._edit_locked_color = data if isinstance(data, QColor) else QColor("#000000")

        # PATCH END 
        self.shape_selected_for_edit.emit()
        self.update()

    def contextMenuEvent(self, event):
        # If a label text overlay is open, commit it but preserve the selection
        # so that Lock/Unlock and other actions remain available.
        if self._text_edit_overlay is not None and self._text_edit_overlay.isVisible():
            saved_idx = self.selected_shape_index
            self._commit_text_overlay()
            self.selected_shape_index = saved_idx

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
            if callable(self.tooltip_callback):
                self.tooltip_callback("Undo")
            self.undo()
            self.update()  
        undo_action.triggered.connect(do_undo)
        menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setEnabled(bool(self.redo_stack))
        def do_redo():
            if callable(self.tooltip_callback):
                self.tooltip_callback("Redo")
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
        
        # Duplicate
        duplicate_action = QAction("Duplicate", self)
        can_duplicate = (
            (
                self.selected_shape_index is not None
                and 0 <= self.selected_shape_index < len(self.shapes)
                and not self.is_shape_locked(self.selected_shape_index)
            )
            or self.preview_shape is not None
        )
        duplicate_action.setEnabled(can_duplicate)
        if can_duplicate:
            duplicate_action.triggered.connect(self.duplicate_selected_object)
        menu.addAction(duplicate_action)

        # Rotate
        rotate_action = QAction("Rotate 90°", self)
        can_rotate = (
            self.selected_shape_index is not None
            and 0 <= self.selected_shape_index < len(self.shapes)
            and self.shapes[self.selected_shape_index][0] not in ["image", "draw", "label"]
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
            fill_color = "transparent"
            # Read border weight from shape's stored dict
            border_weight = 2
            for item in shape[4:]:
                if isinstance(item, dict) and "border_weight" in item:
                    border_weight = item["border_weight"]
                    break

            # Safely extract border color (always at index 3)
            if len(shape) > 3 and isinstance(shape[3], QColor):
                border_color = "transparent" if shape[3].alpha() == 0 else shape[3].name()

            # Extract fill color and rotation from remaining elements
            fill_color_obj = None
            rotation = 0
            for item in shape[4:]:
                if isinstance(item, QColor):
                    fill_color_obj = item
                elif isinstance(item, (int, float)):
                    rotation = item

            if fill_color_obj:
                fill_color = "transparent" if fill_color_obj.alpha() == 0 else fill_color_obj.name()

            border_radius = 0
            for item in shape[4:]:
                if isinstance(item, dict) and "border_radius" in item:
                    border_radius = item["border_radius"]
                    break
            if tool == "roundrect" and border_radius == 0:
                border_radius = 18

            # Sync the custom color slots so the correct button is pre-selected
            # when the shape has a non-preset border or object color.
            _preset_border_colors = {"#000000", "#ffb366", "#ffe066", "#b3ff66"}
            if border_color != "transparent" and border_color.lower() not in _preset_border_colors:
                global CUSTOM_BORDER_COLOR
                CUSTOM_BORDER_COLOR = border_color
            _preset_object_colors = {"#000000", "#ffb366", "#ffe066", "#b3ff66", "#ffffff"}
            if fill_color != "transparent" and fill_color.lower() not in _preset_object_colors:
                global CUSTOM_OBJECT_COLOR
                CUSTOM_OBJECT_COLOR = fill_color

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
                label_text = None
                existing_extra_dicts = []
                for item in old_shape[4:]:
                    if isinstance(item, QColor):
                        existing_fill_color = item
                    elif isinstance(item, str):
                        label_text = item
                    elif isinstance(item, (int, float)) and not isinstance(item, bool):
                        existing_rotation = item
                    elif isinstance(item, dict):
                        existing_extra_dicts.append(item)

                new_shape = [tool, start, end, new_border_color]

                if isinstance(new_object_color, QColor) and new_object_color.alpha() > 0:
                    new_shape.append(new_object_color)
                elif existing_fill_color is not None:
                    new_shape.append(existing_fill_color)

                if existing_rotation != 0:
                    new_shape.append(existing_rotation)

                # Preserve label text
                if label_text is not None:
                    new_shape.append(label_text)

                if new_border_radius:
                    new_shape.append({"border_radius": new_border_radius})

                new_shape.append({"border_weight": new_border_weight})

                # Preserve other existing dicts (e.g. font_size for labels)
                for d in existing_extra_dicts:
                    if "border_radius" not in d and "border_weight" not in d:
                        new_shape.append(d)

                if isinstance(old_shape[-1], bool):
                    new_shape.append(old_shape[-1])

                self.shapes[idx] = tuple(new_shape)

                # Sync quick prop to the new border color before deselecting
                self.shape_selected_for_edit.emit()

                self.preview_shape = None
                self.preview_start = None
                self.preview_end = None
                self.selected_shape_index = None

                # Notify UIMode to update drawing_area.shape_color
                self.shape_deselected.emit()

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
        # Close the text overlay (committing content) before starting rotation,
        # so that mousePressEvent won't intercept clicks to commit the overlay
        # and deselect the shape.
        idx = self.selected_shape_index
        if self._text_edit_widget is not None:
            self._commit_text_overlay()
            # _commit_text_overlay resets selected_shape_index; restore it
            self.selected_shape_index = idx
        self._free_rotating = True
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
                # For non-draw shapes, use preview coords if available, fall back to shape data
                self.preview_shape = shape[0]
                self.preview_start = self.preview_start if self.preview_start is not None else shape[1]
                self.preview_end = self.preview_end if self.preview_end is not None else shape[2]
                self._orig_start = self.preview_start
                self._orig_end = self.preview_end
                self.preview_rotation = rotation
        if callable(self.tooltip_callback):
            self.tooltip_callback("Free Rotate")
        self.update()

        self.shape_layers_overlay.selected_idx = idx
        self.shape_layers_overlay.refresh()

    def rotate_selected_shape(self):
        if self.is_shape_locked(self.selected_shape_index):
            return
        idx = self.selected_shape_index
        if idx is None or idx < 0 or idx >= len(self.shapes):
            return
        # Close text overlay before rotating (same reason as free rotate)
        if self._text_edit_widget is not None:
            self._commit_text_overlay()
            self.selected_shape_index = idx
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
        if callable (self.tooltip_callback):
            self.tooltip_callback("Rotated 90°")
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
            draw_radius = shape_dict.get("draw_radius", None)
            extra_dicts = shape_dict.get("extra_dicts", [])
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
                self.preview_draw_radius = draw_radius if draw_radius is not None else self.draw_radius
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
                if callable(self.tooltip_callback):
                    self.tooltip_callback("Pasted")
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
                # Preserve label text and font dict for label shapes
                pending_extras = list(extra_dicts)
                label_text = shape_dict.get("label_text")
                if tool == "label" and label_text is not None:
                    self._pending_label_text = label_text
                else:
                    self._pending_label_text = None
                self._pending_shape_extras = pending_extras
                self.selected_shape_index = None
                if callable(self.tooltip_callback):
                    self.tooltip_callback("Pasted")
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
                if callable(self.tooltip_callback):
                    self.tooltip_callback("Pasted")
                self.update()

    def copy_selected_image_to_clipboard(self):
        if self.selected_shape_index is not None:
            tool, start, end, data = self.shapes[self.selected_shape_index][:4]
            if tool == "image":
                clipboard = QApplication.clipboard()
                clipboard.setPixmap(data)
                if callable(self.tooltip_callback):
                    self.tooltip_callback("Copied")

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
            draw_radius = None
            extra_dicts = []

            # Parse the rest of the shape tuple
            if tool == "draw":
                # For draw: shape[4] is draw_radius, shape[5] is rotation
                if len(shape) > 4 and isinstance(shape[4], (int, float)):
                    draw_radius = shape[4]
                if len(shape) > 5 and isinstance(shape[5], (int, float)):
                    rotation = shape[5]
            else:
                for v in shape[4:]:
                    if isinstance(v, QColor):
                        fill_color = v
                    elif isinstance(v, str):
                        shape_dict["label_text"] = v
                    elif isinstance(v, dict):
                        extra_dicts.append(v)
                    elif isinstance(v, (int, float)) and not isinstance(v, bool):
                        rotation = v

            # Store fill color if it exists
            if fill_color is not None:
                shape_dict["fill_color"] = fill_color.name()

            # Store rotation if it exists
            if rotation is not None:
                shape_dict["rotation"] = rotation

            # Store draw_radius for freehand shapes
            if draw_radius is not None:
                shape_dict["draw_radius"] = draw_radius

            # Store dict properties (border_weight, border_radius, etc.)
            if extra_dicts:
                shape_dict["extra_dicts"] = extra_dicts

            clipboard = QApplication.clipboard()
            if callable(self.tooltip_callback):
                self.tooltip_callback("Copied")
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
            if callable(self.tooltip_callback):
                self.tooltip_callback("Deleted")
            self.shape_deselected.emit()
            self.update()

    def push_undo(self):
        # Custom copy to avoid deepcopying QPixmap
        new_shapes = []
        for shape in self.shapes:
            tool, start, end, data = shape[:4]
            if tool == "image":
                # QPixmap: shallow copy reference; preserve extras (e.g. rotation)
                new_img = [tool, QPoint(start), QPoint(end), data]
                for item in shape[4:]:
                    new_img.append(item)
                new_shapes.append(tuple(new_img))
            elif tool == "draw":
                # Copy the list of points
                points_copy = [QPoint(p) for p in start] if isinstance(start, list) else []
                color = QColor(data) if isinstance(data, (QColor, str)) else QColor("#000000")
                # Preserve ALL extra fields (draw_radius at [4], rotation at [5], etc.)
                new_draw = [tool, points_copy, None, color]
                for item in shape[4:]:
                    new_draw.append(item)
                new_shapes.append(tuple(new_draw))
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
            # Preserve extras (e.g. rotation at shape[4]); pixmap is ref-copied
            new_img = [tool, QPoint(start), QPoint(end), data]
            for item in shape[4:]:
                new_img.append(item)
            return tuple(new_img)
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
        
    def duplicate_selected_object(self):
        if self.selected_shape_index is None and self.preview_shape is not None:
            self.push_undo()
            if self.preview_shape == "image":
                _rot = getattr(self, "preview_rotation", 0)
                _img_shape = ["image", self.preview_start, self.preview_end, self.preview_pixmap]
                if _rot:
                    _img_shape.append(_rot)
                self.shapes.append(tuple(_img_shape))
            elif self.preview_shape == "draw" and isinstance(self.preview_start, list):
                border_color = getattr(self, "preview_color", self.shape_color)
                draw_radius = getattr(self, "preview_draw_radius", self.draw_radius)
                rotation = getattr(self, "preview_rotation", 0)
                shape_tuple = ["draw", list(self.preview_start), None, border_color, draw_radius]
                if rotation != 0:
                    shape_tuple.append(rotation)
                self.shapes.append(tuple(shape_tuple))
            else:
                border_color = getattr(self, "preview_color", self.shape_color)
                fill_color = getattr(self, "preview_fill_color", None)
                rotation = getattr(self, "preview_rotation", 0)
                shape_tuple = [self.preview_shape, self.preview_start, self.preview_end, border_color]
                if fill_color is not None:
                    shape_tuple.append(fill_color)
                if rotation != 0:
                    shape_tuple.append(rotation)
                pending_label = getattr(self, '_pending_label_text', None)
                if pending_label is not None:
                    shape_tuple.append(pending_label)
                    self._pending_label_text = None
                for item in getattr(self, '_pending_shape_extras', []):
                    shape_tuple.append(item)
                self._pending_shape_extras = []
                self.shapes.append(tuple(shape_tuple))
            self.selected_shape_index = len(self.shapes) - 1
            self.preview_shape = None
            self.preview_start = None
            self.preview_end = None
            self.preview_pixmap = None
            self.preview_fill_color = None
            self.preview_rotation = 0
            
        idx = self.selected_shape_index
        if idx is None or idx < 0 or idx >= len(self.shapes):
            return
        shape = self.shapes[idx]
        new_shape = self._copy_single_shape(shape)
        offset = QPoint(20, 20)
        tool = new_shape[0]
    
        if tool == "draw":
            pts = [p + offset for p in new_shape[1]]
            draw_radius = new_shape[4] if len(new_shape) > 4 and isinstance(new_shape[4], (int, float)) else self.draw_radius
            rotation = new_shape[5] if len(new_shape) > 5 and isinstance(new_shape[5], (int, float)) else 0
            self.preview_shape = "draw"
            self.preview_start = list(pts)
            self.preview_end = None
            self.preview_color = new_shape[3] if isinstance(new_shape[3], QColor) else self.shape_color
            self.preview_draw_radius = draw_radius
            self.preview_rotation = rotation
            self._pending_shape_extras = []
            if pts and len(pts) > 1:
                min_x = min(p.x() for p in pts)
                min_y = min(p.y() for p in pts)
                max_x = max(p.x() for p in pts)
                max_y = max(p.y() for p in pts)
                self.preview_bbox = QRect(QPoint(min_x, min_y), QPoint(max_x, max_y)).normalized()
            else:
                self.preview_bbox = None
        elif tool == "image":
            start = new_shape[1] + offset
            end = new_shape[2] + offset
            self.preview_shape = "image"
            self.preview_start = start
            self.preview_end = end
            self.preview_pixmap = new_shape[3]
            # Preserve rotation from the source shape
            _img_rot = 0
            for _item in new_shape[4:]:
                if isinstance(_item, (int, float)) and not isinstance(_item, bool):
                    _img_rot = _item
            self.preview_rotation = _img_rot
            self._pending_shape_extras = []
        else:
            start = new_shape[1] + offset
            end = new_shape[2] + offset
            color = new_shape[3]
            fill_color = None
            rotation = 0
            extra_dicts = []
            label_text = None
            lock_flag = None
            for item in new_shape[4:]:
                if isinstance(item, QColor):
                    fill_color = item
                elif isinstance(item, bool):
                    lock_flag = item
                elif isinstance(item, str):
                    label_text = item
                elif isinstance(item, (int, float)):
                    rotation = item
                elif isinstance(item, dict):
                    extra_dicts.append(dict(item))

            # For label shapes, commit immediately and select the duplicate
            if tool == "label" and label_text is not None:
                shape_tuple = [tool, start, end, color]
                if fill_color is not None:
                    shape_tuple.append(fill_color)
                if rotation != 0:
                    shape_tuple.append(rotation)
                shape_tuple.append(label_text)
                for d in extra_dicts:
                    shape_tuple.append(d)
                if lock_flag is not None:
                    shape_tuple.append(lock_flag)
                # Close any active text overlay before committing duplicate
                if self._text_edit_widget is not None:
                    self._cancel_text_overlay()
                self.push_undo()
                self.shapes.append(tuple(shape_tuple))
                new_idx = len(self.shapes) - 1
                self.selected_shape_index = new_idx
                self.preview_shape = tool
                self.preview_start = start
                self.preview_end = end
                self.preview_color = color
                self.preview_fill_color = fill_color
                self.preview_rotation = rotation
                self.shape_layers_overlay.update_shapes(self.shapes)
                self.update()
                return

            self.preview_shape = tool
            self.preview_start = start
            self.preview_end = end
            self.preview_color = color
            self.preview_fill_color = fill_color
            self.preview_rotation = rotation
            self._pending_label_text = label_text
            pending = list(extra_dicts)
            if lock_flag is not None:
                pending.append(lock_flag)
            self._pending_shape_extras = pending
    
        self.selected_shape_index = None
        self.update()

    def push_shape_restore(self, idx, action_label):
        # Record a per-shape restore point before a properties change
        if idx is None or idx < 0 or idx >= len(self.shapes):
            return
        shape = self.shapes[idx]    
        shape_label = f"Object{idx + 1}"
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
                # For line tool, preserve the original direction; normalizing the rect loses which endpoint
                # is "start" vs "end" (e.g. a bottom-left→top-right line would be flipped).
                if tool == "line":
                    _local_start = QPoint(start.x() - rect.left(), start.y() - rect.top())
                    _local_end   = QPoint(end.x()   - rect.left(), end.y()   - rect.top())
                else:
                    _local_start = local_rect.topLeft()
                    _local_end   = local_rect.bottomRight()

                # Draw fill only if the original shape actually had a fill_color
                if fill_color is not None:
                    painter_img.setBrush(QBrush(fill_color))
                    painter_img.setPen(Qt.PenStyle.NoPen)
                    self.draw_shape(painter_img, tool, _local_start, _local_end, border_radius=border_radius)
                else:
                    painter_img.setBrush(Qt.BrushStyle.NoBrush)

                # Draw border (scale pen width by supersample factor so stroke thickness is preserved)
                if border_color.alpha() > 0 and border_weight and border_weight > 0:
                    pen = QPen(border_color, border_width_disp * 1.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                    # Because we already scaled the painter, set pen width in display units (painter.scale handles pixel density)
                    pen.setWidthF(border_width_disp)
                    painter_img.setPen(pen)
                    self.draw_shape(painter_img, tool, _local_start, _local_end, border_radius=border_radius, line_width=border_weight)
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
                    return
                continue  # not touched — skip to next shape
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
                return
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
                    return

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
                    border_weight = 2
                    border_radius = None

                    # Extract properties
                    for prop in rest[1:]:
                        if isinstance(prop, QColor):
                            fill_color = prop
                        elif isinstance(prop, dict):
                            if "border_weight" in prop:
                                border_weight = prop["border_weight"]
                            if "border_radius" in prop:
                                border_radius = prop["border_radius"]
                        elif isinstance(prop, (int, float)) and not isinstance(prop, bool):
                            rotation = prop

                    painter.save()
                    if rotation:
                        painter.translate(rect.center())
                        painter.rotate(rotation)
                        painter.translate(-rect.center())

                    # For line tool, preserve the original direction; normalizing the rect loses
                    # which endpoint is "start" vs "end" (e.g. bottom-left→top-right lines get flipped).
                    _draw_start = start if tool == "line" else rect.topLeft()
                    _draw_end   = end   if tool == "line" else rect.bottomRight()

                    # Draw fill first if present
                    if fill_color:
                        painter.setBrush(QBrush(fill_color))
                        painter.setPen(Qt.PenStyle.NoPen)
                        self.draw_shape(painter, tool, _draw_start, _draw_end, border_radius=border_radius)

                    # Draw border (skip if transparent or weight is 0)
                    if color.alpha() > 0 and border_weight and border_weight > 0:
                        painter.setBrush(Qt.BrushStyle.NoBrush)
                        painter.setPen(QPen(color, border_weight))
                        self.draw_shape(painter, tool, _draw_start, _draw_end, line_width=border_weight, border_radius=border_radius)

                    # Draw text content for label shapes
                    if tool == "label":
                        lbl_text = ""
                        lbl_font_size = 14
                        lbl_bold = False
                        lbl_italic = False
                        lbl_underline = False
                        lbl_font_family = getattr(self, "_label_font_family", "Arial")
                        lbl_align = "left"
                        for _item in rest[1:]:
                            if isinstance(_item, str):
                                lbl_text = _item
                            elif isinstance(_item, dict) and "font_size" in _item:
                                lbl_font_size = _item.get("font_size", lbl_font_size)
                                lbl_bold = _item.get("font_bold", False)
                                lbl_italic = _item.get("font_italic", False)
                                lbl_underline = _item.get("font_underline", False)
                                lbl_font_family = _item.get("font_family", lbl_font_family)
                                lbl_align = _item.get("text_align", lbl_align)
                        if lbl_text:
                            try:
                                from PyQt6.QtGui import QTextDocument
                                text_draw_rect = rect.adjusted(4, 4, -4, -4)
                                lbl_font = QFont(lbl_font_family, lbl_font_size)
                                lbl_font.setBold(lbl_bold)
                                lbl_font.setItalic(lbl_italic)
                                lbl_font.setUnderline(lbl_underline)

                                doc = QTextDocument()
                                doc.setDefaultFont(lbl_font)

                                is_html = isinstance(lbl_text, str) and ("<" in lbl_text and ">" in lbl_text and any(k in lbl_text.lower() for k in ("<span", "<p", "<div", "<br", "<b", "<i", "<u", "style=", "<!doctype", "<html")))
                                if is_html:
                                    doc.setHtml(lbl_text)
                                else:
                                    safe_text = (lbl_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"))
                                    doc.setHtml(f'<div style="color:{color.name()}; font-family:{lbl_font_family}; font-size:{lbl_font_size}pt; text-align:{lbl_align};">{safe_text}</div>')

                                doc.setTextWidth(float(text_draw_rect.width()))
                                painter.save()
                                painter.translate(text_draw_rect.left(), text_draw_rect.top())
                                doc.drawContents(painter, QRectF(0, 0, text_draw_rect.width(), text_draw_rect.height()))
                                painter.restore()
                            except Exception:
                                painter.setPen(QPen(color))
                                lbl_font = QFont(lbl_font_family, lbl_font_size)
                                lbl_font.setBold(lbl_bold)
                                lbl_font.setItalic(lbl_italic)
                                lbl_font.setUnderline(lbl_underline)
                                painter.setFont(lbl_font)
                                text_draw_rect = rect.adjusted(4, 4, -4, -4)
                                align_map = {
                                    "left": Qt.AlignmentFlag.AlignLeft,
                                    "center": Qt.AlignmentFlag.AlignHCenter,
                                    "right": Qt.AlignmentFlag.AlignRight,
                                }
                                a_flag = align_map.get(lbl_align, Qt.AlignmentFlag.AlignLeft)
                                painter.drawText(
                                    text_draw_rect,
                                    a_flag | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                                    lbl_text,
                                )

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
                # Split: keep only points that are outside the crop area
                outside_points = [p for p in start if not crop_rect.contains(p)]
                if len(outside_points) >= 2:
                    # Rebuild shape tuple with only the outside points
                    shapes_to_keep.append((tool, outside_points) + tuple(rest))
                elif not any(crop_rect.contains(p) for p in start):
                    # None of the points are inside — keep as-is
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
        self.preview_rotation = 0
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

        # For geometric shapes, convert to rectangle if clipped
        if tool in ["circle", "triangle", "cross"]:
            # Convert complex shapes to rectangles when clipped
            tool = "rect"

        shape_data = [tool, intersect.topLeft(), intersect.bottomRight(), color]
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
                label_text = None
                for item in old_shape[4:]:
                    if isinstance(item, QColor):
                        fill_color = item
                    elif isinstance(item, str):
                        label_text = item
                    elif isinstance(item, (int, float)) and not isinstance(item, bool):
                        rotation = item
                    elif isinstance(item, dict):
                        extra_dicts.append(item)
                shape = [tool, self.preview_start, self.preview_end, border_color]
                if fill_color is not None:
                    shape.append(fill_color)
                if rotation:
                    shape.append(rotation)
                if label_text is not None:
                    shape.append(label_text)
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
            if callable(self.tooltip_callback):
                    self.tooltip_callback("Locked")
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
            if callable(self.tooltip_callback):
                    self.tooltip_callback("Unlocked")
            self.update()

    def points_close(self, p1, p2, tolerance=5):
        return (p1 - p2).manhattanLength() < tolerance

    def _snap_line_angle(self, start: QPoint, end: QPoint) -> QPoint:
        """Snap `end` so the angle from `start` to `end` is a multiple of 45 degrees."""
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.hypot(dx, dy)
        if length == 0:
            return end
        angle = math.degrees(math.atan2(dy, dx))
        snapped_angle = round(angle / 45) * 45
        rad = math.radians(snapped_angle)
        return QPoint(
            int(round(start.x() + length * math.cos(rad))),
            int(round(start.y() + length * math.sin(rad)))
        )


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
                # Determine stroke/color for thumbnail rendering. Default to black.
                if isinstance(data, QColor):
                    color = data
                else:
                    color = QColor("#000000")
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
                        elif tool == "label":
                            # Render a miniature preview for label: draw border/fill and wrapped text
                            # Shape format: ("label", start, end, color, text, font_dict)
                            lbl_text = ""
                            lbl_font_size = getattr(self.drawing_area, "_label_font_size", 14)
                            lbl_bold = False
                            lbl_italic = False
                            lbl_underline = False
                            lbl_font_family = getattr(self.drawing_area, "_label_font_family", "Arial")
                            lbl_align = getattr(self.drawing_area, "_label_text_align", "left")
                            fill_color = None
                            # gather extra items from the full shape tuple
                            full_shape = self.shapes[idx]
                            for item in full_shape[4:]:
                                if isinstance(item, str):
                                    lbl_text = item
                                elif isinstance(item, dict) and "font_size" in item:
                                    lbl_font_size = item.get("font_size", lbl_font_size)
                                    lbl_bold = item.get("font_bold", False)
                                    lbl_italic = item.get("font_italic", False)
                                    lbl_underline = item.get("font_underline", False)
                                    lbl_font_family = item.get("font_family", lbl_font_family)
                                    lbl_align = item.get("text_align", lbl_align)
                                elif isinstance(item, QColor):
                                    fill_color = item
                            # draw fill if present
                            if fill_color is not None:
                                painter.setBrush(QBrush(fill_color))
                                painter.setPen(Qt.PenStyle.NoPen)
                                painter.drawRect(rect)
                            painter.setBrush(Qt.BrushStyle.NoBrush)
                            painter.setPen(QPen(color, 2))
                            painter.drawRect(rect)
                            if lbl_text:
                                # Render miniature preview using QTextDocument to keep per-char styling
                                try:
                                    from PyQt6.QtGui import QTextDocument
                                    est_size = max(6, int(rect.height() * 0.18))
                                    lbl_font = QFont(lbl_font_family, est_size)
                                    lbl_font.setBold(lbl_bold)
                                    lbl_font.setItalic(lbl_italic)
                                    lbl_font.setUnderline(lbl_underline)

                                    text_draw_rect = rect.adjusted(4, 4, -4, -4)
                                    doc = QTextDocument()
                                    doc.setDefaultFont(lbl_font)
                                    is_html = isinstance(lbl_text, str) and ("<" in lbl_text and ">" in lbl_text and any(k in lbl_text.lower() for k in ("<span", "<p", "<div", "<br", "<b", "<i", "<u", "style=", "<!doctype", "<html")))
                                    if is_html:
                                        doc.setHtml(lbl_text)
                                    else:
                                        safe_text = (lbl_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"))
                                        doc.setHtml(f'<div style="color:{color.name()}; font-family:{lbl_font_family}; font-size:{est_size}pt; text-align:{lbl_align};">{safe_text}</div>')
                                    doc.setTextWidth(float(text_draw_rect.width()))
                                    painter.save()
                                    painter.translate(text_draw_rect.left(), text_draw_rect.top())
                                    doc.drawContents(painter, QRectF(0, 0, text_draw_rect.width(), text_draw_rect.height()))
                                    painter.restore()
                                except Exception:
                                    est_size = max(6, int(rect.height() * 0.18))
                                    lbl_font = QFont(lbl_font_family, est_size)
                                    lbl_font.setBold(lbl_bold)
                                    lbl_font.setItalic(lbl_italic)
                                    lbl_font.setUnderline(lbl_underline)
                                    painter.setFont(lbl_font)
                                    painter.setPen(QPen(color))
                                    align_map = {
                                        "left": Qt.AlignmentFlag.AlignLeft,
                                        "center": Qt.AlignmentFlag.AlignHCenter,
                                        "right": Qt.AlignmentFlag.AlignRight,
                                    }
                                    a_flag = align_map.get(lbl_align, Qt.AlignmentFlag.AlignLeft)
                                    painter.drawText(
                                        rect.adjusted(4, 4, -4, -4),
                                        a_flag | Qt.AlignmentFlag.AlignTop | Qt.TextFlag.TextWordWrap,
                                        lbl_text,
                                    )
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

    # Auto-scroll logic for drag ---
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
        
class PageBar(QWidget):
    page_added    = pyqtSignal()
    page_selected = pyqtSignal(int)

    _COLLAPSED_W = 80
    _COLLAPSED_H = 22
    _EXPANDED_H  = 44

    def __init__(self, parent=None, accent="#ff6600"):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self._accent     = accent
        self._pages      = ["Page 1"]
        self._current    = 0
        self._expanded   = False
        self._collapsing = False
        self._page_btns  = []

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._dash_widget = QWidget()
        self._dash_widget.setStyleSheet("background: transparent;")
        dl = QHBoxLayout(self._dash_widget)
        dl.setContentsMargins(0, 0, 0, 0)
        dl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dash_lbl = QLabel("—")
        self._dash_lbl.setStyleSheet(
            "color: #999; font-size: 32pt; font-weight: 900; background: transparent; border: none; letter-spacing: -2px;"
        )
        dl.addWidget(self._dash_lbl)
        outer.addWidget(self._dash_widget)

        self._exp_widget = QWidget()
        self._exp_widget.setStyleSheet("background: transparent;")
        self._exp_widget.setVisible(False)
        el = QHBoxLayout(self._exp_widget)
        el.setContentsMargins(4, 0, 4, 0)
        el.setSpacing(4)

        # Inner widget holds the page buttons; scroll area clips it without a visible bar
        self._btns_widget = QWidget()
        self._btns_widget.setStyleSheet("background: transparent;")
        self._btns_widget.setFixedHeight(self._EXPANDED_H)
        self._page_layout = QHBoxLayout(self._btns_widget)
        self._page_layout.setContentsMargins(10, 0, 10, 0)
        self._page_layout.setSpacing(6)
        self._page_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self._scroll = QScrollArea()
        self._scroll.setWidget(self._btns_widget)
        self._scroll.setWidgetResizable(False)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._scroll.setFixedHeight(self._EXPANDED_H)
        el.addWidget(self._scroll, stretch=1)

        self._add_btn = QPushButton("+")
        self._add_btn.setFixedSize(28, 28)
        self._add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_btn.setStyleSheet(self._add_btn_ss())
        self._add_btn.clicked.connect(self._on_add)
        outer.addWidget(self._exp_widget)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 0))
        self.setGraphicsEffect(shadow)

        self._leave_timer = QTimer(self)
        self._leave_timer.setSingleShot(True)
        self._leave_timer.setInterval(200)
        self._leave_timer.timeout.connect(self._check_leave)

        self._geo_anim = QPropertyAnimation(self, b"geometry")
        self._geo_anim.setDuration(240)
        self._geo_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._geo_anim.finished.connect(self._on_anim_done)

        self._apply_style()
        self._refresh_pages()

    def _apply_style(self):
        self.setStyleSheet("""
            PageBar {
                background: transparent;
                border: none;
            }
        """)

    def _add_btn_ss(self):
        return f"""
            QPushButton {{
                background: transparent; border: none;
                font-size: 18pt; color: #888;
            }}
            QPushButton:hover {{ color: {self._accent}; }}
        """

    def _page_btn_ss(self, active: bool):
        if active:
            bg    = self._accent
            fg    = "white"
            hover = QColor(self._accent).lighter(130).name()
        else:
            bg    = "#f0f0f0"
            fg    = "#333"
            hover = "#e0e0e0"
        return f"""
            QPushButton {{
                background: {bg}; color: {fg};
                border: none; border-radius: 8px;
                padding: 0 12px; font-size: 10pt;
            }}
            QPushButton:hover {{ background: {hover}; }}
        """


    def set_accent(self, color: QColor):
        self._accent = color.name()
        self._apply_style()
        self._add_btn.setStyleSheet(self._add_btn_ss())
        self._refresh_pages()

    def _refresh_pages(self):
        for btn in self._page_btns:
            btn.setParent(None)
        self._page_btns = []
        self._page_layout.removeWidget(self._add_btn)

        fm = self.fontMetrics()
        btns_natural_w = 20  # left+right margins (10 each)
        for i, name in enumerate(self._pages):
            btn = QPushButton(name)
            btn.setFixedHeight(30)
            btn.setMinimumWidth(fm.horizontalAdvance(name) + 24)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(self._page_btn_ss(i == self._current))
            btn.clicked.connect(lambda checked, idx=i: self._on_page_selected(idx))
            self._page_layout.addWidget(btn)
            self._page_btns.append(btn)
            btns_natural_w += fm.horizontalAdvance(name) + 24 + 6 
        if self._pages:
            btns_natural_w -= 6  

        # Add button lives at the end, inside the scroll
        self._page_layout.addWidget(self._add_btn)
        btns_natural_w += 6 + 28  # spacing + add btn width
        
        self._btns_natural_w = max(btns_natural_w, 60)
        self._btns_widget.setFixedWidth(self._btns_natural_w)
        QTimer.singleShot(0, self._fit_btns_widget_to_content)

    def set_pages(self, names: list, current_idx: int):
        self._pages = list(names)
        self._current = current_idx
        self._refresh_pages()
        # If already expanded, animate to the new width
        if self._expanded and self._geo_anim.state() != QPropertyAnimation.State.Running:
            new_rect = self._expanded_rect()
            if self.geometry() != new_rect:
                self._geo_anim.stop()
                self._geo_anim.setStartValue(self.geometry())
                self._geo_anim.setEndValue(new_rect)
                self._geo_anim.start()

    def _on_add(self):
        # Don't mutate internal list — UIMode owns the data
        self.page_added.emit()

    def _on_page_selected(self, idx: int):
        self._current = idx
        self._refresh_pages()
        self.page_selected.emit(idx)

    def _bottom_y(self) -> int:
        ph = self.parentWidget().height() if self.parentWidget() else 600
        margin = 18  # gap from bottom edge
        return ph - self._EXPANDED_H - margin

    def _expanded_w(self) -> int:
        pw = self.parentWidget().width() if self.parentWidget() else 800
        fm = self.fontMetrics()
        btns_w = 20  # margins
        visible_pages = self._pages[:5]  # cap visible area to 5 pages
        for name in visible_pages:
            btns_w += fm.horizontalAdvance(name) + 24 + 6
        if visible_pages:
            btns_w -= 6
        btns_w += 6 + 28
        max_viewport = min(pw - 200, 420)
        visible_w = min(btns_w, max_viewport)
        return max(100, visible_w + 8)

    def _fit_btns_widget_to_content(self):
        # Skip if buttons aren't visible — layout positions are stale
        if not self._exp_widget.isVisible():
            return
        right_margin = self._page_layout.contentsMargins().right()
        add_x = self._add_btn.x()
        min_w = getattr(self, '_btns_natural_w', 60)
        # Layout hasn't been applied yet — keep the pre-calculated width
        if add_x == 0 and self._page_btns:
            self._scroll_to_current()
            return
        exact_w = add_x + self._add_btn.width() + right_margin
        if exact_w > min_w:
            self._btns_widget.setFixedWidth(exact_w)
        self._scroll_to_current()
    
    def _scroll_to_current(self):
        if not self._page_btns or self._current >= len(self._page_btns):
            return
        btn = self._page_btns[self._current]
        bar = self._scroll.horizontalScrollBar()
        viewport_w = self._scroll.viewport().width()
        # Center the active page button in the viewport
        target = btn.x() + btn.width() // 2 - viewport_w // 2
        bar.setValue(max(0, min(bar.maximum(), target)))  

    def _collapsed_rect(self) -> QRect:
        pw = self.parentWidget().width() if self.parentWidget() else 800
        by = self._bottom_y() + (self._EXPANDED_H - self._COLLAPSED_H) // 2
        return QRect((pw - self._COLLAPSED_W) // 2, by,
                     self._COLLAPSED_W, self._COLLAPSED_H)

    def _expanded_rect(self) -> QRect:
        pw = self.parentWidget().width() if self.parentWidget() else 800
        ew = self._expanded_w()
        return QRect((pw - ew) // 2, self._bottom_y(), ew, self._EXPANDED_H)

    def update_position(self, parent_w: int):
        """Call from parent's resizeEvent to re-center."""
        if self._geo_anim.state() == QPropertyAnimation.State.Running:
            return
        rect = self._expanded_rect() if self._expanded else self._collapsed_rect()
        self.setGeometry(rect)


    def enterEvent(self, event):
        self._leave_timer.stop()
        if not self._expanded or self._collapsing:
            self._expanded   = True
            self._collapsing = False
            self._exp_widget.setVisible(True)
            self._dash_widget.setVisible(False)
            self._geo_anim.stop()
            self._geo_anim.setStartValue(self.geometry())
            self._geo_anim.setEndValue(self._expanded_rect())
            self._geo_anim.start()
            # Re-fit once layout recalculates with visible widgets
            QTimer.singleShot(0, self._fit_btns_widget_to_content)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._leave_timer.start()
        super().leaveEvent(event)

    def _check_leave(self):
        if not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
            self._expanded   = False
            self._collapsing = True
            self._geo_anim.stop()
            self._geo_anim.setStartValue(self.geometry())
            self._geo_anim.setEndValue(self._collapsed_rect())
            self._geo_anim.start()

    def _on_anim_done(self):
        if self._collapsing:
            self._collapsing = False
            self._dash_widget.setVisible(True)
            self._exp_widget.setVisible(False)
            
    def wheelEvent(self, event):
        delta = event.angleDelta().y() or event.angleDelta().x()
        bar = self._scroll.horizontalScrollBar()
        bar.setValue(bar.value() - delta // 3)
        event.accept()


class _AutoSaveWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    @pyqtSlot(dict)
    def do_save(self, data):
        try:
            file_path = data["file_path"]
            config_folder = data["config_folder"]
            payload = data["payload"]
            histories_payload = data["histories"]

            # Finalize pages: convert QImage objects to base64 strings
            for sp in payload["spaces"]:
                for page in sp["pages"]:
                    _finalize_page_for_json(page)

            # Finalize history entries that contain image shapes
            for sp_hist in histories_payload:
                for page_hist in sp_hist:
                    for entry in page_hist:
                        shape_d = entry.get("shape_data", {})
                        if "qimage" in shape_d:
                            shape_d["pixmap"] = _encode_qimage_b64(shape_d.pop("qimage"))

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            with open(os.path.join(config_folder, "shape_history.json"), "w", encoding="utf-8") as f:
                json.dump({"version": 3, "spaces": histories_payload}, f, indent=2)

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class UIMode(QWidget):
    _request_auto_save = pyqtSignal(dict)

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
        self._checkpoint_preview_dialogs = {}
        
        self.selected_tool = None
        self._first_ribbon_init = True
        
        self.setWindowTitle("Log Documentation System - Log Mode")
        self.setStyleSheet("font-family: Arial; font-size: 12pt;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        #self.resize(1100, 700)
        self.custom_tooltip = CustomToolTip(self)
        self.init_ui()
        self._show_controls = False
        
        self.drawing_area.shape_selected_for_edit.connect(self.deselect_tool)
        self._tool_btn_anim = None  # Initialize attribute to avoid assignment error
        self._last_category_index = 0
        self.drawing_area.shape_selected_for_edit.connect(self.sync_color_with_selected_shape)
        self.drawing_area.shape_deselected.connect(self._restore_color_after_deselect)
        self._pre_selection_color = None
        #self._was_maximized = False
        
        self._recent_files = self._load_recent_files()
        self._side_menu.refresh_recent_list(self._recent_files, on_open=self.open_canvas, tooltip_fn=self.custom_tooltip.show_tooltip)

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
            QWidget {
                background: white;
                border: none;
            }
            QWidget:hover {
                background: #f0f0f0;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: transparent;
                height: 0px;
            }
            QScrollBar::handle {
                background: #ff6600;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                width: 0px;
                height: 0px;
            }
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
            pixmap = QPixmap(os.path.join(_ASSETS_DIR, "paintprop1.png")).scaled(58, 58, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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
            sel_idx = self.drawing_area.selected_shape_index
            if sel_idx is not None and 0 <= sel_idx < len(self.drawing_area.shapes):
                # Edit the selected shape's border color directly
                shape = self.drawing_area.shapes[sel_idx]
                current_bc = shape[3] if isinstance(shape[3], QColor) else QColor("#000000")
                color = QColorDialog.getColor(current_bc, self, "Pick Border Color")
                if color.isValid():
                    self.drawing_area.push_undo()
                    new_shape = list(self.drawing_area.shapes[sel_idx])
                    new_shape[3] = color
                    self.drawing_area.shapes[sel_idx] = tuple(new_shape)
                    self.current_shape_color = color
                    update_quick_prop_icon()
                    self.drawing_area.set_shape_color(color)
                    self.update_tool_btn_border()
                    self.drawing_area.update()
                return

            color = QColorDialog.getColor(self.current_shape_color, self, "Pick Shape Color")
            if color.isValid():
                self.current_shape_color = color
                update_quick_prop_icon()
                self.drawing_area.set_shape_color(color)  # Pass color to drawing area
                self.update_tool_btn_border()
                self._side_menu.set_accent_color(color)
                self.page_bar.set_accent(color)
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
        self.drawing_area = DrawingArea(self)
        # Page state init (one page per canvas "space")
        _em = QPixmap(self.drawing_area.a4_size)
        _em.fill(Qt.GlobalColor.transparent)
        self._spaces = [{
            "name": "Space 1",
            "current_page": 0,
            "pages": [{
                "name": "Page 1",
                "shapes": [],
                "eraser_mask": _em,
                "eraser_strokes": [],
                "scale_factor": 1.0,
                "zoom_percent": 0,
                "pan_offset": QPoint(0, 0),
                "tool_sizes": dict(self.drawing_area.tool_last_sizes),
                "shape_history": [],
                "undo_stack": [],
                "redo_stack": [],
                "thumbnail": None,
                "created": datetime.now().strftime("%Y-%m-%d"),
            }]
        }]
        self._current_space_idx = 0
        self._current_page_idx = 0
        self.drawing_area.open_file_callback = self.open_canvas
        self.drawing_area.save_file_callback = self.save_canvas
        self.drawing_area.tooltip_callback = self.show_tool_tooltip
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
        # Hotkeys Button Action
        self._side_menu.file_actions["Hotkeys"].clicked.connect(self.show_hotkeys_dialog)
        # Connect Exit action
        self._side_menu.file_actions["Exit"].clicked.connect(self.close)
        
        # History Tab
        self._side_menu.create_checkpoint_btn.clicked.connect(self.create_file_checkpoint)
        self.menu_btn.raise_()
        
        # Floating page bar (top center, hover-to-expand)
        self.page_bar = PageBar(parent=self, accent=self.current_shape_color.name())
        # Wire PageBar ↔ UIMode
        self.page_bar.page_added.connect(self._add_page)
        self.page_bar.page_selected.connect(self._select_page)

        # Wire side panel Pages tab ↔ UIMode
        self._side_menu.create_space_btn.clicked.connect(self._add_space)
        self._side_menu.space_selected.connect(self._select_space)

        # Push initial single page to both UIs
        self._sync_page_ui()
        self.page_bar.show()
        self.page_bar.raise_()
        
        self.ribbon_layout = ribbon_layout
        self.divider = divider  
        
        # Tool button (bottom right, floating)
        self.tool_btn = RotatingToolButton()
        self._rotated = False
        self.tool_btn.setFixedSize(68, 68)
        self.tool_btn.setParent(self)
        self.tool_btn.setIcon(QIcon(os.path.join(_ASSETS_DIR, "tool.png")))
        
        self.tool_btn.setIconSize(QSize(68, 68)) 
        self.update_tool_btn_border()
        self.tool_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Add shadow effect

        self.tool_btn.show()
        btn_margin = 24
        self.tool_btn.move(
            self.width() - self.tool_btn.width() - btn_margin,
            self.height() - self.tool_btn.height() - btn_margin,
        )
    
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

        # Auto-save worker thread setup
        self._auto_save_worker = _AutoSaveWorker()
        self._auto_save_thread = QThread(self)
        self._auto_save_worker.moveToThread(self._auto_save_thread)
        self._request_auto_save.connect(self._auto_save_worker.do_save)
        self._auto_save_worker.finished.connect(self._on_auto_save_done)
        self._auto_save_worker.error.connect(self._on_auto_save_error)
        self._auto_save_thread.start()
        self._auto_save_running = False
        self._auto_save_queued = False
        
        
        
        
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
        if hasattr(self, 'tool_btn'):
            self.tool_btn.move(self.width() - self.tool_btn.width() - btn_margin,
                               self.height() - self.tool_btn.height() - btn_margin)
        
        if hasattr(self, 'page_bar'):
            self.page_bar.update_position(self.width())
            
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

    def closeEvent(self, event):
        self._auto_save_timer.stop()
        self._auto_save_thread.quit()
        self._auto_save_thread.wait(3000)
        super().closeEvent(event)
    
    @property
    def _page_states(self):
        """Convenience: the pages list of the currently active space."""
        return self._spaces[self._current_space_idx]["pages"]    
    
    def show_tool_tooltip(self, text):
        self.custom_tooltip.show_tooltip(text)
    
            
    def keyPressEvent(self, event):
        # Forward arrow keys to drawing area for shape nudging
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            self.drawing_area.keyPressEvent(event)
            return
        
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
        
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_G:
            self.drawing_area.keyPressEvent(event)
        
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_D:
            self.drawing_area.duplicate_selected_object()
                            
        
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
                pixmap = QPixmap(os.path.join(_ASSETS_DIR, "tool-colors-eraser.png"))
                if not pixmap.isNull():
                    size = self.drawing_area.eraser_radius * 2
                    cursor_pix = pixmap.scaled(size, size)
                    self.drawing_area.setCursor(QCursor(cursor_pix, size // 2, size // 2))
    
    def show_hotkeys_dialog(self):
        accent = self.current_shape_color.name()
        darker = self.current_shape_color.darker(120).name()

        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setModal(True)
        dialog.setFixedSize(380, 480)
        dialog.setStyleSheet("background: white; border-radius: 12px; border: 2px solid #222;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        drag_bar = DraggableBar(dialog)
        layout.addWidget(drag_bar)

        title = QLabel("Hotkeys")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)

        hotkeys = [
            ("General", [
                ("Ctrl + Z",        "Undo"),
                ("Ctrl + Y",        "Redo"),
                ("Ctrl + S",        "Save"),
                ("Ctrl + C",        "Copy selected object"),
                ("Ctrl + V",        "Paste object"),
                ("Ctrl + D",        "Duplicate object"),
                ("Delete",          "Delete selected object"),
                ("Escape",          "Cancel / Deselect tool"),
                ("Arrow keys",      "Move object"),
                ("Shift + Arrow keys", "Move object by 10px"),
                ("Shift + Drag to resize", "Resize proportionally"),
            ]),
            ("Canvas", [
                ("Ctrl + Scroll",   "Zoom in / out"),
                ("Shift + Scroll",  "Pan left / right"),
                ("Scroll",          "Pan up / down"),
                ("Ctrl + E",        "Toggle object layers"),
                ("Ctrl + G",        "Toggle snap grid"),
            ]),
            ("Tools", [
                ("Double-click eraser", "Adjust tool size"),
                ("Double-click draw",  "Adjust tool size"),
                ("Shift + Drawing",   "Draw straight lines"),
            ]),
            ("Label Editing", [
                ("Ctrl + B",        "Make the text bold"),
                ("Ctrl + I",        "Make the text italic"),
                ("Ctrl + U",        "Underline the text"),
                ("Ctrl + - or +",   "Control font size"),
                ("Ctrl + Enter",    "Commit edit"),
                ("Ctrl + L",        "Align text to left"),
                ("Ctrl + T",        "Align text to center"),
                ("Ctrl + R",        "Align text to right"),
                ("Alt + Arrow keys","Move label"),
            ])
        ]

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(12)

        for section, items in hotkeys:
            section_lbl = QLabel(section)
            section_lbl.setStyleSheet(
                f"font-size: 9pt; font-weight: bold; color: {accent}; border: none; "
                f"border-bottom: 1px solid #eee; padding-bottom: 2px;"
            )
            container_layout.addWidget(section_lbl)

            for key, desc in items:
                row = QHBoxLayout()
                row.setContentsMargins(4, 0, 4, 0)

                key_lbl = QLabel(key)
                key_lbl.setFixedWidth(140)
                key_lbl.setStyleSheet(
                    "font-size: 9pt; font-weight: bold; color: #333; border: none; "
                    "background: #f0f0f0; border-radius: 4px; padding: 2px 6px;"
                )

                desc_lbl = QLabel(desc)
                desc_lbl.setStyleSheet("font-size: 9pt; color: #555; border: none;")

                row.addWidget(key_lbl)
                row.addWidget(desc_lbl)
                row.addStretch()
                container_layout.addLayout(row)

        container_layout.addStretch()
        scroll.setWidget(container)
        custom_vsb = VerticalScrollBar()
        custom_vsb.connect_to(scroll.verticalScrollBar())

        scroll_row = QHBoxLayout()
        scroll_row.setContentsMargins(0, 0, 0, 0)
        scroll_row.setSpacing(0)
        scroll_row.addWidget(scroll)
        scroll_row.addWidget(custom_vsb)
        layout.addLayout(scroll_row)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(34)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {accent}; color: white; border: none;
                font-weight: bold; border-radius: 6px; font-size: 11pt; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {darker}; }}
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(dialog.accept)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        dialog.exec()

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
            shape = self.drawing_area.shapes[idx]
            border_color = shape[3] if isinstance(shape[3], QColor) else QColor("#000000")
            # Save the pre-selection color so we can restore it on deselect
            if not hasattr(self, "_pre_selection_color") or self._pre_selection_color is None:
                self._pre_selection_color = QColor(self.current_shape_color)
            # Show the shape's border color in quick_prop (skip if transparent)
            if border_color.alpha() > 0:
                self.current_shape_color = QColor(border_color)
            # Update quick_prop icon and tool button border
            if hasattr(self, "quick_prop"):
                pixmap = QPixmap(os.path.join(_ASSETS_DIR, "paintprop1.png")).scaled(58, 58, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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

    def _restore_color_after_deselect(self):
        """Adopt the shape's border color as the new global color on deselect."""
        self._pre_selection_color = None
        # Keep current_shape_color as-is (shape's border color becomes the new global color)
        self.drawing_area.set_shape_color(self.current_shape_color)
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
                    pixmap = QPixmap(os.path.join(_ASSETS_DIR, "tool-colors-eraser.png"))
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
        self._snapshot_current_page()
        self._spaces[self._current_space_idx]["current_page"] = self._current_page_idx

        project_folder = os.path.dirname(file_path)
        config_folder  = os.path.join(project_folder, "config")
        os.makedirs(config_folder, exist_ok=True)

        def _ser_hist(entry):
            e = dict(entry)
            e["shape_data"] = _serialize_shape(entry["shape_data"])
            return e

        payload = {
            "version": 3,
            "current_space": self._current_space_idx,
            "current_shape_color": self.current_shape_color.name(),
            "spaces": [
                {
                    "name": sp["name"],
                    "current_page": sp["current_page"],
                    "pages": [_serialize_page_state(p) for p in sp["pages"]],
                }
                for sp in self._spaces
            ],
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        # Per-page shape histories grouped by space
        all_histories = [
            [[_ser_hist(e) for e in p["shape_history"]] for p in sp["pages"]]
            for sp in self._spaces
        ]
        with open(os.path.join(config_folder, "shape_history.json"), "w", encoding="utf-8") as f:
            json.dump({"version": 3, "spaces": all_histories}, f, indent=2)

        self.current_canvas_file = file_path

    def save_canvas(self):
        # Manual save with file dialog and LoadingOverlay
        if self.current_canvas_file:
            file_path = self.current_canvas_file
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Canvas", "", "LDS File UIMode (*.ldsu)"
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
        
        def _do_save():
            try:
                self._core_save_canvas(self.current_canvas_file)
                self.drawing_area.show_status_overlay("File saved", duration=2000)
            except Exception as e:
                self.custom_tooltip.show_tooltip(f"Save failed: {str(e)[:40]}", duration=3000)
                print(f"Save error: {e}")
            finally:
                if hasattr(self, '_loading_overlay') and self._loading_overlay:
                    self._loading_overlay.hide_overlay()
        QTimer.singleShot(5000, _do_save)
        
    def _do_open_canvas(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            da      = self.drawing_area
            version = payload.get("version", 1)

            if version >= 3:
                self._spaces = []
                for sp_data in payload.get("spaces", []):
                    pages = [_deserialize_page_state(pd, da.a4_size) for pd in sp_data["pages"]]
                    self._spaces.append({
                        "name": sp_data.get("name", "Space 1"),
                        "current_page": sp_data.get("current_page", 0),
                        "pages": pages,
                    })
                self._current_space_idx = payload.get("current_space", 0)
                self._current_page_idx  = self._spaces[self._current_space_idx]["current_page"]

            elif version >= 2:
                pages = [_deserialize_page_state(pd, da.a4_size) for pd in payload["pages"]]
                cp    = payload.get("current_page", 0)
                self._spaces = [{"name": "Space 1", "current_page": cp, "pages": pages}]
                self._current_space_idx = 0
                self._current_page_idx  = cp

            else:
                state = _deserialize_page_state({
                    "name":           "Page 1",
                    "shapes":         payload["shapes"],
                    "eraser_mask":    payload["eraser_mask"],
                    "eraser_strokes": payload["eraser_strokes"],
                    "scale_factor":   payload.get("scale_factor", 1.0),
                    "zoom_percent":   payload.get("zoom_percent", 0),
                    "pan_offset":     payload.get("pan_offset", [0, 0]),
                    "tool_sizes":     payload.get("tool_sizes", {}),
                }, da.a4_size)
                self._spaces = [{"name": "Space 1", "current_page": 0, "pages": [state]}]
                self._current_space_idx = 0
                self._current_page_idx  = 0

            # Load shape histories
            project_folder = os.path.dirname(file_path)
            history_path   = os.path.join(project_folder, "config", "shape_history.json")
            if os.path.exists(history_path):
                with open(history_path, "r", encoding="utf-8") as f:
                    hist_data = json.load(f)

                def _deser_hist(entries):
                    result = []
                    for entry in entries:
                        e = dict(entry)
                        e["shape_data"] = _deserialize_shape(entry["shape_data"])
                        result.append(e)
                    return result

                hist_ver = hist_data.get("version", 1) if isinstance(hist_data, dict) else 1
                if isinstance(hist_data, list):
                    self._spaces[0]["pages"][0]["shape_history"] = _deser_hist(hist_data)
                elif hist_ver >= 3:
                    for si, sp_hist in enumerate(hist_data.get("spaces", [])):
                        if si < len(self._spaces):
                            for pi, page_hist in enumerate(sp_hist):
                                if pi < len(self._spaces[si]["pages"]):
                                    self._spaces[si]["pages"][pi]["shape_history"] = _deser_hist(page_hist)
                else:
                    for i, page_hist in enumerate(hist_data.get("pages", [])):
                        if i < len(self._spaces[0]["pages"]):
                            self._spaces[0]["pages"][i]["shape_history"] = _deser_hist(page_hist)

            color_hex = payload.get("current_shape_color", "#000000")
            self.current_shape_color = QColor(color_hex)

            self._restore_page(self._current_page_idx)
            self.drawing_area.set_shape_color(self.current_shape_color)
            self._side_menu.set_accent_color(self.current_shape_color)

            self.current_canvas_file = file_path
            self._add_to_recent(file_path)
            self.drawing_area.undo_stack.clear()
            self.drawing_area.redo_stack.clear()
            self.drawing_area.update()
            self.refresh_history_list()
            self._sync_page_ui()

        except Exception as e:
            print(f"Error opening canvas: {e}")
            self.custom_tooltip.show_tooltip(f"Failed to open canvas: {str(e)[:40]}", duration=3000)
        finally:
            try:
                size_bytes = os.path.getsize(file_path)
            except OSError:
                size_bytes = 0
            delay_ms = int(size_bytes / 1000 + 5000)
            if hasattr(self, '_loading_overlay') and self._loading_overlay:
                QTimer.singleShot(delay_ms, self._loading_overlay.hide_overlay)

    def _auto_save_tick(self):
        # Called every 30 seconds to auto-save
        if hasattr(self, "current_canvas_file") and self.current_canvas_file:
            self._perform_auto_save()

    def _perform_auto_save(self):
        # Threaded auto-save: snapshot + lightweight serialize on main thread,
        # heavy PNG encoding + disk I/O on worker thread
        if self._auto_save_running:
            self._auto_save_queued = True
            return

        try:
            file_path = self.current_canvas_file
            self._snapshot_current_page()
            self._spaces[self._current_space_idx]["current_page"] = self._current_page_idx

            project_folder = os.path.dirname(file_path)
            config_folder = os.path.join(project_folder, "config")
            os.makedirs(config_folder, exist_ok=True)

            def _ser_hist(entry):
                e = dict(entry)
                e["shape_data"] = _serialize_shape_for_thread(entry["shape_data"])
                return e

            payload = {
                "version": 3,
                "current_space": self._current_space_idx,
                "current_shape_color": self.current_shape_color.name(),
                "spaces": [
                    {
                        "name": sp["name"],
                        "current_page": sp["current_page"],
                        "pages": [_serialize_page_state_for_thread(p) for p in sp["pages"]],
                    }
                    for sp in self._spaces
                ],
            }

            all_histories = [
                [[_ser_hist(e) for e in p["shape_history"]] for p in sp["pages"]]
                for sp in self._spaces
            ]

            self._auto_save_running = True
            self._request_auto_save.emit({
                "file_path": file_path,
                "config_folder": config_folder,
                "payload": payload,
                "histories": all_histories,
            })
        except Exception as e:
            self.drawing_area.show_status_overlay(f"Auto-save failed: {str(e)[:30]}", duration=3000)
            print(f"Auto-save error: {e}")

    def _on_auto_save_done(self):
        self._auto_save_running = False
        self.drawing_area.show_status_overlay("File auto saved", duration=2000)
        if self._auto_save_queued:
            self._auto_save_queued = False
            self._perform_auto_save()

    def _on_auto_save_error(self, msg):
        self._auto_save_running = False
        self.drawing_area.show_status_overlay(f"Auto-save failed: {msg[:30]}", duration=3000)
        print(f"Auto-save error: {msg}")
        if self._auto_save_queued:
            self._auto_save_queued = False
            self._perform_auto_save()
                           
    def open_canvas(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Canvas", "", "LDS File UIMode (*.ldsu)"
            )
        if not file_path:
            return

        if not hasattr(self, '_loading_overlay'):
            self._loading_overlay = LoadingOverlay(self)
        self._loading_overlay.setGeometry(self.rect())
        self._loading_overlay.show_with_text("Opening...")
        
        # Open immediately (do not delay opening itself)
        QTimer.singleShot(50, lambda: self._do_open_canvas(file_path))
            
    def create_file_checkpoint(self):
        if not self.current_canvas_file:
            self.custom_tooltip.show_tooltip("Save a file first before creating checkpoints.", duration=3000)
            return

        accent = self.current_shape_color.name()
        darker = self.current_shape_color.darker(120).name()

        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setModal(True)
        dialog.setFixedSize(320, 210)
        dialog.setStyleSheet("background: white; border-radius: 12px; border: 2px solid #222;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        drag_bar = DraggableBar(dialog)
        layout.addWidget(drag_bar)

        title = QLabel("Create Checkpoint")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)

        input_field = QLineEdit()
        input_field.setMaxLength(20)
        input_field.setPlaceholderText("e.g., First Draft")
        input_field.setFixedHeight(36)
        input_field.setStyleSheet(f"""
            QLineEdit {{
                font-size: 11pt; border: none;
                border-bottom: 2px solid #ddd; background: transparent; padding: 4px 6px;
            }}
            QLineEdit:focus {{ border-bottom: 2px solid {accent}; }}
        """)
        layout.addWidget(input_field)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        ok_btn = QPushButton("Create")
        ok_btn.setFixedHeight(34)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background: {accent}; color: white; border: none;
                font-weight: bold; border-radius: 6px; font-size: 11pt; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {darker}; }}
        """)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(34)
        cancel_btn.setStyleSheet("""
            QPushButton { border: none; color: #222; padding: 0 16px; border-radius: 6px; background: #f0f0f0; }
            QPushButton:hover { background: #ddd; }
        """)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        def on_create():
            name = input_field.text().strip()
            if not name:
                input_field.setStyleSheet("""
                    QLineEdit {
                        font-size: 11pt; border: none;
                        border-bottom: 2px solid #ff3300; background: transparent; padding: 4px 6px;
                    }
                """)
                input_field.setPlaceholderText("Name cannot be empty!")
                return
            dialog.accept()
            self._save_checkpoint(name)

        ok_btn.clicked.connect(on_create)
        cancel_btn.clicked.connect(dialog.reject)
        input_field.returnPressed.connect(on_create)
        dialog.exec()
    
        
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

    def _save_checkpoint(self, checkpoint_name):
        try:
            project_folder = os.path.dirname(self.current_canvas_file)
            history_dir = os.path.join(project_folder, "config", "history")
            os.makedirs(history_dir, exist_ok=True)

            # Find next checkpoint number
            existing = [f for f in os.listdir(history_dir) if f.startswith("checkpoint_") and f.endswith(".json")]
            next_num = len(existing) + 1
            checkpoint_id = f"checkpoint_{next_num}"

            json_path = os.path.join(history_dir, f"{checkpoint_id}.json")
            png_path = os.path.join(history_dir, f"{checkpoint_id}.png")
            meta_path = os.path.join(history_dir, f"{checkpoint_id}.meta")

            # Build canvas payload directly
            da = self.drawing_area
            shapes_data = [_serialize_shape(s) for s in da.shapes]
            eraser_mask_b64 = _serialize_pixmap(da.eraser_mask)
            strokes_data = [[_serialize_qpoint(p) for p in stroke] for stroke in da.eraser_strokes]

            self._snapshot_current_page()

            def _ser_hist(entry):
                e = dict(entry)
                e["shape_data"] = _serialize_shape(entry["shape_data"])
                return e

            self._spaces[self._current_space_idx]["current_page"] = self._current_page_idx
            payload = {
                "version": 3,
                "current_space": self._current_space_idx,
                "current_shape_color": self.current_shape_color.name(),
                "spaces": [
                    {
                        "name": sp["name"],
                        "current_page": sp["current_page"],
                        "pages": [_serialize_page_state(p) for p in sp["pages"]],
                    }
                    for sp in self._spaces
                ],
            }
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            # Save metadata + shape_history
            def _serialize_history_entry(entry):
                e = dict(entry)
                e["shape_data"] = _serialize_shape(entry["shape_data"])
                return e

            meta_data = {
                "name":          checkpoint_name,
                "timestamp":     datetime.now().isoformat(),
                "source_file":   os.path.basename(self.current_canvas_file),
                "space_histories": [
                    [[_ser_hist(e) for e in p["shape_history"]] for p in sp["pages"]]
                    for sp in self._spaces
                ],
            }
            
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta_data, f, indent=2)

            # Save thumbnail
            pixmap = self._capture_drawing_area_snapshot()
            if pixmap:
                pixmap.save(png_path, "PNG")

            self.refresh_history_list()
            self.custom_tooltip.show_tooltip(f"Checkpoint '{checkpoint_name}' saved", duration=2500)
        except Exception as e:
            self.custom_tooltip.show_tooltip(f"Checkpoint failed: {str(e)[:40]}", duration=3000)

    def _load_checkpoint(self, checkpoint_name):
        try:
            history_dir = os.path.join(os.path.dirname(self.current_canvas_file), "config", "history")
            json_path = os.path.join(history_dir, f"{checkpoint_name}.json")
            meta_path = os.path.join(history_dir, f"{checkpoint_name}.meta")

            if not os.path.exists(json_path):
                self.custom_tooltip.show_tooltip(f"Checkpoint file not found", duration=3000)
                return

            with open(json_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            da = self.drawing_area
            version = payload.get("version", 1)

            if version >= 3:
                self._spaces = []
                for sp_data in payload.get("spaces", []):
                    pages = [_deserialize_page_state(pd, da.a4_size) for pd in sp_data["pages"]]
                    self._spaces.append({
                        "name": sp_data.get("name", "Space 1"),
                        "current_page": sp_data.get("current_page", 0),
                        "pages": pages,
                    })
                self._current_space_idx = payload.get("current_space", 0)
                self._current_page_idx  = self._spaces[self._current_space_idx]["current_page"]
            elif version >= 2:
                pages = [_deserialize_page_state(pd, da.a4_size) for pd in payload["pages"]]
                cp    = payload.get("current_page", 0)
                self._spaces = [{"name": "Space 1", "current_page": cp, "pages": pages}]
                self._current_space_idx = 0
                self._current_page_idx  = cp
            else:
                state = _deserialize_page_state({
                    "name":           "Page 1",
                    "shapes":         payload["shapes"],
                    "eraser_mask":    payload["eraser_mask"],
                    "eraser_strokes": payload["eraser_strokes"],
                    "scale_factor":   payload.get("scale_factor", 1.0),
                    "zoom_percent":   payload.get("zoom_percent", 0),
                    "pan_offset":     payload.get("pan_offset", [0, 0]),
                    "tool_sizes":     payload.get("tool_sizes", {}),
                }, da.a4_size)
                self._spaces = [{"name": "Space 1", "current_page": 0, "pages": [state]}]
                self._current_space_idx = 0
                self._current_page_idx  = 0

            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                def _deser_hist(entries):
                    result = []
                    for entry in entries:
                        e = dict(entry)
                        e["shape_data"] = _deserialize_shape(entry["shape_data"])
                        result.append(e)
                    return result
                # v3 checkpoints use space_histories, older ones use page_histories
                if "space_histories" in meta:
                    for si, sp_hist in enumerate(meta["space_histories"]):
                        if si < len(self._spaces):
                            for pi, page_hist in enumerate(sp_hist):
                                if pi < len(self._spaces[si]["pages"]):
                                    self._spaces[si]["pages"][pi]["shape_history"] = _deser_hist(page_hist)
                else:
                    for i, page_hist in enumerate(meta.get("page_histories", [])):
                        if i < len(self._spaces[0]["pages"]):
                            self._spaces[0]["pages"][i]["shape_history"] = _deser_hist(page_hist)

            color_hex = payload.get("current_shape_color", "#000000")
            self.current_shape_color = QColor(color_hex)
            self._restore_page(self._current_page_idx)
            self.drawing_area.set_shape_color(self.current_shape_color)
            self._side_menu.set_accent_color(self.current_shape_color)
            da.undo_stack.clear()
            da.redo_stack.clear()
            da.update()
            self._sync_page_ui()
            self.custom_tooltip.show_tooltip(f"Checkpoint '{checkpoint_name}' loaded", duration=2500)
            
        except Exception as e:
            self.custom_tooltip.show_tooltip(f"Failed to load checkpoint: {str(e)[:40]}", duration=3000)

    def _delete_checkpoint(self, checkpoint_name):
        # Read display name from meta
        try:
            history_dir = os.path.join(os.path.dirname(self.current_canvas_file), "config", "history")
            meta_path = os.path.join(history_dir, f"{checkpoint_name}.meta")
            with open(meta_path, "r", encoding="utf-8") as f:
                display_name = json.load(f).get("name", checkpoint_name)
        except Exception:
            display_name = checkpoint_name

        accent = self.current_shape_color.name()

        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setModal(True)
        dialog.setFixedSize(320, 185)
        dialog.setStyleSheet("background: white; border-radius: 12px; border: 2px solid #222;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        drag_bar = DraggableBar(dialog)
        layout.addWidget(drag_bar)

        title = QLabel("Delete Checkpoint")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)

        msg = QLabel(f"Delete <b>{display_name}</b>?<br><span style='color:#888;font-size:9pt;'>This cannot be undone.</span>")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 10pt; color: #444; border: none;")
        layout.addWidget(msg)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        yes_btn = QPushButton("Delete")
        yes_btn.setFixedHeight(34)
        yes_btn.setStyleSheet(f"""
            QPushButton {{
                background: #cc2200; color: white; border: none;
                font-weight: bold; border-radius: 6px; font-size: 11pt; padding: 0 20px;
            }}
            QPushButton:hover {{ background: #aa1a00; }}
        """)
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        no_btn = QPushButton("Cancel")
        no_btn.setFixedHeight(34)
        no_btn.setStyleSheet("""
            QPushButton { border: none; color: #222; padding: 0 16px; border-radius: 6px; background: #f0f0f0; }
            QPushButton:hover { background: #ddd; }
        """)
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        yes_btn.clicked.connect(dialog.accept)
        no_btn.clicked.connect(dialog.reject)
        btn_row.addWidget(yes_btn)
        btn_row.addWidget(no_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            for ext in [".json", ".png", ".meta"]:
                path = os.path.join(history_dir, f"{checkpoint_name}{ext}")
                if os.path.exists(path):
                    os.remove(path)
            self.refresh_history_list()
            self.custom_tooltip.show_tooltip(f"Checkpoint '{display_name}' deleted", duration=2500)
        except Exception as e:
            self.custom_tooltip.show_tooltip(f"Delete failed: {str(e)[:40]}", duration=3000)
            
    def _confirm_and_load(self, checkpoint_name):
        accent = self.current_shape_color.name()
        darker = self.current_shape_color.darker(120).name()

        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setModal(True)
        dialog.setFixedSize(320, 185)
        dialog.setStyleSheet("background: white; border-radius: 12px; border: 2px solid #222;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        drag_bar = DraggableBar(dialog)
        layout.addWidget(drag_bar)

        title = QLabel("Load Checkpoint")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)

        msg = QLabel(f"Load <b>{checkpoint_name}</b>?<br><span style='color:#888;font-size:9pt;'>This will replace the current canvas.</span>")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 10pt; color: #444; border: none;")
        layout.addWidget(msg)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        yes_btn = QPushButton("Load")
        yes_btn.setFixedHeight(34)
        yes_btn.setStyleSheet(f"""
            QPushButton {{
                background: {accent}; color: white; border: none;
                font-weight: bold; border-radius: 6px; font-size: 11pt; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {darker}; }}
        """)
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        no_btn = QPushButton("Cancel")
        no_btn.setFixedHeight(34)
        no_btn.setStyleSheet("""
            QPushButton { border: none; color: #222; padding: 0 16px; border-radius: 6px; background: #f0f0f0; }
            QPushButton:hover { background: #ddd; }
        """)
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        yes_btn.clicked.connect(dialog.accept)
        no_btn.clicked.connect(dialog.reject)

        btn_row.addWidget(yes_btn)
        btn_row.addWidget(no_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_checkpoint(checkpoint_name)   
            
    def _show_checkpoint_preview(self, checkpoint_id, meta, png_path):
        existing = self._checkpoint_preview_dialogs.get(checkpoint_id)
        if existing is not None and existing.isVisible():
            existing.raise_()
            existing.activateWindow()
            return
    
        dlg = CheckpointPreviewDialog(
            self,
            checkpoint_id=checkpoint_id,
            meta=meta,
            png_path=png_path,
            on_rename=lambda name, cp=checkpoint_id: self._rename_checkpoint(cp, name),
            accent=self.current_shape_color.name(),
        )
        dlg.move(self.geometry().center() - dlg.rect().center())
        dlg.finished.connect(lambda _, cp=checkpoint_id: self._checkpoint_preview_dialogs.pop(cp, None))
        self._checkpoint_preview_dialogs[checkpoint_id] = dlg
        dlg.show()

    def _rename_checkpoint(self, checkpoint_id, new_name):
        try:
            history_dir = os.path.join(os.path.dirname(self.current_canvas_file), "config", "history")
            meta_path = os.path.join(history_dir, f"{checkpoint_id}.meta")
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta["name"] = new_name
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
            self.refresh_history_list()
        except Exception as e:
            self.custom_tooltip.show_tooltip(f"Rename failed: {str(e)[:40]}", duration=3000)       

    def refresh_history_list(self):
        if not self.current_canvas_file:
            return

        history_dir = os.path.join(os.path.dirname(self.current_canvas_file), "config", "history")
        accent = self.current_shape_color.name()

        while self._side_menu.checkpoint_list_layout.count() > 1:
            item = self._side_menu.checkpoint_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self._side_menu._checkpoint_filters.clear()
        if not os.path.exists(history_dir):
            return

        meta_files = sorted(
            [f for f in os.listdir(history_dir) if f.endswith(".meta")],
            key=lambda f: int(f.replace("checkpoint_", "").replace(".meta", "")) if f.replace("checkpoint_", "").replace(".meta", "").isdigit() else 0,
            reverse=True
        )
        if not meta_files:
            return

        for meta_file in meta_files:
            checkpoint_id = meta_file.replace(".meta", "")
            meta_path = os.path.join(history_dir, meta_file)
            png_path = os.path.join(history_dir, f"{checkpoint_id}.png")

            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                display_name = meta.get("name", checkpoint_id)
                timestamp = meta.get("timestamp", "")
            except Exception:
                display_name = checkpoint_id
                timestamp = ""

            item_widget = QWidget()
            item_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            item_widget.setStyleSheet("background: #f9f9f9; border-radius: 4px;")
            item_widget.setCursor(Qt.CursorShape.PointingHandCursor)
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(6, 6, 6, 6)
            item_layout.setSpacing(8)

            # Thumbnail
            thumb_label = QLabel()
            thumb_label.setFixedSize(64, 46)
            thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            thumb_label.setStyleSheet("border: none; background: #e0e0e0; border-radius: 2px;")
            if os.path.exists(png_path):
                pixmap = QPixmap(png_path)
                if not pixmap.isNull():
                    thumb_label.setPixmap(
                        pixmap.scaled(64, 46, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
                    )
            else:
                thumb_label.setText("?")
                thumb_label.setStyleSheet(
                    "border: none; background: #e0e0e0; color: #999; font-size: 9pt; border-radius: 2px;"
                )
            item_layout.addWidget(thumb_label)

            # Name + date
            info_layout = QVBoxLayout()
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(2)
            name_label = QLabel(display_name)
            name_label.setStyleSheet("border: none; background: transparent; font-size: 9pt; font-weight: bold;")
            date_label = QLabel(timestamp[:10])
            date_label.setStyleSheet("border: none; background: transparent; font-size: 8pt; color: #999;")
            info_layout.addWidget(name_label)
            info_layout.addWidget(date_label)
            item_layout.addLayout(info_layout)
            item_layout.addStretch()

            # Delete button only (no Load button)
            delete_btn = QPushButton("✕")
            delete_btn.setFixedSize(22, 22)
            delete_btn.setStyleSheet(f"""
                QPushButton {{ border: none; color: #aaa; font-size: 11pt; background: transparent; }}
                QPushButton:hover {{ color: #ff3300; }}
            """)
            delete_btn.clicked.connect(lambda checked, cp=checkpoint_id: self._delete_checkpoint(cp))
            item_layout.addWidget(delete_btn)

            f = _CheckpointItemFilter(
                item_widget, accent,
                lambda cp=checkpoint_id: self._confirm_and_load(cp),
                on_click=lambda cp=checkpoint_id, m=meta, pp=png_path: (
                    self.custom_tooltip.show_tooltip("Double-click to load", 1500),
                    self._show_checkpoint_preview(cp, m, pp)
                )
            )
            self._side_menu._checkpoint_filters.append(f)

            self._side_menu.checkpoint_list_layout.insertWidget(
                self._side_menu.checkpoint_list_layout.count() - 1, item_widget
            )
    
    def _load_recent_files(self):
        try:
            if _RECENT_FILES_PATH.exists():
                with open(_RECENT_FILES_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return [p for p in data if os.path.exists(p)]
        except Exception:
            pass
        return []

    def _save_recent_files(self):
        try:
            _RECENT_FILES_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(_RECENT_FILES_PATH, "w", encoding="utf-8") as f:
                json.dump(self._recent_files, f, indent=2)
        except Exception:
            pass
        
    def _add_to_recent(self, file_path):
        file_path = str(file_path)
        if file_path in self._recent_files:
            self._recent_files.remove(file_path)
        self._recent_files.insert(0, file_path)
        self._recent_files = self._recent_files[:5]
        self._save_recent_files()
        self._side_menu.refresh_recent_list(self._recent_files, on_open=self.open_canvas, tooltip_fn=self.custom_tooltip.show_tooltip)

    def _snapshot_current_page(self):
        da = self.drawing_area
        state = self._page_states[self._current_page_idx]

        def _copy_shapes(shapes):
            return [da._copy_single_shape(s) for s in shapes]

        def _copy_stack_entry(entry):
            shapes, eraser_mask, eraser_strokes = entry
            return (
                _copy_shapes(shapes),
                eraser_mask.copy(),
                [list(stroke) for stroke in eraser_strokes],
            )

        def _copy_history_entry(entry):
            e = dict(entry)
            e["shape_data"] = da._copy_single_shape(entry["shape_data"])
            return e

        state["shapes"]         = _copy_shapes(da.shapes)
        state["eraser_mask"]    = da.eraser_mask.copy()
        state["eraser_strokes"] = [list(stroke) for stroke in da.eraser_strokes]
        state["scale_factor"]   = da.scale_factor
        state["zoom_percent"]   = da.zoom_percent
        state["pan_offset"]     = QPoint(da.pan_offset)
        state["tool_sizes"]     = dict(da.tool_sizes)
        state["shape_history"]  = [_copy_history_entry(e) for e in da.shape_history]
        state["undo_stack"]     = [_copy_stack_entry(e) for e in da.undo_stack]
        state["redo_stack"]     = [_copy_stack_entry(e) for e in da.redo_stack]
        
        # Capture thumbnail for side-panel display
        snap = self._capture_drawing_area_snapshot()
        if snap:
            state["thumbnail"] = snap.scaled(
                120, 80,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

    def _restore_page(self, idx: int):
        da = self.drawing_area
        state = self._page_states[idx]

        def _copy_shapes(shapes):
            return [da._copy_single_shape(s) for s in shapes]

        def _copy_stack_entry(entry):
            shapes, eraser_mask, eraser_strokes = entry
            return (
                _copy_shapes(shapes),
                eraser_mask.copy(),
                [list(stroke) for stroke in eraser_strokes],
            )

        def _copy_history_entry(entry):
            e = dict(entry)
            e["shape_data"] = da._copy_single_shape(entry["shape_data"])
            return e

        da.shapes         = _copy_shapes(state["shapes"])
        da.eraser_mask    = state["eraser_mask"].copy()
        da.eraser_strokes = [list(stroke) for stroke in state["eraser_strokes"]]
        da.scale_factor   = state["scale_factor"]
        da.zoom_percent   = state["zoom_percent"]
        da.pan_offset     = QPoint(state["pan_offset"])
        da.tool_sizes     = dict(state["tool_sizes"])
        da.shape_history  = [_copy_history_entry(e) for e in state["shape_history"]]
        da.undo_stack     = [_copy_stack_entry(e) for e in state["undo_stack"]]
        da.redo_stack     = [_copy_stack_entry(e) for e in state["redo_stack"]]
        da.selected_shape_index = None
        da.preview_shape  = None
        da.preview_start  = None
        da.preview_end    = None
        da.clamp_pan_offset()
        da.update()

    def _add_space(self):
        space_num = len(self._spaces) + 1
        default_name = f"Space {space_num}"
        accent = self.current_shape_color.name()
        darker = self.current_shape_color.darker(120).name()

        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setModal(True)
        dialog.setFixedSize(320, 210)
        dialog.setStyleSheet("background: white; border-radius: 12px; border: 2px solid #222;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        drag_bar = DraggableBar(dialog)
        layout.addWidget(drag_bar)

        title = QLabel("New Space")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)

        input_field = QLineEdit(default_name)
        input_field.setMaxLength(20)
        input_field.selectAll()
        input_field.setFixedHeight(36)
        input_field.setStyleSheet(f"""
            QLineEdit {{
                font-size: 11pt; border: none;
                border-bottom: 2px solid #ddd; background: transparent; padding: 4px 6px;
            }}
            QLineEdit:focus {{ border-bottom: 2px solid {accent}; }}
        """)
        layout.addWidget(input_field)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        ok_btn = QPushButton("Create")
        ok_btn.setFixedHeight(34)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background: {accent}; color: white; border: none;
                font-weight: bold; border-radius: 6px; font-size: 11pt; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {darker}; }}
        """)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(34)
        cancel_btn.setStyleSheet("""
            QPushButton { border: none; color: #222; padding: 0 16px; border-radius: 6px; background: #f0f0f0; }
            QPushButton:hover { background: #ddd; }
        """)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        def on_create():
            name = input_field.text().strip()
            if not name:
                input_field.setStyleSheet("""
                    QLineEdit {
                        font-size: 11pt; border: none;
                        border-bottom: 2px solid #ff3300; background: transparent; padding: 4px 6px;
                    }
                """)
                input_field.setPlaceholderText("Name cannot be empty!")
                return
            dialog.accept()

        ok_btn.clicked.connect(on_create)
        cancel_btn.clicked.connect(dialog.reject)
        input_field.returnPressed.connect(on_create)

        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        space_name = input_field.text().strip()

        # Original _add_space logic continues here, using space_name instead of default_name
        self._snapshot_current_page()
        self._spaces[self._current_space_idx]["current_page"] = self._current_page_idx
        em = QPixmap(self.drawing_area.a4_size)
        em.fill(Qt.GlobalColor.transparent)
        self._spaces.append({
            "name": space_name,   # <-- user-provided name
            "current_page": 0,
            "pages": [{
                "name": "Page 1",
                "shapes": [],
                "eraser_mask": em,
                "eraser_strokes": [],
                "scale_factor": 1.0,
                "zoom_percent": 0,
                "pan_offset": QPoint(0, 0),
                "tool_sizes": dict(self.drawing_area.tool_last_sizes),
                "shape_history": [],
                "undo_stack": [],
                "redo_stack": [],
                "thumbnail": None,
                "created": datetime.now().strftime("%Y-%m-%d"),
            }]
        })
        self._current_space_idx = len(self._spaces) - 1
        self._current_page_idx  = 0
        self._restore_page(0)
        self._sync_page_ui()

    def _select_space(self, space_idx: int):
        # Switch to a different space, restoring its last active page.
        if space_idx == self._current_space_idx:
            return
        self._snapshot_current_page()
        self._spaces[self._current_space_idx]["current_page"] = self._current_page_idx
        self._current_space_idx = space_idx
        self._current_page_idx  = self._spaces[space_idx]["current_page"]
        self._restore_page(self._current_page_idx)
        self._sync_page_ui()

    def _add_page(self):
        # Add a new page to the current space and switch to it.
        self._snapshot_current_page()
        cur_pages = self._spaces[self._current_space_idx]["pages"]
        existing_nums = []
        for p in cur_pages:
            name = p.get("name", "")
            if name.startswith("Page ") and name[5:].isdigit():
                existing_nums.append(int(name[5:]))
        page_num = max(existing_nums, default=0) + 1
        em = QPixmap(self.drawing_area.a4_size)
        em.fill(Qt.GlobalColor.transparent)
        cur_pages.append({
            "name": f"Page {page_num}",
            "shapes": [],
            "eraser_mask": em,
            "eraser_strokes": [],
            "scale_factor": 1.0,
            "zoom_percent": 0,
            "pan_offset": QPoint(0, 0),
            "tool_sizes": dict(self.drawing_area.tool_last_sizes),
            "shape_history": [],
            "undo_stack": [],
            "redo_stack": [],
            "thumbnail": None,
            "created": datetime.now().strftime("%Y-%m-%d"),
        })
        self._current_page_idx = len(cur_pages) - 1
        self._restore_page(self._current_page_idx)
        self._sync_page_ui()

    def _select_page(self, page_idx: int):
        # Switch pages within the current space.
        if page_idx == self._current_page_idx:
            return
        self._snapshot_current_page()
        self._current_page_idx = page_idx
        self._restore_page(page_idx)
        self._sync_page_ui()

    def _select_page_in_space(self, space_idx: int, page_idx: int):
        # Select a specific page in a specific space (called from side-panel thumbnails).
        if space_idx != self._current_space_idx:
            self._select_space(space_idx)
        if page_idx != self._current_page_idx:
            self._select_page(page_idx)

    def _sync_page_ui(self):
        # Refresh thumbnail for the currently active page before rendering the panel.
        snap = self._capture_drawing_area_snapshot()
        if snap:
            self._page_states[self._current_page_idx]["thumbnail"] = snap.scaled(
                120, 80,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        # Push current space/page state to PageBar and side panel.
        cur_space  = self._spaces[self._current_space_idx]
        
        page_names = [p["name"] for p in cur_space["pages"]]
        self.page_bar.set_pages(page_names, self._current_page_idx)
        self._side_menu.refresh_spaces(
            self._spaces,
            self._current_space_idx,
            self._current_page_idx,
            on_space_selected=self._select_space,
            on_page_selected=self._select_page_in_space,
            on_delete_page=self._delete_page,
            on_rename_page=self._rename_page,
            tooltip_fn=self.custom_tooltip.show_tooltip,
            on_rename_space=self._rename_space,
            on_delete_space=self._delete_space,
        )
        
    def _delete_page(self, space_idx: int, page_idx: int):
        pages = self._spaces[space_idx]["pages"]
        if len(pages) <= 1:
            self.custom_tooltip.show_tooltip("Cannot delete the only page in a space", duration=2000)
            return

        page_name = pages[page_idx]["name"]
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setModal(True)
        dialog.setFixedSize(320, 185)
        dialog.setStyleSheet("background: white; border-radius: 12px; border: 2px solid #222;")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        drag_bar = DraggableBar(dialog)
        layout.addWidget(drag_bar)
        title = QLabel("Delete Page")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)
        msg = QLabel(f"Delete <b>{page_name}</b>?<br><span style='color:#888;font-size:9pt;'>This cannot be undone.</span>")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 10pt; color: #444; border: none;")
        layout.addWidget(msg)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        yes_btn = QPushButton("Delete")
        yes_btn.setFixedHeight(34)
        yes_btn.setStyleSheet("""
            QPushButton { background: #cc2200; color: white; border: none;
                font-weight: bold; border-radius: 6px; font-size: 11pt; padding: 0 20px; }
            QPushButton:hover { background: #aa1a00; }
        """)
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        no_btn = QPushButton("Cancel")
        no_btn.setFixedHeight(34)
        no_btn.setStyleSheet("""
            QPushButton { border: none; color: #222; padding: 0 16px; border-radius: 6px; background: #f0f0f0; }
            QPushButton:hover { background: #ddd; }
        """)
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        yes_btn.clicked.connect(dialog.accept)
        no_btn.clicked.connect(dialog.reject)
        btn_row.addWidget(yes_btn)
        btn_row.addWidget(no_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        if space_idx == self._current_space_idx:
            self._snapshot_current_page()
            del pages[page_idx]
            counter = 1
            for p in pages:
                name = p.get("name", "")
                if name.startswith("Page ") and name[5:].isdigit():
                    p["name"] = f"Page {counter}"
                    counter += 1
            if page_idx < self._current_page_idx:
                new_idx = self._current_page_idx - 1
            else:
                new_idx = min(self._current_page_idx, len(pages) - 1)
            self._current_page_idx = new_idx
            self._spaces[space_idx]["current_page"] = new_idx
            self._restore_page(new_idx)
        else:
            del pages[page_idx]
            counter = 1
            for p in pages:
                name = p.get("name", "")
                if name.startswith("Page ") and name[5:].isdigit():
                    p["name"] = f"Page {counter}"
                    counter += 1
            stored = self._spaces[space_idx]["current_page"]
            if stored >= len(pages):
                self._spaces[space_idx]["current_page"] = len(pages) - 1
        self._sync_page_ui()            

    def _rename_page(self, space_idx: int, page_idx: int):
        page = self._spaces[space_idx]["pages"][page_idx]
        current_name = page["name"]
        accent = self.current_shape_color.name()
        darker = self.current_shape_color.darker(120).name()

        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setModal(True)
        dialog.setFixedSize(320, 210)
        dialog.setStyleSheet("background: white; border-radius: 12px; border: 2px solid #222;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        drag_bar = DraggableBar(dialog)
        layout.addWidget(drag_bar)

        title = QLabel("Rename Page")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)

        input_field = QLineEdit(current_name)
        input_field.setMaxLength(10)
        input_field.selectAll()
        input_field.setFixedHeight(36)
        input_field.setStyleSheet(f"""
            QLineEdit {{
                font-size: 11pt; border: none;
                border-bottom: 2px solid #ddd; background: transparent; padding: 4px 6px;
            }}
            QLineEdit:focus {{ border-bottom: 2px solid {accent}; }}
        """)
        layout.addWidget(input_field)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        ok_btn = QPushButton("Rename")
        ok_btn.setFixedHeight(34)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background: {accent}; color: white; border: none;
                font-weight: bold; border-radius: 6px; font-size: 11pt; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {darker}; }}
        """)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(34)
        cancel_btn.setStyleSheet("""
            QPushButton { border: none; color: #222; padding: 0 16px; border-radius: 6px; background: #f0f0f0; }
            QPushButton:hover { background: #ddd; }
        """)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        def on_rename():
            name = input_field.text().strip()
            if not name:
                input_field.setStyleSheet("""
                    QLineEdit {
                        font-size: 11pt; border: none;
                        border-bottom: 2px solid #ff3300; background: transparent; padding: 4px 6px;
                    }
                """)
                input_field.setPlaceholderText("Name cannot be empty!")
                return
            dialog.accept()

        ok_btn.clicked.connect(on_rename)
        cancel_btn.clicked.connect(dialog.reject)
        input_field.returnPressed.connect(on_rename)

        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        page["name"] = input_field.text().strip()
        # Renumber remaining default-named pages
        pages = self._spaces[space_idx]["pages"]
        counter = 1
        for p in pages:
            name = p.get("name", "")
            if name.startswith("Page ") and name[5:].isdigit():
                p["name"] = f"Page {counter}"
                counter += 1
        self._sync_page_ui()       
        
    def _rename_space(self, space_idx: int):
        space = self._spaces[space_idx]
        current_name = space["name"]
        accent = self.current_shape_color.name()
        darker = self.current_shape_color.darker(120).name()

        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setModal(True)
        dialog.setFixedSize(320, 240)
        dialog.setStyleSheet("background: white; border-radius: 12px; border: 2px solid #222;")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        drag_bar = DraggableBar(dialog)
        layout.addWidget(drag_bar)

        title = QLabel("Space Options")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)

        input_field = QLineEdit(current_name)
        input_field.setMaxLength(20)
        input_field.selectAll()
        input_field.setFixedHeight(36)
        input_field.setStyleSheet(f"""
            QLineEdit {{
                font-size: 11pt; border: none;
                border-bottom: 2px solid #ddd; background: transparent; padding: 4px 6px;
            }}
            QLineEdit:focus {{ border-bottom: 2px solid {accent}; }}
        """)
        layout.addWidget(input_field)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        rename_btn = QPushButton("Rename")
        rename_btn.setFixedHeight(34)
        rename_btn.setStyleSheet(f"""
            QPushButton {{
                background: {accent}; color: white; border: none;
                font-weight: bold; border-radius: 6px; font-size: 11pt; padding: 0 16px;
            }}
            QPushButton:hover {{ background: {darker}; }}
        """)
        rename_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        delete_btn = QPushButton("Delete")
        delete_btn.setFixedHeight(34)
        delete_btn.setStyleSheet("""
            QPushButton { border: none; color: white; padding: 0 16px; border-radius: 6px;
                background: #cc2200; font-weight: bold; font-size: 11pt; }
            QPushButton:hover { background: #aa1a00; }
        """)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(34)
        cancel_btn.setStyleSheet("""
            QPushButton { border: none; color: #222; padding: 0 12px; border-radius: 6px; background: #f0f0f0; }
            QPushButton:hover { background: #ddd; }
        """)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        _result = [None]

        def on_rename():
            name = input_field.text().strip()
            if not name:
                input_field.setStyleSheet("""
                    QLineEdit {
                        font-size: 11pt; border: none;
                        border-bottom: 2px solid #ff3300; background: transparent; padding: 4px 6px;
                    }
                """)
                input_field.setPlaceholderText("Name cannot be empty!")
                return
            _result[0] = "rename"
            dialog.accept()

        def on_delete():
            _result[0] = "delete"
            dialog.accept()

        rename_btn.clicked.connect(on_rename)
        delete_btn.clicked.connect(on_delete)
        cancel_btn.clicked.connect(dialog.reject)
        input_field.returnPressed.connect(on_rename)

        btn_row.addWidget(rename_btn)
        btn_row.addWidget(delete_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        if _result[0] == "rename":
            space["name"] = input_field.text().strip()
            self._sync_page_ui()
        elif _result[0] == "delete":
            self._delete_space(space_idx)

    def _delete_space(self, space_idx: int):
        if len(self._spaces) <= 1:
            self.custom_tooltip.show_tooltip("Cannot delete the only space", duration=2000)
            return

        space_name = self._spaces[space_idx]["name"]
        page_count = len(self._spaces[space_idx]["pages"])
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dialog.setModal(True)
        dialog.setFixedSize(320, 185)
        dialog.setStyleSheet("background: white; border-radius: 12px; border: 2px solid #222;")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        drag_bar = DraggableBar(dialog)
        layout.addWidget(drag_bar)
        title = QLabel("Delete Space")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(title)
        msg = QLabel(f"Delete <b>{space_name}</b> and all {page_count} page(s)?<br><span style='color:#888;font-size:9pt;'>This cannot be undone.</span>")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 10pt; color: #444; border: none;")
        layout.addWidget(msg)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        yes_btn = QPushButton("Delete")
        yes_btn.setFixedHeight(34)
        yes_btn.setStyleSheet("""
            QPushButton { background: #cc2200; color: white; border: none;
                font-weight: bold; border-radius: 6px; font-size: 11pt; padding: 0 20px; }
            QPushButton:hover { background: #aa1a00; }
        """)
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        no_btn = QPushButton("Cancel")
        no_btn.setFixedHeight(34)
        no_btn.setStyleSheet("""
            QPushButton { border: none; color: #222; padding: 0 16px; border-radius: 6px; background: #f0f0f0; }
            QPushButton:hover { background: #ddd; }
        """)
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        yes_btn.clicked.connect(dialog.accept)
        no_btn.clicked.connect(dialog.reject)
        btn_row.addWidget(yes_btn)
        btn_row.addWidget(no_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._snapshot_current_page()
        del self._spaces[space_idx]
        if self._current_space_idx >= len(self._spaces):
            self._current_space_idx = len(self._spaces) - 1
        self._current_page_idx = self._spaces[self._current_space_idx]["current_page"]
        self._restore_page(self._current_page_idx)
        self._sync_page_ui()

class CheckpointPreviewDialog(QDialog):
    def __init__(self, parent=None, checkpoint_id=None, meta=None, png_path=None, on_rename=None, accent="#ff6600"):
        super().__init__(parent)
        self._checkpoint_id = checkpoint_id
        self._on_rename = on_rename
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(False)
        self.setFixedSize(320, 420)
        self.setStyleSheet("background: white; border-radius: 12px; border: 2px solid #222;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        self.draggable_bar = DraggableBar(self)
        layout.addWidget(self.draggable_bar)

        darker = QColor(accent).darker(120).name()
        # Editable title
        self._title_edit = QLineEdit(meta.get("name", checkpoint_id) if meta else (checkpoint_id or ""))
        self._title_edit.setMaxLength(20)
        self._title_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_edit.setStyleSheet(f"""
            QLineEdit {{
                font-size: 13pt; font-weight: bold; border: none;
                border-bottom: 2px solid #ddd; background: transparent; padding: 4px;
            }}
            QLineEdit:focus {{ border-bottom: 2px solid {accent}; }}
        """)
        layout.addWidget(self._title_edit)

        # Snapshot
        snap_label = QLabel()
        snap_label.setFixedSize(280, 175)
        snap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        snap_label.setStyleSheet("background: #f0f0f0; border-radius: 6px; border: 1px solid #ddd;")
        if png_path and os.path.exists(png_path):
            pixmap = QPixmap(png_path)
            if not pixmap.isNull():
                snap_label.setPixmap(
                    pixmap.scaled(280, 175, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
                )
        else:
            snap_label.setText("No snapshot")
            snap_label.setStyleSheet(
                "background: #f0f0f0; border-radius: 6px; border: 1px solid #ddd; color: #999; font-size: 9pt;"
            )
        layout.addWidget(snap_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Date
        timestamp = meta.get("timestamp", "") if meta else ""
        formatted_date = ""
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_date = dt.strftime(f"[%Y-%m-%d %H:%M:%S][UIMode] {checkpoint_id}")
            except Exception:
                formatted_date = timestamp[:16]
        date_label = QLabel(formatted_date)
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_label.setStyleSheet("color: #999; font-size: 9pt; border: none;")
        layout.addWidget(date_label)

        # Buttons
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setFixedHeight(32)
        save_btn.setStyleSheet(f"""
            QPushButton {{ border: none; color: #222; padding: 4px 18px; border-radius: 6px; background: #f0f0f0; }}
            QPushButton:hover {{ background: {accent}; color: white; }}
        """)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(32)
        close_btn.setStyleSheet("""
            QPushButton { border: none; color: #222; padding: 4px 18px; border-radius: 6px; background: #f0f0f0; }
            QPushButton:hover { background: #ddd; }
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        def on_save():
            new_name = self._title_edit.text().strip()
            if new_name and self._on_rename:
                self._on_rename(new_name)
            self.close()

        save_btn.clicked.connect(on_save)
        close_btn.clicked.connect(self.close)

        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(close_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)            
            
class _CheckpointItemFilter(QObject):
    def __init__(self, widget, accent_hex, on_dblclick, on_click=None):
        super().__init__(widget)
        self._widget = widget
        self._accent_hex = accent_hex
        self._on_dblclick = on_dblclick
        self._on_click = on_click
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.setInterval(220)
        self._click_timer.timeout.connect(self._fire_click)
        widget.installEventFilter(self)

    def update_accent(self, hex_color):
        self._accent_hex = hex_color

    def _fire_click(self):
        if self._on_click:
            self._on_click()

    def eventFilter(self, obj, a0):
        if obj is self._widget:
            t = a0.type()
            if t == QEvent.Type.Enter:
                c = QColor(self._accent_hex)
                self._widget.setStyleSheet(
                    f"background: rgba({c.red()},{c.green()},{c.blue()},40); border-radius: 4px;"
                )
            elif t == QEvent.Type.Leave:
                self._widget.setStyleSheet("background: #f9f9f9; border-radius: 4px;")
            elif t == QEvent.Type.MouseButtonRelease:
                if a0.button() == Qt.MouseButton.LeftButton and self._on_click:
                    self._click_timer.start()
            elif t == QEvent.Type.MouseButtonDblClick:
                self._click_timer.stop()
                self._on_dblclick()
                return True
        return False

class _SpaceHeaderFilter(QObject):
    # Click-timer + double-click handler for space header buttons (no hover override).
    def __init__(self, btn, on_click=None, on_dblclick=None):
        super().__init__(btn)
        self._btn = btn
        self._on_click = on_click
        self._on_dblclick = on_dblclick
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(220)
        self._timer.timeout.connect(self._fire_click)
        btn.installEventFilter(self)

    def _fire_click(self):
        if self._on_click:
            self._on_click()

    def eventFilter(self, obj, event):
        if obj is self._btn:
            t = event.type()
            if t == QEvent.Type.MouseButtonRelease:
                if event.button() == Qt.MouseButton.LeftButton and self._on_click:
                    self._timer.start()
            elif t == QEvent.Type.MouseButtonDblClick:
                self._timer.stop()
                if self._on_dblclick:
                    self._on_dblclick()
                return True
        return False       

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
