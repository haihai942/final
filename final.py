import tkinter as tk
from tkinter import messagebox
import random
import sqlite3


class TicTacToeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe-cap")

        self.mode = None
        self.current_player = "X"
        self.board = [" "] * 9
        self.turn_count = 0

        self.create_mode_selection()
        self.buttons = []

        # Initialize the database
        self.initialize_database()

        # Handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

    def initialize_database(self):
        """Initialize the SQLite database."""
        self.conn = sqlite3.connect("tictactoe_stats.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                player TEXT PRIMARY KEY,
                wins INTEGER DEFAULT 0
            )
        """)
        # Ensure both players are in the database
        for player in ("X", "O"):
            self.cursor.execute("""
                INSERT OR IGNORE INTO stats (player, wins) VALUES (?, 0)
            """, (player,))
        self.conn.commit()

    def create_mode_selection(self):
        """Create mode selection screen."""
        self.clear_window()

        self.mode_label = tk.Label(self.root, text="Select Mode:")
        self.mode_label.pack()

        mode1_button = tk.Button(
            self.root, text="Mode 1: Randomize X's second turn",
            command=lambda: self.start_game(1)
        )
        mode1_button.pack(pady=5)

        mode2_button = tk.Button(
            self.root, text="Mode 2: Randomize both players' second turns",
            command=lambda: self.start_game(2)
        )
        mode2_button.pack(pady=5)

        view_stats_button = tk.Button(
            self.root, text="View Records", command=self.view_stats
        )
        view_stats_button.pack(pady=5)

        reset_stats_button = tk.Button(
            self.root, text="Reset Records", command=self.reset_stats
        )
        reset_stats_button.pack(pady=5)

    def clear_window(self):
        """Clear all widgets from the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_game(self, mode):
        """Start the game with the selected mode."""
        self.mode = mode
        self.create_game_board()

    def create_game_board(self):
        """Create the Tic-Tac-Toe game board."""
        self.clear_window()

        frame = tk.Frame(self.root)
        frame.pack()

        for i in range(3):
            for j in range(3):
                button = tk.Button(
                    frame, text="", font=("Arial", 24), width=5, height=2,
                    command=lambda idx=(i * 3 + j): self.make_move(idx)
                )
                button.grid(row=i, column=j)
                self.buttons.append(button)

    def make_move(self, index):
        """Handle player moves."""
        if self.board[index] != " ":
            return  # Ignore if the cell is already occupied

        # Make the move
        self.board[index] = self.current_player
        self.buttons[index].config(text=self.current_player)

        # Check if there's a winner
        if self.check_winner():
            messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
            self.update_stats(winner=self.current_player)
            self.reset_game()
            return

        self.turn_count += 1

        # Check for a draw
        if self.turn_count == 9:
            messagebox.showinfo("Game Over", "It's a draw!")
            self.reset_game()
            return

        # Mode-specific logic
        if self.mode == 1 and self.turn_count == 2:
            self.randomize_turn("X")
            self.switch_player("O")  # After randomization, switch to O
        elif self.mode == 2 and self.turn_count == 2:
            self.randomize_turn("X")
            self.switch_player("O")  # Randomize O's turn
            self.randomize_turn("O")
            self.switch_player("X")  # After both randomizations, switch to X

        # Switch players after the move
        else:
            self.switch_player()

    def randomize_turn(self, player):
        """Randomize a move for the given player."""
        available_moves = [i for i, val in enumerate(self.board) if val == " "]
        if not available_moves:
            return  # No moves available
        random_move = random.choice(available_moves)
        self.board[random_move] = player
        self.buttons[random_move].config(text=player)

    def switch_player(self, to_player=None):
        """Switch the current player. Optionally, set to a specific player."""
        if to_player:
            self.current_player = to_player
        else:
            self.current_player = "X" if self.current_player == "O" else "O"

    def check_winner(self):
        """Check if there is a winner."""
        win_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
            (0, 4, 8), (2, 4, 6)  # Diagonals
        ]

        for combo in win_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != " ":
                return True

        return False

    def reset_game(self):
        """Reset the game."""
        self.board = [" "] * 9
        self.turn_count = 0
        self.current_player = "X"
        self.buttons = []
        self.create_mode_selection()

    def update_stats(self, winner):
        """Update the database with the winner's record."""
        self.cursor.execute("""
            UPDATE stats SET wins = wins + 1 WHERE player = ?
        """, (winner,))
        self.conn.commit()

    def view_stats(self):
        """Display the win stats."""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Player Stats")

        self.cursor.execute("SELECT * FROM stats")
        stats = self.cursor.fetchall()

        for player, wins in stats:
            tk.Label(stats_window, text=f"Player {player}: Wins: {wins}").pack()

    def reset_stats(self):
        """Reset the stats in the database."""
        self.cursor.execute("DELETE FROM stats")
        for player in ("X", "O"):
            self.cursor.execute("""
                INSERT INTO stats (player, wins) VALUES (?, 0)
            """, (player,))
        self.conn.commit()
        messagebox.showinfo("Stats Reset", "All player stats have been reset!")

    def close_application(self):
        """Close the application and clean up."""
        self.conn.close()  # Close the database connection
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeUI(root)
    root.mainloop()
