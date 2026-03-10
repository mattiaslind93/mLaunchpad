"""Main window for HomeLaunchPad."""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QFrame,
    QSplitter,
    QMessageBox,
    QComboBox,
)
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from pathlib import Path

from gui.styles import DARK_STYLESHEET
from core.launchpad import HomeLaunchPad
from core.launcher import Launcher

# Icons directory
ICONS_DIR = Path(__file__).parent.parent / "icons"


class SourceAvailabilityWorker(QThread):
    """Worker thread to check source availability without blocking the GUI."""

    finished = pyqtSignal(str, bool)  # source_id, is_available

    def __init__(self, launchpad, source_id: str):
        super().__init__()
        self.launchpad = launchpad
        self.source_id = source_id

    def run(self):
        is_available = self.launchpad.is_source_available(self.source_id)
        self.finished.emit(self.source_id, is_available)


class MainWindow(QMainWindow):
    """Main application window for HomeLaunchPad."""

    def __init__(self, launchpad: HomeLaunchPad):
        super().__init__()
        self.launchpad = launchpad
        self.launcher = Launcher(launchpad.blender_executable)

        self.setWindowTitle("HomeLaunchPad")
        self.setMinimumSize(900, 600)
        self.resize(1000, 650)

        self._setup_ui()
        self._connect_signals()
        self._update_source_availability()
        self._load_initial_state()

        self.setStyleSheet(DARK_STYLESHEET)

        # Timer to periodically check source availability (every 10 seconds)
        self.availability_timer = QTimer(self)
        self.availability_timer.timeout.connect(self._update_source_availability)
        self.availability_timer.start(10000)

    def _setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Title bar
        title_layout = QHBoxLayout()
        self.title_label = QLabel("HomeLaunchPad")
        self.title_label.setObjectName("titleLabel")
        title_layout.addWidget(self.title_label)

        title_layout.addSpacing(20)

        # Source selector
        source_label = QLabel("Källa:")
        source_label.setObjectName("sourceLabel")
        title_layout.addWidget(source_label)

        self.source_combo = QComboBox()
        self.source_combo.setObjectName("sourceCombo")
        self.source_combo.setMinimumWidth(120)
        for source_id, source_name in self.launchpad.get_source_names():
            self.source_combo.addItem(source_name, source_id)
        # Set current source
        current_idx = self.source_combo.findData(self.launchpad.current_source)
        if current_idx >= 0:
            self.source_combo.setCurrentIndex(current_idx)
        title_layout.addWidget(self.source_combo)

        self.path_label = QLabel("")
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        title_layout.addWidget(self.path_label, 1)
        main_layout.addLayout(title_layout)

        # Main content area with splitter
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)

        # Left side: Project/Sequence/Shot lists
        lists_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Project list
        project_widget = QWidget()
        project_layout = QVBoxLayout(project_widget)
        project_layout.setContentsMargins(0, 0, 0, 0)
        project_layout.setSpacing(4)

        project_header = QLabel("Projekt")
        project_header.setObjectName("headerLabel")
        project_layout.addWidget(project_header)

        self.project_list = QListWidget()
        project_layout.addWidget(self.project_list)
        lists_splitter.addWidget(project_widget)

        # Sequence list
        sequence_widget = QWidget()
        sequence_layout = QVBoxLayout(sequence_widget)
        sequence_layout.setContentsMargins(0, 0, 0, 0)
        sequence_layout.setSpacing(4)

        sequence_header = QLabel("Sekvens")
        sequence_header.setObjectName("headerLabel")
        sequence_layout.addWidget(sequence_header)

        self.sequence_list = QListWidget()
        sequence_layout.addWidget(self.sequence_list)
        lists_splitter.addWidget(sequence_widget)

        # Shot list
        shot_widget = QWidget()
        shot_layout = QVBoxLayout(shot_widget)
        shot_layout.setContentsMargins(0, 0, 0, 0)
        shot_layout.setSpacing(4)

        shot_header = QLabel("Shot")
        shot_header.setObjectName("headerLabel")
        shot_layout.addWidget(shot_header)

        self.shot_list = QListWidget()
        shot_layout.addWidget(self.shot_list)
        lists_splitter.addWidget(shot_widget)

        # Set equal sizes for lists
        lists_splitter.setSizes([250, 250, 250])
        content_layout.addWidget(lists_splitter, 3)

        # Right side: Applications panel
        app_panel = QFrame()
        app_panel.setObjectName("appPanel")
        app_panel.setFixedWidth(160)
        app_layout = QVBoxLayout(app_panel)
        app_layout.setContentsMargins(10, 10, 10, 10)
        app_layout.setSpacing(8)

        app_header = QLabel("Applications")
        app_header.setObjectName("headerLabel")
        app_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_layout.addWidget(app_header)

        app_layout.addSpacing(10)

        # Application buttons
        icon_size = QSize(32, 32)

        self.blender_btn = QPushButton("Blender")
        self.blender_btn.setObjectName("blenderButton")
        self.blender_btn.setIcon(QIcon(str(ICONS_DIR / "blender.png")))
        self.blender_btn.setIconSize(icon_size)
        self.blender_btn.setFixedHeight(50)
        self.blender_btn.setEnabled(False)
        app_layout.addWidget(self.blender_btn)

        self.terminal_btn = QPushButton("Terminal")
        self.terminal_btn.setObjectName("terminalButton")
        self.terminal_btn.setIcon(QIcon(str(ICONS_DIR / "cmd.png")))
        self.terminal_btn.setIconSize(icon_size)
        self.terminal_btn.setFixedHeight(50)
        self.terminal_btn.setEnabled(False)
        app_layout.addWidget(self.terminal_btn)

        self.folder_btn = QPushButton("Folder")
        self.folder_btn.setObjectName("folderButton")
        self.folder_btn.setIcon(QIcon(str(ICONS_DIR / "browse.png")))
        self.folder_btn.setIconSize(icon_size)
        self.folder_btn.setFixedHeight(50)
        self.folder_btn.setEnabled(False)
        app_layout.addWidget(self.folder_btn)

        app_layout.addStretch()
        content_layout.addWidget(app_panel)

        main_layout.addLayout(content_layout, 1)

        # Status bar at bottom
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 8, 10, 8)

        self.user_label = QLabel(f"User: {self.launchpad.user_name}")
        status_layout.addWidget(self.user_label)

        status_layout.addStretch()

        self.status_label = QLabel("Select a project to begin")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_layout.addWidget(self.status_label)

        main_layout.addWidget(status_frame)

    def _connect_signals(self):
        """Connect UI signals to slots."""
        self.source_combo.currentIndexChanged.connect(self._on_source_changed)
        self.project_list.currentItemChanged.connect(self._on_project_changed)
        self.sequence_list.currentItemChanged.connect(self._on_sequence_changed)
        self.shot_list.currentItemChanged.connect(self._on_shot_changed)

        self.blender_btn.clicked.connect(self._launch_blender)
        self.terminal_btn.clicked.connect(self._launch_terminal)
        self.folder_btn.clicked.connect(self._open_folder)

    def _load_initial_state(self):
        """Load initial state from config."""
        # Populate project list
        projects = self.launchpad.projects()
        self.project_list.addItems(projects)

        # Restore previous selection if available
        if self.launchpad.current_project:
            items = self.project_list.findItems(
                self.launchpad.current_project, Qt.MatchFlag.MatchExactly
            )
            if items:
                self.project_list.setCurrentItem(items[0])

    def _on_project_changed(self, current, previous):
        """Handle project selection change."""
        self.sequence_list.clear()
        self.shot_list.clear()

        if not current:
            self.launchpad.current_project = None
            self._update_buttons_state()
            self._update_title()
            return

        project = current.text()
        self.launchpad.set_project(project)

        # Populate sequences
        sequences = self.launchpad.sequences()
        self.sequence_list.addItems(sequences)

        # Restore sequence selection if available
        if self.launchpad.current_sequence:
            items = self.sequence_list.findItems(
                self.launchpad.current_sequence, Qt.MatchFlag.MatchExactly
            )
            if items:
                self.sequence_list.setCurrentItem(items[0])

        self._update_buttons_state()
        self._update_title()

    def _on_sequence_changed(self, current, previous):
        """Handle sequence selection change."""
        self.shot_list.clear()

        if not current:
            self.launchpad.current_sequence = None
            self._update_buttons_state()
            self._update_title()
            return

        sequence = current.text()
        self.launchpad.set_sequence(sequence)

        # Populate shots
        shots = self.launchpad.shots()
        self.shot_list.addItems(shots)

        # Restore shot selection if available
        if self.launchpad.current_shot:
            items = self.shot_list.findItems(
                self.launchpad.current_shot, Qt.MatchFlag.MatchExactly
            )
            if items:
                self.shot_list.setCurrentItem(items[0])

        self._update_buttons_state()
        self._update_title()

    def _on_source_changed(self, index):
        """Handle source selection change."""
        source_id = self.source_combo.currentData()
        if source_id and source_id != self.launchpad.current_source:
            self.launchpad.set_source(source_id)
            self._refresh_project_list()
            self._update_buttons_state()
            self._update_title()
            # Check availability in background (will show warning if unavailable)
            self._update_source_availability()

    def _on_shot_changed(self, current, previous):
        """Handle shot selection change."""
        if not current:
            self.launchpad.current_shot = None
            self._update_buttons_state()
            self._update_title()
            return

        shot = current.text()
        self.launchpad.set_shot(shot)
        self._update_buttons_state()
        self._update_title()

    def _refresh_project_list(self):
        """Refresh the project list from current source."""
        self.project_list.clear()
        self.sequence_list.clear()
        self.shot_list.clear()

        projects = self.launchpad.projects()
        self.project_list.addItems(projects)

    def _update_source_availability(self):
        """Check if current source is still available (runs in background thread)."""
        # Don't start a new check if one is already running
        if hasattr(self, '_availability_worker') and self._availability_worker.isRunning():
            return

        current_source = self.launchpad.current_source
        self._availability_worker = SourceAvailabilityWorker(self.launchpad, current_source)
        self._availability_worker.finished.connect(self._on_availability_checked)
        self._availability_worker.start()

    def _on_availability_checked(self, source_id: str, is_available: bool):
        """Handle result from background availability check."""
        # Only act if this is still the current source
        if source_id != self.launchpad.current_source:
            return

        if not is_available:
            self.status_label.setText(f"Varning: {self.launchpad.current_source_name} är inte tillgänglig")
            self.blender_btn.setEnabled(False)
            self.terminal_btn.setEnabled(False)
            self.folder_btn.setEnabled(False)

    def _update_buttons_state(self):
        """Update button enabled state based on selection."""
        has_full_path = self.launchpad.get_shot_path() is not None
        self.blender_btn.setEnabled(has_full_path)
        self.terminal_btn.setEnabled(has_full_path)
        self.folder_btn.setEnabled(has_full_path)

        if has_full_path:
            self.status_label.setText(f"Path: {self.launchpad.get_shot_path()}")
        else:
            self.status_label.setText("Select project, sequence, and shot")

        # Always show which source and base path is active
        source_name = self.launchpad.current_source_name
        jobs_path = self.launchpad.jobs_path
        self.path_label.setText(f"[{source_name}] {jobs_path}")

    def _update_title(self):
        """Update window title with current path and source info."""
        job_path = self.launchpad.get_job_path()
        source_name = self.launchpad.current_source_name
        if job_path:
            self.setWindowTitle(f"HomeLaunchPad - [{source_name}] {job_path}")
        else:
            self.setWindowTitle(f"HomeLaunchPad - [{source_name}]")

    def _launch_blender(self):
        """Launch Blender with the current environment."""
        env = self.launchpad.build_environment()
        result = self.launcher.launch_blender(env)

        if not result:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not launch Blender.\n\nPath: {self.launchpad.blender_executable}",
            )

    def _launch_terminal(self):
        """Launch terminal with the current environment."""
        env = self.launchpad.build_environment()
        shot_path = self.launchpad.get_shot_path()
        result = self.launcher.launch_terminal(env, shot_path)

        if not result:
            QMessageBox.warning(
                self,
                "Error",
                "Could not find a terminal emulator to launch.",
            )

    def _open_folder(self):
        """Open the shot folder in file manager."""
        shot_path = self.launchpad.get_shot_path()
        if shot_path:
            result = self.launcher.open_folder(shot_path)

            if not result:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not open folder.\n\nPath: {shot_path}",
                )
