import os
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen


class DocumentationContent(QWidget):
    # Custom widget that draws title, separator, circles, lines, and hover boxes with animations
    changelog_clicked = pyqtSignal()
    modules_clicked = pyqtSignal()
    ideas_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.circle_radius = 32
        self.circle_size = self.circle_radius * 2

        # Button positions (x, y)
        self.circles = {
            "changelog": (240, 250, QColor(0, 206, 209), "Changelog"),
            "modules": (400, 250, QColor(255, 255, 0), "Modules"),
            "ideas": (560, 250, QColor(255, 105, 180), "Ideas"),
        }

        self.hovered_button = None
        self.animation_progress = {}  # Track animation progress for each button
        self.animation_duration = 300  # milliseconds
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.setMouseTracking(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        prev_hovered = self.hovered_button
        self.hovered_button = None
        if prev_hovered:
            self.animation_progress[prev_hovered] = 0
            self.animation_timer.start(16)  # ~60fps
        super().leaveEvent(event)
    
    def _update_animation(self):
        # Update animation progress and redraw
        all_done = True
        for button in self.circles.keys():
            if button not in self.animation_progress:
                self.animation_progress[button] = 0
            
            if button == self.hovered_button:
                # Animate IN
                if self.animation_progress[button] < 1.0:
                    self.animation_progress[button] += 16 / self.animation_duration
                    self.animation_progress[button] = min(self.animation_progress[button], 1.0)
                    all_done = False
            else:
                # Animate OUT
                if self.animation_progress[button] > 0.0:
                    self.animation_progress[button] -= 16 / self.animation_duration
                    self.animation_progress[button] = max(self.animation_progress[button], 0.0)
                    all_done = False
        
        self.update()
        
        if all_done:
            self.animation_timer.stop()

    def mouseMoveEvent(self, event):
        pos = event.position()
        prev_hovered = self.hovered_button
        self.hovered_button = None
    
        for key, (x, y, _, _) in self.circles.items():
            dx = pos.x() - x
            dy = pos.y() - y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= self.circle_radius:
                self.hovered_button = key
                break

        # Start animation if hover state changed
        if self.hovered_button != prev_hovered:
            if self.hovered_button not in self.animation_progress:
                self.animation_progress[self.hovered_button] = 0
            self.animation_timer.start(16)  # ~60fps
        
        self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if self.hovered_button == "changelog":
            self.changelog_clicked.emit()
        elif self.hovered_button == "modules":
            self.modules_clicked.emit()
        elif self.hovered_button == "ideas":
            self.ideas_clicked.emit()
        super().mousePressEvent(event)

    def _ease_out_cubic(self, t):
        # Ease-out cubic easing curve
        return 1 - (1 - t) ** 3

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw title
        title_rect = QRect(0, 50, self.width(), 50)
        painter.setFont(QFont("Inter SemiBold", 28, QFont.Weight.Bold))
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "Developed by mathewsa")

        # Draw connecting lines between circles
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        
        # Line from changelog to modules
        x1, y1 = 240 + self.circle_radius, 250
        x2, y2 = 400 - self.circle_radius, 250
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Line from modules to ideas
        x3, y3 = 400 + self.circle_radius, 250
        x4, y4 = 560 - self.circle_radius, 250
        painter.drawLine(int(x3), int(y3), int(x4), int(y4))

        # Draw circles and hover boxes
        for key, (x, y, color, label) in self.circles.items():
            progress = self.animation_progress.get(key, 0.0)
            
            # Apply easing curve
            eased_progress = self._ease_out_cubic(progress)
            
            # Calculate opacity for non-hovered buttons (fade to 50% when another is hovered)
            circle_opacity = 1.0
            if self.hovered_button and self.hovered_button != key:
                # Use the hovered button's progress to control opacity of non-hovered buttons
                hovered_progress = self.animation_progress.get(self.hovered_button, 0.0)
                eased_hovered_progress = self._ease_out_cubic(hovered_progress)
                # Fade from 1.0 (full) to 0.5 (dimmed) as hovered button animates in
                circle_opacity = 1.0 - (0.5 * eased_hovered_progress)
            
            # Draw hover box with animation
            if progress > 0.0:
                box_width = 160
                box_height = 180
                box_x = x - box_width // 2
                
                # Slide up animation: start from y+30, end at y-80
                slide_distance = 30
                box_y = y - self.circle_radius - 80 + (slide_distance * (1 - eased_progress))

                # Draw box background with fade
                box_color = QColor(245, 245, 245)
                box_color.setAlpha(int(255 * eased_progress))
                painter.setBrush(box_color)
                
                border_color = QColor(color)
                border_color.setAlpha(int(255 * eased_progress))
                painter.setPen(QPen(border_color, 2))
                painter.drawRoundedRect(int(box_x), int(box_y), box_width, box_height, 8, 8)

                # Draw label inside box (with fade)
                label_rect = QRect(int(box_x), int(box_y) + 30, box_width, 30)
                label_color = QColor(0, 0, 0)
                label_color.setAlpha(int(255 * eased_progress))
                painter.setPen(label_color)
                painter.setFont(QFont("Inter SemiBold", 10, QFont.Weight.Bold))
                painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, label)
        
            # Draw circle with opacity effect
            circle_color = QColor(color)
            circle_color.setAlpha(int(255 * circle_opacity))
            painter.setBrush(circle_color)
            
            circle_border = QColor(0, 0, 0)
            circle_border.setAlpha(int(255 * circle_opacity))
            painter.setPen(QPen(circle_border, 2))
            
            painter.drawEllipse(int(x - self.circle_radius), int(y - self.circle_radius),
                                self.circle_size, self.circle_size)

        painter.end()
        
