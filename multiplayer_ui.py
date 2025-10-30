# multiplayer_ui.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from game_controller import GameController


class MultiplayerBattleshipUI:
    """
    Local multiplayer Quantum Battleship UI with turn-based gameplay.
    Ships are hidden during opponent turns for fair play.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Battleship - Local Multiplayer")
        self.root.configure(bg="#0a0a0a")
        
        # Game components
        self.player1_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=False)
        self.player2_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=False)
        
        # Game state
        self.grid_size = 8
        self.cell_size = 50
        self.game_phase = "ship_placement"  # "ship_placement" or "battle"
        self.current_player = 1  # 1 or 2
        self.ships_to_place = 8
        self.player1_ships = []
        self.player2_ships = []
        self.selected_region = []
        self.selection_mode = "square"
        self.ready_for_battle = False
        
        # UI elements
        self.player1_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player2_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player1_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player2_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
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
        
        # Turn transition button (hidden initially)
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
            text="CONFIRM PLACEMENT",
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
        # Determine target board and controller
        if clicked_canvas == self.player1_canvas and self.current_player == 2:
            # Player 2 targeting Player 1
            target_controller = self.player1_controller
        elif clicked_canvas == self.player2_canvas and self.current_player == 1:
            # Player 1 targeting Player 2
            target_controller = self.player2_controller
        else:
            # Can't target own board or wrong turn
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
                
                # NEVER show ship locations in multiplayer - only hits/misses are visible
                # Keep all ships hidden for fair play
                self.hide_ships(self.player1_canvas, self.player1_overlays)
                self.hide_ships(self.player2_canvas, self.player2_overlays)
                
            else:
                # Switching to Player 1's turn
                self.current_player = 1
                self.status_label.config(text="PLAYER 1'S TURN - TARGET ENEMY FLEET")
                
                # NEVER show ship locations in multiplayer - only hits/misses are visible
                # Keep all ships hidden for fair play
                self.hide_ships(self.player1_canvas, self.player1_overlays)
                self.hide_ships(self.player2_canvas, self.player2_overlays)
            
            # Hide transition button and clear any target selection
            self.transition_frame.pack_forget()
            self.selected_region = []
            self.target_controller = None
            self.target_canvas = None
            
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
        """Hide ships on a board by making them invisible."""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if overlays[i][j]:
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
        self.status_label.config(text="PLAYER 1'S TURN - TARGET ENEMY FLEET")
        
        # Hide placement controls, show battle controls
        self.placement_frame.pack_forget()
        self.ship_counter.pack_forget()
        self.battle_frame.pack()
        
        # Initialize battle state properly
        self.target_controller = None
        self.target_canvas = None
        self.selected_region = []
        
        # IMPORTANT: In multiplayer, NEVER show opponent's ships - only hits/misses
        # Hide ALL ships for fair play - players should not see ship locations
        self.hide_ships(self.player1_canvas, self.player1_overlays)
        self.hide_ships(self.player2_canvas, self.player2_overlays)
        
        messagebox.showinfo("Battle Begins!", "Ship placement complete! Player 1 goes first.\nClick on the enemy board to select a target region, then choose your targeting mode and fire!\n\nNote: You cannot see enemy ship locations - only your hits and misses will be revealed!", parent=self.root)
        
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
            
    def fire_quantum_shot(self):
        """Execute player's quantum shot."""
        # Check if we're in battle phase
        if self.game_phase != "battle":
            messagebox.showwarning("Not Ready", "Complete ship placement first!", parent=self.root)
            return
            
        # Check if target region is selected
        if not hasattr(self, 'selected_region') or not self.selected_region:
            messagebox.showwarning("No Target", "Please click on the enemy board to select a target region first!", parent=self.root)
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
            
        # Fire shot
        result = self.target_controller.fire_shot(self.selected_region)
        
        if "error" in result:
            messagebox.showwarning("Error", result["error"], parent=self.root)
            return
            
        # Determine which overlays to use
        if self.target_canvas == self.player1_canvas:
            overlays = self.player1_overlays
        else:
            overlays = self.player2_overlays
            
        # Update board display
        if result["type"] == "hit":
            coords_info = f"at {result['coords']}" if result.get("coords") else ""
            messagebox.showinfo("Result", f"🎯 HIT! Enemy ship destroyed {coords_info}!\n\nQuantum measurement: {result.get('message', '')}", parent=self.root)
            # Ensure window focus after dialog
            self.root.lift()
            self.root.focus_force()
            # Reveal the hit ship location only
            if "coords" in result and self.ship_img:
                hit_row, hit_col = result["coords"]
                cx = hit_col * self.cell_size + self.cell_size // 2
                cy = hit_row * self.cell_size + self.cell_size // 2
                # Show the ship image at the hit location
                ship_overlay = self.target_canvas.create_image(cx, cy, image=self.ship_img)
                # Mark this location as having an overlay
                if self.target_canvas == self.player1_canvas:
                    self.player1_overlays[hit_row][hit_col] = ship_overlay
                else:
                    self.player2_overlays[hit_row][hit_col] = ship_overlay
        else:
            coords_info = f"Measured position: {result['coords']}" if result.get("coords") else "No measurement"
            messagebox.showinfo("Result", f"💧 MISS! Quantum scan found no ships.\n{coords_info}\n\nDetails: {result.get('message', '')}", parent=self.root)
            # Ensure window focus after dialog
            self.root.lift()
            self.root.focus_force()
            # Place splash only on measured position
            if "coords" in result and self.splash_img:
                miss_row, miss_col = result["coords"]
                if 0 <= miss_row < self.grid_size and 0 <= miss_col < self.grid_size:
                    if not overlays[miss_row][miss_col]:
                        cx = miss_col * self.cell_size + self.cell_size // 2
                        cy = miss_row * self.cell_size + self.cell_size // 2
                        splash_overlay = self.target_canvas.create_image(cx, cy, image=self.splash_img)
                        overlays[miss_row][miss_col] = splash_overlay
        
        # Clear selection
        self.selected_region = []
        
        # Check for win
        if self.target_controller.is_game_won():
            winner = "PLAYER 1" if self.current_player == 1 else "PLAYER 2"
            messagebox.showinfo("VICTORY!", f"🏆 {winner} WINS! All enemy ships destroyed!", parent=self.root)
            return
            
        # Show transition button for next turn
        self.transition_frame.pack(pady=10)
        next_player = 2 if self.current_player == 1 else 1
        self.transition_btn.config(text=f"PASS TO PLAYER {next_player}")
        
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
        self.ready_for_battle = False
        
        # Reset UI
        self.status_label.config(text="PLAYER 1 - PLACE YOUR 8 SHIPS")
        self.ship_counter.config(text="Ships placed: 0/8")
        self.ship_counter.pack()
        
        # Show placement controls, hide battle controls
        self.battle_frame.pack_forget()
        self.transition_frame.pack_forget()
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
        
        # Clear target highlights
        if hasattr(self, 'target_highlights'):
            self.target_highlights = {}
        
        # Redraw grids
        self.player1_canvas.delete("all")
        self.player2_canvas.delete("all")
        self.draw_grid(self.player1_canvas, self.player1_cells)
        self.draw_grid(self.player2_canvas, self.player2_cells)


def main():
    """Run the multiplayer game."""
    root = tk.Tk()
    game = MultiplayerBattleshipUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()