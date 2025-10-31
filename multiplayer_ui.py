# multiplayer_ui.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from game_controller import GameController
from quantum_weapons import QuantumGameState


class MultiplayerBattleshipUI:
    """
    Local multiplayer Quantum Battleship UI with turn-based gameplay.
    Ships are hidden during opponent turns for fair play.
    """
    
    def __init__(self, root):
        # Track targeted squares per player for each region (dict: region tuple -> set of coords)
        self.player1_targeted_regions = {}
        self.player2_targeted_regions = {}
        self.root = root
        self.root.title("Quantum Battleship - Local Multiplayer")
        self.root.configure(bg="#0a0a0a")
        # Configure window for better scaling
        self.root.geometry("1300x700")  # Wider, less tall
        self.root.minsize(1100, 650)    # Minimum size fits all controls
        # Make window resizable and center it
        self.root.resizable(True, True)
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1300 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f'1300x700+{x}+{y}')
        # Game components
        self.player1_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=False)
        self.player2_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=False)
        # Quantum game state for managing quantum weapons
        self.quantum_state = QuantumGameState()
        # Game state
        self.grid_size = 8
        self.cell_size = 60  # Increased from 50 for bigger grids
        self.game_phase = "ship_placement"  # "ship_placement" or "battle"
        self.current_player = 1  # 1 or 2
        self.ships_to_place = 8
        self.player1_ships = []
        self.player2_ships = []
        self.selected_region = []
        self.selection_mode = "square"
        self.targeting_mode = "2x2"  # Default targeting mode
        self.player1_hits = []  # Track ships hit by player 1
        self.player2_hits = []  # Track ships hit by player 2
        self.ready_for_battle = False
        self.turn_taken = False  # Flag to track if current player has taken their shot
        # UI elements
        self.player1_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player2_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player1_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player2_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        # Track shot results separately from ship placements
        self.player1_shot_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player2_shot_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Initialize visual effect tracking variables to prevent stuck elements
        self.target_highlights = {}
        self.targeting_animation_overlays = []
        self.targeting_animation_step = 0
        self.temp_revealed_ships = []
        
        # Load assets first
        self.load_assets()
        self.setup_ui()

    def load_assets(self):
        """Load image assets for the game."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "assets")
        
        def safe_load(filename):
            path = os.path.join(assets_dir, filename)
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    img = img.resize((self.cell_size, self.cell_size), Image.LANCZOS)
                    return ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Could not load image {path}: {e}")
                    return None
            else:
                print(f"Missing asset: {path}")
                return None
        
        self.water_img = safe_load("water.png")
        self.ship_img = safe_load("ship.png")
        self.splash_img = safe_load("splash.png")
        
    def setup_ui(self):
        """Setup the complete UI."""
        # Title
        title_frame = tk.Frame(self.root, bg="#0a0a0a")
        title_frame.pack(pady=8)
        
        title_label = tk.Label(
            title_frame,
            text="QUANTUM BATTLESHIP - MULTIPLAYER",
            font=("Helvetica", 22, "bold"),
            bg="#0a0a0a",
            fg="#00ffff"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Local multiplayer quantum warfare",
            font=("Helvetica", 10, "italic"),
            bg="#0a0a0a",
            fg="#88ccff"
        )
        subtitle_label.pack()
        
        # Game status
        self.status_frame = tk.Frame(self.root, bg="#0a0a0a")
        self.status_frame.pack(pady=5)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="PLAYER 1 - PLACE YOUR 8 SHIPS",
            font=("Helvetica", 16, "bold"),
            bg="#003366",
            fg="#ffffff",
            padx=15,
            pady=6,
            relief="raised",
            bd=2
        )
        self.status_label.pack()
        
        # Ship counter during placement
        self.ship_counter = tk.Label(
            self.status_frame,
            text="Ships placed: 0/8",
            font=("Helvetica", 12, "bold"),
            bg="#0a0a0a",
            fg="#ffaa00"
        )
        self.ship_counter.pack(pady=3)
        
        # Turn transition button (kept in status area for visibility during all phases)
        self.transition_frame = tk.Frame(self.status_frame, bg="#0a0a0a")
        
        self.transition_btn = tk.Button(
            self.transition_frame,
            text="PASS TO PLAYER 2",
            font=("Helvetica", 14, "bold"),
            bg="#ff6600",
            fg="white",
            activebackground="#ff8833",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=30,
            pady=10,
            command=self.pass_turn
        )
        self.transition_btn.pack()
        
        # Main game area
        self.create_game_boards()
        
        # Controls
        self.create_controls()
        
    def create_game_boards(self):
        """Create the dual board layout."""
        boards_frame = tk.Frame(self.root, bg="#0a0a0a")
        boards_frame.pack(pady=15)
        
        # Player 1's board (left side)
        player1_frame = tk.Frame(boards_frame, bg="#0a0a0a")
        player1_frame.pack(side=tk.LEFT, padx=20)
        
        self.player1_title = tk.Label(
            player1_frame,
            text="PLAYER 1 FLEET",
            font=("Helvetica", 14, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        )
        self.player1_title.pack(pady=(0, 8))
        
        canvas_size = self.grid_size * self.cell_size
        self.player1_canvas = tk.Canvas(
            player1_frame,
            width=canvas_size,
            height=canvas_size,
            highlightthickness=3,
            highlightbackground="#00ff88",
            bg="#004466",
            relief="raised",
            bd=3
        )
        self.player1_canvas.pack()
        self.player1_canvas.bind("<Button-1>", self.on_board_click)
        
        # Player 2's board (right side)
        player2_frame = tk.Frame(boards_frame, bg="#0a0a0a")
        player2_frame.pack(side=tk.LEFT, padx=20)
        
        self.player2_title = tk.Label(
            player2_frame,
            text="PLAYER 2 FLEET",
            font=("Helvetica", 14, "bold"),
            bg="#0a0a0a",
            fg="#ff4444"
        )
        self.player2_title.pack(pady=(0, 8))
        
        self.player2_canvas = tk.Canvas(
            player2_frame,
            width=canvas_size,
            height=canvas_size,
            highlightthickness=3,
            highlightbackground="#ff4444",
            bg="#004466",
            relief="raised",
            bd=3
        )
        self.player2_canvas.pack()
        self.player2_canvas.bind("<Button-1>", self.on_board_click)
        
        # Draw grids
        self.draw_grid(self.player1_canvas, self.player1_cells)
        self.draw_grid(self.player2_canvas, self.player2_cells)
        
    def draw_grid(self, canvas, cells):
        """Draw a game grid with water background."""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0, y0 = j * self.cell_size, i * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                
                # Place water background image
                if self.water_img:
                    canvas.create_image(
                        x0 + self.cell_size // 2,
                        y0 + self.cell_size // 2,
                        image=self.water_img
                    )
                
                # Create transparent rectangle for click handling
                rect = canvas.create_rectangle(
                    x0, y0, x1, y1,
                    outline="#88ccff", 
                    width=1, 
                    fill="",
                    stipple=""
                )
                cells[i][j] = rect
                
    def create_controls(self):
        """Create control buttons and targeting options."""
        control_frame = tk.Frame(self.root, bg="#0a0a0a")
        control_frame.pack(pady=15)
        
        # Ship placement buttons (shown during placement phase)
        self.placement_frame = tk.Frame(control_frame, bg="#0a0a0a")
        self.placement_frame.pack()
        
        placement_section = tk.Frame(
            self.placement_frame, 
            bg="#1a1a2e", 
            relief="raised", 
            bd=2,
            padx=15,
            pady=10
        )
        placement_section.pack()
        
        tk.Label(
            placement_section,
            text="SHIP DEPLOYMENT",
            font=("Helvetica", 12, "bold"),
            bg="#1a1a2e",
            fg="#00ffff"
        ).pack(pady=(0, 8))
        
        button_row = tk.Frame(placement_section, bg="#1a1a2e")
        button_row.pack()
        
        random_btn = tk.Button(
            button_row,
            text="RANDOM PLACEMENT",
            font=("Helvetica", 12, "bold"),
            bg="#ff6600",
            fg="white",
            activebackground="#ff8833",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=20,
            pady=10,
            width=18,
            command=self.place_ships_randomly
        )
        random_btn.pack(side=tk.LEFT, padx=10)
        
        confirm_btn = tk.Button(
            button_row,
            text="CONFIRM PLACEMENT",
            font=("Helvetica", 12, "bold"),
            bg="#00aa00",
            fg="white",
            activebackground="#00cc00",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=20,
            pady=10,
            width=18,
            command=self.confirm_ship_placement
        )
        confirm_btn.pack(side=tk.LEFT, padx=10)
        
        # Battle controls (hidden during placement)
        self.battle_frame = tk.Frame(control_frame, bg="#0a0a0a")
        
        # Targeting mode section
        targeting_section = tk.Frame(self.battle_frame, bg="#0a0a0a")
        targeting_section.pack(pady=10)
        
        tk.Label(
            targeting_section,
            text="QUANTUM TARGETING MODE",
            font=("Helvetica", 12, "bold"),
            bg="#0a0a0a",
            fg="#00ffff"
        ).pack(pady=(0, 8))
        
        # Create frame for targeting buttons
        mode_buttons_frame = tk.Frame(
            targeting_section, 
            bg="#1a1a2e", 
            relief="raised", 
            bd=2,
            padx=12,
            pady=8
        )
        mode_buttons_frame.pack()
        
        self.mode_var = tk.StringVar(value="square")
        self.mode_buttons = {}
        modes = [("Classical", "classical"), ("2x2 Grid", "square"), ("Full Row", "row"), ("Full Column", "column")]
        
        button_frame = tk.Frame(mode_buttons_frame, bg="#1a1a2e")
        button_frame.pack()
        
        for i, (text, mode) in enumerate(modes):
            btn = tk.Button(
                button_frame,
                text=text,
                command=lambda m=mode: self.set_targeting_mode(m),
                font=("Helvetica", 11, "bold"),
                bg="#333366",
                fg="white",
                activebackground="#4455aa",
                activeforeground="white",
                relief="raised",
                bd=3,
                padx=15,
                pady=8,
                width=12
            )
            btn.grid(row=0, column=i, padx=5)
            self.mode_buttons[mode] = btn
        
        # Set initial selection
        self.set_targeting_mode("square")
        
        # Combat action buttons frame
        combat_frame = tk.Frame(
            self.battle_frame, 
            bg="#1a1a2e", 
            relief="raised", 
            bd=2,
            padx=15,
            pady=12
        )
        combat_frame.pack(pady=15)
        
        tk.Label(
            combat_frame,
            text="QUANTUM WEAPONS",
            font=("Helvetica", 12, "bold"),
            bg="#1a1a2e",
            fg="#ff6600"
        ).pack(pady=(0, 10))
        
        # Quantum weapons in a row
        weapons_frame = tk.Frame(combat_frame, bg="#1a1a2e")
        weapons_frame.pack()
        
        # Grover Shot button
        self.grover_btn = tk.Button(
            weapons_frame,
            text="GROVER SHOT\n(Direct Attack)",
            command=lambda: self.fire_quantum_weapon("grover"),
            font=("Helvetica", 12, "bold"),
            bg="#cc3333",
            fg="white",
            activebackground="#ff4444",
            activeforeground="white",
            relief="raised",
            bd=4,
            padx=15,
            pady=10,
            width=15,
            height=3
        )
        self.grover_btn.pack(side=tk.LEFT, padx=5)
        
        # EV Scan button
        self.ev_scan_btn = tk.Button(
            weapons_frame,
            text="EV SCAN\n(Stealth Recon)",
            command=lambda: self.fire_quantum_weapon("ev_scan"),
            font=("Helvetica", 12, "bold"),
            bg="#3366cc",
            fg="white",
            activebackground="#4477dd",
            activeforeground="white",
            relief="raised",
            bd=4,
            padx=15,
            pady=10,
            width=15,
            height=3
        )
        self.ev_scan_btn.pack(side=tk.LEFT, padx=5)
        
        # Zeno Defense button
        self.zeno_btn = tk.Button(
            weapons_frame,
            text="ZENO DEFENSE\n(Quantum Shield)",
            command=lambda: self.activate_zeno_defense(),
            font=("Helvetica", 12, "bold"),
            bg="#cc9900",
            fg="white",
            activebackground="#dd9900",
            activeforeground="white",
            relief="raised",
            bd=4,
            padx=15,
            pady=10,
            width=15,
            height=3
        )
        self.zeno_btn.pack(side=tk.LEFT, padx=5)
        
        # Classical Shot button
        self.classical_btn = tk.Button(
            weapons_frame,
            text="CLASSICAL SHOT\n(Single Target)",
            command=lambda: self.fire_quantum_weapon("classical"),
            font=("Helvetica", 12, "bold"),
            bg="#669933",
            fg="white",
            activebackground="#77aa44",
            activeforeground="white",
            relief="raised",
            bd=4,
            padx=15,
            pady=10,
            width=15,
            height=3
        )
        self.classical_btn.pack(side=tk.LEFT, padx=5)
        
        # New game button
        new_game_btn = tk.Button(
            control_frame,
            text="NEW GAME",
            font=("Helvetica", 14, "bold"),
            bg="#666666",
            fg="white",
            activebackground="#888888",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=25,
            pady=10,
            width=12,
            command=self.new_game
        )
        new_game_btn.pack(pady=15)
        
    def on_board_click(self, event):
        """Handle clicks on either board."""
        # Determine which canvas was clicked
        clicked_canvas = event.widget
        
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if row >= self.grid_size or col >= self.grid_size:
            return
            
        if self.game_phase == "ship_placement":
            self.handle_ship_placement(clicked_canvas, row, col)
        elif self.game_phase == "battle":
            self.handle_targeting(clicked_canvas, row, col)
            
    def handle_ship_placement(self, clicked_canvas, row, col):
        """Handle ship placement during setup phase."""
        pos = (row, col)
        
        # Determine which player's board was clicked
        if clicked_canvas == self.player1_canvas and self.current_player == 1:
            current_ships = self.player1_ships
            overlays = self.player1_overlays
            canvas = self.player1_canvas
        elif clicked_canvas == self.player2_canvas and self.current_player == 2:
            current_ships = self.player2_ships
            overlays = self.player2_overlays
            canvas = self.player2_canvas
        else:
            # Wrong board for current player
            return
        
        # Toggle ship placement
        if pos in current_ships:
            # Remove ship
            current_ships.remove(pos)
            if overlays[row][col]:
                canvas.delete(overlays[row][col])
                overlays[row][col] = None
        else:
            # Add ship (if under limit)
            if len(current_ships) < 8:
                current_ships.append(pos)
                # Place ship image
                if self.ship_img:
                    cx = col * self.cell_size + self.cell_size // 2
                    cy = row * self.cell_size + self.cell_size // 2
                    ship_overlay = canvas.create_image(cx, cy, image=self.ship_img)
                    overlays[row][col] = ship_overlay
        
        self.update_ship_counter()
        
    def handle_targeting(self, clicked_canvas, row, col):
        """Handle targeting during battle phase."""
        # Check for defense mode
        if hasattr(self, 'targeting_mode') and self.targeting_mode == "defense":
            # Defense mode: player clicks on own board to apply Zeno defense
            own_canvas = self.player1_canvas if self.current_player == 1 else self.player2_canvas
            
            if clicked_canvas == own_canvas:
                # Clear any previous targeting highlights before applying defense
                self.clear_all_visual_effects()
                # Player clicked on own board - apply Zeno defense
                if self.apply_zeno_defense_to_ship((row, col)):
                    return  # Defense applied successfully
            else:
                # Player clicked on wrong board during defense - cancel and clear visuals
                self.clear_all_visual_effects()
                messagebox.showinfo("Defense Cancelled", "Zeno defense mode cancelled. Select a quantum weapon to continue.", parent=self.root)
                return
        
        # Normal targeting mode
        # Check if current player has already taken their turn
        if self.turn_taken:
            messagebox.showinfo("Turn Complete", "You have already taken your shot this turn!\nClick 'PASS TO PLAYER X' to continue.", parent=self.root)
            self.root.lift()
            self.root.focus_force()
            return
            
        # Determine target board and controller
        if clicked_canvas == self.player1_canvas and self.current_player == 2:
            # Player 2 targeting Player 1
            target_controller = self.player1_controller
        elif clicked_canvas == self.player2_canvas and self.current_player == 1:
            # Player 1 targeting Player 2
            target_controller = self.player2_controller
        else:
            # Can't target own board or wrong turn  
            if self.targeting_mode == "defense":
                # Cancel defense mode if clicking on wrong board
                self.targeting_mode = "2x2"
                self.hide_revealed_ships()
                messagebox.showinfo("Defense Cancelled", "Zeno defense mode cancelled. Select a quantum weapon to continue.", parent=self.root)
            return
            
        self.highlight_target_region(clicked_canvas, row, col, target_controller)
        
    def highlight_target_region(self, canvas, row, col, controller):
        """Highlight the selected targeting region."""
        # Clear previous selection highlights
        if hasattr(self, 'target_highlights'):
            for highlight in self.target_highlights.values():
                if highlight:
                    canvas.delete(highlight)
        else:
            self.target_highlights = {}
        
        # Get new region
        self.selected_region = controller.get_region_coords(
            row, col, self.selection_mode, 2
        )
        self.target_canvas = canvas
        self.target_controller = controller
        
        # Validate region was created successfully
        if not self.selected_region:
            return
        
        # Highlight new selection with yellow overlay
        for rr, cc in self.selected_region:
            if 0 <= rr < self.grid_size and 0 <= cc < self.grid_size:
                # Get the appropriate overlay array
                if canvas == self.player1_canvas:
                    overlays = self.player1_overlays
                else:
                    overlays = self.player2_overlays
                    
                # In multiplayer, ALWAYS highlight the entire region to prevent information leaks
                # Don't check for existing overlays as that would reveal ship/hit locations
                cx = cc * self.cell_size + self.cell_size // 2
                cy = rr * self.cell_size + self.cell_size // 2
                # Create yellow selection overlay
                highlight = canvas.create_rectangle(
                    cc * self.cell_size + 5, rr * self.cell_size + 5,
                    (cc + 1) * self.cell_size - 5, (rr + 1) * self.cell_size - 5,
                    fill="#ffff00", outline="#ffaa00", width=2, stipple="gray50"
                )
                self.target_highlights[(rr, cc)] = highlight
                    
    def place_ships_randomly(self):
        """Randomly place all ships for current player."""
        if self.current_player == 1:
            self.player1_ships = self.player1_controller.game.generate_random_ships()
            self.update_ship_display(self.player1_canvas, self.player1_ships, self.player1_overlays)
        else:
            self.player2_ships = self.player2_controller.game.generate_random_ships()
            self.update_ship_display(self.player2_canvas, self.player2_ships, self.player2_overlays)
        
        self.update_ship_counter()
        
    def update_ship_display(self, canvas, ships, overlays):
        """Update the visual display of ships on a board."""
        # Clear current ship displays
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if overlays[i][j]:
                    canvas.delete(overlays[i][j])
                    overlays[i][j] = None
        
        # Show ships with images
        for row, col in ships:
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                if self.ship_img:
                    cx = col * self.cell_size + self.cell_size // 2
                    cy = row * self.cell_size + self.cell_size // 2
                    ship_overlay = canvas.create_image(cx, cy, image=self.ship_img)
                    overlays[row][col] = ship_overlay
                    
    def update_ship_counter(self):
        """Update the ship counter display."""
        if self.current_player == 1:
            count = len(self.player1_ships)
        else:
            count = len(self.player2_ships)
        self.ship_counter.config(text=f"Ships placed: {count}/8")
        
    def confirm_ship_placement(self):
        """Confirm ship placement for current player."""
        current_ships = self.player1_ships if self.current_player == 1 else self.player2_ships
        
        if len(current_ships) < 8:
            messagebox.showwarning("Incomplete", "Please place all 8 ships!", parent=self.root)
            return
            
        if self.current_player == 1:
            # Player 1 done, move to Player 2
            self.player1_controller.game.ship_positions = self.player1_ships
            self.current_player = 2
            self.status_label.config(text="PLAYER 2 - PLACE YOUR 8 SHIPS")
            self.ship_counter.config(text="Ships placed: 0/8")
            
            # Hide ships and show transition button
            self.hide_ships(self.player1_canvas, self.player1_overlays)
            self.transition_frame.pack(pady=10)
            self.transition_btn.config(text="READY FOR PLAYER 2 SETUP")
            
        else:
            # Player 2 done, prepare for battle but don't start immediately
            self.player2_controller.game.ship_positions = self.player2_ships
            
            # Hide Player 2's ships and show transition to battle
            self.hide_ships(self.player2_canvas, self.player2_overlays)
            self.transition_frame.pack(pady=10)
            self.transition_btn.config(text="START BATTLE - PLAYER 1 GOES FIRST")
            self.status_label.config(text="SHIP PLACEMENT COMPLETE - READY FOR BATTLE")
            
            # Set flag to start battle on next transition
            self.ready_for_battle = True
            
    def pass_turn(self):
        """Handle turn transition between players."""
        # Clear all visual effects when passing turn
        self.clear_all_visual_effects()
        
        if self.game_phase == "ship_placement":
            if hasattr(self, 'ready_for_battle') and self.ready_for_battle:
                # Start battle phase
                self.ready_for_battle = False
                self.start_battle()
            elif self.current_player == 2:
                # Show Player 2's area and hide transition button temporarily
                self.show_ships(self.player2_canvas, self.player2_ships, self.player2_overlays)
                self.transition_frame.pack_forget()
            
        elif self.game_phase == "battle":
            # Switch turns in battle
            if self.current_player == 1:
                # Switching to Player 2's turn
                self.current_player = 2
                self.status_label.config(text="PLAYER 2'S TURN - TARGET ENEMY FLEET")
            else:
                # Switching to Player 1's turn
                self.current_player = 1
                self.status_label.config(text="PLAYER 1'S TURN - TARGET ENEMY FLEET")
                
            # NEVER show ship locations in multiplayer - only hits/misses are visible
            # Keep all ships hidden for fair play
            self.hide_ships(self.player1_canvas, self.player1_overlays)
            self.hide_ships(self.player2_canvas, self.player2_overlays)
            
            # Hide Zeno protection visuals from opponent
            self.hide_protection_visuals_from_opponent()
            
        # Reset turn flag for the new player
        self.turn_taken = False
        
        # Handle quantum protection expiration
        if hasattr(self, 'quantum_state'):
            expired_positions = self.quantum_state.end_turn()
            if expired_positions:
                # Remove visual protection indicators for expired positions
                for coords in expired_positions:
                    self.remove_zeno_protection_visual(coords)
        
        # Hide transition button and clear any target selection
        self.transition_frame.pack_forget()
        self.selected_region = []
        self.target_controller = None
        self.target_canvas = None
        
        # Reset targeting mode to default
        if hasattr(self, 'targeting_mode'):
            self.targeting_mode = "2x2"
        
        # Clear target highlights properly
        if hasattr(self, 'target_highlights'):
            for highlight in self.target_highlights.values():
                if highlight:
                    try:
                        # Try to delete from both canvases since we don't know which one
                        self.player1_canvas.delete(highlight)
                    except:
                        try:
                            self.player2_canvas.delete(highlight)
                        except:
                            pass
            self.target_highlights = {}
            
    def hide_ships(self, canvas, overlays):
        """Hide original ship placements (not shot results) on a board."""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if overlays[i][j]:
                    # Only hide if it's not a shot result (ship image or splash from shots)
                    # Check if this is a shot result by looking at shot overlay arrays
                    if canvas == self.player1_canvas:
                        is_shot_result = self.player1_shot_overlays[i][j] is not None
                    else:
                        is_shot_result = self.player2_shot_overlays[i][j] is not None
                    
                    # Only hide original ship placements, keep shot results visible
                    if not is_shot_result:
                        canvas.itemconfig(overlays[i][j], state="hidden")
                    
    def show_ships(self, canvas, ships, overlays):
        """Show ships on a board by making them visible."""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if overlays[i][j]:
                    canvas.itemconfig(overlays[i][j], state="normal")
                    
    def start_battle(self):
        """Start the battle phase."""
        self.game_phase = "battle"
        self.current_player = 1
        self.turn_taken = False  # Reset turn flag for battle start
        self.status_label.config(text="PLAYER 1'S TURN - TARGET ENEMY FLEET")
        
        # Hide placement controls, show battle controls
        self.placement_frame.pack_forget()
        self.ship_counter.pack_forget()
        
        # Make sure transition button is hidden when starting battle
        self.transition_frame.pack_forget()
        
        # Show battle controls
        self.battle_frame.pack()
        
        # Initialize battle state properly
        self.target_controller = None
        self.target_canvas = None
        self.selected_region = []
        
        # IMPORTANT: In multiplayer, NEVER show opponent's ships - only hits/misses
        # Hide ALL ships for fair play - players should not see ship locations
        self.hide_ships(self.player1_canvas, self.player1_overlays)
        self.hide_ships(self.player2_canvas, self.player2_overlays)
        
        # Hide protection visuals from opponent
        self.hide_protection_visuals_from_opponent()
        
        messagebox.showinfo("Battle Begins!", "Ship placement complete! Player 1 goes first.\nClick on the enemy board to select a target region, then choose your targeting mode and fire!\n\nNote: You cannot see enemy ship locations - only your hits and misses will be revealed!", parent=self.root)
        
        # Ensure the main window stays on top and focused after dialog
        self.root.lift()
        self.root.focus_force()
        
    def set_targeting_mode(self, mode):
        """Set the targeting mode and highlight selected button."""
        # Clear any stuck visual effects when changing modes, but preserve target selection
        self.clear_all_visual_effects(preserve_selection=True)
        
        self.selection_mode = mode
        self.targeting_mode = mode  # Fix: Also update targeting_mode for validation
        self.mode_var.set(mode)
        # Don't clear selected_region - let the user keep their target selection
        
        # Update button appearances
        for btn_mode, button in self.mode_buttons.items():
            if btn_mode == mode:
                button.config(bg="#00aa44", fg="white", relief="sunken", bd=3)
            else:
                button.config(bg="#333366", fg="white", relief="raised", bd=2)
                
        # Clear any existing target highlights
        if hasattr(self, 'target_highlights'):
            for highlight in self.target_highlights.values():
                if highlight:
                    # Clean up properly by using the stored canvas reference
                    try:
                        if hasattr(self, 'target_canvas'):
                            self.target_canvas.delete(highlight)
                    except:
                        pass
            self.target_highlights = {}
            
    def fire_quantum_weapon(self, weapon_type):
        """Execute player's selected quantum weapon."""
        # Save current selection before any processing that might clear it
        saved_region = getattr(self, 'selected_region', []).copy() if hasattr(self, 'selected_region') else []
        saved_canvas = getattr(self, 'target_canvas', None)
        saved_controller = getattr(self, 'target_controller', None)
        
        # Clear stuck visual effects but preserve target selection
        self.clear_all_visual_effects(preserve_selection=True)
        
        # Restore selection if it was cleared accidentally
        if hasattr(self, 'selected_region') and not self.selected_region and saved_region:
            self.selected_region = saved_region
            self.target_canvas = saved_canvas
            self.target_controller = saved_controller
        
        # Check if we're in battle phase
        if self.game_phase != "battle":
            messagebox.showwarning("Not Ready", "Complete ship placement first!", parent=self.root)
            return
            
        # Check if current player has already taken their turn
        if self.turn_taken and weapon_type != "zeno_defense":
            messagebox.showinfo("Turn Complete", "You have already taken your shot this turn!\nClick 'PASS TO PLAYER X' to continue.", parent=self.root)
            self.root.lift()
            self.root.focus_force()
            return
            
        # Check if target region is selected (not needed for Zeno defense)
        if weapon_type != "zeno_defense":
            if not hasattr(self, 'selected_region') or not self.selected_region:
                messagebox.showwarning("No Target", "Please click on the enemy board to select a target region first!", parent=self.root)
                return
                
            # Validate targeting mode compatibility with weapon type
            if hasattr(self, 'targeting_mode'):
                if weapon_type in ["grover", "ev_scan"] and self.targeting_mode == "classical":
                    messagebox.showwarning("Invalid Targeting", f"{weapon_type.upper()} requires a 2x2 region target, not single square. Switch to '2x2 Square' targeting mode.", parent=self.root)
                    return
                elif weapon_type == "classical" and self.targeting_mode != "classical":
                    messagebox.showwarning("Invalid Targeting", "Classical shot requires single square targeting mode. Switch to 'Classical' targeting mode.", parent=self.root)
                    return
                
            # Check if target controller is set
            if not hasattr(self, 'target_controller') or not self.target_controller:
                messagebox.showwarning("No Target", "Please click on the enemy board to select a target first!", parent=self.root)
                return
        
        # Clear selection highlights
        if hasattr(self, 'target_highlights'):
            for highlight in self.target_highlights.values():
                if highlight:
                    try:
                        self.target_canvas.delete(highlight)
                    except:
                        pass
            self.target_highlights = {}
        
        # Determine region key for tracking (tuple of sorted coords)
        region_key = tuple(sorted(self.selected_region)) if weapon_type == "grover" else None
        # Get targeted squares for this region
        if weapon_type == "grover" and region_key:
            if self.current_player == 1:
                targeted = self.player1_targeted_regions.get(region_key, set())
            else:
                targeted = self.player2_targeted_regions.get(region_key, set())
            # If all squares in region have been targeted, show message and abort
            if set(self.selected_region) == targeted:
                messagebox.showinfo("Region Exhausted", "You must choose a different region to attack on the grid.", parent=self.root)
                return
        # Get enemy ship positions, excluding already hit ships
        if self.current_player == 1:
            enemy_ships = [pos for pos in self.player2_ships if pos not in self.player2_hits]
        else:
            enemy_ships = [pos for pos in self.player1_ships if pos not in self.player1_hits]
        
        # Execute the quantum weapon
        if weapon_type == "grover":
            # Get already targeted squares for this region to exclude them
            excluded_squares = None
            if region_key:
                if self.current_player == 1:
                    excluded_squares = self.player1_targeted_regions.get(region_key, set())
                else:
                    excluded_squares = self.player2_targeted_regions.get(region_key, set())
            result = self.quantum_state.execute_attack("grover", self.selected_region, enemy_ships, excluded_squares)
        elif weapon_type == "ev_scan":
            result = self.quantum_state.execute_attack("ev_scan", self.selected_region, enemy_ships)
        elif weapon_type == "classical":
            # Classical shot - single target
            if len(self.selected_region) != 1:
                messagebox.showwarning("Invalid Target", "Classical shot requires exactly one target square!", parent=self.root)
                return
            target_coord = self.selected_region[0]
            # Check if target has a ship
            if target_coord in enemy_ships:
                result = {
                    "type": "hit",
                    "coords": target_coord,
                    "message": f"Classical shot hit enemy ship at {target_coord}!",
                    "method": "classical"
                }
            else:
                result = {
                    "type": "miss",
                    "coords": target_coord,
                    "message": f"Classical shot missed at {target_coord}.",
                    "method": "classical"
                }
        else:
            messagebox.showwarning("Error", f"Unknown weapon type: {weapon_type}", parent=self.root)
            return
            
        if "error" in result:
            messagebox.showwarning("Error", result["error"], parent=self.root)
            return
            
        # Mark that this player has taken their turn (except for Zeno defense)
        if weapon_type != "zeno_defense":
            self.turn_taken = True
            # Show transition button for next player
            self.transition_frame.pack(pady=10)
            next_player = 2 if self.current_player == 1 else 1
            self.transition_btn.config(text=f"PASS TO PLAYER {next_player}")
        
        # Show result based on weapon type
        if weapon_type == "ev_scan":
            # EV scans don't need targeting animation - show result directly
            self.complete_targeting_shot(result)
        else:
            # Show targeting animation for Grover and classical shots
            self.show_targeting_animation(result)
    
    def activate_zeno_defense(self):
        """Activate Zeno defense mode - reveal own ships and allow selection."""
        # Clear any stuck visual effects first
        self.clear_all_visual_effects()
        
        # Check if we're in battle phase
        if self.game_phase != "battle":
            messagebox.showwarning("Not Ready", "Complete ship placement first!", parent=self.root)
            return
        
        # Set targeting mode to defense
        self.targeting_mode = "defense"
        
        # Reveal player's own ships temporarily for selection
        self.reveal_own_ships_for_defense()
        
        # Show instruction message
        messagebox.showinfo("Zeno Defense", 
                          f"Player {self.current_player}: Click on one of your ships to protect it with Zeno defense!", 
                          parent=self.root)
        self.root.lift()
        self.root.focus_force()
    
    def reveal_own_ships_for_defense(self):
        """Temporarily reveal player's own ships for Zeno defense selection."""
        own_ships = self.player1_ships if self.current_player == 1 else self.player2_ships
        own_canvas = self.player1_canvas if self.current_player == 1 else self.player2_canvas
        
        # Store current revealed ships to restore later
        if not hasattr(self, 'temp_revealed_ships'):
            self.temp_revealed_ships = []
        
        # Reveal own ships with a special color for defense selection
        for row, col in own_ships:
            cx = col * self.cell_size + self.cell_size // 2
            cy = row * self.cell_size + self.cell_size // 2
            
            ship_marker = own_canvas.create_oval(
                cx - 15, cy - 15, cx + 15, cy + 15,
                fill="#4169E1", outline="#000080", width=2  # Blue color for own ships
            )
            self.temp_revealed_ships.append(ship_marker)
    
    def hide_revealed_ships(self):
        """Hide temporarily revealed ships after defense selection."""
        if hasattr(self, 'temp_revealed_ships'):
            own_canvas = self.player1_canvas if self.current_player == 1 else self.player2_canvas
            for marker in self.temp_revealed_ships:
                own_canvas.delete(marker)
            self.temp_revealed_ships = []
    
    def apply_zeno_defense_to_ship(self, coords):
        """Apply Zeno defense to a specific ship coordinate."""
        # Verify this is player's own ship
        own_ships = self.player1_ships if self.current_player == 1 else self.player2_ships
        
        if coords not in own_ships:
            messagebox.showwarning("Invalid Target", "You can only apply Zeno defense to your own ships!", parent=self.root)
            return False
        
        # Apply Zeno protection
        result = self.quantum_state.add_zeno_protection(coords, strength=3, duration=1)
        
        # Show protection effect visually
        self.show_zeno_protection(coords)
        
        # Hide revealed ships
        self.hide_revealed_ships()
        
        # Clear all visual effects to ensure clean state
        self.clear_all_visual_effects()
        
        # Display result and end turn
        messagebox.showinfo("Zeno Defense", f"{result['message']} (Protection lasts 1 round)", parent=self.root)
        self.root.lift()
        self.root.focus_force()
        
        # Clear selection and end turn
        self.selected_region = []
        self.targeting_mode = "2x2"  # Reset to default
        
        # End turn immediately for Zeno defense
        self.turn_taken = True
        
        # Show transition button for next player
        next_player = 2 if self.current_player == 1 else 1
        self.transition_btn.config(text=f"PASS TO PLAYER {next_player}")
        self.transition_frame.pack(pady=20)
        
        return True
    
    def complete_turn(self):
        """Complete current player's turn and prepare for transition."""
        self.turn_taken = True
        
        # Show transition button for next player
        next_player = 2 if self.current_player == 1 else 1
        self.transition_btn.config(text=f"PASS TO PLAYER {next_player}")
        self.transition_frame.pack(pady=20)
    
    def show_zeno_protection(self, coords):
        """Show visual indication of Zeno protection."""
        row, col = coords
        canvas = self.player1_canvas if self.current_player == 1 else self.player2_canvas
        
        cx = col * self.cell_size + self.cell_size // 2
        cy = row * self.cell_size + self.cell_size // 2
        
        # Create a golden shield overlay
        shield = canvas.create_oval(
            cx - 25, cy - 25, cx + 25, cy + 25,
            outline="#ffd700", width=3, fill="", stipple="gray25"
        )
        
        # Store shield for removal later
        if not hasattr(self, 'protection_visuals'):
            self.protection_visuals = {}
        self.protection_visuals[coords] = shield
    
    def remove_zeno_protection_visual(self, coords):
        """Remove visual indication of Zeno protection."""
        if hasattr(self, 'protection_visuals') and coords in self.protection_visuals:
            # Determine which canvas
            canvas = self.player1_canvas if self.current_player == 1 else self.player2_canvas
            try:
                canvas.delete(self.protection_visuals[coords])
            except:
                # Try other canvas
                other_canvas = self.player2_canvas if self.current_player == 1 else self.player1_canvas
                try:
                    other_canvas.delete(self.protection_visuals[coords])
                except:
                    pass
            del self.protection_visuals[coords]
    
    def hide_protection_visuals_from_opponent(self):
        """Hide Zeno protection visuals so opponent can't see protected ship locations."""
        if hasattr(self, 'protection_visuals'):
            for coords, shield_visual in self.protection_visuals.items():
                # Determine which player owns this protection
                player1_ships = set(self.player1_ships)
                player2_ships = set(self.player2_ships)
                
                if coords in player1_ships:
                    # Player 1's protection - hide when it's Player 2's turn
                    if self.current_player == 2:
                        try:
                            self.player1_canvas.itemconfig(shield_visual, state="hidden")
                        except:
                            pass
                    else:
                        # Show when it's Player 1's turn
                        try:
                            self.player1_canvas.itemconfig(shield_visual, state="normal")
                        except:
                            pass
                            
                elif coords in player2_ships:
                    # Player 2's protection - hide when it's Player 1's turn
                    if self.current_player == 1:
                        try:
                            self.player2_canvas.itemconfig(shield_visual, state="hidden")
                        except:
                            pass
                    else:
                        # Show when it's Player 2's turn
                        try:
                            self.player2_canvas.itemconfig(shield_visual, state="normal")
                        except:
                            pass
    
    def show_targeting_animation(self, shot_result):
        """Show visual animation of player's targeting pattern."""
        # Use the original selected region for animation, not the shot result coords
        # The shot result coords are the MEASURED position after quantum measurement
        if self.selected_region:
            # Get the top-left corner of the selected region for 2x2 pattern
            rows = [r for r, c in self.selected_region]
            cols = [c for r, c in self.selected_region]
            target_row = min(rows)  # Use minimum (top-left) instead of center
            target_col = min(cols)  # Use minimum (top-left) instead of center
        else:
            return
        
        # Create animation overlay based on selection mode
        self.animate_targeting_pattern(self.selection_mode, target_row, target_col, shot_result)
        
    def animate_targeting_pattern(self, pattern, target_row, target_col, shot_result):
        """Animate the targeting pattern on target board."""
        animation_cells = []
        
        # Define cells to highlight based on pattern
        if pattern == "row":
            animation_cells = [(target_row, col) for col in range(self.grid_size)]
        elif pattern == "column":
            animation_cells = [(row, target_col) for row in range(self.grid_size)]
        elif pattern == "square":
            # Highlight 2x2 area
            for dr in range(2):
                for dc in range(2):
                    r, c = target_row + dr, target_col + dc
                    if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
                        animation_cells.append((r, c))
        else:
            animation_cells = [(target_row, target_col)]
        
        # Create red pulse animation for all players
        player_color = "#cc3333"    # Red for all players
        player_outline = "#ff0000"  # Bright red outline
        
        self.targeting_animation_overlays = []
        for row, col in animation_cells:
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                cx = col * self.cell_size + self.cell_size // 2
                cy = row * self.cell_size + self.cell_size // 2
                
                # Create pulsing overlay for targeting
                overlay = self.target_canvas.create_rectangle(
                    cx - 20, cy - 20, cx + 20, cy + 20,
                    fill=player_color, outline=player_outline, width=2, stipple="gray25"
                )
                self.targeting_animation_overlays.append(overlay)
        
        # Start pulsing animation
        self.targeting_animation_step = 0
        self.targeting_pulse_animation(shot_result)
    
    def targeting_pulse_animation(self, shot_result):
        """Create pulsing effect for targeting animation."""
        if self.targeting_animation_step < 6:  # Pulse 3 times
            # Alternate visibility
            if self.targeting_animation_step % 2 == 0:
                # Show overlays
                for overlay in self.targeting_animation_overlays:
                    self.target_canvas.itemconfig(overlay, state="normal")
            else:
                # Hide overlays
                for overlay in self.targeting_animation_overlays:
                    self.target_canvas.itemconfig(overlay, state="hidden")
            
            self.targeting_animation_step += 1
            # Continue animation after 300ms
            self.root.after(300, lambda: self.targeting_pulse_animation(shot_result))
        else:
            # Animation complete - clean up and show result
            for overlay in self.targeting_animation_overlays:
                self.target_canvas.delete(overlay)
            self.targeting_animation_overlays = []
            
            # Show the actual result after animation
            self.complete_targeting_shot(shot_result)
    
    def complete_targeting_shot(self, result):
        """Complete the targeting shot after animation."""
        # Determine which overlays to use
        if hasattr(self, 'target_canvas') and self.target_canvas:
            if self.target_canvas == self.player1_canvas:
                overlays = self.player1_overlays
                shot_overlays = self.player1_shot_overlays
            else:
                overlays = self.player2_overlays
                shot_overlays = self.player2_shot_overlays
        else:
            # Fallback for cases where target_canvas isn't set
            overlays = self.player2_overlays if self.current_player == 1 else self.player1_overlays
            shot_overlays = self.player2_shot_overlays if self.current_player == 1 else self.player1_shot_overlays
            self.target_canvas = self.player2_canvas if self.current_player == 1 else self.player1_canvas
            
        # Handle different quantum weapon results
        result_type = result.get("type", "miss")
        weapon_method = result.get("method", "unknown")
        
        if result_type == "hit":
            # Standard Grover hit
            coords_info = f"at {result['coords']}" if result.get("coords") else ""
            messagebox.showinfo("Grover Hit!", f"🎯 DIRECT HIT! Enemy ship destroyed {coords_info}!\n\n{result.get('message', '')}", parent=self.root)
            self.show_hit_result(result, overlays, shot_overlays)
            # Track hit ship
            if self.current_player == 1 and result.get("coords"):
                if result["coords"] not in self.player2_hits:
                    self.player2_hits.append(result["coords"])
            elif self.current_player == 2 and result.get("coords"):
                if result["coords"] not in self.player1_hits:
                    self.player1_hits.append(result["coords"])
            
        elif result_type == "detected":
            # EV scan successful detection - region only, no specific coordinates
            region_info = f"Region: {len(result.get('region', []))} squares scanned"
            ship_count = result.get('ship_count', 'unknown')
            messagebox.showinfo("EV Detection!", f"🔍 SHIPS DETECTED! EV scan found {ship_count} ship(s) in region!\n{region_info}\n\n{result.get('message', '')}", parent=self.root)
            self.root.lift()
            self.root.focus_force()
            self.show_detection_result(result)
            
        elif result_type == "interaction":
            # EV scan with interaction - region affected, no specific coordinates
            region_info = f"Region: {len(result.get('region', []))} squares affected"
            ship_count = result.get('ship_count', 'unknown')
            messagebox.showinfo("EV Interaction!", f"⚡ REGION INTERACTION! EV scan affected {ship_count} ship(s) in region!\n{region_info}\n\n{result.get('message', '')}", parent=self.root)
            self.root.lift()
            self.root.focus_force()
            self.show_interaction_result(result, overlays, shot_overlays)
            
        elif result_type == "clear":
            # EV scan - no ships detected
            region_info = f"Region: {len(result.get('region', []))} squares scanned"
            messagebox.showinfo("EV Clear!", f"✅ REGION CLEAR! EV scan confirmed no ships in scanned area.\n{region_info}\n\n{result.get('message', '')}", parent=self.root)
            self.root.lift()
            self.root.focus_force()
            
        elif result_type == "inconclusive":
            # EV scan - inconclusive result
            region_info = f"Region: {len(result.get('region', []))} squares scanned"
            messagebox.showinfo("EV Inconclusive", f"❓ INCONCLUSIVE! EV scan could not determine ship presence in region.\n{region_info}\n\n{result.get('message', '')}", parent=self.root)
            self.root.lift()
            self.root.focus_force()
            
        elif result_type == "noise":
            # EV scan - false positive
            region_info = f"Region: {len(result.get('region', []))} squares scanned"
            messagebox.showinfo("EV Noise", f"📡 QUANTUM NOISE! EV scan detected interference in region.\n{region_info}\n\n{result.get('message', '')}", parent=self.root)
            self.root.lift()
            self.root.focus_force()
            self.show_noise_result(result, overlays, shot_overlays)
            
        elif result_type == "blocked":
            # Attack blocked by Zeno defense
            messagebox.showinfo("Attack Blocked!", f"🛡️ ZENO DEFENSE! Attack blocked by quantum shield!\n\n{result.get('message', '')}", parent=self.root)
            
        elif result_type == "obfuscated":
            # EV scan blocked by Zeno defense
            messagebox.showinfo("Scan Obfuscated!", f"🌀 ZENO INTERFERENCE! EV scan blocked by quantum defense!\n\n{result.get('message', '')}", parent=self.root)
            
        else:
            # Standard miss (Grover or other)
            coords_info = f"Measured position: {result['coords']}" if result.get("coords") else "No measurement"
            messagebox.showinfo("Miss!", f"💧 MISS! Quantum scan found no ships.\n{coords_info}\n\n{result.get('message', '')}", parent=self.root)
            self.show_miss_result(result, overlays, shot_overlays)
        
        # Track hit/miss for ALL Grover shots in region (both hits and misses)
        if result.get("method") == "grover" and result.get("coords") and self.selected_region:
            region_key = tuple(sorted(self.selected_region))
            coord = result["coords"]
            if self.current_player == 1:
                targeted = self.player1_targeted_regions.setdefault(region_key, set())
                targeted.add(coord)
            else:
                targeted = self.player2_targeted_regions.setdefault(region_key, set())
                targeted.add(coord)
        
        # Ensure window focus after dialog
        self.root.lift()
        self.root.focus_force()
        
        # Clear selection
        self.selected_region = []
        
        # Check for win (only for destructive hits)
        if result_type in ["hit", "interaction"] and hasattr(self, 'target_controller'):
            if self.target_controller.is_game_won():
                winner = "PLAYER 1" if self.current_player == 1 else "PLAYER 2"
                messagebox.showinfo("VICTORY!", f"🏆 {winner} WINS! All enemy ships destroyed!", parent=self.root)
                return
    
    def show_hit_result(self, result, overlays, shot_overlays):
        """Show visual result for a direct hit."""
        if "coords" in result and self.ship_img:
            hit_row, hit_col = result["coords"]
            cx = hit_col * self.cell_size + self.cell_size // 2
            cy = hit_row * self.cell_size + self.cell_size // 2
            
            # Show the ship image at the hit location
            ship_overlay = self.target_canvas.create_image(cx, cy, image=self.ship_img)
            overlays[hit_row][hit_col] = ship_overlay
            shot_overlays[hit_row][hit_col] = ship_overlay
            
            # Add red X over the hit ship
            x_size = 20
            x_mark1 = self.target_canvas.create_line(
                cx - x_size, cy - x_size, cx + x_size, cy + x_size,
                fill="#ff0000", width=4
            )
            x_mark2 = self.target_canvas.create_line(
                cx - x_size, cy + x_size, cx + x_size, cy - x_size,
                fill="#ff0000", width=4
            )
    
    def show_detection_result(self, result):
        """Show visual result for EV detection (region detection only, no specific coordinates)."""
        # EV scans now only detect presence in region, not specific coordinates
        if "region" in result:
            region = result["region"]
            for row, col in region:
                cx = col * self.cell_size + self.cell_size // 2
                cy = row * self.cell_size + self.cell_size // 2
                
                # Show region scan indicator (not specific ship location)
                detection_marker = self.target_canvas.create_rectangle(
                    cx - 20, cy - 20, cx + 20, cy + 20,
                    outline="#00ff00", width=2, fill="", stipple="gray75"
                )
                
                # Store for cleanup
                if not hasattr(self, 'detection_markers'):
                    self.detection_markers = []
                self.detection_markers.append(detection_marker)
    
    def show_interaction_result(self, result, overlays, shot_overlays):
        """Show visual result for EV interaction (region affected, not specific ships)."""
        # EV interaction affects region but doesn't pinpoint exact ship locations
        if "region" in result:
            region = result["region"]
            for row, col in region:
                cx = col * self.cell_size + self.cell_size // 2
                cy = row * self.cell_size + self.cell_size // 2
                
                # Show interaction effect on region
                interaction_mark = self.target_canvas.create_oval(
                    cx - 15, cy - 15, cx + 15, cy + 15,
                    outline="#ffaa00", width=2, fill="", stipple="gray50"
                )
                
                # Store for cleanup
                if not hasattr(self, 'interaction_markers'):
                    self.interaction_markers = []
                self.interaction_markers.append(interaction_mark)
    
    def show_noise_result(self, result, overlays, shot_overlays):
        """Show visual result for quantum noise in scanned region."""
        # EV noise affects entire scanned region, not specific coordinates
        if "region" in result:
            region = result["region"]
            for row, col in region:
                cx = col * self.cell_size + self.cell_size // 2
                cy = row * self.cell_size + self.cell_size // 2
                
                # Show noise/static indicator across region
                noise_marker = self.target_canvas.create_rectangle(
                    cx - 8, cy - 8, cx + 8, cy + 8,
                    outline="#888888", width=1, fill="", stipple="gray25"
                )
                
                # Store for cleanup
                if not hasattr(self, 'noise_markers'):
                    self.noise_markers = []
                self.noise_markers.append(noise_marker)
    
    def show_miss_result(self, result, overlays, shot_overlays):
        """Show visual result for a miss."""
        if "coords" in result and self.splash_img:
            miss_row, miss_col = result["coords"]
            if 0 <= miss_row < self.grid_size and 0 <= miss_col < self.grid_size:
                if not overlays[miss_row][miss_col]:
                    cx = miss_col * self.cell_size + self.cell_size // 2
                    cy = miss_row * self.cell_size + self.cell_size // 2
                    splash_overlay = self.target_canvas.create_image(cx, cy, image=self.splash_img)
                    overlays[miss_row][miss_col] = splash_overlay
                    shot_overlays[miss_row][miss_col] = splash_overlay
        
    def new_game(self):
        """Start a new game."""
        # Reset game state
        self.player1_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=False)
        self.player2_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=False)
        
        self.game_phase = "ship_placement"
        self.current_player = 1
        self.player1_ships = []
        self.player2_ships = []
        self.selected_region = []
        self.turn_taken = False  # Reset turn flag
        self.ready_for_battle = False
        
        # Reset UI
        self.status_label.config(text="PLAYER 1 - PLACE YOUR 8 SHIPS")
        self.ship_counter.config(text="Ships placed: 0/8")
        self.ship_counter.pack()
        
        # Show placement controls, hide battle controls
        self.battle_frame.pack_forget()
        self.transition_frame.pack_forget()  # Hide transition button
        self.placement_frame.pack()
        
        # Clear all overlays
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.player1_overlays[i][j]:
                    self.player1_canvas.delete(self.player1_overlays[i][j])
                    self.player1_overlays[i][j] = None
                if self.player2_overlays[i][j]:
                    self.player2_canvas.delete(self.player2_overlays[i][j])
                    self.player2_overlays[i][j] = None
                    
        # Reset shot tracking arrays
        self.player1_shot_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player2_shot_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Clear target highlights
        if hasattr(self, 'target_highlights'):
            self.target_highlights = {}
        
        # Redraw grids
        self.player1_canvas.delete("all")
        self.player2_canvas.delete("all")
        self.draw_grid(self.player1_canvas, self.player1_cells)
        self.draw_grid(self.player2_canvas, self.player2_cells)

    def clear_all_visual_effects(self, preserve_selection=False):
        """Clear all temporary visual effects to prevent stuck elements."""
        # Clear target highlights more aggressively
        if hasattr(self, 'target_highlights'):
            for highlight in self.target_highlights.values():
                if highlight:
                    # Try deleting from both canvases to be sure
                    for canvas in [self.player1_canvas, self.player2_canvas]:
                        try:
                            canvas.delete(highlight)
                        except:
                            pass
            self.target_highlights = {}
        
        # Clear selection region only if not preserving it
        if not preserve_selection and hasattr(self, 'selected_region'):
            self.selected_region = []
        
        # Reset target canvas references only if not preserving selection
        if not preserve_selection:
            if hasattr(self, 'target_canvas'):
                self.target_canvas = None
            if hasattr(self, 'target_controller'):
                self.target_controller = None
        
        # Clear targeting animations
        if hasattr(self, 'targeting_animation_overlays'):
            for overlay in self.targeting_animation_overlays:
                if overlay:
                    try:
                        if hasattr(self, 'target_canvas') and self.target_canvas:
                            self.target_canvas.delete(overlay)
                    except:
                        # Try both canvases if target_canvas isn't available
                        try:
                            self.player1_canvas.delete(overlay)
                        except:
                            try:
                                self.player2_canvas.delete(overlay)
                            except:
                                pass
            self.targeting_animation_overlays = []
        
        # Reset animation step counter
        if hasattr(self, 'targeting_animation_step'):
            self.targeting_animation_step = 0
        
        # Clear temporarily revealed ships (Zeno defense circles)
        if hasattr(self, 'temp_revealed_ships'):
            own_canvas = None
            try:
                own_canvas = self.player1_canvas if self.current_player == 1 else self.player2_canvas
            except:
                # If current_player is undefined, try both canvases
                pass
            
            for marker in self.temp_revealed_ships:
                if marker:
                    try:
                        if own_canvas:
                            own_canvas.delete(marker)
                        else:
                            # Try both canvases
                            try:
                                self.player1_canvas.delete(marker)
                            except:
                                try:
                                    self.player2_canvas.delete(marker)
                                except:
                                    pass
                    except:
                        pass
            self.temp_revealed_ships = []
        
        # Reset targeting mode to default if it's in defense mode
        if hasattr(self, 'targeting_mode') and self.targeting_mode == "defense":
            self.targeting_mode = "2x2"
        
        # Clear selection region
        if hasattr(self, 'selected_region'):
            self.selected_region = []


def main():
    """Run the multiplayer game."""
    root = tk.Tk()
    game = MultiplayerBattleshipUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()