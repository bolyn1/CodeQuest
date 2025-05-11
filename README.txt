# СodeQuest Game Application

## Description
A fun and interactive quiz game built with PyQt5.
The game features multiple difficulty levels, time-based challenges, and tracks user progress with a built-in scoring system.
Users can register, select difficulty levels, and attempt quizzes to earn XP and progress through levels.

## Features
- User registration and login system
- Multiple difficulty levels: Easy, Medium, Hard
- Timer to track quiz duration
- XP system and level progression
- User statistics tracking (XP, level, achievements)
- Database integration to store user progress and quiz attempts

## Installation

### Prerequisites
Make sure you have Python 3.x installed on your system.

### Install dependencies
Run the following command to install the necessary dependencies:

pip install -r requirements.txt

Running the application
Once all dependencies are installed, you can run the game by executing:

python main.py
This will launch the application and you can start interacting with the game.

Project Structure
main.py: The main entry point for the game application.
game/game_window.py: Contains the logic for the quiz game window and user interactions.
database/db_manager.py: Handles database interactions (registration, quiz progress, etc.).
data/questions.json: Contains the quiz questions and answers for different difficulty levels.
assets/: Directory for storing any images or resources used in the app.(it has styling for the UI)

Contributing
If you'd like to contribute to this project, feel free to fork the repository and create a pull request.
Please make sure to follow the code style and include tests for any new features.

### To-do:
1. **Game_window.py** - Add hard mode which will include given code where you should fill in or fix code
2. **Seed_challenges** - Here you should add weekly challenges(about, xp and items gain for them and 2nd leaderboard)
                            Everything for the weekly challenges is ready in DB(use challenges window)
3. **settings_window** - Well, I did nothing to it, I think that's good to do something like sound effects or whatever
                            (I would recommend to add password change and profile icon)

Feel free to modify these based on your exact needs! Let me know if you need further tweaks. :)