#!/usr/sbin/python
import sys                                                      # System-specific parameters and functions
import os                                                       # Operating system dependent functionality
import yaml                                                     # YAML file parsing
from PySide6.QtWidgets import (                                 # Import Qt widgets for GUI
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QGroupBox, QScrollArea, QComboBox, QLineEdit,
    QDoubleSpinBox, QMessageBox, QSizePolicy, QGridLayout, QSpinBox
)
from PySide6.QtCore import Qt                                   # Core Qt constants
from PySide6.QtGui import QGuiApplication                       # Access to GUI application info

# Path and Config Setup
BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))        # Base directory of current script
PACKAGE_DIR = os.path.join(BASE_DIR, "../build/packages")       # Directory containing package configs
OUTPUT_DIR = os.path.join(BASE_DIR, "Output")                   # Directory to save output files
STYLE_FILE = os.path.join(BASE_DIR, "style.qss")                # Path to style sheet file
CONFIGURATOR_FILENAME = 'configurator.yaml'                     # Config filename to look for in packages

# Package Configuration Widget
class PackageWidget(QGroupBox):
    def __init__(self, pkg_data, app_ref):
        super().__init__(pkg_data['package']['name'])   # Initialize group box with package name
        self.pkg_data = pkg_data                        # Store package configuration data
        self.app_ref = app_ref                          # Reference to main app
        self.option_inputs = {}                         # Dict to hold input widgets by var name
        self.session_blocks = []                        # List to hold session UI blocks

        self.selected = QCheckBox("Enable")             # Checkbox to enable/disable package

        self.options_frame = QWidget()                  # Container widget for options
        self.options_frame.setLayout(QVBoxLayout())     # Vertical layout for options
        self.options_frame.setVisible(False)            # Start with options hidden

        self._build_header()                            # Build header with checkbox and toggle
        self._build_options()                           # Build options UI

        layout = QVBoxLayout()                          # Main vertical layout for widget
        layout.addLayout(self.header_layout)            # Add header layout
        layout.addWidget(self.options_frame)            # Add options container
        self.setLayout(layout)                          # Set main layout

    # Header (Checkbox + Toggle)
    def _build_header(self):
        self.header_layout = QHBoxLayout()                              # Horizontal layout for header
        self.header_layout.addWidget(self.selected)                     # Add enable checkbox

        self.header_layout.addStretch()                                 # Push everything hereafter to the right.
        self.toggle_btn = QPushButton("\u25BC")                         # Toggle button (down arrow)
        self.toggle_btn.setFixedWidth(30)                               # Fix width of toggle button
        self.toggle_btn.setCheckable(True)                              # Make toggle button checkable
        self.toggle_btn.clicked.connect(lambda: self._toggle_options()) # Connect toggle action
        self.header_layout.addWidget(self.toggle_btn)                   # Add toggle button to header

    def _toggle_options(self):
        expanded = self.toggle_btn.isChecked()                      # Check toggle button state
        self.options_frame.setVisible(expanded)                     # Show/hide options frame
        self.toggle_btn.setText("\u25B2" if expanded else "\u25BC") # Change arrow direction

    # Build Session Blocks
    def _build_options(self):
        if self.pkg_data['package'].get('has-sessions', False): # Check if package has sessions
            self._add_session_block()                           # Add initial session block
            add_btn = QPushButton("+ Add Session")              # Button to add more sessions
            add_btn.clicked.connect(self._add_session_block)    # Connect add session action
            self.options_frame.layout().addWidget(add_btn)      # Add button to options layout
        else:
            self._add_session_block()                           # Add single session block (no sessions)

    def _add_session_block(self):
        container = QWidget()                           # Container for session block
        layout = QVBoxLayout(container)                 # Vertical layout for session block

        # Session Header: Input + Remove Button
        header_layout = QHBoxLayout()                   # Horizontal layout for header
        session_input = QSpinBox()                      # Session number input field
        session_input.setMinimum(0)
        session_input.setSingleStep(1)
        session_input.setFixedWidth(80)

        remove_btn = QPushButton("Remove")              # Button to remove this session
        remove_btn.setFixedWidth(70)                    # Fix width
        remove_btn.clicked.connect(
            lambda: self._remove_session_block(
                container, 
                session_input
            )
        )

        header_layout.addWidget(QLabel("Session:"))     # Label for session input
        header_layout.addWidget(session_input)          # Add session input
        header_layout.addStretch()                      # Add stretch to align
        header_layout.addWidget(remove_btn)             # Add remove button
        layout.addLayout(header_layout)                 # Add header layout to session block

        # Create Variable Input Widgets
        inputs = {}                                                                             # Dictionary to hold input widgets
        for var in self.pkg_data.get("variables", []):                                          # Loop over variables
            widget = self._create_input_widget(var)                                             # Create appropriate widget
            label = QLabel(var.get("description", var['name']))                                 # Label with session number
            row = QWidget()                                                                     # Row container
            row_layout = QHBoxLayout(row)                                                       # Horizontal layout for row
            row_layout.addWidget(label)                                                         # Add label to row
            row_layout.addWidget(widget)                                                        # Add widget to row
            layout.addWidget(row)                                                               # Add row to session layout
            inputs[var['name']] = widget                                                        # Store widget keyed by variable name

        self.option_inputs.update(inputs)                                                       # Update main option_inputs dict
        self.options_frame.layout().insertWidget(len(self.session_blocks), container)           # Insert session widget in layout
        self.session_blocks.append({                                                            # Track session block
            'widget': container, 
            'session_input': session_input, 
            'inputs': inputs
        })

    def _remove_session_block(self, container, session_input):
        container.setParent(None)           # Remove widget from layout
        self.session_blocks = [
            b for b 
            in self.session_blocks 
            if b['widget'] != container
        ]                                   # Remove from tracking list
        self._rebuild_option_inputs()       # Rebuild option_inputs dictionary

    def _rebuild_option_inputs(self):
        self.option_inputs = {}                         # Reset option_inputs dict
        for block in self.session_blocks:               # For each session block
            self.option_inputs.update(block['inputs'])  # Update option_inputs

    # Variable Option Input
    def _create_input_widget(self, var):
        input_type = var.get('type', 'default')                     # Get variable type
        if input_type == 'boolean':
            widget = QCheckBox()                                    # Checkbox for boolean
            widget.setChecked(bool(var.get('default', False)))      # Set default value
        elif input_type == 'range':
            widget = QDoubleSpinBox()                               # Spinbox for numeric range
            step = var.get('step', 1)                               # Step size
            widget.setSingleStep(step)                              # Set step increment
            widget.setDecimals(                                     # Set decimals
                max(0, str(step)[::-1].find('.'))                   # To whatever the step uses (e.g., 0.1 has 1 decimal place)
                if isinstance(step, float) else 0                   # Or use 0 if the step is an integer.
            )
            widget.setMinimum(var.get('min', 0))                    # Minimum value
            widget.setMaximum(var.get('max', 100))                  # Maximum value
            widget.setValue(var.get('default', var.get('min', 0)))  # Default value
        elif input_type == 'list':
            widget = QComboBox()                                    # Dropdown for list
            widget.addItems(var.get('options', []))                 # Add options
            default = var.get('default')                            # Default selection
            if default:
                idx = widget.findText(default)                      # Find default index
                if idx >= 0:
                    widget.setCurrentIndex(idx)                     # Set default selection
        else:
            widget = QLineEdit()                                    # Text input for default/unknown type
            widget.setText(str(var.get('default', '')))             # Set default text
        return widget                                               # Return created widget

    def is_selected(self):
        return self.selected.isChecked()                            # Return whether package is enabled

    # Gather All Options for Submission
    def get_options(self):
        opts = {}                                                   # Dictionary to store all options
        for block in self.session_blocks:                           # For each session block
            session_text = block['session_input'].text().strip()    # Get session number text
            if not session_text.isdigit():                          # Skip if not a number
                continue
            session_num = session_text
            for varname, widget in block['inputs'].items():         # Loop over inputs
                if isinstance(widget, QCheckBox):                   # Get value for checkbox
                    val = widget.isChecked()
                elif isinstance(widget, QComboBox):                 # Get value for combo box
                    val = widget.currentText()
                else:
                    val = widget.text()                             # Get text value
                opts[varname.replace("#", session_num)] = val       # Store option with session number replaced
        return opts

