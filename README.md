# log-documentation-system
An application to make developing organized and enhance productivity.

## Command-line logging

`lds_cli.py` provides a Python-standard-library-only interactive interface for an
existing LDS project. Run the script from any directory:

```bash
python /path/to/lds_cli.py
```

The script prompts for the existing LDS project folder. It verifies the path is
a folder containing both a `config` directory and at least one `.ldsg` or
`.ldsd` file before continuing. If the project contains multiple logs, choose
which one to open when prompted.

At the `lds>` prompt, choose a category the first time you add an entry. You
can specify a new category on later entries or omit it to reuse the last one.
Quote entry and category arguments; this is required for category names with
spaces:

```text
add "Investigated the startup issue" "Bug"
add "Reviewed the release notes" "Just Details"
add "Found another issue" "Bug"
add "Added another note"
```

Use `:categories` to list categories, `:all` to print all entries,
`:filter "<category>"` to show entries in a category, and `:find "<text>"` to
search entry text. Use `:save` to write changes to the existing log and `:help`
for command help. Unsaved changes are discarded on exit unless you choose to
save when prompted. The CLI does not create a new LDS project or provide
GUI-only features such as export and dictionary tools.