class ChangelogPage(QWidget):
    # Changelog page with scrollable version timeline."""
    back_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.circle_color = QColor(0, 206, 209)
        self.circle_start_pos = (240, 250)
        self.circle_start_radius = 32
        
        # Animation
        self.animation_duration = 500
        self.animation_progress = 0.0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        
        self.content_opacity = 0.0
        self.is_animating_in = True
        
        # Changelog data structure
        # Add changelog entries here
        # Latest version should be first in the list for easier management
        self.changelog_entries = [
            {"version": "1.2.0", "date": "May 18, 2026", "features": ["Added search functionality", "Improved PDF export", "Bug fixes"]},
            {"version": "1.1.0", "date": "May 10, 2026", "features": ["Multi-log type support", "Custom naming"]},
            {"version": "1.0.0", "date": "May 1, 2026", "features": ["Core logging features", "PDF export", "Basic UI"]},
            {"version": "1.0.0", "date": "May 1, 2026", "features": ["Core logging features", "PDF export", "Basic UI"]},
        ]
        
        # Scroll position for infinite scrolling effect
        self.scroll_offset = 0

    def add_changelog_entry(self, version, date, features):
        """Add a new changelog entry. Use this to manage entries cleanly."""
        self.changelog_entries.insert(0, {
            "version": version,
            "date": date,
            "features": features
        })
        self.update()

    def showEvent(self, event):
        """Start animation when page becomes visible."""
        self.animation_progress = 0.0
        self.content_opacity = 0.0
        self.is_animating_in = True
        self.animation_timer.start(16)
        super().showEvent(event)

    def animate_out(self):
        """Start reverse animation."""
        self.is_animating_in = False
        self.animation_progress = 1.0
        self.animation_timer.start(16)

    def _ease_out_cubic(self, t):
        return 1 - (1 - t) ** 3

    def _update_animation(self):
        """Update animation progress."""
        if self.is_animating_in:
            if self.animation_progress < 1.0:
                self.animation_progress += 16 / self.animation_duration
                self.animation_progress = min(self.animation_progress, 1.0)
            else:
                if self.content_opacity < 1.0:
                    self.content_opacity += 16 / 300
                    self.content_opacity = min(self.content_opacity, 1.0)
                else:
                    self.animation_timer.stop()
        else:
            if self.animation_progress > 0.0:
                self.animation_progress -= 16 / self.animation_duration
                self.animation_progress = max(self.animation_progress, 0.0)
                self.content_opacity = self.animation_progress
            else:
                self.animation_timer.stop()
                self.back_clicked.emit()
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        eased_progress = self._ease_out_cubic(self.animation_progress)
        
        # Draw expanding circle (entrance animation)
        start_x, start_y = self.circle_start_pos
        start_radius = self.circle_start_radius
        max_radius = int((self.width() ** 2 + self.height() ** 2) ** 0.5 / 2) + 200
        current_radius = start_radius + (max_radius - start_radius) * eased_progress
        
        circle_opacity = 1.0 - (eased_progress * 0.4)
        circle_color = QColor(self.circle_color)
        circle_color.setAlpha(int(255 * circle_opacity))
        painter.setBrush(circle_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(start_x - current_radius), int(start_y - current_radius),
                            int(current_radius * 2), int(current_radius * 2))
        
        # Draw content (fades in/out)
        if self.content_opacity > 0.0:
            # Back button
            back_button_rect = QRect(10, 20, 80, 40)
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 22))
            painter.drawText(back_button_rect, Qt.AlignmentFlag.AlignCenter, "<")
            
            # Title
            title_color = QColor(0, 0, 0)
            title_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(title_color)
            painter.setFont(QFont("Inter SemiBold", 28, QFont.Weight.Bold))
            title_rect = QRect(0, 20, self.width(), 50)
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "Changelog")
            
            # Draw scrollable changelog entries
            self._draw_changelog_entries(painter)
        
        painter.end()

    def _draw_changelog_entries(self, painter):
        # Draw all changelog entries with decorative circles and connecting line."""
        entry_y_start = 100
        entry_height = 150  # Adjust this to control spacing between entries
        circle_x = self.width() // 2
        circle_radius = 28
        text_width = 350
        text_offset = 15  # Gap between circle and text

        # Define scrollable viewport (below "Changelog" title)
        viewport_top = 80
        viewport_bottom = self.height() + 150

        # Set clipping region for smooth scrolling
        painter.setClipRect(0, viewport_top, self.width(), viewport_bottom - viewport_top)

        # Find first and last visible entries to draw connecting line
        first_visible_y = None
        last_visible_y = None

        for idx, entry in enumerate(self.changelog_entries):
            y = entry_y_start + (idx * entry_height) + self.scroll_offset

            # Only process if potentially visible in viewport
            if y + entry_height < viewport_top or y > viewport_bottom:
                continue
            
            if first_visible_y is None:
                first_visible_y = y + circle_radius
            last_visible_y = y + circle_radius

        # Draw vertical connecting line
        if first_visible_y is not None and last_visible_y is not None:
            line_color = QColor(0, 0, 0)
            line_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(QPen(line_color, 2))
            painter.drawLine(circle_x, int(first_visible_y), circle_x, int(last_visible_y))

        # Draw entries
        for idx, entry in enumerate(self.changelog_entries):
            y = entry_y_start + (idx * entry_height) + self.scroll_offset

            if y + entry_height < viewport_top or y > viewport_bottom:
                continue
            
            # Determine if text goes on right or left (alternate)
            is_right = idx % 2 == 0

            if is_right:
                text_x = circle_x + circle_radius + text_offset
                alignment = Qt.AlignmentFlag.AlignLeft
            else:
                text_x = circle_x - circle_radius - 365
                alignment = Qt.AlignmentFlag.AlignRight

            # Draw decorative circle
            colors = QColor(0, 206, 209)
            circle_color = colors
            circle_color.setAlpha(int(255 * self.content_opacity))

            painter.setBrush(circle_color)
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawEllipse(circle_x - circle_radius, int(y), circle_radius * 2, circle_radius * 2)

            # Draw version
            version_color = QColor(0, 0, 0)
            version_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(version_color)
            painter.setFont(QFont("Inter SemiBold", 14, QFont.Weight.Bold))
            painter.drawText(text_x, int(y - 5), text_width, 20, alignment, entry["version"])

            # Draw date
            date_color = QColor(100, 100, 100)
            date_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(date_color)
            painter.setFont(QFont("Arial", 10))
            painter.drawText(text_x, int(y + 20), text_width, 15, alignment, entry["date"])

            # Draw features
            features_text = " • ".join(entry["features"])
            features_color = QColor(80, 80, 80)
            features_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(features_color)
            painter.setFont(QFont("Arial", 9))
            painter.drawText(text_x, int(y + 35), text_width, 35, alignment | Qt.TextFlag.TextWordWrap, features_text)

        painter.setClipRect(self.rect())

    def wheelEvent(self, event):
        # Handle mouse wheel for scrolling
        delta = event.angleDelta().y()
        self.scroll_offset += delta // 11  # Smooth scrolling
        self.update()
        super().wheelEvent(event)

    def mousePressEvent(self, event):
        # Handle back button click
        back_button_rect = QRect(10, 20, 80, 40)
        if back_button_rect.contains(event.position().toPoint()):
            if self.is_animating_in and self.content_opacity > 0.5:
                self.animate_out()
        super().mousePressEvent(event)