# Main Application
class PackageApp(QWidget):
    def __init__(self):
        super().__init__()                      # Initialize QWidget
        self.setWindowTitle("Package Selector") # Set window title
        self.packages = self.load_packages()    # Load package configs
        self.package_widgets = []               # List to track package widgets
        self._init_ui()                         # Build UI

    # Load YAML Packages from Directories
    def load_packages(self):
        data = {}                                           # Dictionary for packages by category
        for folder in os.listdir(PACKAGE_DIR):              # Iterate package directories
            path = os.path.join(                            # Path to config file
                PACKAGE_DIR, 
                folder, 
                CONFIGURATOR_FILENAME
            )
            if os.path.isfile(path):                        # If configurator exists (ignore package otherwise):
                with open(path, 'r') as f:
                    configurator = yaml.safe_load(f)        # Parse configurator.yaml
                    pkg = configurator.get("package", {})   # Get package info
                    if pkg.get("visible", True):            # Check if package is set to visible
                        data.setdefault(
                            pkg.get("category", "Misc"),[]  # Get its category ('Misc' by default)
                        ).append(configurator)              # Add to list of that category
        return data

    # Build Scrollable UI
    def _init_ui(self):
        layout = QVBoxLayout()                                      # Main vertical layout
        scroll_widget = QWidget()                                   # Widget inside scroll area
        scroll_layout = QVBoxLayout(scroll_widget)                  # Layout inside scroll widget

        for category, pkgs in self.packages.items():                # For each package category
            scroll_layout.addWidget(QLabel(f"<b>{category}</b>"))   # Add category label
            grid = QGridLayout()                                    # Grid layout for packages
            grid.setSpacing(10)                                     # Set spacing between widgets
            for i, pkg in enumerate(pkgs):                          # Iterate packages
                widget = PackageWidget(pkg, self)                   # Create package widget
                self.package_widgets.append(widget)                 # Track widget
                row, col = divmod(i, 3)                             # Position in grid (3 columns)
                grid.addWidget(widget, row, col)                    # Add widget to grid
            container = QWidget()                                   # Container widget for grid
            container.setLayout(grid)                               # Set grid layout
            scroll_layout.addWidget(container)                      # Add container to scroll layout

        scroll_layout.addStretch()                                  # Add stretch to push widgets up
        scroll_area = QScrollArea()                                 # Scroll area to hold all content
        scroll_area.setWidget(scroll_widget)                        # Set scroll widget
        scroll_area.setWidgetResizable(True)                        # Allow resizing
        layout.addWidget(scroll_area)                               # Add scroll area to main layout

        submit_btn = QPushButton("Submit")                          # Submit button
        submit_btn.clicked.connect(self.submit)                     # Connect submit action
        layout.addWidget(submit_btn)                                # Add button to layout

        self.setLayout(layout)                                      # Set main layout
        screen = QGuiApplication.primaryScreen().geometry()         # Get primary screen geometry
        self.resize(                                                # Resize window to 60% of screen
            int(screen.width() * 0.6), 
            int(screen.height() * 0.6)
        )

    # Handle Submit
    def submit(self):
        if not any(widget.is_selected() for widget in self.package_widgets):                            # If no packages are selected:
            QMessageBox.warning(self, "Validation Error", "Please select at least one package before submitting.")
            return                                                                                      # Submit fails.
        os.makedirs(OUTPUT_DIR, exist_ok=True)                                                          # Ensure output directory exists
        seen_sessions = set()                                                                           # Set to track session numbers
        for widget in self.package_widgets:                                                             # For each package:
            if widget.is_selected():                                                                    # Only check if selected.
                for block in widget.session_blocks:                                                     # For each session block:
                    session_val = str(block['session_input'].value())                                   # Get the session number.
                    if session_val in seen_sessions:                                                    # Check for duplicates.
                        QMessageBox.warning(self, "Validation Error", f"Duplicate session number across packages: '{session_val}'")
                        return                                                                          # Submit fails, no duplicates allowed.
                    seen_sessions.add(session_val)                                                      # Add to seen sessions.

        with open(os.path.join(OUTPUT_DIR, 'build.conf'), 'w') as f_pkg, \
             open(os.path.join(OUTPUT_DIR, 'thinstation.conf.buildtime'), 'w') as f_opt:                # Open package and options output files

            for cat, pkgs in self.packages.items():                                                     # For each category:
                widgets = [w for w in self.package_widgets if w.pkg_data in pkgs and w.is_selected()]   # Get selected packages.
                if not widgets:
                    continue                                                                            # Skip if none selected
                f_pkg.write(f"### {cat} ###\n")                                                         # Write category header
                for widget in widgets:
                    f_pkg.write(f"package {widget.pkg_data['package']['name']}\n")                      # Write package line to build.conf
                    f_opt.write(f"### {widget.pkg_data['package']['name']} ###\n")                      # Write header for package to thinstation.conf.buildtime
                    for k, v in widget.get_options().items():                                           # Write all options for package to thinstation.conf.buildtime
                        f_opt.write(f"{k}={v}\n")

        QMessageBox.information(self, "Done", "Configuration files written successfully!")              # Notify user when finished.

# Running the App
if __name__ == "__main__":
    app = QApplication(sys.argv)            # Create Qt application
    if os.path.exists(STYLE_FILE):          # Load stylesheet if exists
        with open(STYLE_FILE, "r") as f:
            app.setStyleSheet(f.read())
    window = PackageApp()                   # Create main window
    window.show()                           # Show window
    sys.exit(app.exec())                    # Start app event loop

