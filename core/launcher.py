"""Launcher module - starts applications with the correct environment."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional


class Launcher:
    """Handles launching applications with the correct environment."""

    def __init__(self, blender_executable: str):
        self.blender_executable = blender_executable

    def launch_blender(self, env: dict[str, str]) -> Optional[subprocess.Popen]:
        """Launch Blender with the given environment.

        Args:
            env: Environment dictionary with job variables

        Returns:
            Popen object if successful, None if Blender not found
        """
        if not Path(self.blender_executable).exists():
            return None

        try:
            process = subprocess.Popen(
                [self.blender_executable],
                env=env,
                start_new_session=True,  # Detach from parent process
            )
            return process
        except OSError:
            return None

    def launch_terminal(self, env: dict[str, str], working_dir: Optional[Path] = None) -> Optional[subprocess.Popen]:
        """Open a terminal with the given environment.

        Tries common Linux terminal emulators in order of preference.

        Args:
            env: Environment dictionary with job variables
            working_dir: Optional working directory for the terminal

        Returns:
            Popen object if successful, None if no terminal found
        """
        # Terminal emulators to try, in order of preference
        terminals = [
            ("gnome-terminal", ["gnome-terminal", "--"]),
            ("konsole", ["konsole", "-e", "bash"]),
            ("xfce4-terminal", ["xfce4-terminal", "-e", "bash"]),
            ("xterm", ["xterm", "-e", "bash"]),
            ("kitty", ["kitty"]),
            ("alacritty", ["alacritty", "-e", "bash"]),
        ]

        cwd = str(working_dir) if working_dir else env.get("SHOTPATH")

        for name, cmd in terminals:
            if shutil.which(name):
                try:
                    process = subprocess.Popen(
                        cmd,
                        env=env,
                        cwd=cwd,
                        start_new_session=True,
                    )
                    return process
                except OSError:
                    continue

        return None

    def open_folder(self, path: Path) -> Optional[subprocess.Popen]:
        """Open the file manager at the given path.

        Args:
            path: Directory path to open

        Returns:
            Popen object if successful, None if no file manager found
        """
        if not path.exists():
            return None

        # File managers to try
        file_managers = [
            ("nautilus", ["nautilus", str(path)]),
            ("dolphin", ["dolphin", str(path)]),
            ("thunar", ["thunar", str(path)]),
            ("nemo", ["nemo", str(path)]),
            ("pcmanfm", ["pcmanfm", str(path)]),
            ("xdg-open", ["xdg-open", str(path)]),  # Fallback
        ]

        for name, cmd in file_managers:
            if shutil.which(name):
                try:
                    process = subprocess.Popen(
                        cmd,
                        start_new_session=True,
                    )
                    return process
                except OSError:
                    continue

        return None
