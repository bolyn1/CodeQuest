class AuthManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def authenticate_user(self, username, password):
        return self.db_manager.authenticate_user(username, password)
