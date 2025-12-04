from PySide6.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox
)
from PySide6.QtCore import Qt
from .input_widget import input_widget

class PackageWidget(QGroupBox):
    def __init__(self, package_data, app_ref):
        super().__init__(package_data['package']['name'])
        self.package_data = package_data
        self.app_ref = app_ref
        self.option_inputs = {}
        self.session_blocks = []

        self.selected = QCheckBox("Enable")
        self.options_frame = QWidget()
        self.options_frame.setLayout(QVBoxLayout())
        self.options_frame.setVisible(False)

        self._build_header()
        self._build_options()

        layout = QVBoxLayout()
        layout.addLayout(self.header_layout)
        layout.addWidget(self.options_frame)
        self.setLayout(layout)
        self.setMaximumWidth(500)

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
    
    def is_selected(self):
        return self.selected.isChecked()

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
        if uses_sessions:
            header_layout = QHBoxLayout()
            session_input = QSpinBox()
            session_input.setMinimum(0)
            session_input.setSingleStep(1)
            session_input.setFixedWidth(80)
            header_layout.addWidget(QLabel("Session:"))
            header_layout.addWidget(session_input)
            header_layout.addStretch()
            layout.addLayout(header_layout)

        inputs = {v['name']: self._create_input_widget(v) for v in self.package_data.get("variables", [])}
        for name, widget in inputs.items():
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.addWidget(QLabel(name))
            row_layout.addWidget(widget)
            layout.addWidget(row)

        self.option_inputs.update(inputs)
        self.session_blocks.append({
            "widget": container,
            "session_input": session_input,
            "inputs": inputs
        })
        self.options_frame.layout().insertWidget(len(self.session_blocks)-1, container)

    def _create_input_widget(self, var):
        return input_widget(var)

    def get_options(self):
        # Gather options from all session blocks
        options = {}
        uses_sessions = self.package_data['package'].get('has-sessions', False)
        for block in self.session_blocks:
            session_num = "-1" if not uses_sessions else str(block['session_input'].value())
            for name, widget in block['inputs'].items():
                if isinstance(widget, QCheckBox):
                    value = widget.true_value if widget.isChecked() else widget.false_value
                elif isinstance(widget, QComboBox):
                    value = widget.currentText()
                elif hasattr(widget, "values"):
                    value = widget.values()
                elif hasattr(widget, "text"):
                    value = widget.text().strip()
                else:
                    value = None
                if value is None or value == "":
                    continue
                if isinstance(value, list):
                    for i, v in enumerate(value):
                        options[name.replace("#", str(i))] = v
                else:
                    key = name if not uses_sessions else name.replace("#", session_num)
                    options[key] = value
        return options