import tkinter as tk
from tkinter import messagebox
import random
import sqlite3

class TicTacToeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe-cap")

        self.mode = None
        self.current_player = "X"
        self.board = [" "] * 9
        self.turn_count = 0

        self.create_mode_selection()
        self.buttons = []

        # Initialize the database
        self.initialize_database()

        # Handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

    def initialize_database(self):
        """Initialize the SQLite database."""
        self.conn = sqlite3.connect("tictactoe_stats.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                player TEXT PRIMARY KEY,
                wins INTEGER DEFAULT 0
            )
        """)
        # Ensure both players are in the database
        for player in ("X", "O"):
            self.cursor.execute("""
                INSERT OR IGNORE INTO stats (player, wins) VALUES (?, 0)
            """, (player,))
        self.conn.commit()

    def create_mode_selection(self):
        """Create mode selection screen."""
        self.clear_window()

        self.mode_label = tk.Label(self.root, text="Select Mode:")
        self.mode_label.pack()

        mode1_button = tk.Button(
            self.root, text="Mode 1: Randomize X's second turn",
            command=lambda: self.start_game(1)
        )
        mode1_button.pack(pady=5)

        mode2_button = tk.Button(
            self.root, text="Mode 2: Randomize both players' second turns",
            command=lambda: self.start_game(2)
        )
        mode2_button.pack(pady=5)

        view_stats_button = tk.Button(
            self.root, text="View Records", command=self.view_stats
        )
        view_stats_button.pack(pady=5)

        reset_stats_button = tk.Button(
            self.root, text="Reset Records", command=self.reset_stats
        )
        reset_stats_button.pack(pady=5)

    def clear_window(self):
        """Clear all widgets from the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_game(self, mode):
        """Start the game with the selected mode."""
        self.mode = mode
        self.create_game_board()

    def create_game_board(self):
        """Create the Tic-Tac-Toe game board."""
        self.clear_window()

        frame = tk.Frame(self.root)
        frame.pack()

        for i in range(3):
            for j in range(3):
                button = tk.Button(
                    frame, text="", font=("Arial", 24), width=5, height=2,
                    command=lambda idx=(i * 3 + j): self.make_move(idx)
                )
                button.grid(row=i, column=j)
                self.buttons.append(button)

    def make_move(self, index):
        """Handle player moves."""
        if self.board[index] != " ":
            return  # Ignore if the cell is already occupied

        # Make the move
        self.board[index] = self.current_player
        self.buttons[index].config(text=self.current_player)

        # Check if there's a winner
        if self.check_winner():
            messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
            self.update_stats(winner=self.current_player)
            self.reset_game()
            return

        self.turn_count += 1

        # Check for a draw
        if self.turn_count == 8:
            messagebox.showinfo("Game Over", "It's a draw!")
            if self.mode == 1:
                self.reset_game_mode_1()  # Return to mode selection for Mode 1
            elif self.mode == 2:
                self.reset_game_mode_2()  # Return to mode selection for Mode 2
            return

        # Special condition for Mode 2 after 7 turns
        if self.mode == 2 and self.turn_count == 7:
            messagebox.showinfo("Game Over", "It's a draw!")
            self.reset_game_mode_2()  # Return to mode selection for Mode 2

        # Mode-specific logic
        if self.mode == 1 and self.turn_count == 2:
            self.randomize_turn("X")
            self.switch_player("O")  # After randomization, switch to O
        elif self.mode == 2 and self.turn_count == 2:
            self.randomize_turn("X")
            self.switch_player("O")  # Randomize O's turn
            self.randomize_turn("O")
            self.switch_player("X")  # After both randomizations, switch to X

        # Switch players after the move
        else:
            self.switch_player()

    def randomize_turn(self, player):
        """Randomize a move for the given player."""
        available_moves = [i for i, val in enumerate(self.board) if val == " "]
        if not available_moves:
            return  # No moves available
        random_move = random.choice(available_moves)
        self.board[random_move] = player
        self.buttons[random_move].config(text=player)

    def switch_player(self, to_player=None):
        """Switch the current player. Optionally, set to a specific player."""
        if to_player:
            self.current_player = to_player
        else:
            self.current_player = "X" if self.current_player == "O" else "O"

    def check_winner(self):
        """Check if there is a winner."""
        win_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
            (0, 4, 8), (2, 4, 6)  # Diagonals
        ]

        for combo in win_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != " ":
                return True

        return False

    def reset_game(self):
        """Reset the game and return to the mode selection screen."""
        self.board = [" "] * 9  # Clear the board
        self.turn_count = 0  # Reset the turn count
        self.current_player = "X"  # Reset to player X
        self.buttons = []  # Clear the list of buttons

        self.clear_window()  # Explicitly clear the window
        self.create_mode_selection()  # Create the mode selection screen

    def reset_game_mode_1(self):
        """Reset the game and return to the mode selection screen for Mode 1."""
        self.board = [" "] * 9  # Clear the board
        self.turn_count = 0  # Reset the turn count
        self.current_player = "X"  # Reset to player X
        self.buttons = []  # Clear the list of buttons

        self.clear_window()  # Explicitly clear the window
        self.create_mode_selection()  # Create the mode selection screen

    def reset_game_mode_2(self):
        """Reset the game and return to the mode selection screen for Mode 2."""
        self.board = [" "] * 9  # Clear the board
        self.turn_count = 0  # Reset the turn count
        self.current_player = "X"  # Reset to player X
        self.buttons = []  # Clear the list of buttons

        self.clear_window()  # Explicitly clear the window
        self.create_mode_selection()  # Create the mode selection screen

    def update_stats(self, winner):
        """Update the database with the winner's record."""
        self.cursor.execute("""
            UPDATE stats SET wins = wins + 1 WHERE player = ?
        """, (winner,))
        self.conn.commit()

    def view_stats(self):
        """Display the win stats."""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Player Stats")

        self.cursor.execute("SELECT * FROM stats")
        stats = self.cursor.fetchall()

        for player, wins in stats:
            tk.Label(stats_window, text=f"Player {player}: Wins: {wins}").pack()

    def reset_stats(self):
        """Reset the stats in the database."""
        self.cursor.execute("DELETE FROM stats")
        for player in ("X", "O"):
            self.cursor.execute("""
                INSERT INTO stats (player, wins) VALUES (?, 0)
            """, (player,))
        self.conn.commit()
        messagebox.showinfo("Stats Reset", "All player stats have been reset!")

    def close_application(self):
        """Close the application and clean up."""
        self.conn.close()  # Close the database connection
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeUI(root)
    root.mainloop()
