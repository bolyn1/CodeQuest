import re  # Regular expressions for pattern matching
class AuthManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def authenticate_user(self, username, password):
        return self.db_manager.authenticate_user(username, password)

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
        self.show_success_message("Success", "User registered successfully!")
        self.login()  # Automatically log in after successful registration
    except Exception as e:
        self.show_error_message("Registration Failed", f"An error occurred during registration: {str(e)}")
