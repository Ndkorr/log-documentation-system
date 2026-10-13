"""Interactive command-line logger for existing LDS projects."""

from datetime import datetime
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shlex
import stat
import sys
import tempfile


DEFAULT_CATEGORIES = [
    {"id": "problem", "icon": "★", "category": "Problem", "background": "#fff4bf", "foreground": "#111111"},
    {"id": "bug", "icon": "▲", "category": "Bug", "background": "#ffd9d9", "foreground": "#111111"},
    {"id": "solution", "icon": "■", "category": "Solution", "background": "#d8f5df", "foreground": "#111111"},
    {"id": "changes", "icon": "◆", "category": "Changes", "background": "#d8f5df", "foreground": "#111111"},
    {"id": "details", "icon": "", "category": "Just Details", "background": "transparent", "foreground": "#111111"},
]
CATEGORY_STYLE_MARKER_PREFIX = "<!-- LDS_CAT_STYLE:"
CATEGORY_STYLE_MARKER_SUFFIX = " -->"
LOG_NUMBER_PATTERN = re.compile(r"#(\d+)\s*$")
SAFE_COLOR_PATTERN = re.compile(r"(?:#[0-9a-fA-F]{3,8}|[a-zA-Z]+)")


class PlainTextParser(HTMLParser):
    """Extract readable text from an LDS HTML log line."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in {"br", "p", "div"}:
            self.parts.append(" ")

    def get_text(self):
        return " ".join("".join(self.parts).split())


def plain_text(html_line):
    parser = PlainTextParser()
    parser.feed(html_line)
    return parser.get_text()


def project_log_files(project_dir):
    project_dir = Path(project_dir)
    if not (project_dir / "config").is_dir():
        return []
    return sorted(
        (
            path
            for path in project_dir.iterdir()
            if path.is_file() and path.suffix.lower() in {".ldsg", ".ldsd"}
        ),
        key=lambda path: (path.suffix.lower(), path.name.lower()),
    )


def discover_project(project_path):
    project_path = Path(project_path).expanduser().resolve()
    if not project_path.is_dir():
        raise ValueError(f"Project path is not a folder: {project_path}")
    if not (project_path / "config").is_dir():
        raise ValueError(f"Project config folder does not exist: {project_path / 'config'}")
    files = project_log_files(project_path)
    if not files:
        raise ValueError(f"No .ldsg or .ldsd log file found in {project_path}")
    return project_path, files


def load_categories(config_path):
    if not config_path.exists():
        return [dict(category) for category in DEFAULT_CATEGORIES]

    with config_path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        raise ValueError(f"Expected a JSON object in {config_path}")

    configured = config.get("editor_categories", config.get("editor_categories_default"))
    if configured is None:
        configured = []
    if not isinstance(configured, list):
        raise ValueError(f"'editor_categories' must be a list in {config_path}")

    categories = []
    seen_names = set()
    for item in configured:
        if not isinstance(item, dict):
            continue
        name = str(item.get("category", "")).strip()
        if not name or name in seen_names:
            continue
        seen_names.add(name)
        categories.append(
            {
                "id": str(item.get("id", "")).strip() or re.sub(r"\W+", "-", name.lower()).strip("-"),
                "icon": str(item.get("icon", "")).strip(),
                "category": name,
                "background": str(item.get("background", "transparent")),
                "foreground": str(item.get("foreground", "#111111")),
            }
        )

    for category in DEFAULT_CATEGORIES:
        if category["category"] not in seen_names:
            categories.append(dict(category))
    return categories


def categories_for_log(categories, log_path):
    if log_path.suffix.lower() == ".ldsd":
        return [c for c in categories if c["category"] in {"Just Details", "Bug"}]
    return [c for c in categories if c["category"] != "Solution"]


def _category_marker(log_line):
    start = log_line.find(CATEGORY_STYLE_MARKER_PREFIX)
    if start == -1:
        return {}
    end = log_line.find(CATEGORY_STYLE_MARKER_SUFFIX, start)
    if end == -1:
        return {}
    payload = log_line[start + len(CATEGORY_STYLE_MARKER_PREFIX):end]
    return {
        key.strip(): value.strip()
        for part in payload.split(";")
        if "=" in part
        for key, value in [part.split("=", 1)]
    }


def _load_counters(counters_path):
    if not counters_path.exists():
        return {}
    with counters_path.open(encoding="utf-8") as counters_file:
        data = json.load(counters_file)
    counters = {}
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("id"):
                try:
                    counters[str(item["id"])] = max(0, int(item.get("count", 0)))
                except (TypeError, ValueError):
                    continue
    elif isinstance(data, dict):
        for key, value in data.items():
            try:
                counters[str(key)] = max(0, int(value))
            except (TypeError, ValueError):
                continue
    else:
        raise ValueError(f"Expected a counter list or object in {counters_path}")
    return counters


def _category_count(log_lines, category, log_type):
    highest = 0
    icon = category["icon"]
    category_id = category["id"]
    for line in log_lines:
        marker = _category_marker(line)
        text = plain_text(line)
        match = LOG_NUMBER_PATTERN.search(text)
        if not match:
            continue
        if marker.get("id") == category_id:
            highest = max(highest, int(match.group(1)))
        elif icon and icon in text:
            highest = max(highest, int(match.group(1)))
        elif not marker and not icon and (
            f"[{log_type}]" in text and not any(c in text for c in "★▲◆■")
        ):
            highest = max(highest, int(match.group(1)))
    return highest


def make_log_entry(entry, category, log_type, number, user_name=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%SH")
    foreground = category["foreground"]
    background = category["background"]
    if not SAFE_COLOR_PATTERN.fullmatch(foreground):
        foreground = "#111111"
    if not SAFE_COLOR_PATTERN.fullmatch(background):
        background = "transparent"
    style_marker = (
        f"{CATEGORY_STYLE_MARKER_PREFIX}id={category['id']};"
        f"bg={background};fg={foreground}{CATEGORY_STYLE_MARKER_SUFFIX}"
    )
    extra = f" - User: {user_name}" if log_type == "General" and user_name else ""
    return (
        f'{style_marker}<span style="color:{escape(foreground, quote=True)};">'
        f'{escape(category["icon"])}</span> '
        f'<span style="color:{escape(foreground, quote=True)};">'
        f'[{timestamp}] [{log_type}] {escape(entry).replace(chr(10), "<br>")}'
        f'{escape(extra)} #{number}</span>'
    )


def _atomic_write(path, text):
    path = Path(path)
    try:
        existing_mode = stat.S_IMODE(path.stat().st_mode)
    except FileNotFoundError:
        existing_mode = None
    fd, temporary_path = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as output:
            if existing_mode is not None:
                os.chmod(temporary_path, existing_mode)
            output.write(text)
        os.replace(temporary_path, path)
    except Exception:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise


class LDSCommandLine:
    def __init__(self, log_path, categories, all_categories=None):
        self.log_path = Path(log_path)
        self.categories = categories
        self.all_categories = all_categories if all_categories is not None else categories
        with self.log_path.open(encoding="utf-8") as log_file:
            self.log_lines = [line.rstrip("\r\n") for line in log_file if line.strip()]
        config_path = self.log_path.parent / "config" / "user_config.json"
        config = {}
        if config_path.exists():
            with config_path.open(encoding="utf-8") as config_file:
                config = json.load(config_file)
        self.user_name = str(config.get("user_name", "")) if isinstance(config, dict) else ""
        self.counters_path = self.log_path.parent / "config" / "counters.json"
        self.counters = _load_counters(self.counters_path)
        self.dirty = False
        self.log_type = "Debugging" if self.log_path.suffix.lower() == ".ldsd" else "General"
        self.last_category = None

    def add(self, entry, category_name=None):
        if category_name is None:
            if self.last_category is None:
                raise ValueError(
                    'Choose a category on the first add: add "<entry>" "<category>".'
                )
            category = self.last_category
        else:
            category = next(
                (
                    item
                    for item in self.categories
                    if item["category"].casefold() == category_name.casefold()
                ),
                None,
            )
        if category is None:
            raise ValueError(f"Unknown category '{category_name}'. Use :categories to list categories.")
        self.last_category = category
        count = max(
            self.counters.get(category["id"], 0),
            _category_count(self.log_lines, category, self.log_type),
        ) + 1
        self.counters[category["id"]] = count
        self.log_lines.append(
            make_log_entry(entry, category, self.log_type, count, self.user_name)
        )
        self.dirty = True
        print(f"Added {category['category']} entry #{count} (not saved).")

    def save(self):
        if not self.dirty:
            print("No unsaved changes.")
            return
        if not self.log_path.is_file():
            raise FileNotFoundError(f"Existing LDS log file is missing: {self.log_path}")
        _atomic_write(self.log_path, "".join(line + "\n" for line in self.log_lines))
        ordered_counters = [
            {
                "id": category["id"],
                "category": category["category"],
                "icon": category["icon"],
                "count": self.counters.get(category["id"], 0),
            }
            for category in self.all_categories
        ]
        _atomic_write(self.counters_path, json.dumps(ordered_counters, indent=4) + "\n")
        self.dirty = False
        print(f"Saved {len(self.log_lines)} entries to {self.log_path}.")

    def print_logs(self, entries):
        if not entries:
            print("No matching log entries.")
            return
        for index, entry in enumerate(entries, start=1):
            print(f"{index}. {plain_text(entry)}")

    def _log_matches_category(self, log_line, category):
        marker = _category_marker(log_line)
        if marker.get("id"):
            return marker["id"] == category["id"]
        if category["icon"]:
            return category["icon"] in plain_text(log_line)
        text = plain_text(log_line)
        return (
            category["category"] == "Just Details"
            and f"[{self.log_type}]" in text
            and not any(icon in text for icon in "★▲◆■")
        )

    def run(self):
        print(f"Using existing {self.log_path}")
        print('Commands: add "<entry>" ["<category>"], :all, :filter "<category>", :find "<text>", :categories, :save, :help, :quit')
        while True:
            try:
                command = input("lds> ").strip()
            except EOFError:
                command = ":quit"
            if not command:
                continue
            try:
                self.handle_command(command)
            except (ValueError, OSError, json.JSONDecodeError) as error:
                print(f"Error: {error}", file=sys.stderr)
            if command.split(maxsplit=1)[0].casefold() == ":quit":
                return

    def handle_command(self, command):
        parts = shlex.split(command)
        if not parts:
            return
        action = parts[0].casefold()
        if action == ":all":
            self.print_logs(self.log_lines)
        elif action == ":filter":
            if len(parts) != 2:
                raise ValueError('Usage: :filter "<category>"')
            category = next(
                (
                    item
                    for item in self.categories
                    if item["category"].casefold() == parts[1].casefold()
                ),
                None,
            )
            if category is None:
                raise ValueError(f"Unknown category '{parts[1]}'. Use :categories to list categories.")
            self.print_logs(
                [line for line in self.log_lines if self._log_matches_category(line, category)]
            )
        elif action == ":find":
            term = " ".join(parts[1:]).strip()
            if not term:
                raise ValueError('Usage: :find "<text>"')
            self.print_logs(
                [line for line in self.log_lines if term.casefold() in plain_text(line).casefold()]
            )
        elif action == ":categories":
            for category in self.categories:
                label = f" {category['icon']}" if category["icon"] else ""
                print(f"{category['category']}{label}")
        elif action == ":save":
            self.save()
        elif action == ":help":
            print('add "<entry>" ["<category>"]  Add using the previous category by default.')
            print('Example: add "Reviewed release notes" "Just Details"')
            print('         add "Another entry"')
            print(":all                    Print all entries.")
            print(':filter "<category>"    Print entries in that category.')
            print(':find "<text>"          Search entry text.')
            print(":categories             List available categories.")
            print(":save                   Save to the existing LDS file.")
            print(":quit                   Exit; choose whether to save unsaved entries.")
        elif action == ":quit":
            if self.dirty:
                try:
                    answer = input("Save unsaved changes before exiting? [y/N] ").strip().casefold()
                except EOFError:
                    answer = ""
                if answer in {"y", "yes"}:
                    self.save()
        elif action == "add":
            if len(parts) not in {2, 3}:
                raise ValueError('Usage: add "<entry>" ["<category>"]')
            entry = parts[1].strip()
            if not entry:
                raise ValueError("Log entry cannot be empty.")
            self.add(entry, parts[2] if len(parts) == 3 else None)
        else:
            raise ValueError("Unknown command. Enter :help to see available commands.")


def main():
    try:
        project_path = input("Enter LDS project folder path: ").strip()
        if len(project_path) >= 2 and project_path[0] == project_path[-1] and project_path[0] in {"'", '"'}:
            project_path = project_path[1:-1]
        if not project_path:
            raise ValueError("Project folder path cannot be empty.")
        project_dir, files = discover_project(project_path)
        if len(files) > 1:
            print("Select the log to open:")
            for index, path in enumerate(files, start=1):
                print(f"{index}. {path.name}")
            selection = input("Choice: ").strip()
            if not selection.isdigit() or not 1 <= int(selection) <= len(files):
                raise ValueError("Invalid log selection.")
            log_path = files[int(selection) - 1]
        else:
            log_path = files[0]

        config_path = project_dir / "config" / "user_config.json"
        all_categories = load_categories(config_path)
        categories = categories_for_log(all_categories, log_path)
        LDSCommandLine(log_path, categories, all_categories).run()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
