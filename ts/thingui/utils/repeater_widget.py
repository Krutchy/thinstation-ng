from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Qt

class RepeaterWidget(QWidget):
    def __init__(self, widget_factory, label_text=None, start=0, limit=0):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.rows = []
        self.widget_factory = widget_factory

        self.start = int(start) # What do the mounts start at?
        self.limit = int(limit) # 0 means there is no limit.

        self.add_btn = QPushButton(f"+Add {label_text or ''}")
        self.add_btn.clicked.connect(lambda: self.add_row())
        self.layout.addWidget(self.add_btn)

        self.add_row() # Create initial first row.

    def add_row(self, input_widget=None):
        if self.limit > 0 and len(self.rows) >= self.limit:
            # Note that this isn't expected to happen, since
            # the add button is disabled. This is just here for safety.
            QMessageBox.information(self, f"Cannot add beyond limit {self.limit}.")
            return

        if input_widget is None:
            input_widget = self.widget_factory() if callable(self.widget_factory) else QLineEdit()

        row = QWidget()
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 0, 0, 0)

        index_label = QLabel()
        index_label.setFixedWidth(25)
        index_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        remove_btn = QPushButton("Remove")
        remove_btn.setFixedWidth(70)
        remove_btn.clicked.connect(lambda _, r=row: self.remove_row(r))

        hl.addWidget(index_label)
        hl.addWidget(input_widget)
        hl.addWidget(remove_btn)

        self.rows.append((row, input_widget, index_label))
        self.layout.insertWidget(self.layout.count() - 1, row)

        self._update_indices()

        if self.limit > 0 and len(self.rows) >= self.limit:
            self.add_btn.setVisible(False)

    def remove_row(self, row):
        for i, (r, _, _) in enumerate(self.rows):
            if r == row:
                self.rows.pop(i)
                break
        row.setParent(None)

        self._update_indices()

        if self.limit > 0 and len(self.rows) < self.limit:
            self.add_btn.setVisible(True)

    def _update_indices(self):
        n = self.start
        for (_, _, index_label) in self.rows:
            index_label.setText(str(n))
            n += 1

    def values(self):
        vals = []
        for _, widget, _ in self.rows:
            if hasattr(widget, "text"):
                val = widget.text().strip()
            elif hasattr(widget, "currentText"):
                val = widget.currentText().strip()
            elif hasattr(widget, "value"):
                val = str(widget.value())
            else:
                continue
            if val:
                vals.append(val)
        return vals
