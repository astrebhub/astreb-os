from __future__ import annotations

import shutil
import subprocess
import sys


class ClipboardBridgeError(RuntimeError):
    """Raised when explicit local clipboard reading is unavailable."""


def _command_for_platform() -> list[str]:
    if sys.platform == "win32":
        return [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            (
                "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); "
                "$value = Get-Clipboard -Raw -ErrorAction Stop; "
                "[Console]::Out.Write($value)"
            ),
        ]
    if sys.platform == "darwin":
        return ["pbpaste"]
    for command in (["wl-paste", "--no-newline"], ["xclip", "-selection", "clipboard", "-out"]):
        if shutil.which(command[0]):
            return command
    raise ClipboardBridgeError("No supported local clipboard reader is installed.")


def read_local_clipboard_text() -> str:
    """Read text only after an explicit request from the local user interface."""

    try:
        completed = subprocess.run(
            _command_for_platform(),
            check=False,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=4,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ClipboardBridgeError("Local clipboard could not be read.") from exc
    if completed.returncode != 0:
        raise ClipboardBridgeError("Local clipboard could not be read.")
    return completed.stdout.lstrip("\ufeff")
