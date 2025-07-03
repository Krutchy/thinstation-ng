import os
import yaml
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QGroupBox, QScrollArea, QComboBox, QSlider, QLineEdit,
    QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

PACKAGE_DIR = "../build/packages"
OUTPUT_DIR = "Output"
CONFIGURATOR_FILENAME = 'configurator.yaml'

class PackageWidget(QGroupBox):
    def __init__(self, pkg_data):
        super().__init__(pkg_data['package']['name'])
        self.pkg_data = pkg_data
        self.package_name = pkg_data['package']['name']
        self.selected = QCheckBox("Enable")
        self.options_frame = QWidget()
        self.options_layout = QVBoxLayout()
        self.options_frame.setLayout(self.options_layout)
        self.option_inputs = {}

        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()
        header = QHBoxLayout()
        header.addWidget(self.selected)
        toggle_btn = QPushButton("▼") # Button for opening/closing package options
        toggle_btn.setFixedWidth(30)
        header.addStretch()
        header.addWidget(toggle_btn)
        layout.addLayout(header)

        self.options_frame.setVisible(False)
        layout.addWidget(self.options_frame)

        toggle_btn.clicked.connect(lambda: self.options_frame.setVisible(not self.options_frame.isVisible()))
        self.setLayout(layout)

        # For each option in a given package:
        for var in self.pkg_data.get("variables", []):
            # Label option as its description
            desc = var.get("description", var['name'])
            label = QLabel(desc)
            layout = QHBoxLayout()
            layout.addWidget(label)

            # Handling different option input types
            if var['type'] == 'boolean': # Checkbox/toggle
                input_widget = QCheckBox()
                input_widget.setChecked(var.get('default', False))
            elif var['type'] == 'range': # Text input with buttons to increment/decrement
                input_widget = QDoubleSpinBox()
                input_widget.setDecimals(2)
                input_widget.setMinimum(var['min'])
                input_widget.setMaximum(var['max'])
                input_widget.setSingleStep(0.1)
                input_widget.setValue(var.get('default', var['min']))
            elif var['type'] == 'list': # Dropdown
                input_widget = QComboBox()
                input_widget.addItems(var['options'])
                if 'default' in var:
                    index = input_widget.findText(var['default'])
                    if index >= 0:
                        input_widget.setCurrentIndex(index)
            else: # Textbox for input (default)
                input_widget = QLineEdit()
                input_widget.setText(str(var.get('default', '')))

            layout.addWidget(input_widget)
            wrapper = QWidget()
            wrapper.setLayout(layout)
            self.options_layout.addWidget(wrapper)
            self.option_inputs[var['name']] = input_widget

    def is_selected(self):
        return self.selected.isChecked()

    def get_options(self):
        opts = {}
        for key, widget in self.option_inputs.items():
            if isinstance(widget, QCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, QSlider):
                value = widget.value()
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
            else:
                value = widget.text()
            opts[key] = value
        return opts


class PackageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Package Selector")
        self.packages = self.load_packages()
        self.package_widgets = []
        self.init_ui()

    def load_packages(self):
        data = {}
        # For each folder in packages:
        for folder in os.listdir(PACKAGE_DIR):
            # Check if configurator file exists in folder
            path = os.path.join(PACKAGE_DIR, folder, CONFIGURATOR_FILENAME)
            # If it does:
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    config = yaml.safe_load(f)
                    # Get package name and options
                    pkg = config.get("package", {})
                    if pkg.get("visible", True):
                        # Assigns package to its category or 'Misc' if none is defined
                        cat = pkg.get("category", "Misc")
                        data.setdefault(cat, []).append(config)
        return data

    def init_ui(self):
        main_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        for category, pkgs in self.packages.items():
            # Organize packages under each category header
            scroll_layout.addWidget(QLabel(f"<b>{category}</b>"))
            for pkg in pkgs:
                widget = PackageWidget(pkg)
                self.package_widgets.append(widget)
                scroll_layout.addWidget(widget)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.submit)
        main_layout.addWidget(submit_btn)

        self.setLayout(main_layout)
        self.resize(800, 600)

    # Handle submit button
    def submit(self):
        # Make output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(os.path.join(OUTPUT_DIR, 'build.conf'), 'w') as f_pkg, \
            open(os.path.join(OUTPUT_DIR, 'thinstation.conf.buildtime'), 'w') as f_opt:

        # Group selected packages by category
            selected_by_cat = {}
            for widget in self.package_widgets:
                if widget.is_selected():
                    # Find category for this package
                    for cat, pkgs in self.packages.items():
                        if widget.pkg_data in pkgs:
                            selected_by_cat.setdefault(cat, []).append(widget)
                            break

            # Write with category headers
            for cat, widgets in selected_by_cat.items():
                # Write category name as header above its packages
                f_pkg.write(f"### {cat} ###\n")
                # Write package name as header above its options
                f_opt.write(f"### {widget.package_name} ###\n")
                for widget in widgets:
                    f_pkg.write(f"package {widget.package_name}\n")
                    for k, v in widget.get_options().items():
                        f_opt.write(f"{k}={v}\n")
        # Success message
        QMessageBox.information(self, "Done", "Configuration files written successfully!")

# Run script
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = PackageApp()
    window.show()
    sys.exit(app.exec_())
