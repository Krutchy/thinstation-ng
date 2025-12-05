#!/usr/sbin/python
import sys
import os
from PySide6.QtWidgets import QApplication
from .utils.package_app import PackageApp
from .conf.config import _load_main_config

def _load_styles(app, STYLE_FILES):
    WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
    for file in STYLE_FILES:
        path = os.path.join(WORKING_DIR, file)
        if os.path.exists(path):
            with open(path, "r") as style:
                app.setStyleSheet(app.styleSheet() + style.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_config_data = _load_main_config()
    STYLE_FILES = main_config_data.get("STYLE_FILES", [])
    if STYLE_FILES: _load_styles(app, STYLE_FILES)
    window = PackageApp()
    window.show()
    sys.exit(app.exec())