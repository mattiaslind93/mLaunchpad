#!/usr/bin/env python3
"""HomeLaunchPad - A streamlined LaunchPad for home use.

Entry point for the application.
"""

import sys

from PyQt6.QtWidgets import QApplication

from core import HomeLaunchPad
from gui.main_window import MainWindow


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("HomeLaunchPad")
    app.setDesktopFileName("homelaunchpad")

    # Initialize core logic
    launchpad = HomeLaunchPad()

    # Create and show main window
    window = MainWindow(launchpad)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
