import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import lds_cli


class LDSCliTests(unittest.TestCase):
    def test_project_detection_requires_existing_config_and_log(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "config").mkdir()
            log_file = project / "notes.ldsg"
            log_file.write_text("", encoding="utf-8")

            found_project, files = lds_cli.discover_project(project)

            self.assertEqual(found_project, project.resolve())
            self.assertEqual(files, [log_file])

    def test_project_detection_rejects_log_file_path(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "config").mkdir()
            log_file = project / "notes.ldsd"
            log_file.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Project path is not a folder"):
                lds_cli.discover_project(log_file)

    def test_project_detection_requires_config_folder(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "notes.ldsg").write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Project config folder does not exist"):
                lds_cli.discover_project(project)

    def test_project_detection_requires_lds_log(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "config").mkdir()

            with self.assertRaisesRegex(ValueError, "No \\.ldsg or \\.ldsd log file"):
                lds_cli.discover_project(project)

    def test_main_prompts_for_project_folder_before_starting(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "config").mkdir()
            (project / "notes.ldsg").write_text("", encoding="utf-8")

            with patch("builtins.input", return_value=str(project)) as prompt:
                with patch.object(lds_cli.LDSCommandLine, "run") as run:
                    result = lds_cli.main()

            self.assertEqual(result, 0)
            prompt.assert_called_once_with("Enter LDS project folder path: ")
            run.assert_called_once()

    def test_categories_follow_log_type(self):
        categories = [dict(category) for category in lds_cli.DEFAULT_CATEGORIES]

        general = lds_cli.categories_for_log(categories, Path("work.ldsg"))
        debugging = lds_cli.categories_for_log(categories, Path("work.ldsd"))

        self.assertNotIn("Solution", [category["category"] for category in general])
        self.assertEqual(
            [category["category"] for category in debugging],
            ["Bug", "Just Details"],
        )

    def test_add_and_save_preserves_format_and_updates_existing_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            config_dir = project / "config"
            config_dir.mkdir()
            log_file = project / "work.ldsg"
            log_file.write_text("", encoding="utf-8")
            categories = lds_cli.categories_for_log(
                [dict(category) for category in lds_cli.DEFAULT_CATEGORIES],
                log_file,
            )
            cli = lds_cli.LDSCommandLine(log_file, categories)

            cli.handle_command('add "<started> today" "Bug"')
            cli.save()

            saved_log = log_file.read_text(encoding="utf-8")
            self.assertIn("id=bug;", saved_log)
            self.assertIn("&lt;started&gt; today", saved_log)
            counters = json.loads((config_dir / "counters.json").read_text(encoding="utf-8"))
            self.assertEqual(next(item["count"] for item in counters if item["id"] == "bug"), 1)
            self.assertFalse((project / "work.ldsd").exists())
            self.assertFalse((project / "work.ldsg.new").exists())

    def test_add_requires_quoted_entry_and_multiword_category(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "config").mkdir()
            log_file = project / "work.ldsg"
            log_file.write_text("", encoding="utf-8")
            categories = lds_cli.categories_for_log(
                [dict(category) for category in lds_cli.DEFAULT_CATEGORIES],
                log_file,
            )
            cli = lds_cli.LDSCommandLine(log_file, categories)

            cli.handle_command('add "Reviewed release notes" "Just Details"')
            self.assertIn("Reviewed release notes", lds_cli.plain_text(cli.log_lines[0]))

            with self.assertRaisesRegex(ValueError, "Usage: add"):
                cli.handle_command('add "Reviewed release notes" Just Details')

    def test_add_reuses_last_category_when_category_is_omitted(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "config").mkdir()
            log_file = project / "work.ldsg"
            log_file.write_text("", encoding="utf-8")
            categories = lds_cli.categories_for_log(
                [dict(category) for category in lds_cli.DEFAULT_CATEGORIES],
                log_file,
            )
            cli = lds_cli.LDSCommandLine(log_file, categories)

            cli.handle_command('add "First entry" "Just Details"')
            cli.handle_command('add "Second entry"')

            self.assertEqual(
                [lds_cli._category_marker(line)["id"] for line in cli.log_lines],
                ["details", "details"],
            )

    def test_add_requires_category_before_first_entry(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "config").mkdir()
            log_file = project / "work.ldsg"
            log_file.write_text("", encoding="utf-8")
            cli = lds_cli.LDSCommandLine(log_file, [])

            with self.assertRaisesRegex(ValueError, "Choose a category on the first add"):
                cli.handle_command('add "First entry"')

    def test_filter_selects_category_and_find_searches_entry_text(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            (project / "config").mkdir()
            log_file = project / "work.ldsg"
            log_file.write_text("", encoding="utf-8")
            categories = lds_cli.categories_for_log(
                [dict(category) for category in lds_cli.DEFAULT_CATEGORIES],
                log_file,
            )
            cli = lds_cli.LDSCommandLine(log_file, categories)
            cli.handle_command('add "Found startup issue" "Bug"')
            cli.handle_command('add "Reviewed release notes" "Just Details"')

            with patch.object(cli, "print_logs") as print_logs:
                cli.handle_command(':filter "Bug"')
                category_results = print_logs.call_args.args[0]
                self.assertEqual(len(category_results), 1)
                self.assertIn("Found startup issue", lds_cli.plain_text(category_results[0]))

                cli.handle_command(':find "release notes"')
                text_results = print_logs.call_args.args[0]
                self.assertEqual(len(text_results), 1)
                self.assertIn("Reviewed release notes", lds_cli.plain_text(text_results[0]))

    def test_debugging_save_preserves_counters_for_other_categories(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            config_dir = project / "config"
            config_dir.mkdir()
            log_file = project / "work.ldsd"
            log_file.write_text("", encoding="utf-8")
            all_categories = [dict(category) for category in lds_cli.DEFAULT_CATEGORIES]
            counters_path = config_dir / "counters.json"
            counters_path.write_text(
                json.dumps([{"id": "problem", "count": 7}]),
                encoding="utf-8",
            )
            categories = lds_cli.categories_for_log(all_categories, log_file)
            cli = lds_cli.LDSCommandLine(log_file, categories, all_categories)

            cli.add("Still investigating", "Bug")
            cli.save()

            saved_counters = json.loads(counters_path.read_text(encoding="utf-8"))
            self.assertEqual(
                next(item["count"] for item in saved_counters if item["id"] == "problem"),
                7,
            )


if __name__ == "__main__":
    unittest.main()
