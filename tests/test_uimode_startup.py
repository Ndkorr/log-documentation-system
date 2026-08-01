import json
import tempfile
import unittest
from pathlib import Path

import UIMode


class UIModeStartupTests(unittest.TestCase):
    def test_resolve_startup_file_from_cli(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            config_dir = project_dir / "config"
            config_dir.mkdir()
            file_path = project_dir / "sample.ldsu"
            file_path.write_text(
                json.dumps({
                    "version": 1,
                    "spaces": [{
                        "name": "Space 1",
                        "current_page": 0,
                        "pages": [{
                            "name": "Page 1",
                            "shapes": [],
                            "eraser_mask": "",
                            "eraser_strokes": [],
                            "scale_factor": 1.0,
                            "zoom_percent": 0,
                            "pan_offset": [0, 0],
                            "tool_sizes": {},
                        }],
                    }],
                    "current_space": 0,
                }),
                encoding="utf-8",
            )
            (config_dir / "user_config.json").write_text(
                json.dumps({
                    "user_name": "Alice",
                    "pdf_title": "Project Title",
                    "pdf_font_size": 14,
                    "pdf_line_spacing": 1.8,
                    "pdf_font": "Verdana",
                    "custom_dictionary": "",
                }),
                encoding="utf-8",
            )

            resolved = UIMode._resolve_startup_file([str(file_path)])
            self.assertEqual(resolved, str(file_path))


if __name__ == "__main__":
    unittest.main()
