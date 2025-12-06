from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QHBoxLayout, QSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt
from .input_widget import create_input_widget

class OptionBlock(QWidget):
    def __init__(self, options, uses_sessions=False):
        super().__init__()
        self.options = options
        self.uses_sessions = uses_sessions
        self.session_input = None
        self.inputs = {}

        layout = QVBoxLayout(self)

        if uses_sessions:
            header = QHBoxLayout()
            self.session_input = QSpinBox()
            self.session_input.setMinimum(0)
            self.session_input.setFixedWidth(80)
            header.addWidget(self.session_input)
            header.addStretch()
            layout.addLayout(header)

        grid = QGridLayout()
        row = 0
        for opt in options:
            name = opt['name']
            widget = create_input_widget(opt)
            self.inputs[name] = widget

            label = QLabel(name)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            grid.addWidget(label, row, 0, Qt.AlignLeft)
            grid.addWidget(widget, row, 1, alignment=Qt.AlignRight)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            row += 1

            description = opt.get("description")
            if description:
                desc_label = QLabel(description)
                desc_label.setWordWrap(True)
                desc_label.setObjectName("description")
                desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                grid.addWidget(desc_label, row, 0, 1, 2)  # Span both columns.
                row += 1

        layout.addLayout(grid)

    def get_options(self, uses_sessions=False):
        """
        Returns a dict of options.
        """
        if not hasattr(self, "inputs") or self.inputs is None:
            return {}

        session_num = str(self.session_input.value()) if self.session_input else "-1"
        options = {}

        for name, widget in self.inputs.items():
            value = None

            # Boolean
            if hasattr(widget, "isChecked"):
                value = widget.true_value if widget.isChecked() else widget.false_value
            # Repeatable
            elif hasattr(widget, "values"):
                vals = widget.values()
                for i, v in enumerate(vals):
                    key = name.replace("#", str(i)) if "#" in name else f"{name}{i}"
                    if uses_sessions:
                        key = key.replace("#", session_num)
                    options[key] = v
                continue
            # List with "XX" value (e.g., "MENUXX")
            elif hasattr(widget, "combo"):
                value = widget.combo.currentText()
                if "XX" in value and hasattr(widget, "spinbox") and widget.spinbox.isVisible():
                    value = value.replace("XX", f"{int(widget.spinbox.value()):02d}")
            # List
            elif hasattr(widget, "currentText"):
                value = widget.currentText()
            # Text
            elif hasattr(widget, "text"):
                value = widget.text().strip()
            if value is None or value == "":
                continue

            key = name
            if uses_sessions and "#" in key:
                key = key.replace("#", session_num)
            options[key] = value

        return options
