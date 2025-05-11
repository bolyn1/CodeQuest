from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from src.ui.main_game_window import MainGameWindow
import re

class LoginAuth(QWidget):
    """
    Login and registration screen for the user.
    Provides input fields for username and password,
    and handles login and registration logic.
    """
    def __init__(self, main_window, db_manager, is_register=False):
        super().__init__()
        self.main_window = main_window  # Reference to the main window
        self.db_manager = db_manager  # Reference to the database manager
        self.is_register = is_register  # Flag for registration mode

        """ Set window title, geometry, and styles """
        self.setWindowTitle("🔐 CodeQuest Login")
        self.setGeometry(300, 300, 420, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 14px;
                margin: 5px 0;
            }
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #555;
                border-radius: 10px;
                background-color: #3c3c3c;
                color: #fff;
            }
            QPushButton {
                padding: 12px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                background-color: #5CDB95;
                color: #1e1e1e;
                border: 2px solid #4CAF50;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        """ Layout setup with input fields and buttons """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(40, 30, 40, 30)  # Set margins
        self.layout.setSpacing(15)  # Set spacing between elements

        self.layout.addWidget(QLabel("🧑‍💻 Username"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.layout.addWidget(self.username_input)

        self.layout.addWidget(QLabel("🔑 Password"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)  # Mask password
        self.password_input.setPlaceholderText("Enter your password")
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("🚪 Login")
        self.register_button = QPushButton("📝 Register")
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

        if self.is_register:
            self.layout.addWidget(self.register_button)
        else:
            self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

    def login(self):
        """ Handle user login logic """
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            print("Username and password cannot be empty")
            return

        user_id = self.db_manager.authenticate_user(username, password)
        if user_id:
            self.close()  # Close login window
            self.main_window.open_game_window(user_id)
        else:
            print("Invalid credentials")

    def register(self):
        """ Handle user registration logic """
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Check if username and password are provided
        if not username or not password:
            self.show_error_message("Error", "Username and password cannot be empty.")
            return

        # Define password validation rules
        password_checks = [
            (len(password) >= 8, "Password must be at least 8 characters long."),
            (re.search(r"[A-Z]", password), "Password must contain at least one uppercase letter."),
            (re.search(r"[a-z]", password), "Password must contain at least one lowercase letter."),
            (re.search(r"\d", password), "Password must contain at least one digit."),
            (re.search(r"[\W_]", password), "Password must contain at least one special character (e.g., @, #, !).")
        ]

        # Run password checks
        for condition, error_msg in password_checks:
            if not condition:
                self.show_error_message("Error", error_msg)
                return

        # Check if username is already taken
        if self.db_manager.is_username_taken(username):
            self.show_error_message("Error", "Username is already taken, please choose another.")
            return

        # Add user to the database if all checks pass
        try:
            self.db_manager.add_user(username, password)
            self.show_success_message("Success", "🎉 You have successfully registered!")
            self.login()  # Automatically log in after successful registration
        except Exception as e:
            self.show_error_message("Registration Failed", f"An error occurred during registration: {str(e)}")

    def show_error_message(self, title, message):
        """ Show error message box """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def show_success_message(self, title, message):
        """ Show success message box """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
