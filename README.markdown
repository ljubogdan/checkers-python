## Checkers-AI-SV2

## About
Checkers-AI-SV2 is an interactive checkers game developed in Python, utilizing Pygame for a dynamic graphical interface and a Minimax algorithm with alpha-beta pruning for intelligent AI gameplay. The project incorporates a SQLite-based transposition table to optimize move calculations and supports forced capture rules. It serves as an excellent demonstration of advanced algorithms, game development, and GUI programming in Python.

## Features
- **Graphical Interface**: Built with Pygame for a responsive and visually appealing checkers board.
- **AI Opponent**: Implements Minimax with alpha-beta pruning for efficient and strategic gameplay.
- **Transposition Table**: Uses SQLite to store and retrieve board states, reducing computation time.
- **Forced Captures**: Configurable rule for mandatory captures, enhancing strategic depth.
- **Performance Metrics**: Tracks and displays move calculation times (best, worst, average).
- **Customizable Gameplay**: Supports dynamic depth search based on remaining time and piece count.

## Technologies
- **Python**: Core programming language for the project.
- **Pygame**: Library for rendering the game board and handling user interactions.
- **SQLite**: Database for storing transposition table data.
- **Pickle**: Serialization for efficient storage of board states.
- **Minimax Algorithm**: Enhanced with alpha-beta pruning for AI decision-making.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/checkers-ai-sv2.git
   ```
2. Navigate to the project directory:
   ```bash
   cd checkers-ai-sv2
   ```
3. Install dependencies:
   ```bash
   pip install pygame
   ```
4. Run the game:
   ```bash
   python main.py
   ```

## Usage
- Launch the game and choose whether forced captures are enabled (Enter for yes, Space for no).
- Play as the purple (LILA) pieces against the AI controlling the white (BELA) pieces.
- Click on a piece to select it and view legal moves highlighted in green.
- The AI computes moves using a dynamic depth search, with performance metrics printed to the console.
- The game ends when a winner is determined or no legal moves remain.

## Project Structure
- `main.py`: Entry point for running the game.
- `tabla.py`: Manages the game board and piece logic.
- `dame_igra.py`: Handles game state and user interactions.
- `algoritam.py`: Implements the Minimax algorithm and transposition table.
- `figura.py`: Defines piece properties and rendering.
- `konstante.py`: Stores game constants and color definitions.

## Tags
- Python
- Pygame
- Minimax
- Alpha-Beta-Pruning
- Checkers
- Artificial-Intelligence
- SQLite
- Transposition-Table
- Game-Development
- GUI

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Inspired by classic checkers gameplay and AI research.
- Built as a showcase for algorithmic efficiency and Python game development.