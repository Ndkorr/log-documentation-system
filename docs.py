import os
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QFontMetrics


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
            {"version": "1.0.31", "date": "June, 11, 2026", "features": ["Format images saved on dictonary to use UTC format", "Rearrange recent files correctly on nav pane"]},
            {"version": "1.0.30", "date": "May 29, 2026", "features": ["Added clipboard support for editing keywords on dictionary"]},
            {"version": "1.0.29", "date": "May 22, 2026", "features": ["Documentation window | changelog - module - idea", "Modified dictionary to support multiple image", "Allows import/export of dictionary/ldsdict"]},
            {"version": "1.0.28", "date": "May 09, 2026", "features": ["Category Edit", "Preferences", "Log Importance", "arrow keys and mouse wheel to scroll horizontally"]},
            {"version": "1.0.27", "date": "May 01, 2026", "features": ["Added editor's background which will edit main window"]},
            {"version": "1.0.26", "date": "April 25, 2026", "features": ["Modified ldsg and ldsd main.py", "added view logs window"]},
            {"version": "1.0.25", "date": "April 17, 2026", "features": ["Added description tool", "Settings UI but not currently working"]},
            {"version": "1.0.24", "date": "April 02, 2026", "features": ["Furhter improve label tool", "Hotkeys and wire it on hotkeys window", "Sync quick prop color on border color", "Changes the default color(background) of shapes to transparent", "Custom Cursor", "Added arrow tool", "Multi select and group",
                                                                         "Supports copy and duplicate on grouped objects", "MarqueTool on select tool"]},
            {"version": "1.0.23", "date": "March 28, 2026", "features": ["Side panel complete ui and function", "Spaces and Pages", "Added a page bar that'll automatically open once hover (really good implementation)", "Spaces contains pages", "Added qthread for background processing of saving", "Supports page renaming",
                                                                         "Duplicate are now spammable", "Added arrowkeys movement to drag selected objects", "Snap to grid", "Hold shift while resizing to maintain aspect ratio", "Wire save file on statusoverlay", "Added Label tool"]},
            {"version": "1.0.22", "date": "March 17, 2026", "features": ["Animation on saving and opening files"]},
            {"version": "1.0.21", "date": "March 14, 2026", "features": ["Improved undo/redo system", "restore points implementation", "save/auto save feature", "working on hamburger icon(side panel)"]},
            {"version": "1.0.20", "date": "March 09, 2026", "features": ["Added lock feature under context menu which will lock object to prevent interactions"]},
            {"version": "1.0.19", "date": "March 01, 2026", "features": ["Custom color added on properties", "Idea to add a restore points under properties"]},
            {"version": "1.0.18", "date": "February 24, 2026", "features": ["Border radius option is now only available on rect and rounded rect", "Border color and Border weight fixed bug not working"]},
            {"version": "1.0.17", "date": "January 17, 2026", "features": ["Hamburger icon/side panel on welcome screen which displays all recent opened lds files", "Make the properties only available on shapes"]},
            {"version": "1.0.16", "date": "January 14, 2026", "features": ["Been back from christmas and new year holidays", "Crisis happens deleted all python files but thankfully recovered it using git restore"]},
            {"version": "1.0.15", "date": "December 17, 2025", "features": ["Been busy on another project cake kiosk", "Update the github to add github actions (CI/CD)", "Remove unneccessary files and folders to make the project more clean"]},
            {"version": "1.0.14", "date": "October 26, 2025", "features": ["erase tool now actually erase the object instead of putting a white color on it"]},
            {"version": "1.0.13", "date": "October 23, 2025", "features": ["Resize window for eraser and draw tool"]},
            {"version": "1.0.12", "date": "August 16, 2025", "features": ["Fix quick prop lock color during preview edit", "Readjust crop tool"]},
            {"version": "1.0.11", "date": "August 05, 2025", "features": ["Rotate 90 degrees only applicable on shapes. Rotate 90 Degrees now working after moving during preview mode. FIll color now works upon first filling. Copy can now copy shapes color and border"]},
            {"version": "1.0.10", "date": "July 21, 2025", "features": ["Properties on Context Menu", "Crop and Fill Tool", "Rotation degree info overlay when rotating"]},
            {"version": "1.0.9", "date": "May 24, 2025", "features": ["Draw and erase tool is now working", "Layers Overlay"]},
            {"version": "1.0.8", "date": "May 14, 2025", "features": ["Added shapelayer, hotkeys, arctool menu, improve deselection by mousepressevent and keypressevent, Allow copy and pasting screenshots, Added context menu that includes: Undo, Redo, Copy, Paste, Rotate, Rotate Freely and properties. Also improve more hotkeys."]},
            {"version": "1.0.7", "date": "April 24, 2025", "features": ["Early implementation of UIMode .ldsu"]},
            {"version": "1.0.6", "date": "April 22, 2025", "features": ["Project folder structure with config file and auto generated folders for logs, definitions, etc."]},
            {"version": "1.0.5", "date": "April 10, 2025", "features": ["Integration of welcome screen (setup.py)", "Divides debugging and general into two different .lds files: .ldsg and .ldsd",
                                                                        "Recent Opened Files", "Added a setup wizard to create a lds project"]},
            {"version": "1.0.4", "date": "March 30, 2025", "features": ["Dictionary where definition sits (user can now enter custom definitions)", "Also added an image field besides definition"]},
            {"version": "1.0.3", "date": "March 26, 2025", "features": ["Implementation of definition and counters", "Context menu", "Problem, Bug and Solution connections",
                                                                        "Version Control System", "Log Filter", "Wire the vcs to config file and auto create restore points with random hard coded names"]},
            {"version": "1.0.2", "date": "March 23, 2025", "features": ["Focuses on debugging like cpu and gpu temperature each log entry", "Exporting as pdf and html",
                                                                        "Customization (how exported document behave like line spacing etc.)", "Added auto save function",
                                                                        "Wire the customization to config file .json", "Added username", "Set focus on added logs"]},
            {"version": "1.0.1", "date": "March 19, 2025", "features": ["Divided main into debugging and general log documentation system", "Drag & Drop", "Hotkeys (ctrl + s to save) etc.",
                                                                        "Limited log categories (Solution, Bug, Problem)"]},
            {"version": "1.0.0", "date": "March 17, 2025", "features": ["Start uploading the initial project idea on github"]},
        ]
        
        # Scroll position for infinite scrolling effect
        self.scroll_offset = 0
        self.hovered_entry_index = None
        self.expanded_entry_index = None
        self.setMouseTracking(True)

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

    def _entry_text_rect(self, idx):
        """Return the text block rectangle for a changelog entry index."""
        entry_y_start = 100
        entry_height = 150
        circle_radius = 28
        text_width = 350
        text_offset = 15
        circle_x = self.width() // 2

        y = entry_y_start + (idx * entry_height) + self.scroll_offset
        is_right = idx % 2 == 0
        if is_right:
            text_x = circle_x + circle_radius + text_offset
        else:
            text_x = circle_x - circle_radius - 365

        return QRect(int(text_x), int(y - 8), text_width, 90)

    def _entry_at_pos(self, pos):
        """Find the hovered changelog entry by mouse position."""
        viewport_top = 80
        viewport_bottom = self.height() + 150
        entry_y_start = 100
        entry_height = 150

        for idx, _entry in enumerate(self.changelog_entries):
            y = entry_y_start + (idx * entry_height) + self.scroll_offset
            if y + entry_height < viewport_top or y > viewport_bottom:
                continue
            if self._entry_text_rect(idx).contains(pos):
                return idx
        return None

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

            # Draw hover background for the active entry text block
            if idx == self.hovered_entry_index:
                hover_rect = self._entry_text_rect(idx).adjusted(-10, -6, 10, 6)
                hover_fill = QColor(255, 255, 255)
                hover_fill.setAlpha(int(185 * self.content_opacity))
                hover_border = QColor(0, 0, 0)
                hover_border.setAlpha(int(60 * self.content_opacity))
                painter.setBrush(hover_fill)
                painter.setPen(QPen(hover_border, 1))
                painter.drawRoundedRect(hover_rect, 10, 10)

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

    def _compute_entry_layout(self):
        """Compute dynamic entry positions/heights for drawing and hit-testing."""
        entry_y_start = 100
        base_entry_height = 150
        circle_x = self.width() // 2
        circle_radius = 28
        text_width = 350
        text_offset = 15

        features_font = QFont("Arial", 9)
        features_metrics = QFontMetrics(features_font)
        current_y = entry_y_start + self.scroll_offset
        layout = []

        for idx, entry in enumerate(self.changelog_entries):
            is_right = idx % 2 == 0
            if is_right:
                text_x = circle_x + circle_radius + text_offset
                alignment = Qt.AlignmentFlag.AlignLeft
            else:
                text_x = circle_x - circle_radius - 365
                alignment = Qt.AlignmentFlag.AlignRight

            features_text = " | ".join(entry["features"])
            wrap_flags = int(alignment | Qt.TextFlag.TextWordWrap)
            measured_rect = features_metrics.boundingRect(QRect(text_x, 0, text_width, 3000), wrap_flags, features_text)
            full_features_height = max(35, measured_rect.height())

            is_expanded = idx == self.expanded_entry_index
            features_height = full_features_height if is_expanded else 35
            text_rect = QRect(int(text_x), int(current_y - 8), text_width, int(49 + features_height))
            hover_rect = text_rect.adjusted(-10, -6, 10, 6)
            row_height = max(base_entry_height, int(65 + features_height))

            layout.append({
                "idx": idx,
                "entry": entry,
                "y": current_y,
                "row_height": row_height,
                "circle_x": circle_x,
                "circle_radius": circle_radius,
                "circle_center_y": current_y + circle_radius,
                "text_x": text_x,
                "text_width": text_width,
                "alignment": alignment,
                "features_text": features_text,
                "features_height": features_height,
                "hover_rect": hover_rect,
            })

            current_y += row_height

        return layout

    def _entry_text_rect(self, idx):
        """Return the text block rectangle for a changelog entry index."""
        for row in self._compute_entry_layout():
            if row["idx"] == idx:
                return row["hover_rect"]
        return QRect()

    def _entry_at_pos(self, pos):
        """Find the hovered/clicked changelog entry by mouse position."""
        viewport_top = 80
        viewport_bottom = self.height() + 150
        for row in self._compute_entry_layout():
            y = row["y"]
            row_bottom = y + row["row_height"]
            if row_bottom < viewport_top or y > viewport_bottom:
                continue
            if row["hover_rect"].contains(pos):
                return row["idx"]
        return None

    def _draw_changelog_entries(self, painter):
        # Draw all changelog entries with decorative circles and connecting line.
        layout = self._compute_entry_layout()

        viewport_top = 80
        viewport_bottom = self.height() + 150
        painter.setClipRect(0, viewport_top, self.width(), viewport_bottom - viewport_top)

        first_visible_y = None
        last_visible_y = None

        for row in layout:
            y = row["y"]
            row_bottom = y + row["row_height"]
            if row_bottom < viewport_top or y > viewport_bottom:
                continue
            if first_visible_y is None:
                first_visible_y = row["circle_center_y"]
            last_visible_y = row["circle_center_y"]

        if first_visible_y is not None and last_visible_y is not None:
            line_color = QColor(0, 0, 0)
            line_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(QPen(line_color, 2))
            circle_x = layout[0]["circle_x"] if layout else self.width() // 2
            painter.drawLine(circle_x, int(first_visible_y), circle_x, int(last_visible_y))

        for row in layout:
            idx = row["idx"]
            entry = row["entry"]
            y = row["y"]
            row_bottom = y + row["row_height"]
            if row_bottom < viewport_top or y > viewport_bottom:
                continue

            circle_color = QColor(0, 206, 209)
            circle_color.setAlpha(int(255 * self.content_opacity))
            painter.setBrush(circle_color)
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawEllipse(row["circle_x"] - row["circle_radius"], int(y), row["circle_radius"] * 2, row["circle_radius"] * 2)

            if idx == self.hovered_entry_index:
                hover_fill = QColor(255, 255, 255)
                hover_fill.setAlpha(int(185 * self.content_opacity))
                hover_border = QColor(0, 0, 0)
                hover_border.setAlpha(int(60 * self.content_opacity))
                painter.setBrush(hover_fill)
                painter.setPen(QPen(hover_border, 1))
                painter.drawRoundedRect(row["hover_rect"], 10, 10)

            version_color = QColor(0, 0, 0)
            version_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(version_color)
            painter.setFont(QFont("Inter SemiBold", 14, QFont.Weight.Bold))
            painter.drawText(row["text_x"], int(y - 5), row["text_width"], 20, row["alignment"], entry["version"])

            date_color = QColor(100, 100, 100)
            date_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(date_color)
            painter.setFont(QFont("Arial", 10))
            painter.drawText(row["text_x"], int(y + 20), row["text_width"], 15, row["alignment"], entry["date"])

            features_color = QColor(80, 80, 80)
            features_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(features_color)
            painter.setFont(QFont("Arial", 9))
            painter.drawText(row["text_x"], int(y + 35), row["text_width"], row["features_height"], row["alignment"] | Qt.TextFlag.TextWordWrap, row["features_text"])

        painter.setClipRect(self.rect())

    def wheelEvent(self, event):
        # Handle mouse wheel for scrolling
        delta = event.angleDelta().y()
        self.scroll_offset += delta // 6  # Smooth scrolling
        self.update()
        super().wheelEvent(event)

    def mouseMoveEvent(self, event):
        hovered_idx = self._entry_at_pos(event.position().toPoint())
        if hovered_idx != self.hovered_entry_index:
            self.hovered_entry_index = hovered_idx
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        if self.hovered_entry_index is not None:
            self.hovered_entry_index = None
            self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        # Handle back button click
        pos = event.position().toPoint()
        back_button_rect = QRect(10, 20, 80, 40)
        if back_button_rect.contains(pos):
            if self.is_animating_in and self.content_opacity > 0.5:
                self.animate_out()
                return

        clicked_idx = self._entry_at_pos(pos)
        if clicked_idx is not None:
            if self.expanded_entry_index == clicked_idx:
                self.expanded_entry_index = None
            else:
                self.expanded_entry_index = clicked_idx
            self.update()
            return
        super().mousePressEvent(event)

