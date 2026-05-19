"""Native file picker (Windows / macOS / Linux) via tkinter."""

from pathlib import Path


def pick_file(
    *,
    title: str,
    extensions: tuple[str, ...],
    initial_dir: Path | None = None,
) -> Path | None:
    """
    Open an OS file dialog. Returns None if cancelled or tkinter unavailable.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print("  File picker not available (tkinter missing). Type a path instead.")
        return None

    start = str(initial_dir or Path.home() / "Downloads")
    filetypes = [("All files", "*.*")]
    if extensions == (".csv",):
        filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
    elif extensions == (".xlsx", ".xls"):
        filetypes = [
            ("Excel files", "*.xlsx;*.xls"),
            ("All files", "*.*"),
        ]

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()

    chosen = filedialog.askopenfilename(
        title=title,
        initialdir=start,
        filetypes=filetypes,
    )
    root.destroy()

    if not chosen:
        return None

    path = Path(chosen)
    if path.suffix.lower() not in extensions:
        print(f"  Wrong file type (need {', '.join(extensions)}): {path}")
        return None
    return path
