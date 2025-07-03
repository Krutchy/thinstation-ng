import os
import yaml
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QGroupBox, QScrollArea, QComboBox, QLineEdit,
    QDoubleSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt

PACKAGE_DIR = "../build/packages"
OUTPUT_DIR = "Output"
CONFIGURATOR_FILENAME = 'configurator.yaml'

class PackageWidget(QGroupBox):
    # Map variable types to widget constructors
    TYPE_WIDGETS = {
        'boolean': lambda var: QCheckBox(),
        'range': lambda var: QDoubleSpinBox(),
        'list': lambda var: QComboBox(),
        'default': lambda var: QLineEdit()
    }

    def __init__(self, pkg_data, app_ref):
        super().__init__(pkg_data['package']['name'])
        self.pkg_data = pkg_data
        self.app_ref = app_ref
        self.option_inputs = {}  # Store input widgets by variable name
        self.session_dropdown = None
        self.assigned_session = None

        self.selected = QCheckBox("Enable")  # Enable package checkbox
        self.options_frame = QWidget()       # Container for option inputs
        self.options_frame.setLayout(QVBoxLayout())

        self._build_header()   # Header with enable, session selector, toggle
        self._build_options()  # Build option input widgets

        self.options_frame.setVisible(False)  # Options hidden initially

        # Main layout combining header and options
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.header_layout)
        main_layout.addWidget(self.options_frame)
        self.setLayout(main_layout)

        self.update_session_dropdown()  # Setup sessions in dropdown

    def _build_header(self):
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.selected)

        # Add session dropdown if package supports sessions
        if self.pkg_data['package'].get('has-sessions', False):
            self.session_dropdown = QComboBox()
            self.session_dropdown.addItem("No session assigned")
            self.session_dropdown.currentIndexChanged.connect(self.on_session_selected)
            self.header_layout.addStretch()
            self.header_layout.addWidget(QLabel("Session:"))
            self.header_layout.addWidget(self.session_dropdown)
        else:
            self.header_layout.addStretch()

        # Toggle button to show/hide options
        toggle_btn = QPushButton("▼")
        toggle_btn.setFixedWidth(30)
        toggle_btn.setCheckable(True)
        toggle_btn.clicked.connect(lambda: self._toggle_options(toggle_btn))
        self.toggle_btn = toggle_btn
        self.header_layout.addWidget(toggle_btn)

    def _toggle_options(self, btn):
        expanded = btn.isChecked()
        self.options_frame.setVisible(expanded)
        btn.setText("▲" if expanded else "▼")

    def _build_options(self):
        # Create input widgets based on variable type and defaults
        for var in self.pkg_data.get("variables", []):
            desc = var.get("description", var['name'])
            row_layout = QHBoxLayout()
            row_layout.addWidget(QLabel(desc))

            widget = self._create_input_widget(var)
            row_layout.addWidget(widget)

            container = QWidget()
            container.setLayout(row_layout)
            self.options_frame.layout().addWidget(container)
            self.option_inputs[var['name']] = widget

    def _create_input_widget(self, var):
        var_type = var.get('type', 'default')
        constructor = self.TYPE_WIDGETS.get(var_type, self.TYPE_WIDGETS['default'])
        widget = constructor(var)

        # Initialize widget with default values and properties
        if var_type == 'boolean':
            widget.setChecked(var.get('default', False))
        elif var_type == 'range':
            widget.setDecimals(2)
            widget.setMinimum(var['min'])
            widget.setMaximum(var['max'])
            widget.setSingleStep(var['step'])
            widget.setValue(var.get('default', var['min']))
        elif var_type == 'list':
            widget.addItems(var['options'])
            if 'default' in var:
                idx = widget.findText(var['default'])
                if idx >= 0:
                    widget.setCurrentIndex(idx)
        else:
            widget.setText(str(var.get('default', '')))
        return widget

    def is_selected(self):
        return self.selected.isChecked()

    def get_options(self):
        # Extract values from input widgets into a dict
        opts = {}
        for key, widget in self.option_inputs.items():
            if isinstance(widget, QCheckBox):
                opts[key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                opts[key] = widget.currentText()
            else:
                opts[key] = widget.text()
        return opts

    def update_session_dropdown(self):
        if not self.session_dropdown:
            return

        self.session_dropdown.blockSignals(True)
        current = self.session_dropdown.currentText()
        self.session_dropdown.clear()
        self.session_dropdown.addItem("No session assigned")

        # Find sessions assigned to other widgets
        used_sessions = {num for num, w in self.app_ref.session_assignments.items() if w != self}
        assigned = next((num for num, w in self.app_ref.session_assignments.items() if w == self), None)
        self.assigned_session = assigned

        max_used = max(used_sessions, default=0)
        # Add available session numbers to dropdown
        for i in range(1, max_used + 2):
            if i not in used_sessions or i == assigned:
                self.session_dropdown.addItem(f"Session {i}")

        idx = self.session_dropdown.findText(current)
        if idx >= 0:
            self.session_dropdown.setCurrentIndex(idx)
        else:
            self.session_dropdown.setCurrentIndex(0)

        # Enable/disable toggle and checkbox based on session selection
        enabled = idx > 0
        self.toggle_btn.setEnabled(enabled)
        self.selected.setEnabled(enabled)
        if not enabled:
            self.selected.setChecked(False)

        self.session_dropdown.blockSignals(False)

    def on_session_selected(self):
        # Assign or remove session number for this package
        text = self.session_dropdown.currentText()
        session_num = int(text.split()[1]) if text.startswith("Session ") else None

        # Remove old assignment and add new one
        self.app_ref.session_assignments = {num: w for num, w in self.app_ref.session_assignments.items() if w != self}
        if session_num:
            self.app_ref.session_assignments[session_num] = self

        # Update all widgets to refresh their dropdowns
        for widget in self.app_ref.package_widgets:
            widget.update_session_dropdown()


class PackageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Package Selector")
        self.packages = self.load_packages()  # Load packages from configs
        self.package_widgets = []
        self.session_assignments = {}
        self._init_ui()

    def load_packages(self):
        data = {}
        # Read package configs and group by category
        for folder in os.listdir(PACKAGE_DIR):
            path = os.path.join(PACKAGE_DIR, folder, CONFIGURATOR_FILENAME)
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    config = yaml.safe_load(f)
                    pkg = config.get("package", {})
                    if pkg.get("visible", True):
                        data.setdefault(pkg.get("category", "Misc"), []).append(config)
        return data

    def _init_ui(self):
        main_layout = QVBoxLayout()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Add package widgets grouped by category
        for category, pkgs in self.packages.items():
            scroll_layout.addWidget(QLabel(f"<b>{category}</b>"))
            for pkg in pkgs:
                widget = PackageWidget(pkg, self)
                self.package_widgets.append(widget)
                scroll_layout.addWidget(widget)

        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        # Submit button to write config files
        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.submit)
        main_layout.addWidget(submit_btn)

        self.setLayout(main_layout)
        self.resize(800, 600)

    def submit(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(os.path.join(OUTPUT_DIR, 'build.conf'), 'w') as f_pkg, \
             open(os.path.join(OUTPUT_DIR, 'thinstation.conf.buildtime'), 'w') as f_opt:

            # Group selected packages by category
            selected_by_cat = {
                cat: [w for w in widgets if w.is_selected()]
                for cat, widgets in
                {cat: [w for w in self.package_widgets if w.pkg_data in pkgs] for cat, pkgs in self.packages.items()}.items()
            }

            # Write package names and options to config files
            for cat, widgets in selected_by_cat.items():
                if not widgets:
                    continue
                f_pkg.write(f"### {cat} ###\n")
                for widget in widgets:
                    f_pkg.write(f"package {widget.pkg_data['package']['name']}\n")
                    f_opt.write(f"### {widget.pkg_data['package']['name']} ###\n")
                    for k, v in widget.get_options().items():
                        session_num = widget.assigned_session
                        key = k.replace('#', str(session_num)) if session_num is not None else k
                        f_opt.write(f"{key}={v}\n")

        QMessageBox.information(self, "Done", "Configuration files written successfully!")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = PackageApp()
    window.show()
    sys.exit(app.exec_())

