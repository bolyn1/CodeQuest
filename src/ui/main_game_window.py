from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from src.ui.profile_window import ProfileWindow
from src.game.game_window import GameWindow
from src.ui.leaderboard_window import LeaderboardWindow
from src.ui.challenges_window import ChallengesWindow

class MainGameWindow(QWidget):
    """
    Main game window after user logs in.
    Provides navigation to game, profile, challenges, and leaderboard.
    """
    def __init__(self, user_id, db_manager):
        super().__init__()
        self.user_id = user_id
        self.db_manager = db_manager
        self.game_window = None

        """ Set window title and geometry """
        self.setWindowTitle("CodeQuest - Main Game Window")
        self.setGeometry(300, 300, 500, 400)
        self.init_ui()

    def init_ui(self):
        """ Create layout and navigation buttons """
        self.layout = QVBoxLayout()
        self.welcome_label = QLabel("Welcome to CodeQuest!", self)
        self.layout.addWidget(self.welcome_label)

        self.start_game_button = QPushButton("Start Game", self)
        self.start_game_button.clicked.connect(self.start_game)
        self.layout.addWidget(self.start_game_button)

        self.profile_button = QPushButton("Profile", self)
        self.profile_button.clicked.connect(self.open_profile)
        self.layout.addWidget(self.profile_button)

        self.challenges_button = QPushButton("Challenges", self)
        self.challenges_button.clicked.connect(self.open_challenges)
        self.layout.addWidget(self.challenges_button)

        self.leaderboard_button = QPushButton("Leaderboard", self)
        self.leaderboard_button.clicked.connect(self.open_leaderboard)
        self.layout.addWidget(self.leaderboard_button)

        self.exit_button = QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.close)
        self.layout.addWidget(self.exit_button)

        self.setLayout(self.layout)

    def start_game(self):
        """ Start the game by opening the game window """
        if not self.game_window:
            self.game_window = GameWindow(self.user_id, self.db_manager, parent=self)
        self.game_window.show()
        self.hide()

    def open_profile(self):
        """ Open the user's profile window """
        self.profile_window = ProfileWindow(self.user_id, self.db_manager)
        self.profile_window.show()

    def open_challenges(self):
        """ Open the challenges window """
        self.challenges_window = ChallengesWindow(self.user_id, self.db_manager)
        self.challenges_window.show()

    def open_leaderboard(self):
        """ Open the leaderboard window """
        self.leaderboard_window = LeaderboardWindow(self.db_manager)
        self.leaderboard_window.show()

    def closeEvent(self, event):
        """ Handle window close event """
        if self.game_window:
            self.game_window.close()
        event.accept()
