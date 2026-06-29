"""Platform-specific helpers so HomeLaunchPad runs on both Linux and macOS.

All OS-dependent behaviour (Blender discovery, default source paths) lives here
so the rest of the codebase can stay platform-agnostic. The current platform is
detected once via ``sys.platform`` and exposed as module-level constants.
"""

import plistlib
import re
import sys
from pathlib import Path

IS_MAC = sys.platform == "darwin"
IS_WINDOWS = sys.platform.startswith("win")
IS_LINUX = not IS_MAC and not IS_WINDOWS


# ---------------------------------------------------------------------------
# Blender discovery
# ---------------------------------------------------------------------------

# Linux: extracted Blender builds live here, named ``blender-X.Y.Z-linux-x64/``.
LINUX_BLENDER_CONFIG_DIR = Path.home() / "Dokument" / "Blender" / "blender_config"
_LINUX_BLENDER_RE = re.compile(r"^blender-(\d+\.\d+\.\d+)-linux-x64$")

# macOS: Blender ships as an ``.app`` bundle; look in the standard app folders.
MAC_BLENDER_SEARCH_DIRS = [
    Path("/Applications"),
    Path.home() / "Applications",
]


def _version_sort_key(version: str) -> list[int]:
    """Return a list of ints for sorting version strings (newest first)."""
    parts = []
    for chunk in version.split("."):
        try:
            parts.append(int(chunk))
        except ValueError:
            parts.append(0)
    return parts


def _mac_blender_version(app_bundle: Path) -> str:
    """Read the Blender version from an ``.app`` bundle.

    Prefers ``CFBundleShortVersionString`` in Info.plist (e.g. "5.1.2"); falls
    back to the numbered folder under Contents/Resources (e.g. "5.1"); else "0.0".
    """
    info_plist = app_bundle / "Contents" / "Info.plist"
    try:
        with open(info_plist, "rb") as f:
            data = plistlib.load(f)
        version = data.get("CFBundleShortVersionString")
        if version:
            return str(version)
    except (OSError, plistlib.InvalidFileException, ValueError):
        pass

    resources = app_bundle / "Contents" / "Resources"
    if resources.exists():
        try:
            for entry in resources.iterdir():
                if entry.is_dir() and re.match(r"^\d+\.\d+", entry.name):
                    return entry.name
        except (PermissionError, OSError):
            pass
    return "0.0"


def _discover_mac_blender() -> list[tuple[str, str]]:
    """Find Blender ``.app`` bundles on macOS.

    Returns (version, executable_path) tuples where executable_path points at
    the inner Mach-O binary (``Contents/MacOS/Blender``) so it can be launched
    with a custom environment via subprocess.
    """
    found: dict[str, str] = {}  # executable_path -> version
    for base in MAC_BLENDER_SEARCH_DIRS:
        if not base.exists():
            continue
        try:
            entries = list(base.iterdir())
        except (PermissionError, OSError):
            continue
        for entry in entries:
            # Match "Blender.app", "Blender 4.2.app", etc.
            if not (entry.name.startswith("Blender") and entry.suffix == ".app"):
                continue
            executable = entry / "Contents" / "MacOS" / "Blender"
            if not executable.exists():
                continue
            found[str(executable)] = _mac_blender_version(entry)

    versions = [(version, exe) for exe, version in found.items()]
    versions.sort(key=lambda item: _version_sort_key(item[0]), reverse=True)
    return versions


def _discover_linux_blender(config_dir: Path) -> list[tuple[str, str]]:
    """Find extracted Blender builds in the Linux blender_config directory."""
    versions = []
    if not config_dir.exists():
        return versions
    try:
        entries = list(config_dir.iterdir())
    except (PermissionError, OSError):
        return versions
    for entry in entries:
        if entry.is_dir():
            match = _LINUX_BLENDER_RE.match(entry.name)
            if match:
                executable = entry / "blender"
                if executable.exists():
                    versions.append((match.group(1), str(executable)))
    versions.sort(key=lambda item: _version_sort_key(item[0]), reverse=True)
    return versions


def discover_blender_versions(
    linux_config_dir: Path = LINUX_BLENDER_CONFIG_DIR,
) -> list[tuple[str, str]]:
    """Return available (version, executable_path) tuples, sorted newest first."""
    if IS_MAC:
        return _discover_mac_blender()
    return _discover_linux_blender(linux_config_dir)


# ---------------------------------------------------------------------------
# Default sources (first-run config)
# ---------------------------------------------------------------------------

def default_sources() -> dict[str, dict]:
    """Return the default source definitions for the current platform.

    On macOS network shares mount under ``/Volumes`` and the home folder lives
    under ``/Users``; on Linux they use ``/var/mnt`` and ``/home``. The "private"
    source mirrors the same relative Insync/Google Drive structure on both.
    """
    home = Path.home()
    if IS_MAC:
        private_path = home / "Insync" / "mattiaslind93@gmail.com" / "Google Drive" / "Pipeline"
        return {
            "milford": {
                "name": "Milford",
                "jobs_path": "/Volumes/jack/JOBS",
                "system_path": "/Volumes/jack/SYSTEM",
            },
            "private": {
                "name": "Privat",
                "jobs_path": str(private_path),
                "system_path": "/Volumes/jack/SYSTEM",
            },
        }

    # Linux (default)
    return {
        "milford": {
            "name": "Milford",
            "jobs_path": "/var/mnt/jack/JOBS",
            "system_path": "/var/mnt/jack/SYSTEM",
        },
        "private": {
            "name": "Privat",
            "jobs_path": "/home/mlind/Insync/mattiaslind93@gmail.com/Google Drive/Pipeline",
            "system_path": "/var/mnt/jack/SYSTEM",
        },
    }
