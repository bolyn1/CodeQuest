from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox, QListWidgetItem
from PyQt5.QtCore import Qt


class ChallengesWindow(QWidget):
    """
    Displays the weekly challenges for the user.
    Allows refreshing and viewing available challenges.
    """
    def __init__(self, user_id, db_manager):
        super().__init__()
        self.user_id = user_id
        self.db_manager = db_manager

        """ Set window title, geometry, and style """
        self.setWindowTitle("🔥 Weekly Challenges")
        self.setGeometry(350, 350, 550, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: #e0e0e0;
            }
            QLabel {
                font-size: 26px;
                font-weight: bold;
                color: #FFA726;  /* Fire emoji color */
                text-align: center;
            }
            QListWidget {
                background-color: #333333;
                font-size: 16px;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton {
                background-color: #5CDB95;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
        """)

        """ Create layout and add widgets """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.setSpacing(20)

        self.title_label = QLabel("🔥 Weekly Challenges", self)
        self.layout.addWidget(self.title_label)

        self.challenges_list = QListWidget(self)
        self.layout.addWidget(self.challenges_list)

        self.refresh_button = QPushButton("🔄 Refresh Challenges", self)
        self.refresh_button.clicked.connect(self.load_challenges)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)
        self.load_challenges()

    def load_challenges(self):
        """ Load challenges from the database and display them """
        self.challenges_list.clear()
        challenges = self.db_manager.get_weekly_challenges()

        if not challenges:
            empty_item = QListWidgetItem("✨ No challenges available yet. Check back soon!")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsSelectable)
            self.challenges_list.addItem(empty_item)
        else:
            for name, description, xp in challenges:
                item = QListWidgetItem()
                item.setText(f"🏆 {name}\n{description}\nXP Reward: +{xp}")
                item.setData(Qt.UserRole, (name, description, xp))
                self.challenges_list.addItem(item)
