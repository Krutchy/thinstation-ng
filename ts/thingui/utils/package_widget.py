from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton
from .option_block import OptionBlock

class PackageWidget(QWidget):
    def __init__(self, package_data, app_ref):
        super().__init__()
        self.package_data = package_data
        self.app_ref = app_ref
        self.option_blocks = []

        self.selected = QCheckBox(f"Enable {package_data['package']['name']}")
        layout = QVBoxLayout(self)
        layout.addWidget(self.selected)

        self.blocks_layout = QVBoxLayout()
        layout.addLayout(self.blocks_layout)
        layout.addStretch()

        self.build_options()

    def build_options(self):
        uses_sessions = self.package_data['package'].get("has-sessions", False)
        self.add_option_block(uses_sessions)
        if uses_sessions:
            add_btn = QPushButton("+ Add Session")
            add_btn.clicked.connect(lambda: self.add_option_block(True))
            self.blocks_layout.addWidget(add_btn)

    def add_option_block(self, uses_sessions=False):
        block = OptionBlock(self.package_data.get("variables", []), uses_sessions)
        self.option_blocks.append(block)
        self.blocks_layout.insertWidget(len(self.option_blocks) - 1, block)

    def get_options(self):
        uses_sessions = self.package_data['package'].get("has-sessions", False)
        options = {}
        for block in self.option_blocks:
            options.update(block.get_options(uses_sessions))
        return options