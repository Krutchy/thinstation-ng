from PySide6.QtWidgets import (
    QCheckBox, QWidget, QVBoxLayout, QSpinBox, 
    QDoubleSpinBox, QComboBox, QLabel, QLineEdit
)
from .repeater_widget import RepeaterWidget

def boolean_input(var):
    """
    Creates a toggleable checkbox.

    Variables:
        @default (bool): Should option start out enabled or disabled (default: False)?
        @true_value (string): What should be written if the option is enabled instead of 'True' (e.g., 'ON')?
        @false_value (string): What should be written if the option is disabled instead of 'False' (e.g., 'OFF')?
    """
    widget = QCheckBox()
    widget.setChecked(var.get('default', False))
    widget.true_value = var.get('true_value', 'True')
    widget.false_value = var.get('false_value', 'False')

    return widget

def range_input(var):
    """
    Creates an input field with a numerical range.

    Variables:
        @step (int or float): How much does the value increment or decrement by (default: 1)?
        @min (int or float): What is the minimum allowable value (default: 0)?
        @max (int or float): What is the maximum allowable value (default: 100)?
        @default (int or float): What should the value be by default (default: min)?
    """
    step = var.get('step', 1)
    if isinstance(step, int):
        widget = QSpinBox()
    else:
        widget = QDoubleSpinBox()
    widget.setSingleStep(step)
    widget.setMinimum(var.get('min', 0))
    widget.setMaximum(var.get('max', 100))
    widget.setValue(var.get('default', var.get('min', 0)))

    return widget

def list_input(var):
    """
    Creates a dropdown field with a list of selectable values.

    Variables:
        @options (list of strings): What options can be selected?
            @name (string): What it is called (and what should be written)?
            @tooltip (string): What does the option do? Optional, and must be after a ':' (e.g., "ON:Turn this option on.").
        @default (string): What option should be selected by default, if any?
    """
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    combo = QComboBox()
    spinbox = QSpinBox()
    spinbox.setRange(0, 99)
    spinbox.setSingleStep(1)
    spinbox.setVisible(False)

    description_label = QLabel()
    description_label.setWordWrap(True)
    description_label.setObjectName("description")
    description_label.setVisible(False)

    option_map = {}
    for opt in var.get('options', []):
        if isinstance(opt, str) and ':' in opt:
            display_text, suboption_description = opt.split(':', 1)
        else:
            display_text, suboption_description = str(opt), ""
        combo.addItem(display_text)
        option_map[display_text] = suboption_description

    def on_index_changed(index):
        text = combo.itemText(index)
        # Show spinbox if option ends with "XX"
        spinbox.setVisible("XX" in text)
        # Update description
        suboption_description = option_map.get(text, "")
        description_label.setText(suboption_description)
        description_label.setVisible(bool(suboption_description))

    on_index_changed(combo.currentIndex()) # Refresh immediately to show description.
    combo.currentIndexChanged.connect(on_index_changed)

    default = var.get('default')
    if default:
        idx = combo.findText(default)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    layout.addWidget(combo)
    layout.addWidget(spinbox)
    layout.addWidget(description_label)

    combo._spinbox = spinbox
    container.combo = combo
    container.spinbox = spinbox
    container.description_label = description_label

    return container

def text_input(var):
    """
    Creates field for text input.

    Variables:
        @default (string): What should be in the text field by default (optional)?
    """
    widget = QLineEdit()
    widget.setText(str(var.get('default', '')))

    return widget

INPUT_TYPE_MAP = {
    "boolean": boolean_input,
    "checkbox": boolean_input,
    "range": range_input,
    "list": list_input,
    "dropdown": list_input,
    "text": text_input,
}

def create_input_widget(var):
    input_type = var.get('type', 'text').lower()
    factory = INPUT_TYPE_MAP.get(input_type, text_input)
    widget = factory(var)

    if var.get("repeatable", False):
        start = int(var.get("start", 0)) # What do the mounts start at?
        limit = int(var.get("limit", 0)) # 0 means there is no limit.
        if (start > limit): raise ValueError(f"Start value {start} exceeds limit value {limit} for a repeatable option.")
        return RepeaterWidget(lambda: factory(var), label_text=var.get("name"), start=start, limit=limit)

    return widget