class ModulePage(QWidget):
    # Module page with expanding circle animation and reverse animation on back
    back_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.circle_color = QColor(255, 255, 0)
        self.circle_start_pos = (400, 250)  # Position from DocumentationDialog
        self.circle_start_radius = 32
        
        # Animation
        self.animation_duration = 500  # milliseconds
        self.animation_progress = 0.0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        
        # Content opacity (fades in after circle expands)
        self.content_opacity = 0.0
        
        # Direction: True = expanding in, False = contracting out
        self.is_animating_in = True

    def showEvent(self, event):
        # Start animation when page becomes visible
        self.animation_progress = 0.0
        self.content_opacity = 0.0
        self.is_animating_in = True
        self.animation_timer.start(16)
        super().showEvent(event)

    def animate_out(self):
        # Start reverse animation (circle contracts, content fades out).
        self.is_animating_in = False
        self.animation_progress = 1.0  # Start from fully expanded
        self.animation_timer.start(16)

    def _ease_out_cubic(self, t):
        # Ease-out cubic easing curve
        return 1 - (1 - t) ** 3

    def _update_animation(self):
        # Update animation progress (handles both in and out).
        if self.is_animating_in:
            # EXPANDING IN
            if self.animation_progress < 1.0:
                self.animation_progress += 16 / self.animation_duration
                self.animation_progress = min(self.animation_progress, 1.0)
            else:
                # Keep content fading in after circle is done
                if self.content_opacity < 1.0:
                    self.content_opacity += 16 / 300  # 300ms fade
                    self.content_opacity = min(self.content_opacity, 1.0)
                else:
                    self.animation_timer.stop()
        else:
            # CONTRACTING OUT (reverse)
            if self.animation_progress > 0.0:
                self.animation_progress -= 16 / self.animation_duration
                self.animation_progress = max(self.animation_progress, 0.0)
                # Fade content out as circle contracts
                self.content_opacity = self.animation_progress
            else:
                self.animation_timer.stop()
                # Animation complete, emit signal to switch pages
                self.back_clicked.emit()
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        eased_progress = self._ease_out_cubic(self.animation_progress)
        
        # Calculate expanding/contracting circle
        start_x, start_y = self.circle_start_pos
        start_radius = self.circle_start_radius
        
        # Maximum radius to cover screen
        max_radius = int((self.width() ** 2 + self.height() ** 2) ** 0.5 / 2) + 200
        
        # Interpolate radius
        current_radius = start_radius + (max_radius - start_radius) * eased_progress
        
        # Draw expanding/contracting circle
        circle_opacity = 1.0 - (eased_progress * 0.4)  # Fade slightly as it expands
        circle_color = QColor(self.circle_color)
        circle_color.setAlpha(int(255 * circle_opacity))
        painter.setBrush(circle_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(start_x - current_radius), int(start_y - current_radius),
                            int(current_radius * 2), int(current_radius * 2))
        
        # Draw content (fades in/out)
        if self.content_opacity > 0.0:
            # Back button
            back_button_rect = QRect(10, 20, 80, 40)
            painter.setBrush(QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(back_button_rect)
            
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 22))
            painter.drawText(back_button_rect, Qt.AlignmentFlag.AlignCenter, "<")
            
            # Title
            title_color = QColor(0, 0, 0)
            title_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(title_color)
            painter.setFont(QFont("Inter SemiBold", 28, QFont.Weight.Bold))
            title_rect = QRect(0, 25, self.width(), 50)
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "Module")
            
            # Placeholder content
            content_color = QColor(100, 100, 100)
            content_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(content_color)
            painter.setFont(QFont("Arial", 14))
            content_rect = QRect(50, 180, self.width() - 100, 200)
            painter.drawText(content_rect, Qt.TextFlag.TextWordWrap,
                           "v1.0.0 - Initial Release\n\n"
                           "• Added core logging features\n"
                           "• Support for multiple log types\n"
                           "• PDF export functionality")
        
        painter.end()
        
    def mousePressEvent(self, event):
        # Handle back button click - start reverse animation
        back_button_rect = QRect(10, 20, 80, 40)
        if back_button_rect.contains(event.position().toPoint()):
            # Only trigger if we're not already animating out
            if self.is_animating_in and self.content_opacity > 0.5:
                self.animate_out()
        super().mousePressEvent(event)
        
