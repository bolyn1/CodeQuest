from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from src.database.db_manager import DBManager


class LeaderboardWindow(QWidget):
    def __init__(self, db_manager: DBManager):
        super().__init__()

        self.db_manager = db_manager
        self.setWindowTitle("Leaderboard")
        self.setGeometry(300, 300, 500, 500)  # Slightly larger window

        # Apply QSS styling
        self.setStyleSheet("""
            LeaderboardWindow {
                background-color: #2e2e2e;
                border-radius: 15px;
            }

            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: #5CDB95;
                padding: 10px;
                text-align: center;
                margin-bottom: 20px;
            }

            QListWidget {
                background-color: #333333;
                border-radius: 12px;
                padding: 15px;
                font-size: 16px;
                color: #e0e0e0;
                border: 1px solid #444444;
                outline: 0;
            }

            QListWidget::item {
                background-color: #3a3a3a;
                border-radius: 8px;
                padding: 12px;
                margin: 5px 0;
            }

            QListWidget::item:hover {
                background-color: #444444;
            }

            QListWidget::item:selected {
                background-color: #5CDB95;
                color: #2e2e2e;
            }

            QScrollBar:vertical {
                border: none;
                background: #333333;
                width: 10px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #5CDB95;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Title label with ID for specific styling
        self.title_label = QLabel("Leaderboard", self)
        self.title_label.setObjectName("title")
        self.layout.addWidget(self.title_label)

        # Leaderboard list
        self.leaderboard_list = QListWidget(self)
        self.leaderboard_list.setAlternatingRowColors(True)
        self.layout.addWidget(self.leaderboard_list)

        # Get leaderboard data
        leaderboard = self.db_manager.get_leaderboard()

        # Add formatted items to the list
        for username, xp, wins, losses in leaderboard:
            item_text = f"👑 {username}   •   XP: {xp}   •   Wins: {wins}   •   Losses: {losses}"
            self.leaderboard_list.addItem(item_text)

        self.setLayout(self.layout)