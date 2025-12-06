import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QStackedWidget, 
    QPushButton, QScrollArea, QSplitter, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from .package_widget import PackageWidget

class PackageApp(QWidget):
    def __init__(self, packages, output_dir, app_title):
        super().__init__()
        self.packages = packages
        self.OUTPUT_DIR = output_dir
        self.setWindowTitle(app_title)
        self.package_widgets = {}
        self.init_ui()

    def init_ui(self):
        splitter = QSplitter(Qt.Horizontal)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setMinimumWidth(150)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        splitter.addWidget(self.tree_widget)

        self.stack_widget = QStackedWidget()
        splitter.addWidget(self.stack_widget)
        splitter.setSizes([250, 750])

        for category, pkgs in self.packages.items():
            cat_item = QTreeWidgetItem([category])
            self.tree_widget.addTopLevelItem(cat_item)
            for pkg in pkgs:
                pkg_item = QTreeWidgetItem([pkg['package']['name']])
                cat_item.addChild(pkg_item)

                widget = PackageWidget(pkg, self)
                scroll_area = QScrollArea()
                scroll_area.setWidget(widget)
                scroll_area.setWidgetResizable(True)

                self.package_widgets[pkg['package']['name']] = scroll_area
                self.stack_widget.addWidget(scroll_area)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(splitter)
        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.submit)
        main_layout.addWidget(submit_btn)

        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.6), int(screen.height() * 0.6))
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        first_pkg_item = self.tree_widget.topLevelItem(0).child(0) if self.tree_widget.topLevelItemCount() > 0 else None
        if first_pkg_item:
            self.tree_widget.setCurrentItem(first_pkg_item)
            self.display_package_options(first_pkg_item)

    def on_item_clicked(self, item, column):
        if item.parent():
            self.display_package_options(item)

    def display_package_options(self, item):
        name = item.text(0)
        scroll_area = self.package_widgets.get(name)
        if scroll_area:
            self.stack_widget.setCurrentWidget(scroll_area)

    def submit(self):
        # Check if at least one package is selected
        selected_widgets = [sa.widget() for sa in self.package_widgets.values() if sa.widget().selected.isChecked()]
        if not selected_widgets:
            QMessageBox.warning(self, "Validation Error", "Please select at least one package.")
            return

        # Validate global uniqueness of session numbers
        all_session_numbers = {}
        for pkg_widget in selected_widgets:
            pkg_name = pkg_widget.package_data['package']['name']
            for block in pkg_widget.session_blocks:
                if block.session_input:
                    num = block.session_input.value()
                    if num in all_session_numbers:
                        conflicting_pkg = all_session_numbers[num]
                        QMessageBox.warning(
                            self,
                            "Validation Error",
                            f"Session number {num} is duplicated between packages '{conflicting_pkg}' and '{pkg_name}'."
                        )
                        return
                    all_session_numbers[num] = pkg_name

        # All checks passed, write files
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        pkg_file = os.path.join(self.OUTPUT_DIR, "build.conf")
        opt_file = os.path.join(self.OUTPUT_DIR, "thinstation.conf.buildtime")
        with open(pkg_file, 'w') as f_pkg, open(opt_file, 'w') as f_opt:
            for category, pkgs in self.packages.items():
                widgets = [
                    sa.widget() for sa in self.package_widgets.values()
                    if sa.widget().package_data in pkgs and sa.widget().selected.isChecked()
                ]
                if not widgets:
                    continue
                f_pkg.write(f"### {category} ###\n")
                for w in widgets:
                    f_pkg.write(f"package {w.package_data['package']['name']}\n")
                    options = w.get_options()
                    if options:
                        f_opt.write(f"### {w.package_data['package']['name']} ###\n")
                        for k, v in options.items():
                            f_opt.write(f"{k}={v}\n")

        QMessageBox.information(self, "Done", "Configuration files written successfully!")
