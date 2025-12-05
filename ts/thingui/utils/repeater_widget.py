from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton

class RepeaterWidget(QWidget):
    def __init__(self, label_text):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.rows = []

        add_btn = QPushButton(f"+Add {label_text}")
        add_btn.clicked.connect(self.add_row)
        self.layout.addWidget(add_btn)

    def add_row(self, default=None):
        row = QWidget()
        hl = QHBoxLayout(row)

        edit_field = QLineEdit()
        edit_field.setText("" if default is None else str(default))

        remove_btn = QPushButton("Remove")
        remove_btn.setFixedWidth(70)
        remove_btn.clicked.connect(lambda: self.remove_row(row))

        hl.addWidget(edit_field)
        hl.addWidget(remove_btn)
        self.rows.append(edit_field)
        self.layout.insertWidget(self.layout.count() - 1, row)

    def remove_row(self, row):
        for index, e in enumerate(self.rows):
            if e.parent() == row:
                self.rows.pop(index)
                break
        row.setParent(None)

    def values(self):
        return [row.text().strip() for row in self.rows if row.text().strip()]
