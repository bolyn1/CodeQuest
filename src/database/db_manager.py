import sqlite3
import bcrypt
from typing import Optional, Tuple, List


class DBManager:
    """Handles all database operations, including user authentication, leaderboard management,
    inventory management, quiz attempt tracking, and challenges."""

    def __init__(self, db_name: str = "codequest.db"):
        """Initializes the database connection and sets up tables if they do not exist."""
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._initialize_database()

    def _initialize_database(self):
        """Creates necessary database tables with proper constraints if they do not exist."""
        try:
            # Enable foreign key support
            self.cursor.execute('PRAGMA foreign_keys = ON;')

            # Create users table
            self.cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    xp INTEGER DEFAULT 0 CHECK(xp >= 0),
                    level INTEGER DEFAULT 1 CHECK(level >= 1),
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create leaderboard table
            self.cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS leaderboard (
                    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    xp INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0 CHECK(wins >= 0),
                    losses INTEGER DEFAULT 0 CHECK(losses >= 0),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create inventory table
            self.cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    item_name TEXT NOT NULL,
                    item_type TEXT NOT NULL,
                    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create xp_transactions table to track quiz attempts
            self.cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS xp_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    amount INTEGER NOT NULL,
                    difficulty TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, difficulty, level)
                )
            ''')

            # Create challenges table
            self.cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    reward_xp INTEGER DEFAULT 0,
                    is_completed INTEGER DEFAULT 0 CHECK(is_completed IN (0, 1)),
                    week_start DATE NOT NULL
                )
            ''')

            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Database initialization failed: {e}")

    def add_user(self, username: str, password: str) -> Optional[int]:
        """Adds a new user with a hashed password and returns the user ID."""
        try:
            if self.is_username_taken(username):
                return None

            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.cursor.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error:
            self.connection.rollback()
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        """Authenticates the user and returns the user ID if the credentials are valid."""
        try:
            self.cursor.execute(
                'SELECT id, password_hash FROM users WHERE username = ?',
                (username,))
            result = self.cursor.fetchone()
            if result and bcrypt.checkpw(password.encode('utf-8'), result[1]):
                return result[0]
            return None
        except sqlite3.Error:
            return None

    def get_user_progress(self, user_id: int) -> Optional[Tuple[int, int]]:
        """Fetches the user's current XP and level."""
        try:
            self.cursor.execute(
                'SELECT xp, level FROM users WHERE id = ?',
                (user_id,))
            return self.cursor.fetchone()
        except sqlite3.Error:
            return None

    def update_xp(self, user_id: int, xp_delta: int) -> bool:
        """Updates the user's XP and leaderboard position (used for non-quiz XP sources)."""
        try:
            self.cursor.execute('BEGIN TRANSACTION')

            # Update user's XP
            self.cursor.execute(
                'UPDATE users SET xp = xp + ? WHERE id = ?',
                (xp_delta, user_id))

            # Update the leaderboard table
            self.cursor.execute(
                '''INSERT OR IGNORE INTO leaderboard (user_id) VALUES (?)''',
                (user_id,))
            self.cursor.execute(
                '''UPDATE leaderboard SET xp = (SELECT xp FROM users WHERE id = ?)
                   WHERE user_id = ?''',
                (user_id, user_id))

            self.connection.commit()
            return True
        except sqlite3.Error:
            self.connection.rollback()
            return False

    def update_level(self, user_id: int, new_level: int) -> bool:
        """Updates the user's level."""
        try:
            self.cursor.execute(
                'UPDATE users SET level = ? WHERE id = ?',
                (new_level, user_id))
            self.connection.commit()
            return True
        except sqlite3.Error:
            self.connection.rollback()
            return False

    def update_stats(self, user_id: int, win: bool = False, loss: bool = False) -> bool:
        """Updates the user's game statistics (wins and losses)."""
        try:
            # Ensure user exists in leaderboard
            self.cursor.execute(
                '''INSERT OR IGNORE INTO leaderboard (user_id) VALUES (?)''',
                (user_id,))

            if win:
                self.cursor.execute(
                    'UPDATE leaderboard SET wins = wins + 1 WHERE user_id = ?',
                    (user_id,))
            elif loss:
                self.cursor.execute(
                    'UPDATE leaderboard SET losses = losses + 1 WHERE user_id = ?',
                    (user_id,))

            self.connection.commit()
            return True
        except sqlite3.Error:
            self.connection.rollback()
            return False

    def add_inventory_item(self, user_id: int, item_name: str, item_type: str) -> bool:
        """Adds an item to the user's inventory."""
        try:
            self.cursor.execute(
                '''INSERT INTO inventory (user_id, item_name, item_type)
                   VALUES (?, ?, ?)''',
                (user_id, item_name, item_type))
            self.connection.commit()
            return True
        except sqlite3.Error:
            self.connection.rollback()
            return False

    def get_user_inventory(self, user_id) -> List[Tuple[str, str]]:
        """Fetches the items in a user's inventory."""
        try:
            self.cursor.execute(
                '''SELECT item_name, item_type FROM inventory
                   WHERE user_id = ? ORDER BY acquired_at DESC''',
                (user_id,))
            return self.cursor.fetchall()
        except sqlite3.Error:
            return []

    def is_username_taken(self, username: str) -> bool:
        """Checks if the username is already taken."""
        try:
            self.cursor.execute(
                'SELECT 1 FROM users WHERE username = ?',
                (username,))
            return bool(self.cursor.fetchone())
        except sqlite3.Error:
            return False

    def get_leaderboard(self, limit: int = 10) -> List[Tuple[str, int, int, int]]:
        """Fetches the leaderboard, sorted by XP, wins, and losses."""
        try:
            self.cursor.execute(''' 
                SELECT u.username, l.xp, l.wins, l.losses
                FROM leaderboard l
                JOIN users u ON u.id = l.user_id
                ORDER BY l.xp DESC, l.wins DESC, l.losses ASC
                LIMIT ? 
            ''', (limit,))
            return self.cursor.fetchall()
        except sqlite3.Error:
            return []

    def get_weekly_challenges(self) -> List[Tuple[int, str, str, int, int]]:
        """Fetches the current week's challenges."""
        try:
            self.cursor.execute(''' 
                SELECT id, title, description, reward_xp, is_completed
                FROM challenges
                WHERE week_start = date('now', 'weekday 0', '-7 days')
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error:
            return []

    def mark_challenge_completed(self, challenge_id: int) -> bool:
        """Marks a challenge as completed."""
        try:
            self.cursor.execute(
                'UPDATE challenges SET is_completed = 1 WHERE id = ?',
                (challenge_id,))
            self.connection.commit()
            return True
        except sqlite3.Error:
            self.connection.rollback()
            return False

    def record_quiz_attempt(self, user_id: int, xp: int, difficulty: str, level: int) -> bool:
        """Records a quiz attempt, ensuring only the highest XP attempt per level is saved."""
        try:
            self.cursor.execute('BEGIN TRANSACTION')

            # Check for existing attempts
            self.cursor.execute(''' 
                SELECT amount FROM xp_transactions
                WHERE user_id = ? AND difficulty = ? AND level = ?
            ''', (user_id, difficulty, level))
            existing = self.cursor.fetchone()

            if existing:
                # Update if new attempt is better
                if xp > existing[0]:
                    self.cursor.execute(''' 
                        UPDATE xp_transactions 
                        SET amount = ?, timestamp = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND difficulty = ? AND level = ?
                    ''', (xp, user_id, difficulty, level))
            else:
                # Insert new attempt if none exists
                self.cursor.execute(''' 
                    INSERT INTO xp_transactions
                    (user_id, amount, difficulty, level)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, xp, difficulty, level))

            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"[DB] Error recording quiz attempt: {e}")
            self.connection.rollback()
            return False

    def get_best_quiz_attempt(self, user_id: int, difficulty: str, level: int):
        """Fetches the best quiz attempt for a user at a specific difficulty and level."""
        try:
            self.cursor.execute(''' 
                SELECT amount FROM xp_transactions
                WHERE user_id = ? AND difficulty = ? AND level = ?
            ''', (user_id, difficulty, level))
            row = self.cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            print(f"[DB] Error fetching best attempt: {e}")
            return None

    def close(self):
        """Closes the database connection."""
        try:
            if self.connection:
                self.connection.close()
        except sqlite3.Error:
            pass