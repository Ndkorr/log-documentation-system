from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QSizePolicy, QApplication, QScrollArea, QStackedLayout,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QSize, QPropertyAnimation, QRect,
    QPoint, QEasingCurve, QTimer
    )
from PyQt6.QtGui import (
    QIcon, QPainter, QPen, QColor, QMouseEvent,
    QCursor
    )
import sys

class ToolButton(QPushButton):
    def __init__(self, text, tooltip, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setToolTip(tooltip)
        self.setCheckable(True)
        self.setFixedSize(44, 44)
        self.setStyleSheet("""
            border: none; 
            margin: 0; 
            font-size: 18pt;
            font-weight: bold; 
            background: white;
            color: black;
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class DrawingArea(QFrame):
    HANDLE_SIZE = 12
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #e5e5e5; border: none;")
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.current_tool = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        
        self.preview_shape = None
        self.preview_start = None
        self.preview_end = None
        
        self._dragging_handle = None
        self._dragging_box = False
        self._drag_offset = QPoint()
        self.shapes = []  # Store drawn shapes
        
        # --- Zoom state ---
        self.scale_factor = 1.0
        self.zoom_percent = 0  # Relative to 100%
        self.pan_offset = QPoint(0, 0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # To receive wheel events
        
        self.a4_size = QSize(1123, 794)

        # Overlay label for zoom info (hidden by default)
        self.zoom_overlay = QLabel(self)
        self.zoom_overlay.setStyleSheet("background: rgba(0,0,0,120); color: white; padding: 2px 8px; border-radius: 8px;")
        self.zoom_overlay.move(10, 10)
        self.zoom_overlay.resize(120, 28)
        self.zoom_overlay.hide()
        self._zoom_overlay_timer = QTimer(self)
        self._zoom_overlay_timer.setSingleShot(True)
        self._zoom_overlay_timer.timeout.connect(self.zoom_overlay.hide)
    
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
        self.zoom_overlay.setText(f"Zoom: {percent}%")
        self.zoom_overlay.show()
        self._zoom_overlay_timer.start(1200)  # Hide

    def set_tool(self, tool):
        self.current_tool = tool
        if tool:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mousePressEvent(self, event):
        if self.current_tool and event.button() == Qt.MouseButton.LeftButton:
            pt = self.widget_to_canvas(event.position().toPoint())
            if self.preview_start is not None and self.preview_end is not None:
                margin = 8
                rect = QRect(self.preview_start, self.preview_end).normalized()
                box_rect = rect.adjusted(-margin, -margin, margin, margin)
                for idx, handle in enumerate(self.handle_points(box_rect)):
                    if (handle - pt).manhattanLength() < self.HANDLE_SIZE:
                        self._dragging_handle = idx
                        self.set_resize_cursor(idx)
                        return
                # Check if inside box (for moving)
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
                else:
                    self.shapes.append((self.preview_shape, self.preview_start, self.preview_end))
                    self.preview_shape = None
                    self.preview_start = None
                    self.preview_end = None
                self.update()

    def mouseMoveEvent(self, event):
        pt = self.widget_to_canvas(event.position().toPoint())
        margin = 8
        if self._dragging_handle is not None:
            self.set_resize_cursor(self._dragging_handle)
            pt = self.widget_to_canvas(event.position().toPoint())
            # Get current rect
            rect = QRect(self.preview_start, self.preview_end)
            x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
            # Update according to handle index
            if self._dragging_handle == 0:  # Top-left
                self.preview_start = pt
                self.preview_end = QPoint(x2, y2)
            elif self._dragging_handle == 1:  # Top-middle
                self.preview_start = QPoint(x1, pt.y())
                self.preview_end = QPoint(x2, y2)
            elif self._dragging_handle == 2:  # Top-right
                self.preview_start = QPoint(x1, pt.y())
                self.preview_end = QPoint(pt.x(), y2)
            elif self._dragging_handle == 3:  # Right-middle
                self.preview_start = QPoint(x1, y1)
                self.preview_end = QPoint(pt.x(), y2)
            elif self._dragging_handle == 4:  # Bottom-right
                self.preview_start = QPoint(x1, y1)
                self.preview_end = pt
            elif self._dragging_handle == 5:  # Bottom-middle
                self.preview_start = QPoint(x1, y1)
                self.preview_end = QPoint(x2, pt.y())
            elif self._dragging_handle == 6:  # Bottom-left
                self.preview_start = QPoint(pt.x(), y1)
                self.preview_end = QPoint(x2, pt.y())
            elif self._dragging_handle == 7:  # Left-middle
                self.preview_start = QPoint(pt.x(), y1)
                self.preview_end = QPoint(x2, y2)
            self.update()
            return
        elif self._dragging_box:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            pt = self.widget_to_canvas(event.position().toPoint())
            margin = 8
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
            # Change cursor when hovering over handles or box
            if self.preview_start is not None and self.preview_end is not None:
                rect = QRect(self.preview_start, self.preview_end).normalized()
                box_rect = rect.adjusted(-margin, -margin, margin, margin)
                for idx, handle in enumerate(self.handle_points(box_rect)):
                    if (handle - pt).manhattanLength() < self.HANDLE_SIZE:
                        self.set_resize_cursor(idx)
                        break
                else:
                    if box_rect.contains(pt):
                        self.setCursor(Qt.CursorShape.OpenHandCursor)
                    elif self.current_tool:
                        self.setCursor(Qt.CursorShape.CrossCursor)
                    else:
                        self.setCursor(Qt.CursorShape.ArrowCursor)

        if self.preview_shape:
            pt = self.widget_to_canvas(event.position().toPoint())
            self.preview_end = pt
            self.update()

    def mouseReleaseEvent(self, event):
        self._dragging_handle = None
        self._dragging_box = False
        if self.current_tool:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
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

        # Draw shapes
        pen = QPen(QColor("#ff6600"), 3)
        painter.setPen(pen)
        for tool, start, end in self.shapes:
            self.draw_shape(painter, tool, start, end)
            
        # Draw the preview shape (solid orange) and bounding box (dashed blue)
        if self.preview_shape and self.preview_start is not None and self.preview_end is not None:
            margin = 8  # Margin in canvas coordinates
            rect = QRect(self.preview_start, self.preview_end).normalized()
            box_rect = rect.adjusted(-margin, -margin, margin, margin)

            # Draw bounding box and handles
            box_pen = QPen(QColor("#0078d7"), 2, Qt.PenStyle.DashLine)
            painter.setPen(box_pen)
            self.draw_bounding_box_and_handles(painter, box_rect)

            # Draw the preview shape with solid orange on top
            preview_pen = QPen(QColor("#ff6600"), 3)
            painter.setPen(preview_pen)
            self.draw_shape(painter, self.preview_shape, self.preview_start, self.preview_end)

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
            
    def handle_points(self, rect):
        x1, y1, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
        xm, ym = (x1 + x2)//2, (y1 + y2)//2
        return [
            QPoint(x1, y1), QPoint(xm, y1), QPoint(x2, y1),  # Top: left, mid, right
            QPoint(x2, ym),                                 # Right mid
            QPoint(x2, y2), QPoint(xm, y2), QPoint(x1, y2), # Bottom: right, mid, left
            QPoint(x1, ym),                                 # Left mid
        ][:8]  # Only 8 handles!
    

    def draw_shape(self, painter, tool, start, end):
        rect = QRect(start, end).normalized()
        if tool == "circle":
            painter.drawEllipse(rect)
        elif tool == "rect":
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
    
    
class UIMode(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Documentation System - Log Mode")
        self.setStyleSheet("font-family: Arial; font-size: 12pt;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.resize(1100, 700)
        self.init_ui()
        self._show_controls = False
        self.selected_tool = None
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
        ribbon_layout.setSpacing(44)
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
    
        
        # Create each tool button individually
        self.circle_btn = ToolButton("◯", "Circle")
        self.circle_btn.setStyleSheet("font-size: 28pt; color: #222; border: none; background: transparent; font-weight: bold;")
        self.rect_btn = ToolButton("▭", "Rectangle")
        self.rect_btn.setStyleSheet("font-size: 58pt; color: #222; border: none; background: transparent;")
        self.triangle_btn = ToolButton("△", "Triangle")
        self.triangle_btn.setStyleSheet("font-size: 30pt; color: #222; border: none; background: transparent;")
        self.line_btn = ToolButton("—", "Line")
        self.line_btn.setStyleSheet("font-size: 28pt; color: #222; border: none; background: transparent;")
        self.cross_btn = ToolButton("✕", "Cross")
        self.cross_btn.setStyleSheet("font-size: 28pt; color: #222; border: none; background: transparent;")

        # Add to layout
        ribbon_layout.addWidget(self.circle_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        ribbon_layout.addWidget(self.rect_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        ribbon_layout.addWidget(self.triangle_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        ribbon_layout.addWidget(self.line_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        ribbon_layout.addWidget(self.cross_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        ribbon_layout.addStretch()
        
        
        ribbon_layout.addStretch()
        #ribbon_layout.insertStretch(0, 1)  # Add stretch above and below for centering
        
        quick_prop = QLabel()
        quick_prop.setFixedSize(48, 48)
        quick_prop.setStyleSheet("background: #ff6600; border-radius: 24px; margin-top: 15px;")
        ribbon_layout.insertWidget(0, quick_prop, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        # Add a divider below the quick_prop with adjustable thickness
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("color: black; background: black; height: 3px; margin: 3px 0; margin-left: 15px; margin-right: 15px;")
        ribbon_layout.insertWidget(1, divider)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(ribbon_widget)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFixedWidth(80)
        scroll.setStyleSheet("background: white; border: none;")  # Blend scroll area too

        self.ribbon_shadow = QGraphicsDropShadowEffect(scroll)
        self.ribbon_shadow.setBlurRadius(24)
        self.ribbon_shadow.setOffset(0, 0)
        self.ribbon_shadow.setColor(Qt.GlobalColor.blue)
        scroll.setGraphicsEffect(None)  # No shadow by default
        
        # Drawing Area
        self.drawing_area = DrawingArea()

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

        # Hamburger menu (right)
        self.menu_btn = QPushButton("≡")
        self.menu_btn.setFixedSize(42, 42)
        self.menu_btn.setStyleSheet("background: none; border: none; font-size: 38pt; margin-right: 15px; margin-top: 15px;")
        top_bar_layout.addWidget(self.menu_btn)

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
        self.circle_btn.clicked.connect(lambda: self.select_tool("circle"))
        self.rect_btn.clicked.connect(lambda: self.select_tool("rect"))
        self.triangle_btn.clicked.connect(lambda: self.select_tool("triangle"))
        self.line_btn.clicked.connect(lambda: self.select_tool("line"))
        self.cross_btn.clicked.connect(lambda: self.select_tool("cross"))
        self.ribbon_widget = scroll  # Save for eventFilter

        # Layout assembly
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.top_bar)
        content_layout.addWidget(self.drawing_area)
        main_layout.addWidget(scroll)
        main_layout.addLayout(content_layout)

        # Tool button (bottom right, floating)
        self.tool_btn = QPushButton()
        self.tool_btn.setFixedSize(48, 48)
        self.tool_btn.setStyleSheet("border: 2px solid #ff6600; border-radius: 24px; background: none;")
        self.tool_btn.setParent(self)
        self.tool_btn.show()
    
    
    def select_tool(self, tool):
        self.selected_tool = tool
        # Uncheck all, then check the selected
        for btn in [self.circle_btn, self.rect_btn, self.triangle_btn, self.line_btn, self.cross_btn]:
            btn.setChecked(False)
        btn_map = {
            "circle": self.circle_btn,
            "rect": self.rect_btn,
            "triangle": self.triangle_btn,
            "line": self.line_btn,
            "cross": self.cross_btn,
        }
        btn_map[tool].setChecked(True)
        # Pass the tool to the drawing area
        self.drawing_area.set_tool(tool)    
        

    def eventFilter(self, obj, event):
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
                shadow.setColor(Qt.GlobalColor.blue)
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
        # Place the tool button at the bottom right
        btn_margin = 24
        self.tool_btn.move(self.width() - self.tool_btn.width() - btn_margin, self.height() - self.tool_btn.height() - btn_margin)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = UIMode()
    win.show()
    sys.exit(app.exec())