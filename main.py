# main.py
import tkinter as tk
from tkinter import messagebox
from single_player_ui import SinglePlayerBattleshipUI
from multiplayer_ui import MultiplayerBattleshipUI


class GameModeSelector:
    """
    Main menu for selecting game mode in Quantum Battleship.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Battleship - Game Mode Selection")
        self.root.configure(bg="#0a0a0a")
        self.root.geometry("600x500")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main menu UI."""
        # Title section
        title_frame = tk.Frame(self.root, bg="#0a0a0a")
        title_frame.pack(pady=40)
        
        title_label = tk.Label(
            title_frame,
            text="QUANTUM BATTLESHIP",
            font=("Helvetica", 28, "bold"),
            bg="#0a0a0a",
            fg="#00ffff"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Harness the power of quantum mechanics in naval warfare",
            font=("Helvetica", 12, "italic"),
            bg="#0a0a0a",
            fg="#88ccff"
        )
        subtitle_label.pack(pady=(10, 0))
        
        # Description
        desc_frame = tk.Frame(self.root, bg="#0a0a0a")
        desc_frame.pack(pady=20)
        
        description = tk.Label(
            desc_frame,
            text="Experience battleship like never before with quantum targeting algorithms.\nUse Grover's search to locate enemy ships across multiple dimensions!",
            font=("Helvetica", 11),
            bg="#0a0a0a",
            fg="#cccccc",
            justify="center"
        )
        description.pack()
        
        # Game mode selection
        mode_frame = tk.Frame(self.root, bg="#0a0a0a")
        mode_frame.pack(pady=40)
        
        mode_title = tk.Label(
            mode_frame,
            text="CHOOSE YOUR BATTLE MODE",
            font=("Helvetica", 16, "bold"),
            bg="#0a0a0a",
            fg="#ffffff"
        )
        mode_title.pack(pady=(0, 30))
        
        # Single Player button
        single_player_frame = tk.Frame(
            mode_frame,
            bg="#1a1a2e",
            relief="raised",
            bd=3,
            padx=20,
            pady=15
        )
        single_player_frame.pack(pady=10)
        
        single_player_btn = tk.Button(
            single_player_frame,
            text="SINGLE PLAYER",
            font=("Helvetica", 16, "bold"),
            bg="#00aa44",
            fg="white",
            activebackground="#00cc55",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=40,
            pady=15,
            command=self.launch_single_player,
            cursor="hand2"
        )
        single_player_btn.pack()
        
        single_desc = tk.Label(
            single_player_frame,
            text="Battle against AI opponents with quantum targeting systems\nChoose difficulty: Easy, Medium, or Hard",
            font=("Helvetica", 10),
            bg="#1a1a2e",
            fg="#cccccc",
            justify="center"
        )
        single_desc.pack(pady=(8, 0))
        
        # Multiplayer button
        multiplayer_frame = tk.Frame(
            mode_frame,
            bg="#1a1a2e",
            relief="raised",
            bd=3,
            padx=20,
            pady=15
        )
        multiplayer_frame.pack(pady=10)
        
        multiplayer_btn = tk.Button(
            multiplayer_frame,
            text="LOCAL MULTIPLAYER",
            font=("Helvetica", 16, "bold"),
            bg="#cc3333",
            fg="white",
            activebackground="#ff4444",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=40,
            pady=15,
            command=self.launch_multiplayer,
            cursor="hand2"
        )
        multiplayer_btn.pack()
        
        multi_desc = tk.Label(
            multiplayer_frame,
            text="Face off against a friend on the same computer\nTurn-based gameplay with hidden ship positions",
            font=("Helvetica", 10),
            bg="#1a1a2e",
            fg="#cccccc",
            justify="center"
        )
        multi_desc.pack(pady=(8, 0))
        
        # Footer
        footer_frame = tk.Frame(self.root, bg="#0a0a0a")
        footer_frame.pack(side="bottom", pady=20)
        
        footer_label = tk.Label(
            footer_frame,
            text="Powered by Qiskit Quantum Computing Framework",
            font=("Helvetica", 9, "italic"),
            bg="#0a0a0a",
            fg="#666666"
        )
        footer_label.pack()
        
    def launch_single_player(self):
        """Launch single player mode."""
        self.root.withdraw()  # Hide main menu
        
        # Create new window for single player
        single_window = tk.Toplevel()
        single_window.protocol("WM_DELETE_WINDOW", lambda: self.on_game_close(single_window))
        
        try:
            game = SinglePlayerBattleshipUI(single_window)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch single player mode: {e}")
            single_window.destroy()
            self.root.deiconify()
        
    def launch_multiplayer(self):
        """Launch multiplayer mode."""
        self.root.withdraw()  # Hide main menu
        
        # Create new window for multiplayer
        multi_window = tk.Toplevel()
        multi_window.protocol("WM_DELETE_WINDOW", lambda: self.on_game_close(multi_window))
        
        try:
            game = MultiplayerBattleshipUI(multi_window)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch multiplayer mode: {e}")
            multi_window.destroy()
            self.root.deiconify()
    
    def on_game_close(self, game_window):
        """Handle game window closure."""
        game_window.destroy()
        self.root.deiconify()  # Show main menu again


def main():
    """Launch Quantum Battleship with game mode selection."""
    root = tk.Tk()
    selector = GameModeSelector(root)
    root.mainloop()


if __name__ == "__main__":
    main()
