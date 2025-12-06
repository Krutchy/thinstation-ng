#!/usr/sbin/python
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from .utils.package_app import PackageApp
from .conf.config import load_yaml_file, load_packages

WORKING_DIR = Path(__file__).resolve().parent

def load_styles(app, style_files):
    if not style_files:
        return
    styles = []
    for file in style_files:
        path = WORKING_DIR / file
        if path.exists():
            styles.append(path.read_text())
    app.setStyleSheet(app.styleSheet() + "\n".join(styles))

def main():
    app = QApplication(sys.argv)
    config = load_yaml_file("thingui_config.yaml")

    packages = load_packages(
        config.get("PACKAGE_DIR", "../../build/packages"),
        config.get("CONFIGURATOR_FILENAME", "configurator.yaml"),
        config.get("SESSION_CONFIGURATOR_FILEPATH", "../../build/packages/base/session_configurator.yaml"),
        config.get("DEFAULT_CATEGORY", "Misc")
    )

    load_styles(app, config.get("STYLE_FILES", []))

    window = PackageApp(
        packages,
        config.get("OUTPUT_DIR", "./thingui/output"),
        config.get("APP_TITLE", "Package Selector")
    )
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
