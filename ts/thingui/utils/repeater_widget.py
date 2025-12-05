from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton

class RepeaterWidget(QWidget):
    def __init__(self, widget_factory, label_text):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.rows = []
        self.widget_factory = widget_factory

        add_btn = QPushButton(f"+Add")
        add_btn.clicked.connect(lambda: self.add_row())
        self.layout.addWidget(add_btn)

    def add_row(self, input_widget=None):
        if isinstance(input_widget, bool):
            input_widget = None

        if input_widget is None:
            if callable(self.widget_factory):
                input_widget = self.widget_factory()
            else:
                input_widget = QLineEdit()

        row = QWidget()
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 0, 0, 0)

        remove_btn = QPushButton("Remove")
        remove_btn.setFixedWidth(70)
        remove_btn.clicked.connect(lambda _, r=row: self.remove_row(r))

        hl.addWidget(input_widget)
        hl.addWidget(remove_btn)

        self.rows.append((row, input_widget))
        self.layout.insertWidget(self.layout.count() - 1, row)

    def remove_row(self, row):
        for i, (r, _) in enumerate(self.rows):
            if r == row:
                self.rows.pop(i)
                break
        row.setParent(None)

    def values(self):
        vals = []
        for _, widget in self.rows:
            if hasattr(widget, "text"):
                text = widget.text().strip()
            elif hasattr(widget, "currentText"):
                text = widget.currentText().strip()
            elif hasattr(widget, "value"):
                text = str(widget.value())
            else:
                continue

            if text:
                vals.append(text)

        return vals
