from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QComboBox, QLabel, QLineEdit
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
        @max (int or float): What is the maximum allowable value (default: 0)?
        @default (int or float): What should the value be by default (default: min if exists, else 0)?
    """
    widget = QDoubleSpinBox()
    widget.setSingleStep(var.get('step', 1))
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
            @tooltip (string): What does the option do? This is optional, and when given should be delimited from name by a ':' (e.g., "ON:Turn this option on.").
        @default (string): What option should be selected by default, if any?
    """
    widget = QComboBox()
    for opt in var.get('options', []):
        if isinstance(opt, str) and ':' in opt:
            display_text, tooltip = opt.split(':', 1)
        else:
            display_text, tooltip = str(opt), ""
        widget.addItem(display_text)
    default = var.get('default')
    if default:
        idx = widget.findText(default)
        if idx >= 0:
            widget.setCurrentIndex(idx)

    return widget

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

def _create_input_widget(var):
    """
    Returns a widget for a variable. Handles repeater case.
    """

    if var['name'].endswith("#"):
        # Use RepeaterWidget but delegate row creation to normal type
        base_name = var['name'][:-1]
        repeater = RepeaterWidget(base_name)
        default = var.get('default', None)
        input_type = var.get('type', 'text')
        factory = INPUT_TYPE_MAP.get(input_type, text_input)

        if isinstance(default, list):
            for d in default:
                repeater.add_row(factory({'name': base_name, 'default': d, **var}))
        elif default is not None:
            repeater.add_row(factory({'name': base_name, 'default': default, **var}))

        return repeater

    input_type = var.get('type', 'text').lower()
    if input_type in INPUT_TYPE_MAP:
        return INPUT_TYPE_MAP[input_type](var)
    else:
        raise ValueError(f"Unknown input type: {input_type}")
