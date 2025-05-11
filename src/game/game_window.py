from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget,
    QGridLayout, QLineEdit, QTextEdit, QDialog, QProgressBar
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont
import json, os, random


class GameWindow(QWidget):
    MAX_ATTEMPTS = 0

    def __init__(self, user_id, db_manager, parent=None):
        super().__init__()
        self.user_id = user_id
        self.db_manager = db_manager
        self.parent = parent

        self.difficulty = None
        self.level = None
        self.questions = []
        self.current_question_index = 0
        self.option_widgets = []
        self.attempts = 0
        self.session_xp = 0

        self.stacked_widget = QStackedWidget()
        self.answered_questions = set()
        self.result_shown = False

        self.init_difficulty_screen()
        self.init_level_selection_screen()
        self.init_quiz_screen()
        self.init_result_screen()

        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self.stacked_widget.setCurrentIndex(0)

    """
    ---------------------------
    Screen Initialization
    ---------------------------
    """
    def init_difficulty_screen(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("🎯 Select Difficulty Level:")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)

        for diff, icon in zip(["Easy", "Medium", "Hard"], ["🧩", "⚙️", "🔥"]):
            btn = QPushButton(f"{icon} {diff}")
            btn.clicked.connect(lambda _, d=diff.lower(): self.select_difficulty(d))
            layout.addWidget(btn)

        back_btn = QPushButton("🔙 Back to Main Menu")
        back_btn.clicked.connect(self.return_to_main_menu)
        layout.addWidget(back_btn)

        self.stacked_widget.addWidget(page)

    def init_level_selection_screen(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setAlignment(Qt.AlignCenter)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        grid_layout.setAlignment(Qt.AlignCenter)

        level = 1
        for row in range(2):
            for col in range(3):
                btn = QPushButton(f"{level}")
                btn.setFont(QFont("Arial", 16, QFont.Bold))
                btn.setFixedSize(QSize(80, 80))
                btn.setStyleSheet(""" 
                    QPushButton { 
                        background-color: #2d2d2d; 
                        color: white; 
                        border: 2px solid #00ffcc; 
                        border-radius: 10px; 
                    } 
                    QPushButton:hover { 
                        background-color: #00ffcc; 
                        color: black; 
                    } 
                """)
                btn.clicked.connect(lambda _, lvl=level: self.start_quiz(lvl))
                grid_layout.addWidget(btn, row, col)
                level += 1

        main_layout.addLayout(grid_layout)

        back_btn = QPushButton("🔙 Back to Difficulty")
        back_btn.setFont(QFont("Arial", 14, QFont.Bold))
        back_btn.setFixedHeight(40)
        back_btn.setStyleSheet(""" 
            QPushButton { 
                background-color: #444; 
                color: white; 
                border: 2px solid #888; 
                border-radius: 8px; 
            } 
            QPushButton:hover { 
                background-color: #888; 
                color: black; 
            } 
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        main_layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        self.stacked_widget.addWidget(page)

    def init_quiz_screen(self):
        self.quiz_page = QWidget()
        self.quiz_layout = QVBoxLayout(self.quiz_page)

        self.timer_label = QLabel("⏳ Time Left: --")
        self.timer_label.setFont(QFont("Arial", 12))
        self.quiz_layout.addWidget(self.timer_label)

        self.progress_bar = QProgressBar()
        self.quiz_layout.addWidget(self.progress_bar)

        self.question_label = QLabel("", wordWrap=True, alignment=Qt.AlignCenter)
        self.question_label.setTextFormat(Qt.RichText)
        self.quiz_layout.addWidget(self.question_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.time_left = 0

        self.stacked_widget.addWidget(self.quiz_page)

    def init_result_screen(self):
        self.result_page = QWidget()
        result_layout = QVBoxLayout(self.result_page)

        self.result_label = QLabel("", wordWrap=True, alignment=Qt.AlignCenter)
        self.result_label.setTextFormat(Qt.RichText)
        result_layout.addWidget(self.result_label)

        back_btn = QPushButton("🔙 Back to Main Menu")
        back_btn.clicked.connect(self.reset_game)
        result_layout.addWidget(back_btn)

        self.stacked_widget.addWidget(self.result_page)

    """
    ---------------------------
    Navigation and Transitions
    ---------------------------
    """
    def return_to_main_menu(self):
        if self.parent:
            self.parent.show()
        self.close()

    def reset_game(self):
        """Reset game state and return to difficulty selection"""
        self.answered_questions.clear()
        self.session_xp = 0
        self.current_question_index = 0
        self.result_shown = False
        self.stacked_widget.setCurrentIndex(0)

    def select_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.stacked_widget.setCurrentIndex(1)

    """
    ---------------------------
    Quiz Logic and Start
    ---------------------------
    """
    def start_quiz(self, level):
        self.level = level
        self.session_xp = 0
        self.result_shown = False
        self.current_question_index = 0
        self.load_user_progress()
        self.load_questions()
        self.progress_bar.setMaximum(len(self.questions))
        self.stacked_widget.setCurrentIndex(2)
        self.start_timer()
        self.load_next_question()

    def load_questions(self):
        try:
            path = os.path.join(os.path.dirname(__file__), '../data/questions.json')
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.questions = data.get(self.difficulty, {}).get(f"level_{self.level}", [])
                random.shuffle(self.questions)
        except Exception as e:
            print(f"Failed to load questions: {e}")
            self.questions = []

    def load_user_progress(self):
        progress = self.db_manager.get_user_progress(self.user_id)
        self.current_xp = progress[0] if progress else 0

    def load_next_question(self):
        self.clear_option_widgets()
        self.attempts = 0

        if self.current_question_index >= len(self.questions):
            self.show_result()
            return

        self.current_question = self.questions[self.current_question_index]
        self.question_label.setText(
            f"❓ <b>Question {self.current_question_index + 1}/{len(self.questions)}</b><br>{self.current_question['question']}"
        )
        self.progress_bar.setValue(self.current_question_index + 1)

        q_type = self.current_question.get("type", "multi")
        handler = {
            "multi": self.init_multi_choice,
            "text": self.init_text_answer
        }.get(q_type, self.init_multi_choice)
        handler()

    """
    ---------------------------
    Question UI Elements
    ---------------------------
    """
    def init_multi_choice(self):
        options = self.current_question.get("options", [])
        for option in options:
            btn = QPushButton(option)
            btn.clicked.connect(lambda _, opt=option: self.validate_answer(opt))
            self.quiz_layout.addWidget(btn)
            self.option_widgets.append(btn)

    def init_text_answer(self):
        self.answer_input = QTextEdit()
        self.answer_input.setPlaceholderText("Enter your code here...")
        self.answer_input.setAcceptRichText(False)
        self.quiz_layout.addWidget(self.answer_input)

        submit_btn = QPushButton("🚀 Submit Code")
        submit_btn.clicked.connect(lambda: self.validate_answer(
            self.answer_input.toPlainText(),
            is_text=True
        ))
        self.quiz_layout.addWidget(submit_btn)
        self.option_widgets.extend([self.answer_input, submit_btn])

    def clear_option_widgets(self):
        for widget in self.option_widgets:
            self.quiz_layout.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()
        self.option_widgets.clear()

    """
    ---------------------------
    Answers, Validation, and XP
    ---------------------------
    """
    def validate_answer(self, user_input, is_text=False):
        if self.current_question_index in self.answered_questions:
            self.current_question_index += 1
            self.load_next_question()
            return

        correct_answers = self.current_question.get('answers', [])
        if isinstance(correct_answers, str):
            correct_answers = [correct_answers]
        normalized_answers = [str(a).strip().lower() for a in correct_answers]
        normalized_input = str(user_input).strip().lower()
        is_correct = normalized_input in normalized_answers

        xp_gain = {"easy": 1, "medium": 10, "hard": 50}.get(self.difficulty, 10)
        explanation = self.current_question.get('explanation', 'No explanation provided.')

        if is_correct:
            self.answered_questions.add(self.current_question_index)
            self.session_xp += xp_gain
            self.current_question_index += 1
            self.show_feedback_dialog("✅ Correct!", xp_gain, explanation)
        else:
            self.attempts += 1
            if self.attempts < self.MAX_ATTEMPTS:
                remaining = self.MAX_ATTEMPTS - self.attempts
                self.show_feedback_dialog("❌ Try Again", 0,
                    f"Incorrect. {remaining} attempt{'s' if remaining > 1 else ''} left.")
            else:
                self.answered_questions.add(self.current_question_index)
                correct = "\n".join(f"• {a}" for a in correct_answers)
                self.current_question_index += 1
                self.show_feedback_dialog("❌ Incorrect", 0,
                    f"Correct answer(s):\n{correct}\n\n{explanation}")

    def show_feedback_dialog(self, title, xp, explanation):
        self.pause_timer()
        dialog = QDialog(self)
        dialog.setWindowTitle("📢 Result")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(title))
        layout.addWidget(QLabel(f"🏅 XP: +{xp}"))
        text = QTextEdit(explanation)
        text.setReadOnly(True)
        layout.addWidget(text)
        dialog.exec_()
        self.resume_timer()
        self.load_next_question()

    """
    ---------------------------
    Timer and Time Count
    ---------------------------
    """
    def start_timer(self):
        self.time_left = {"easy": 60, "medium": 300, "hard": 1800}.get(self.difficulty, 90)
        self.timer.start(1000)
        self.update_timer_label()

    def pause_timer(self):
        self.timer.stop()

    def resume_timer(self):
        self.timer.start(1000)

    def update_timer(self):
        self.time_left -= 1
        self.update_timer_label()
        if self.time_left <= 0:
            self.timer.stop()
            self.show_time_up_dialog()

    def update_timer_label(self):
        self.timer_label.setText(f"⏳ Time Left: {self.time_left} seconds")

    def show_time_up_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("⏰ Time's Up")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Time's up! The quiz has ended."))
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(lambda: (dialog.accept(), self.show_result()))
        layout.addWidget(ok_btn)
        dialog.exec_()

    """
    ---------------------------
    Finalizing and Showing Results
    ---------------------------
    """
    def show_result(self):
        if self.result_shown:
            return
        self.result_shown = True
        self.timer.stop()

        best_attempt = self.db_manager.get_best_quiz_attempt(self.user_id, self.difficulty, self.level)

        if best_attempt is None or self.session_xp > best_attempt:
            xp_diff = self.session_xp - (best_attempt or 0)

            if xp_diff > 0:
                success = self.db_manager.record_quiz_attempt(
                    user_id=self.user_id,
                    xp=self.session_xp,
                    difficulty=self.difficulty,
                    level=self.level
                )
                if not success:
                    print("Failed to save quiz attempt")
                    return

                current_xp, current_level = self.db_manager.get_user_progress(self.user_id)
                new_xp = current_xp + xp_diff
                new_level = (new_xp // 100) + 1

                if not self.db_manager.update_xp(self.user_id, xp_diff):
                    print("Failed to update XP")
                    return

                if new_level > current_level:
                    self.db_manager.update_level(self.user_id, new_level)
                    self.db_manager.add_inventory_item(
                        self.user_id,
                        f"🎖️ Level {new_level} Badge",
                        "achievement"
                    )

                self.db_manager.update_stats(self.user_id, win=True)

                result_text = f"🎉 <b>New Record!</b><br>🏅 XP Earned: {self.session_xp}<br>"
            else:
                result_text = f"✅ Level already completed.<br>Your best XP: {best_attempt}<br>This attempt: {self.session_xp}<br>"
        else:
            result_text = f"📉 No XP earned.<br>Previous best: {best_attempt}<br>This attempt: {self.session_xp}<br>"

        progress = self.db_manager.get_user_progress(self.user_id)
        if progress:
            xp, level = progress
            result_text += f"📊 Total XP: {xp}<br>🎓 Level: {level}"
            self.result_label.setText(result_text)
            self.stacked_widget.setCurrentIndex(3)
