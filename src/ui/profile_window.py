from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt


class ProfileWindow(QWidget):
    def __init__(self, user_id, db_manager):
        """ Initializes the ProfileWindow and sets up the user profile view. """
        super().__init__()
        self.user_id = user_id
        self.db_manager = db_manager

        self.setWindowTitle("User Profile")
        self.setGeometry(300, 300, 500, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # User statistics labels
        self.xp_label = QLabel("XP: ")
        self.level_label = QLabel("Level: ")
        self.layout.addWidget(self.xp_label)
        self.layout.addWidget(self.level_label)

        # Inventory section header
        self.inventory_label = QLabel("Inventory:")
        self.inventory_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.layout.addWidget(self.inventory_label)

        # Scrollable area for inventory items
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.layout.addWidget(self.scroll_area)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.update_profile)
        self.layout.addWidget(refresh_btn)

        # Initial profile update
        self.update_profile()

    def update_profile(self):
        """ Updates the user profile information such as XP and level. """
        progress = self.db_manager.get_user_progress(self.user_id)
        if progress:
            xp, level = progress
            self.xp_label.setText(f"XP: {xp}")
            self.level_label.setText(f"Level: {level}")
        self.display_inventory()

    def display_inventory(self):
        """ Displays the user's inventory in the scrollable area. """
        # Clear old widgets
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        items = self.db_manager.get_user_inventory(self.user_id)
        if not items:
            empty_label = QLabel("No items found in inventory.")
            empty_label.setStyleSheet("color: gray;")
            self.scroll_layout.addWidget(empty_label)
            return

        # Display each inventory item
        for name, item_type in items:
            item_widget = self.create_inventory_item_widget(name, item_type)
            self.scroll_layout.addWidget(item_widget)

    def create_inventory_item_widget(self, name, item_type):
        """ Creates a stylish widget to represent an item in the inventory. """
        item_frame = QFrame()
        item_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.get_background_color(item_type)};
                border-radius: 12px;
                padding: 12px;
                margin-bottom: 8px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
            }}
        """)

        layout = QHBoxLayout(item_frame)

        # Icon based on the item type
        icon = self.get_icon_for_type(item_type)
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px; margin-right: 10px;")
        layout.addWidget(icon_label)

        # Item name and type
        text_layout = QVBoxLayout()
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        type_label = QLabel(f"Type: {item_type}")
        type_label.setStyleSheet("color: #333; font-size: 12px;")

        text_layout.addWidget(name_label)
        text_layout.addWidget(type_label)
        layout.addLayout(text_layout)

        return item_frame

    def get_background_color(self, item_type):
        """ Returns a background color based on the item type. """
        colors = {
            "Reward": "#e6ffe6",  # Light green
            "Tool": "#e6f0ff",  # Light blue
            "Potion": "#fff0f5",  # Light pink
            "Key": "#fff5e6",  # Light orange
            "Scroll": "#f5f5dc",  # Beige
        }
        return colors.get(item_type, "#f9f9f9")