class IdeaPage(QWidget):
    # Module page with expanding circle animation and reverse animation on back
    back_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.circle_color = QColor(255, 105, 180)
        self.circle_start_pos = (560, 250)  # Position from DocumentationDialog
        self.circle_start_radius = 32
        
        # Animation
        self.animation_duration = 500  # milliseconds
        self.animation_progress = 0.0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        
        # Content opacity (fades in after circle expands)
        self.content_opacity = 0.0
        
        # Direction: True = expanding in, False = contracting out
        self.is_animating_in = True

    def showEvent(self, event):
        # Start animation when page becomes visible
        self.animation_progress = 0.0
        self.content_opacity = 0.0
        self.is_animating_in = True
        self.animation_timer.start(16)
        super().showEvent(event)

    def animate_out(self):
        # Start reverse animation (circle contracts, content fades out).
        self.is_animating_in = False
        self.animation_progress = 1.0  # Start from fully expanded
        self.animation_timer.start(16)

    def _ease_out_cubic(self, t):
        # Ease-out cubic easing curve
        return 1 - (1 - t) ** 3

    def _update_animation(self):
        # Update animation progress (handles both in and out).
        if self.is_animating_in:
            # EXPANDING IN
            if self.animation_progress < 1.0:
                self.animation_progress += 16 / self.animation_duration
                self.animation_progress = min(self.animation_progress, 1.0)
            else:
                # Keep content fading in after circle is done
                if self.content_opacity < 1.0:
                    self.content_opacity += 16 / 300  # 300ms fade
                    self.content_opacity = min(self.content_opacity, 1.0)
                else:
                    self.animation_timer.stop()
        else:
            # CONTRACTING OUT (reverse)
            if self.animation_progress > 0.0:
                self.animation_progress -= 16 / self.animation_duration
                self.animation_progress = max(self.animation_progress, 0.0)
                # Fade content out as circle contracts
                self.content_opacity = self.animation_progress
            else:
                self.animation_timer.stop()
                # Animation complete, emit signal to switch pages
                self.back_clicked.emit()
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        eased_progress = self._ease_out_cubic(self.animation_progress)
        
        # Calculate expanding/contracting circle
        start_x, start_y = self.circle_start_pos
        start_radius = self.circle_start_radius
        
        # Maximum radius to cover screen
        max_radius = int((self.width() ** 2 + self.height() ** 2) ** 0.5 / 2) + 200
        
        # Interpolate radius
        current_radius = start_radius + (max_radius - start_radius) * eased_progress
        
        # Draw expanding/contracting circle
        circle_opacity = 1.0 - (eased_progress * 0.4)  # Fade slightly as it expands
        circle_color = QColor(self.circle_color)
        circle_color.setAlpha(int(255 * circle_opacity))
        painter.setBrush(circle_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(start_x - current_radius), int(start_y - current_radius),
                            int(current_radius * 2), int(current_radius * 2))
        
        # Draw content (fades in/out)
        if self.content_opacity > 0.0:
            # Back button
            back_button_rect = QRect(10, 20, 80, 40)
            painter.setBrush(QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(back_button_rect)
            
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 22))
            painter.drawText(back_button_rect, Qt.AlignmentFlag.AlignCenter, "<")
            
            # Title
            title_color = QColor(0, 0, 0)
            title_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(title_color)
            painter.setFont(QFont("Inter SemiBold", 28, QFont.Weight.Bold))
            title_rect = QRect(0, 25, self.width(), 50)
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "Ideas")
            
            # Placeholder content
            content_color = QColor(100, 100, 100)
            content_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(content_color)
            painter.setFont(QFont("Arial", 14))
            content_rect = QRect(50, 180, self.width() - 100, 200)
            painter.drawText(content_rect, Qt.TextFlag.TextWordWrap,
                           "v1.0.0 - Initial Release\n\n"
                           "• Added core logging features\n"
                           "• Support for multiple log types\n"
                           "• PDF export functionality")
        
        painter.end()
        
    def mousePressEvent(self, event):
        # Handle back button click - start reverse animation
        back_button_rect = QRect(10, 20, 80, 40)
        if back_button_rect.contains(event.position().toPoint()):
            # Only trigger if we're not already animating out
            if self.is_animating_in and self.content_opacity > 0.5:
                self.animate_out()
        super().mousePressEvent(event)

