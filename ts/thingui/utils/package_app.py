from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGridLayout, QPushButton, QMessageBox
from PySide6.QtGui import QGuiApplication
from .package_widget import PackageWidget
from ..conf.config import _load_main_config, _load_packages
import os

class PackageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.main_config_data = _load_main_config()
        self.setWindowTitle(self.main_config_data.get("APP_TITLE", "Package Selector"))
        self.OUTPUT_DIR = self.main_config_data.get("OUTPUT_DIR", "./thingui/output")
        self.packages = _load_packages(self.main_config_data)
        self.package_widgets = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for category, pkgs in self.packages.items():
            category_header = QLabel(category)
            category_header.setObjectName("category")

            scroll_layout.addWidget(category_header)
            grid = QGridLayout()
            for i, pkg in enumerate(pkgs):
                widget = PackageWidget(pkg, self)
                self.package_widgets.append(widget)
                row, col = divmod(i, 3)
                grid.addWidget(widget, row, col)
            container = QWidget()
            container.setLayout(grid)
            scroll_layout.addWidget(container)

        scroll_layout.addStretch()
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.submit)
        layout.addWidget(submit_btn)

        self.setLayout(layout)
        screen = QGuiApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.6), int(screen.height() * 0.6))

    def submit(self):
        if not any(w.selected.isChecked() for w in self.package_widgets):
            QMessageBox.warning(self, "Validation Error", "Please select at least one package before submitting.")
            return

        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        seen_sessions = set()
        for widget in self.package_widgets:
            if widget.selected.isChecked():
                for block in widget.session_blocks:
                    session_val = str(block['session_input'].value()) if block['session_input'] else "-1"
                    if session_val in seen_sessions:
                        QMessageBox.warning(self, "Validation Error", f"Duplicate session number: {session_val}")
                        return
                    seen_sessions.add(session_val)

        pkg_file = os.path.join(self.OUTPUT_DIR, "build.conf")
        opt_file = os.path.join(self.OUTPUT_DIR, "thinstation.conf.buildtime")
        with open(pkg_file, 'w') as f_pkg, open(opt_file, 'w') as f_opt:
            for cat, pkgs in self.packages.items():
                widgets = [w for w in self.package_widgets if w.package_data in pkgs and w.selected.isChecked()]
                if not widgets:
                    continue
                f_pkg.write(f"### {cat} ###\n")
                for w in widgets:
                    f_pkg.write(f"package {w.package_data['package']['name']}\n")
                    options = w.get_options()
                    if options:
                        f_opt.write(f"### {w.package_data['package']['name']} ###\n")
                        for k, v in options.items():
                            f_opt.write(f"{k}={v}\n")

        QMessageBox.information(self, "Done", "Configuration files written successfully!")