class ModulePage(QWidget):
    # Module page with left-side circles showing completion percentage and right-side descriptions
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
        
        # Module data structure with name, description, and percentage completion
        self.modules = [
            {"name": "docs.py", "description": "Document Page\nModified Module Page", "percentage": 75},
            {"name": "main.py", "description": "LDSD and LDSG\nFormat saved image to use UTC Format", "percentage": 60},
            {"name": "UIMode.py", "description": "LDSU - User Interface Design Mode", "percentage": 80},
            {"name": "setup.py", "description": "Welcome Page\nRearrange recent files on nav pane", "percentage": 90},
            {"name": "gui.py", "description": "Setup Wizard", "percentage": 40},
        ]
        
        # Scroll position and hover state
        self.scroll_offset = 0
        self.hovered_module_index = None
        self.setMouseTracking(True)

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

    def _module_at_pos(self, pos):
        """Find the hovered module by mouse position."""
        viewport_top = 100
        viewport_bottom = self.height()
        entry_y_start = 100
        entry_height = 140
        circle_x = 80
        circle_radius = 28
        text_width = 500
        text_offset = 15

        for idx, _module in enumerate(self.modules):
            y = entry_y_start + (idx * entry_height) + self.scroll_offset
            if y + entry_height < viewport_top or y > viewport_bottom:
                continue
            
            text_x = circle_x + circle_radius + text_offset
            text_rect = QRect(int(text_x), int(y - 8), text_width, 90)
            if text_rect.contains(pos):
                return idx
        return None

    def _draw_module_entries(self, painter):
        """Draw all module entries with circles, percentages, and descriptions."""
        entry_y_start = 100
        entry_height = 140
        circle_x = 80
        circle_radius = 28
        text_width = 500
        text_offset = 15

        viewport_top = 100
        viewport_bottom = self.height()
        
        painter.setClipRect(0, viewport_top, self.width(), viewport_bottom - viewport_top)

        first_visible_y = None
        last_visible_y = None

        for idx, module in enumerate(self.modules):
            y = entry_y_start + (idx * entry_height) + self.scroll_offset
            
            if y + entry_height < viewport_top or y > viewport_bottom:
                continue
            
            if first_visible_y is None:
                first_visible_y = y + circle_radius
            last_visible_y = y + circle_radius

        # Draw connecting vertical line
        if first_visible_y is not None and last_visible_y is not None and len(self.modules) > 1:
            line_color = QColor(0, 0, 0)
            line_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(QPen(line_color, 2))
            painter.drawLine(circle_x, int(first_visible_y), circle_x, int(last_visible_y))

        # Draw each module entry
        for idx, module in enumerate(self.modules):
            y = entry_y_start + (idx * entry_height) + self.scroll_offset
            
            if y + entry_height < viewport_top or y > viewport_bottom:
                continue
            
            # Draw circle with percentage inside
            circle_color = QColor(255, 255, 0)
            circle_color.setAlpha(int(255 * self.content_opacity))
            painter.setBrush(circle_color)
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawEllipse(int(circle_x - circle_radius), int(y), circle_radius * 2, circle_radius * 2)

            # Draw percentage text inside circle
            percentage_text = f"{module['percentage']}%"
            percentage_color = QColor(0, 0, 0)
            percentage_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(percentage_color)
            painter.setFont(QFont("Inter SemiBold", 11, QFont.Weight.Bold))
            circle_rect = QRect(int(circle_x - circle_radius), int(y), circle_radius * 2, circle_radius * 2)
            painter.drawText(circle_rect, Qt.AlignmentFlag.AlignCenter, percentage_text)

            # Draw hover background for text block
            text_x = circle_x + circle_radius + text_offset
            text_rect = QRect(int(text_x), int(y - 8), text_width, 90)
            
            if idx == self.hovered_module_index:
                hover_rect = text_rect.adjusted(-10, -6, 10, 6)
                hover_fill = QColor(255, 255, 255)
                hover_fill.setAlpha(int(185 * self.content_opacity))
                hover_border = QColor(0, 0, 0)
                hover_border.setAlpha(int(60 * self.content_opacity))
                painter.setBrush(hover_fill)
                painter.setPen(QPen(hover_border, 1))
                painter.drawRoundedRect(hover_rect, 10, 10)

            # Draw module name
            name_color = QColor(0, 0, 0)
            name_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(name_color)
            painter.setFont(QFont("Inter SemiBold", 12, QFont.Weight.Bold))
            painter.drawText(int(text_x), int(y - 5), text_width, 20, Qt.AlignmentFlag.AlignLeft, module["name"])

            # Draw module description
            description_color = QColor(80, 80, 80)
            description_color.setAlpha(int(255 * self.content_opacity))
            painter.setPen(description_color)
            painter.setFont(QFont("Arial", 10))
            painter.drawText(int(text_x), int(y + 20), text_width, 60, Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, module["description"])

        painter.setClipRect(self.rect())

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
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "Modules")
            
            # Draw module entries
            self._draw_module_entries(painter)
        
        painter.end()

    def wheelEvent(self, event):
        """Handle mouse wheel for scrolling."""
        delta = event.angleDelta().y()
        self.scroll_offset += delta // 6  # Smooth scrolling
        self.update()
        super().wheelEvent(event)

    def mouseMoveEvent(self, event):
        """Track hovered module."""
        hovered_idx = self._module_at_pos(event.position().toPoint())
        if hovered_idx != self.hovered_module_index:
            self.hovered_module_index = hovered_idx
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Clear hover state when leaving widget."""
        if self.hovered_module_index is not None:
            self.hovered_module_index = None
            self.update()
        super().leaveEvent(event)
        
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