class DocumentationDialog(QDialog):
    # Dialog with stacked pages for smooth transitions
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Documentations")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(800, 450)

        # Create stacked widget for page transitions
        self.stacked = QStackedWidget()
        
        # Page 0: Documentation content
        self.content = DocumentationContent()
        self.content.changelog_clicked.connect(self._show_changelog)
        self.content.modules_clicked.connect(self._show_module)
        self.content.ideas_clicked.connect(self._show_idea)
        self.stacked.addWidget(self.content)
        
        # Page 1: Changelog
        self.changelog_page = ChangelogPage()
        self.changelog_page.back_clicked.connect(self._show_content)
        self.stacked.addWidget(self.changelog_page)
        
        # Page 2: Module
        self.module_page = ModulePage()
        self.module_page.back_clicked.connect(self._show_content)
        self.stacked.addWidget(self.module_page)
        
        # Page 3: Ideas
        self.idea_page = IdeaPage()
        self.idea_page.back_clicked.connect(self._show_content)
        self.stacked.addWidget(self.idea_page)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stacked)
        
        self.stacked.setCurrentIndex(0)
        
    def _show_idea(self):
        # Transition to idea page
        self.stacked.setCurrentIndex(3)
    
    def _show_module(self):
        # Transition to module page
        self.stacked.setCurrentIndex(2)
        
    def _show_changelog(self):
        # Transition to changelog page
        self.stacked.setCurrentIndex(1)

    def _show_content(self):
        # Transition back to documentation content
        self.stacked.setCurrentIndex(0)