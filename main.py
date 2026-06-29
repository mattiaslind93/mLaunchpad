#!/usr/bin/env python3
"""HomeLaunchPad - A streamlined LaunchPad for home use.

Entry point for the application.
"""

import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from core import HomeLaunchPad
from gui.main_window import MainWindow

ICON_PATH = Path(__file__).parent / "icons" / "homelaunchpad_icon.png"


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("HomeLaunchPad")
    app.setDesktopFileName("homelaunchpad")

    # Dock / taskbar / window icon (Milford logo).
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    # Initialize core logic
    launchpad = HomeLaunchPad()

    # Create and show main window
    window = MainWindow(launchpad)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
