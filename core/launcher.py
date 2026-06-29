"""Launcher module - starts applications with the correct environment."""

import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .platform_utils import IS_MAC

# Pipeline environment variables set by HomeLaunchPad.build_environment(). On
# macOS these are re-exported explicitly into the Terminal session (see
# _launch_terminal_mac), since `open` cannot pass a custom environment along.
PIPELINE_ENV_KEYS = [
    "JOBS",
    "JOBROOT",
    "SYSTEM",
    "USER_NAME",
    "MF_ROOT",
    "JOBPROJ",
    "JOBSEQ",
    "JOBSHOT",
    "JOBPATH",
    "SHOTPATH",
]


class Launcher:
    """Handles launching applications with the correct environment."""

    def __init__(self, blender_executable: str):
        self.blender_executable = blender_executable

    def launch_blender(self, env: dict[str, str]) -> Optional[subprocess.Popen]:
        """Launch Blender with the given environment.

        On both Linux and macOS the executable points at the real binary (on
        macOS the inner ``Blender.app/Contents/MacOS/Blender``), so it can be
        spawned directly with a custom environment.

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

    def launch_terminal(
        self, env: dict[str, str], working_dir: Optional[Path] = None
    ) -> Optional[subprocess.Popen]:
        """Open a terminal with the given environment.

        Args:
            env: Environment dictionary with job variables
            working_dir: Optional working directory for the terminal

        Returns:
            Popen object if successful, None if no terminal found
        """
        cwd = str(working_dir) if working_dir else env.get("SHOTPATH")

        if IS_MAC:
            return self._launch_terminal_mac(env, cwd)
        return self._launch_terminal_linux(env, cwd)

    def _launch_terminal_mac(
        self, env: dict[str, str], cwd: Optional[str]
    ) -> Optional[subprocess.Popen]:
        """Open Terminal.app and inject the pipeline environment via AppleScript.

        `open`/`open -a` cannot pass a custom environment, so we build a shell
        snippet that cd's into the shot folder and re-exports the pipeline
        variables, then hand it to Terminal via `do script`.
        """
        parts = []
        if cwd:
            parts.append(f"cd {shlex.quote(cwd)}")
        for key in PIPELINE_ENV_KEYS:
            value = env.get(key)
            if value:
                parts.append(f"export {key}={shlex.quote(value)}")
        parts.append("clear")
        shell_cmd = "; ".join(parts)

        # Escape for embedding inside an AppleScript double-quoted string.
        escaped = shell_cmd.replace("\\", "\\\\").replace('"', '\\"')
        applescript = (
            'tell application "Terminal"\n'
            "    activate\n"
            f'    do script "{escaped}"\n'
            "end tell"
        )

        try:
            return subprocess.Popen(["osascript", "-e", applescript])
        except OSError:
            return None

    def _launch_terminal_linux(
        self, env: dict[str, str], cwd: Optional[str]
    ) -> Optional[subprocess.Popen]:
        """Try common Linux terminal emulators, in order of preference."""
        terminals = [
            ("gnome-terminal", ["gnome-terminal", "--"]),
            ("konsole", ["konsole", "-e", "bash"]),
            ("xfce4-terminal", ["xfce4-terminal", "-e", "bash"]),
            ("xterm", ["xterm", "-e", "bash"]),
            ("kitty", ["kitty"]),
            ("alacritty", ["alacritty", "-e", "bash"]),
        ]

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

        if IS_MAC:
            try:
                return subprocess.Popen(["open", str(path)])
            except OSError:
                return None

        # Linux file managers to try, in order of preference.
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
