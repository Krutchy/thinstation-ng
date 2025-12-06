from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton, QLabel, QHBoxLayout
from .option_block import OptionBlock

class PackageWidget(QWidget):
    def __init__(self, package_data, app_ref):
        super().__init__()
        self.package_data = package_data
        self.app_ref = app_ref
        self.global_block = None
        self.session_blocks = []


        self.selected = QCheckBox(f"Enable {package_data['package']['name']}")
        layout = QVBoxLayout(self)
        layout.addWidget(self.selected)

        self.blocks_layout = QVBoxLayout()
        layout.addLayout(self.blocks_layout)
        layout.addStretch()

        self.build_options()

    def build_options(self):
        global_options = self.package_data.get("options", [])
        session_options = self.package_data.get("session_options", [])
        uses_sessions = self.package_data['package'].get("has-sessions", False)

        # Add global options at the very top
        if global_options and session_options:
            global_options_label = QLabel("Global Options")
            global_options_label.setObjectName("global_options_label")
            self.blocks_layout.addWidget(global_options_label)
        if global_options:
            self.global_block = OptionBlock(global_options, uses_sessions=False)
            self.blocks_layout.addWidget(self.global_block)

        # Add session blocks container
        if uses_sessions and session_options:
            self.add_session_block(session_options)

            # Add "Add Session" button below the session blocks
            self.add_session_btn = QPushButton("+ Add Session")
            self.add_session_btn.clicked.connect(lambda: self.add_session_block(session_options))
            self.blocks_layout.addWidget(self.add_session_btn)

    def add_session_block(self, session_options):
        container = QWidget()
        v_layout = QVBoxLayout(container)

        # Header layout with "Session #:" label, spinbox, and remove button
        header_layout = QHBoxLayout()
        session_label = QLabel("Session #:")
        header_layout.addWidget(session_label)

        # Create the session spinbox from OptionBlock if not already created
        block = OptionBlock(session_options, uses_sessions=True)
        if block.session_input:
            header_layout.addWidget(block.session_input)

        header_layout.addStretch()  # push remove button to the right
        remove_btn = QPushButton("Remove")
        header_layout.addWidget(remove_btn)
        v_layout.addLayout(header_layout)

        # Add the rest of the session options below
        v_layout.addWidget(block)

        # Connect remove button
        remove_btn.clicked.connect(lambda: self.remove_session_block(container, block))

        # Insert above the "Add Session" button if it exists
        insert_index = self.blocks_layout.count() - 1 if hasattr(self, "add_session_btn") else self.blocks_layout.count()
        self.blocks_layout.insertWidget(insert_index, container)

        self.session_blocks.append(block)

    def remove_session_block(self, container_widget, block):
        self.blocks_layout.removeWidget(container_widget)
        container_widget.setParent(None)
        if block in self.session_blocks:
            self.session_blocks.remove(block)

    def get_options(self):
        options = {}
        # Global options first
        if self.global_block:
            options.update(self.global_block.get_options())
        # Then session options
        for block in self.session_blocks:
            options.update(block.get_options(uses_sessions=True))
        return options
