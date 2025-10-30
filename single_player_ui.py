# single_player_ui.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from game_controller import GameController
from ai_player import AIPlayer


class SinglePlayerBattleshipUI:
    """
    Single player Quantum Battleship UI with dual boards.
    Left board: Your ships (defensive view)
    Right board: Enemy ships (offensive view)
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Battleship - Single Player")
        self.root.configure(bg="#0a0a0a")  # Darker background for better contrast
        
        # Game components
        self.player_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=False)
        self.ai_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=True)
        self.ai_player = AIPlayer(difficulty="hard")  # Default, will be overridden by user selection
        
        # Game state
        self.grid_size = 8
        self.cell_size = 50  # Reduced from 60 for more compact layout
        self.game_phase = "ship_placement"  # "ship_placement" or "battle"
        self.player_turn = True
        self.ships_to_place = 8
        self.placed_ships = []
        
        # UI elements
        self.player_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ai_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ai_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.selected_region = []
        self.selection_mode = "square"
        
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
            text="QUANTUM BATTLESHIP",
            font=("Helvetica", 24, "bold"),
            bg="#0a0a0a",
            fg="#00ffff"  # Bright cyan for better visibility
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Harness the power of quantum mechanics",
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
            text="PLACE YOUR 8 SHIPS",
            font=("Helvetica", 16, "bold"),
            bg="#003366",  # Dark blue background
            fg="#ffffff",  # White text
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
            fg="#ffaa00"  # Bright orange
        )
        self.ship_counter.pack(pady=3)
        
        # AI difficulty selection
        self.difficulty_frame = tk.Frame(self.status_frame, bg="#0a0a0a")
        self.difficulty_frame.pack(pady=8)
        
        difficulty_title = tk.Label(
            self.difficulty_frame,
            text="Choose AI Opponent:",
            font=("Helvetica", 12, "bold"),
            bg="#0a0a0a",
            fg="#00ffaa"
        )
        difficulty_title.pack(pady=(0, 5))
        
        self.difficulty_var = tk.StringVar(value="hard")
        difficulty_options = [
            ("Easy (Random shots)", "easy"),
            ("Medium (Smart hunting)", "medium"), 
            ("Hard (Quantum targeting)", "hard")
        ]
        
        # Create a frame with border for the radio buttons
        radio_frame = tk.Frame(
            self.difficulty_frame, 
            bg="#1a1a2e", 
            relief="raised", 
            bd=2,
            padx=10,
            pady=8
        )
        radio_frame.pack()
        
        for text, value in difficulty_options:
            rb = tk.Radiobutton(
                radio_frame,
                text=text,
                variable=self.difficulty_var,
                value=value,
                font=("Helvetica", 12),
                bg="#1a1a2e",
                fg="white",
                selectcolor="#004466",
                activebackground="#2a2a4e",
                activeforeground="white",
                relief="flat",
                padx=10,
                pady=3
            )
            rb.pack(anchor="w", pady=2)
        
        # Main game area
        self.create_game_boards()
        
        # Controls
        self.create_controls()
        
    def create_game_boards(self):
        """Create the dual board layout."""
        boards_frame = tk.Frame(self.root, bg="#0a0a0a")
        boards_frame.pack(pady=15)
        
        # Player's board (left side - defensive)
        player_frame = tk.Frame(boards_frame, bg="#0a0a0a")
        player_frame.pack(side=tk.LEFT, padx=20)
        
        player_title = tk.Label(
            player_frame,
            text="YOUR FLEET",
            font=("Helvetica", 14, "bold"),
            bg="#0a0a0a",
            fg="#00ff88"
        )
        player_title.pack(pady=(0, 8))
        
        canvas_size = self.grid_size * self.cell_size
        self.player_canvas = tk.Canvas(
            player_frame,
            width=canvas_size,
            height=canvas_size,
            highlightthickness=3,
            highlightbackground="#00ff88",
            bg="#004466",
            relief="raised",
            bd=3
        )
        self.player_canvas.pack()
        self.player_canvas.bind("<Button-1>", self.on_player_board_click)
        
        # AI's board (right side - offensive) 
        ai_frame = tk.Frame(boards_frame, bg="#0a0a0a")
        ai_frame.pack(side=tk.LEFT, padx=20)
        
        ai_title = tk.Label(
            ai_frame,
            text="ENEMY WATERS",
            font=("Helvetica", 14, "bold"),
            bg="#0a0a0a",
            fg="#ff4444"
        )
        ai_title.pack(pady=(0, 8))
        
        self.ai_canvas = tk.Canvas(
            ai_frame,
            width=canvas_size,
            height=canvas_size,
            highlightthickness=3,
            highlightbackground="#ff4444",
            bg="#004466",
            relief="raised",
            bd=3
        )
        self.ai_canvas.pack()
        self.ai_canvas.bind("<Button-1>", self.on_ai_board_click)
        
        # Initially disable AI board
        self.ai_canvas.config(state="disabled")
        
        # Draw grids
        self.draw_player_grid()
        self.draw_ai_grid()
        
    def draw_player_grid(self):
        """Draw the player's defensive grid with water background."""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0, y0 = j * self.cell_size, i * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                
                # Place water background image
                if self.water_img:
                    self.player_canvas.create_image(
                        x0 + self.cell_size // 2,
                        y0 + self.cell_size // 2,
                        image=self.water_img
                    )
                
                # Create transparent rectangle for click handling
                rect = self.player_canvas.create_rectangle(
                    x0, y0, x1, y1,
                    outline="#88ccff", 
                    width=1, 
                    fill="",  # Transparent so water shows through
                    stipple=""
                )
                self.player_cells[i][j] = rect
                
    def draw_ai_grid(self):
        """Draw the AI's grid for targeting with water background."""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0, y0 = j * self.cell_size, i * self.cell_size
                x1, y1 = x0 + self.cell_size, y0 + self.cell_size
                
                # Place water background image
                if self.water_img:
                    self.ai_canvas.create_image(
                        x0 + self.cell_size // 2,
                        y0 + self.cell_size // 2,
                        image=self.water_img
                    )
                
                # Create transparent rectangle for click handling
                rect = self.ai_canvas.create_rectangle(
                    x0, y0, x1, y1,
                    outline="#88ccff", 
                    width=1, 
                    fill="",  # Transparent so water shows through
                    stipple=""
                )
                self.ai_cells[i][j] = rect
                
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
            font=("Helvetica", 11, "bold"),
            bg="#ff6600",
            fg="white",
            activebackground="#ff8833",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=15,
            pady=8,
            command=self.place_ships_randomly
        )
        random_btn.pack(side=tk.LEFT, padx=8)
        
        confirm_btn = tk.Button(
            button_row,
            text="CONFIRM & START BATTLE",
            font=("Helvetica", 11, "bold"),
            bg="#00aa00",
            fg="white",
            activebackground="#00cc00",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=15,
            pady=8,
            command=self.confirm_ship_placement
        )
        confirm_btn.pack(side=tk.LEFT, padx=8)
        
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
        modes = [("2x2 Grid", "square"), ("Full Row", "row"), ("Full Column", "column")]
        
        button_frame = tk.Frame(mode_buttons_frame, bg="#1a1a2e")
        button_frame.pack()
        
        for i, (text, mode) in enumerate(modes):
            btn = tk.Button(
                button_frame,
                text=text,
                command=lambda m=mode: self.set_targeting_mode(m),
                font=("Helvetica", 10, "bold"),
                bg="#333366",
                fg="white",
                activebackground="#4455aa",
                activeforeground="white",
                relief="raised",
                bd=2,
                padx=12,
                pady=6,
                width=10
            )
            btn.grid(row=0, column=i, padx=3)
            self.mode_buttons[mode] = btn
        
        # Set initial selection
        self.set_targeting_mode("square")
        
        # Fire button
        self.fire_btn = tk.Button(
            self.battle_frame,
            text="QUANTUM FIRE!",
            command=self.fire_quantum_shot,
            font=("Helvetica", 14, "bold"),
            bg="#cc3333",
            fg="white",
            activebackground="#ff4444",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=30,
            pady=10
        )
        self.fire_btn.pack(pady=15)
        
        # New game button
        new_game_btn = tk.Button(
            control_frame,
            text="NEW GAME",
            font=("Helvetica", 12, "bold"),
            bg="#666666",
            fg="white",
            activebackground="#888888",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=20,
            pady=8,
            command=self.new_game
        )
        new_game_btn.pack(pady=10)
        
    def on_player_board_click(self, event):
        """Handle clicks on player's board (ship placement)."""
        if self.game_phase != "ship_placement":
            return
            
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if row >= self.grid_size or col >= self.grid_size:
            return
            
        pos = (row, col)
        
        # Toggle ship placement
        if pos in self.placed_ships:
            # Remove ship
            self.placed_ships.remove(pos)
            if self.player_overlays[row][col]:
                self.player_canvas.delete(self.player_overlays[row][col])
                self.player_overlays[row][col] = None
        else:
            # Add ship (if under limit)
            if len(self.placed_ships) < 8:
                self.placed_ships.append(pos)
                # Place ship image
                if self.ship_img:
                    cx = col * self.cell_size + self.cell_size // 2
                    cy = row * self.cell_size + self.cell_size // 2
                    ship_overlay = self.player_canvas.create_image(cx, cy, image=self.ship_img)
                    self.player_overlays[row][col] = ship_overlay
        
        self.update_ship_counter()
        
    def on_ai_board_click(self, event):
        """Handle clicks on AI board (targeting)."""
        if self.game_phase != "battle" or not self.player_turn:
            return
            
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if row >= self.grid_size or col >= self.grid_size:
            return
            
        self.highlight_target_region(row, col)
        
    def highlight_target_region(self, row, col):
        """Highlight the selected targeting region."""
        # Clear previous selection by removing yellow highlights
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Remove yellow highlight if it exists
                if hasattr(self, 'target_highlights') and (i, j) in self.target_highlights:
                    if self.target_highlights[(i, j)]:
                        self.ai_canvas.delete(self.target_highlights[(i, j)])
        
        # Initialize target highlights dict if not exists
        if not hasattr(self, 'target_highlights'):
            self.target_highlights = {}
        
        # Get new region
        self.selected_region = self.ai_controller.get_region_coords(
            row, col, self.selection_mode, 2
        )
        
        # Highlight new selection with yellow overlay
        for rr, cc in self.selected_region:
            if 0 <= rr < self.grid_size and 0 <= cc < self.grid_size:
                # Only highlight if not already hit/missed
                if not self.ai_overlays[rr][cc]:
                    cx = cc * self.cell_size + self.cell_size // 2
                    cy = rr * self.cell_size + self.cell_size // 2
                    # Create yellow selection overlay
                    highlight = self.ai_canvas.create_rectangle(
                        cc * self.cell_size + 5, rr * self.cell_size + 5,
                        (cc + 1) * self.cell_size - 5, (rr + 1) * self.cell_size - 5,
                        fill="#ffff00", outline="#ffaa00", width=2, stipple="gray50"
                    )
                    self.target_highlights[(rr, cc)] = highlight
    
    def place_ships_randomly(self):
        """Randomly place all ships."""
        self.placed_ships = self.player_controller.game.generate_random_ships()
        self.update_player_ship_display()
        self.update_ship_counter()
        
    def update_player_ship_display(self):
        """Update the visual display of player ships."""
        # Clear current ship displays
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.player_overlays[i][j]:
                    self.player_canvas.delete(self.player_overlays[i][j])
                    self.player_overlays[i][j] = None
        
        # Show ships with images
        for row, col in self.placed_ships:
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                if self.ship_img:
                    cx = col * self.cell_size + self.cell_size // 2
                    cy = row * self.cell_size + self.cell_size // 2
                    ship_overlay = self.player_canvas.create_image(cx, cy, image=self.ship_img)
                    self.player_overlays[row][col] = ship_overlay
                
    def update_ship_counter(self):
        """Update the ship counter display."""
        count = len(self.placed_ships)
        self.ship_counter.config(text=f"Ships placed: {count}/8")
        
    def confirm_ship_placement(self):
        """Confirm ship placement and start battle."""
        if len(self.placed_ships) < 8:
            messagebox.showwarning("Incomplete", "Please place all 8 ships!", parent=self.root)
            return
            
        # Set ships in game controller
        self.player_controller.game.ship_positions = self.placed_ships
        
        # Create AI with selected difficulty
        selected_difficulty = self.difficulty_var.get()
        self.ai_player = AIPlayer(difficulty=selected_difficulty)
        
        # Switch to battle phase
        self.game_phase = "battle"
        difficulty_names = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}
        self.status_label.config(text=f"BATTLE PHASE - YOUR TURN (vs {difficulty_names[selected_difficulty]} AI)")
        
        # Hide placement controls and difficulty selector, show battle controls
        self.placement_frame.pack_forget()
        self.difficulty_frame.pack_forget()
        self.battle_frame.pack()
        
        # Enable AI board for targeting
        self.ai_canvas.config(state="normal")
        
        # Hide ship counter
        self.ship_counter.pack_forget()
        
        messagebox.showinfo("Battle Begins!", f"Ship placement complete! Facing {difficulty_names[selected_difficulty]} AI. Target the enemy fleet!", parent=self.root)
        
        # Ensure the main window stays on top and focused after dialog
        self.root.lift()
        self.root.focus_force()
        
    def set_targeting_mode(self, mode):
        """Set the targeting mode and highlight selected button."""
        self.selection_mode = mode
        self.mode_var.set(mode)
        self.selected_region = []
        
        # Update button appearances
        for btn_mode, button in self.mode_buttons.items():
            if btn_mode == mode:
                # Highlight selected button
                button.config(
                    bg="#00aa44",
                    fg="white",
                    relief="sunken",
                    bd=3
                )
            else:
                # Reset unselected buttons
                button.config(
                    bg="#333366",
                    fg="white", 
                    relief="raised",
                    bd=2
                )
        
        # Clear any existing target highlights
        if hasattr(self, 'target_highlights'):
            for highlight in self.target_highlights.values():
                if highlight:
                    self.ai_canvas.delete(highlight)
            self.target_highlights = {}
                    
    def fire_quantum_shot(self):
        """Execute player's quantum shot."""
        if not self.player_turn or not self.selected_region:
            return
            
        # Clear selection highlights first
        if hasattr(self, 'target_highlights'):
            for highlight in self.target_highlights.values():
                if highlight:
                    self.ai_canvas.delete(highlight)
            self.target_highlights = {}
            
        # Fire at AI using quantum measurement
        result = self.ai_controller.fire_shot(self.selected_region)
        
        if "error" in result:
            messagebox.showwarning("Error", result["error"], parent=self.root)
            return
            
        # Update AI board display with appropriate images
        if result["type"] == "hit":
            coords_info = f"at {result['coords']}" if result.get("coords") else ""
            messagebox.showinfo("Result", f"🎯 HIT! Enemy ship destroyed {coords_info}!\n\nQuantum measurement: {result.get('message', '')}", parent=self.root)
            # Ensure window focus after dialog
            self.root.lift()
            self.root.focus_force()
            # Place ship image only on the specific measured coordinate
            if "coords" in result and self.ship_img:
                hit_row, hit_col = result["coords"]
                cx = hit_col * self.cell_size + self.cell_size // 2
                cy = hit_row * self.cell_size + self.cell_size // 2
                ship_overlay = self.ai_canvas.create_image(cx, cy, image=self.ship_img)
                self.ai_overlays[hit_row][hit_col] = ship_overlay
        else:
            coords_info = f"Measured position: {result['coords']}" if result.get("coords") else "No measurement"
            messagebox.showinfo("Result", f"💧 MISS! Quantum scan found no ships.\n{coords_info}\n\nDetails: {result.get('message', '')}", parent=self.root)
            # Ensure window focus after dialog
            self.root.lift()
            self.root.focus_force()
            # Place splash image only on the specific measured coordinate (not entire region)
            if "coords" in result and self.splash_img:
                miss_row, miss_col = result["coords"]
                if 0 <= miss_row < self.grid_size and 0 <= miss_col < self.grid_size:
                    if not self.ai_overlays[miss_row][miss_col]:
                        cx = miss_col * self.cell_size + self.cell_size // 2
                        cy = miss_row * self.cell_size + self.cell_size // 2
                        splash_overlay = self.ai_canvas.create_image(cx, cy, image=self.splash_img)
                        self.ai_overlays[miss_row][miss_col] = splash_overlay
        
        # Clear selection
        self.selected_region = []
        
        # Check if player won
        if self.ai_controller.is_game_won():
            messagebox.showinfo("VICTORY!", "🏆 You destroyed the enemy fleet! YOU WIN!", parent=self.root)
            self.player_turn = False
            return
            
        # AI's turn
        self.player_turn = False
        self.status_label.config(text="AI IS THINKING...")
        self.root.after(1000, self.ai_turn)
        
    def ai_turn(self):
        """Execute AI's turn."""
        # AI makes its move using quantum shots
        ai_result = self.ai_player.make_move(self.player_controller)
        
        # Get the actual result from the AI's quantum shot
        shot_result = ai_result.get("result", {})
        
        # Show AI targeting animation first
        self.show_ai_targeting_animation(ai_result, shot_result)
    
    def show_ai_targeting_animation(self, ai_result, shot_result):
        """Show visual animation of AI's targeting pattern."""
        # Extract targeting info from AI message
        ai_message = ai_result.get("message", "")
        
        # Determine animation pattern based on AI action
        if "quantum row" in ai_message.lower():
            pattern = "row"
        elif "quantum column" in ai_message.lower():
            pattern = "column"
        elif "quantum square" in ai_message.lower():
            pattern = "square"
        else:
            pattern = "single"  # For easy/medium AI
        
        # Get the target coordinate
        target_coord = shot_result.get("coords")
        if not target_coord:
            # Skip animation if no coordinate
            self.complete_ai_turn(ai_result, shot_result)
            return
            
        target_row, target_col = target_coord
        
        # Create animation overlay
        self.animate_targeting_pattern(pattern, target_row, target_col, ai_result, shot_result)
    
    def animate_targeting_pattern(self, pattern, target_row, target_col, ai_result, shot_result):
        """Animate the targeting pattern on player's board."""
        animation_cells = []
        
        # Define cells to highlight based on pattern
        if pattern == "row":
            # Highlight entire row
            animation_cells = [(target_row, col) for col in range(self.grid_size)]
        elif pattern == "column":
            # Highlight entire column
            animation_cells = [(row, target_col) for row in range(self.grid_size)]
        elif pattern == "square":
            # Highlight 2x2 area starting from target position (not centered around it)
            for dr in range(2):
                for dc in range(2):
                    r, c = target_row + dr, target_col + dc
                    if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
                        animation_cells.append((r, c))
        else:
            # Single cell for easy/medium AI
            animation_cells = [(target_row, target_col)]
        
        # Create yellow pulse animation
        self.animation_overlays = []
        for row, col in animation_cells:
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                cx = col * self.cell_size + self.cell_size // 2
                cy = row * self.cell_size + self.cell_size // 2
                
                # Create pulsing yellow overlay
                overlay = self.player_canvas.create_rectangle(
                    cx - 20, cy - 20, cx + 20, cy + 20,
                    fill="#ffff00", outline="#ffaa00", width=2, stipple="gray25"
                )
                self.animation_overlays.append(overlay)
        
        # Start pulsing animation
        self.animation_step = 0
        self.pulse_animation(ai_result, shot_result)
    
    def pulse_animation(self, ai_result, shot_result):
        """Create pulsing effect for targeting animation."""
        if self.animation_step < 6:  # Pulse 3 times
            # Alternate visibility
            if self.animation_step % 2 == 0:
                # Show overlays
                for overlay in self.animation_overlays:
                    self.player_canvas.itemconfig(overlay, state="normal")
            else:
                # Hide overlays
                for overlay in self.animation_overlays:
                    self.player_canvas.itemconfig(overlay, state="hidden")
            
            self.animation_step += 1
            # Continue animation after 300ms
            self.root.after(300, lambda: self.pulse_animation(ai_result, shot_result))
        else:
            # Animation complete - clean up and show result
            for overlay in self.animation_overlays:
                self.player_canvas.delete(overlay)
            self.animation_overlays = []
            
            # Show the actual result after animation
            self.complete_ai_turn(ai_result, shot_result)
    
    def complete_ai_turn(self, ai_result, shot_result):
        """Complete the AI turn after animation."""
        # Update player board with AI's shot
        if shot_result.get("type") == "hit":
            hit_pos = shot_result.get("coords", "unknown")
            message = f"ENEMY HIT! Your ship at {hit_pos} is destroyed!\n\nAI Action: {ai_result.get('message', '')}"
            
            # Show hit on the specific coordinate that was measured
            if shot_result.get("coords"):
                hit_row, hit_col = shot_result["coords"]
                if 0 <= hit_row < self.grid_size and 0 <= hit_col < self.grid_size:
                    # Create a red X overlay on top of the ship
                    cx = hit_col * self.cell_size + self.cell_size // 2
                    cy = hit_row * self.cell_size + self.cell_size // 2
                    
                    # Draw red X
                    x_size = 20
                    x_mark1 = self.player_canvas.create_line(
                        cx - x_size, cy - x_size, cx + x_size, cy + x_size,
                        fill="#ff0000", width=4
                    )
                    x_mark2 = self.player_canvas.create_line(
                        cx - x_size, cy + x_size, cx + x_size, cy - x_size,
                        fill="#ff0000", width=4
                    )
        else:
            miss_pos = shot_result.get("coords", "unknown")
            message = f"Enemy missed! Shot at {miss_pos} found only water.\n\nAI Action: {ai_result.get('message', '')}"
            
            # Show splash only on the specific coordinate that was measured
            if shot_result.get("coords"):
                miss_row, miss_col = shot_result["coords"]
                if 0 <= miss_row < self.grid_size and 0 <= miss_col < self.grid_size:
                    # Only show splash if it's not a ship location
                    if (miss_row, miss_col) not in self.placed_ships and self.splash_img:
                        cx = miss_col * self.cell_size + self.cell_size // 2
                        cy = miss_row * self.cell_size + self.cell_size // 2
                        splash_overlay = self.player_canvas.create_image(cx, cy, image=self.splash_img)
        
        messagebox.showinfo("AI Turn", message, parent=self.root)
        
        # Ensure window focus after dialog
        self.root.lift()
        self.root.focus_force()
        
        # Check if AI won
        if self.player_controller.is_game_won():
            messagebox.showinfo("DEFEAT!", "The AI destroyed your fleet! GAME OVER!", parent=self.root)
            self.root.lift()
            self.root.focus_force()
            return
            
        # Player's turn again
        self.player_turn = True
        self.status_label.config(text="YOUR TURN - TARGET ENEMY FLEET")
        
    def new_game(self):
        """Start a new game."""
        # Reset game state
        self.player_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=False)
        self.ai_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=True)
        self.ai_player = AIPlayer(difficulty="hard")  # Use hard difficulty for quantum shots
        
        self.game_phase = "ship_placement"
        self.player_turn = True
        self.placed_ships = []
        self.selected_region = []
        
        # Reset UI
        self.status_label.config(text="PLACE YOUR 8 SHIPS")
        self.ship_counter.config(text="Ships placed: 0/8")
        self.ship_counter.pack()
        
        # Show placement controls and difficulty selector, hide battle controls
        self.battle_frame.pack_forget()
        self.placement_frame.pack()
        self.difficulty_frame.pack(pady=15)
        
        # Reset difficulty to default
        self.difficulty_var.set("hard")
        
        # Disable AI board
        self.ai_canvas.config(state="disabled")
        
        # Clear all overlays
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.player_overlays[i][j]:
                    self.player_canvas.delete(self.player_overlays[i][j])
                    self.player_overlays[i][j] = None
                if self.ai_overlays[i][j]:
                    self.ai_canvas.delete(self.ai_overlays[i][j])
                    self.ai_overlays[i][j] = None
        
        # Clear target highlights
        if hasattr(self, 'target_highlights'):
            for highlight in self.target_highlights.values():
                if highlight:
                    self.ai_canvas.delete(highlight)
            self.target_highlights = {}
        
        # Redraw grids with fresh water backgrounds
        self.player_canvas.delete("all")
        self.ai_canvas.delete("all")
        self.draw_player_grid()
        self.draw_ai_grid()


def main():
    """Run the single player game."""
    root = tk.Tk()
    game = SinglePlayerBattleshipUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()