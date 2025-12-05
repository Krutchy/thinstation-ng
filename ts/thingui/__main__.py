#!/usr/sbin/python
import sys
import os
from PySide6.QtWidgets import QApplication
from .utils.package_app import PackageApp
from .conf.config import load_main_config, load_packages

def load_styles(app, STYLE_FILES):
    if not STYLE_FILES: return

    WORKING_DIR = os.path.dirname(os.path.abspath(__file__))
    for file in STYLE_FILES:
        path = os.path.join(WORKING_DIR, file)
        if os.path.exists(path):
            with open(path, "r") as style:
                app.setStyleSheet(app.styleSheet() + style.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_config_data = load_main_config()
    packages = load_packages(main_config_data)
    load_styles(app, main_config_data.get("STYLE_FILES", []))
    window = PackageApp(
        packages, 
        main_config_data.get("OUTPUT_DIR", "./thingui/output"), 
        main_config_data.get("APP_TITLE", "Package Selector")
    )
    window.show()
    sys.exit(app.exec())