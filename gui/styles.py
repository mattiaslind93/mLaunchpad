"""Dark theme stylesheet for HomeLaunchPad."""

DARK_STYLESHEET = """
QMainWindow {
    background-color: #2b2b2b;
}

QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: ".AppleSystemUIFont", "SF Pro Text", "Helvetica Neue", "Segoe UI", "Ubuntu", sans-serif;
    font-size: 12px;
}

QLabel {
    color: #e0e0e0;
    padding: 2px;
}

QLabel#titleLabel {
    font-size: 14px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#headerLabel {
    font-size: 11px;
    font-weight: bold;
    color: #a0a0a0;
    padding: 4px 8px;
    background-color: #363636;
    border-radius: 3px;
}

QLabel#sourceLabel {
    font-size: 11px;
    color: #a0a0a0;
}

QComboBox#sourceCombo {
    background-color: #404040;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
    min-width: 100px;
}

QComboBox#sourceCombo:hover {
    background-color: #4a4a4a;
    border-color: #606060;
}

QComboBox#sourceCombo::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox#sourceCombo::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #a0a0a0;
    margin-right: 4px;
}

QComboBox#sourceCombo QAbstractItemView {
    background-color: #323232;
    border: 1px solid #505050;
    selection-background-color: #0d6efd;
    outline: none;
}

QComboBox#blenderCombo {
    background-color: #404040;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e87d0d;
    min-width: 80px;
}

QComboBox#blenderCombo:hover {
    background-color: #4a4a4a;
    border-color: #e87d0d;
}

QComboBox#blenderCombo::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox#blenderCombo::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #e87d0d;
    margin-right: 4px;
}

QComboBox#blenderCombo QAbstractItemView {
    background-color: #323232;
    border: 1px solid #505050;
    selection-background-color: #e87d0d;
    outline: none;
}

QListWidget {
    background-color: #1e1e1e;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 6px 8px;
    border-radius: 3px;
    margin: 1px 0;
}

QListWidget::item:hover {
    background-color: #3a3a3a;
}

QListWidget::item:selected {
    background-color: #0d6efd;
    color: #ffffff;
}

QPushButton {
    background-color: #404040;
    border: 1px solid #505050;
    border-radius: 4px;
    padding: 8px 16px;
    color: #e0e0e0;
    font-weight: bold;
    min-width: 70px;
}

QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #606060;
}

QPushButton:pressed {
    background-color: #353535;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    color: #606060;
    border-color: #353535;
}

QPushButton#blenderButton {
    background-color: #e87d0d;
    border-color: #f08d1d;
    color: #ffffff;
}

QPushButton#blenderButton:hover {
    background-color: #f08d1d;
}

QPushButton#blenderButton:pressed {
    background-color: #d06d00;
}

QPushButton#blenderButton:disabled {
    background-color: #5a4020;
    color: #808080;
    border-color: #4a3010;
}

QPushButton#terminalButton {
    background-color: #2d7d46;
    border-color: #3d8d56;
    color: #ffffff;
}

QPushButton#terminalButton:hover {
    background-color: #3d8d56;
}

QPushButton#terminalButton:pressed {
    background-color: #1d6d36;
}

QPushButton#terminalButton:disabled {
    background-color: #1a3d26;
    color: #808080;
    border-color: #152d1e;
}

QPushButton#folderButton {
    background-color: #3a6ea5;
    border-color: #4a7eb5;
    color: #ffffff;
}

QPushButton#folderButton:hover {
    background-color: #4a7eb5;
}

QPushButton#folderButton:pressed {
    background-color: #2a5e95;
}

QPushButton#folderButton:disabled {
    background-color: #1a3050;
    color: #808080;
    border-color: #152540;
}

QGroupBox {
    border: 1px solid #404040;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: #a0a0a0;
}

QStatusBar {
    background-color: #252525;
    border-top: 1px solid #404040;
    color: #a0a0a0;
    padding: 4px;
}

QFrame#statusFrame {
    background-color: #252525;
    border-top: 1px solid #404040;
    padding: 8px;
}

QFrame#appPanel {
    background-color: #323232;
    border: 1px solid #404040;
    border-radius: 4px;
}

QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #505050;
    border-radius: 5px;
    min-height: 30px;
    margin: 1px;
}

QScrollBar::handle:vertical:hover {
    background-color: #606060;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #505050;
    border-radius: 5px;
    min-width: 30px;
    margin: 1px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #606060;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
"""
