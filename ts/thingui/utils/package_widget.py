from PySide6.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt
from .input_widget import create_input_widget

class PackageWidget(QGroupBox):
    def __init__(self, package_data, app_ref):
        super().__init__(package_data['package']['name'])
        self.package_data = package_data
        self.app_ref = app_ref
        self.option_inputs = {}
        self.session_blocks = []

        self.selected = QCheckBox("Enable")
        self.selected.setObjectName("selection_checkbox")
        self.options_frame = QWidget()
        self.options_frame.setLayout(QVBoxLayout())
        self.options_frame.setVisible(False)
        self._build_header()
        self._build_options()

        layout = QVBoxLayout()
        layout.addLayout(self.header_layout)
        layout.addWidget(self.options_frame)
        self.setLayout(layout)
        self.setMaximumWidth(350)

    def _build_header(self):
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.selected)
        self.header_layout.addStretch()

        self.toggle_btn = QPushButton("\u25BC")
        self.toggle_btn.setFixedWidth(30)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self._toggle_options)
        self.header_layout.addWidget(self.toggle_btn)

    def _toggle_options(self):
        expanded = self.toggle_btn.isChecked()
        self.options_frame.setVisible(expanded)
        self.toggle_btn.setText("\u25B2" if expanded else "\u25BC")

    def _build_options(self):
        uses_sessions = self.package_data['package'].get('has-sessions', False)
        self._add_option_block(uses_sessions=uses_sessions)

        if uses_sessions:
            add_session_btn = QPushButton("+Add Session")
            add_session_btn.clicked.connect(lambda: self._add_option_block(uses_sessions=True))
            self.options_frame.layout().addWidget(add_session_btn)

    def _add_option_block(self, uses_sessions=False):
        container = QWidget()
        layout = QVBoxLayout(container)

        session_input = None
        header_layout = None
        if uses_sessions:
            header_layout = QHBoxLayout()
            session_input = QSpinBox()
            session_input.setMinimum(0)
            session_input.setSingleStep(1)
            session_input.setFixedWidth(80)
            header_layout.addWidget(QLabel("Session:"))
            header_layout.addWidget(session_input)
            header_layout.addStretch()

            # Add Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.setFixedWidth(70)
            remove_btn.clicked.connect(lambda _, c=container: self._remove_session_block(c))
            header_layout.addWidget(remove_btn)

            layout.addLayout(header_layout)

        inputs = {v['name']: create_input_widget(v) for v in self.package_data.get("variables", [])}
        for v in self.package_data.get("variables", []):
            name = v['name']
            widget_container = inputs[name]

            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            name_label = QLabel(name)
            row_layout.addWidget(name_label)
            row_layout.addWidget(widget_container)
            layout.addWidget(row)

            description = v.get("description", None)
            if description:
                description_label = QLabel(description)
                description_label.setObjectName("description")
                description_label.setWordWrap(True)
                layout.addWidget(description_label)

        self.option_inputs.update(inputs)
        self.session_blocks.append({
            "widget": container,
            "session_input": session_input,
            "inputs": inputs
        })
        self.options_frame.layout().insertWidget(len(self.session_blocks)-1, container)

    def _remove_session_block(self, container):
        # Find the block in session_blocks
        for i, block in enumerate(self.session_blocks):
            if block['widget'] == container:
                self.session_blocks.pop(i)
                break
        # Remove from layout
        self.options_frame.layout().removeWidget(container)
        container.setParent(None)

    def get_options(self):
        # Gather options from all session blocks
        options = {}
        uses_sessions = self.package_data['package'].get('has-sessions', False)
        
        for block in self.session_blocks:
            session_num = "-1" if not uses_sessions else str(block['session_input'].value())
            for name, widget in block['inputs'].items():
                value = None

                # QCheckBox
                if isinstance(widget, QCheckBox):
                    value = widget.true_value if widget.isChecked() else widget.false_value

                # Container widget for list_input with combo and optional spinbox
                elif isinstance(widget, QWidget) and hasattr(widget, "combo"):
                    combo = widget.combo
                    value = combo.currentText()
                    # Replace XX with spinbox value if visible
                    if "XX" in value and hasattr(widget, "spinbox") and widget.spinbox.isVisible():
                        value = value.replace("XX", f"{int(widget.spinbox.value()):02d}")

                # QComboBox directly (if not using container)
                elif isinstance(widget, QComboBox):
                    value = widget.currentText()

                # Has text() method (QLineEdit, etc.)
                elif hasattr(widget, "text"):
                    value = widget.text().strip()

                # Has values() method
                elif hasattr(widget, "values"):
                    value = widget.values()

                if value is None or value == "":
                    continue

                if isinstance(value, list):
                    for i, v in enumerate(value):
                        options[name.replace("#", str(i))] = v
                else:
                    key = name if not uses_sessions else name.replace("#", session_num)
                    options[key] = value

        return options
