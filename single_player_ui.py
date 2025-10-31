# single_player_ui.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from game_controller import GameController
from ai_player import AIPlayer
from quantum_weapons import QuantumGameState


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
        
        # Configure window for better scaling
        self.root.geometry("1000x800")  # Set initial size (increased height)
        self.root.minsize(800, 600)     # Set minimum size (increased height)
        
        # Make window resizable and center it
        self.root.resizable(True, True)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f'1000x800+{x}+{y}')
        
        # Game components
        self.player_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=False)
        self.ai_controller = GameController(grid_size=8, num_ships=8, auto_place_ships=True)
        self.ai_player = AIPlayer(difficulty="hard")  # Default, will be overridden by user selection
        
        # Game state
        self.grid_size = 8
        self.cell_size = 60  # Increased for better visibility
        self.game_phase = "ship_placement"  # "ship_placement" or "battle"
        self.player_turn = True
        self.ships_to_place = 8
        self.placed_ships = []
        
        # Weapon selection mode
        self.current_weapon = None
        self.zeno_mode = False  # Track if we're in Zeno defense mode
        
        # UI elements
        self.player_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ai_cells = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.player_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.ai_overlays = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.selected_region = []
        self.selection_mode = "square"
        
        # Initialize quantum weapons system
        self.quantum_state = QuantumGameState()
        
        # Load assets first
        self.load_assets()
        
        self.setup_ui()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 4 or event.delta > 0:
            self.main_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.main_canvas.yview_scroll(1, "units")
    
    def _center_content(self, event):
        """Center the content in the canvas."""
        canvas_width = event.width
        frame_width = self.scrollable_frame.winfo_reqwidth()
        
        if frame_width < canvas_width:
            # Center the frame if it's smaller than canvas
            x = (canvas_width - frame_width) // 2
            self.main_canvas.coords(self.canvas_window, x, 0)
        
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
        """Setup the complete UI with scrolling capability."""
        # Create main canvas for scrolling
        self.main_canvas = tk.Canvas(self.root, bg="#0a0a0a", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas, bg="#0a0a0a")
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        # Center the content window
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind canvas resize to center content
        self.main_canvas.bind('<Configure>', self._center_content)
        
        # Pack scrolling components
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to scrolling
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel)  # Linux
        self.root.bind_all("<Button-5>", self._on_mousewheel)  # Linux
        
        # Title
        title_frame = tk.Frame(self.scrollable_frame, bg="#0a0a0a")
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
        self.status_frame = tk.Frame(self.scrollable_frame, bg="#0a0a0a")
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
        boards_frame = tk.Frame(self.scrollable_frame, bg="#0a0a0a")
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
        control_frame = tk.Frame(self.scrollable_frame, bg="#0a0a0a")
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
            text="TARGETING MODE",
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
                padx=12,
                pady=8,
                width=10
            )
            btn.grid(row=0, column=i, padx=5)
            self.mode_buttons[mode] = btn
        
        # Set initial selection
        self.set_targeting_mode("classical")
        
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
        
        # Weapons in two rows for better layout
        weapons_frame = tk.Frame(combat_frame, bg="#1a1a2e")
        weapons_frame.pack()
        
        # Top row: Offensive weapons
        offensive_frame = tk.Frame(weapons_frame, bg="#1a1a2e")
        offensive_frame.pack(pady=5)
        
        # Classical Shot button
        self.classical_btn = tk.Button(
            offensive_frame,
            text="CLASSICAL SHOT\n(Single Target)",
            command=lambda: self.fire_quantum_weapon("classical"),
            font=("Helvetica", 11, "bold"),
            bg="#669933",
            fg="white",
            activebackground="#77aa44",
            activeforeground="white",
            relief="raised",
            bd=4,
            padx=12,
            pady=10,
            width=14,
            height=3
        )
        self.classical_btn.pack(side=tk.LEFT, padx=5)
        
        # Grover Shot button
        self.grover_btn = tk.Button(
            offensive_frame,
            text="GROVER SHOT\n(Direct Attack)",
            command=lambda: self.fire_quantum_weapon("grover"),
            font=("Helvetica", 11, "bold"),
            bg="#cc3333",
            fg="white",
            activebackground="#ff4444",
            activeforeground="white",
            relief="raised",
            bd=4,
            padx=12,
            pady=10,
            width=14,
            height=3
        )
        self.grover_btn.pack(side=tk.LEFT, padx=5)
        
        # EV Scan button
        self.ev_scan_btn = tk.Button(
            offensive_frame,
            text="EV SCAN\n(Stealth Recon)",
            command=lambda: self.fire_quantum_weapon("ev_scan"),
            font=("Helvetica", 11, "bold"),
            bg="#3366cc",
            fg="white",
            activebackground="#4477dd",
            activeforeground="white",
            relief="raised",
            bd=4,
            padx=12,
            pady=10,
            width=14,
            height=3
        )
        self.ev_scan_btn.pack(side=tk.LEFT, padx=5)
        
        # Bottom row: Defensive weapon
        defensive_frame = tk.Frame(weapons_frame, bg="#1a1a2e")
        defensive_frame.pack(pady=5)
        
        # Zeno Defense button
        self.zeno_btn = tk.Button(
            defensive_frame,
            text="ZENO DEFENSE\n(Protect Your Ships)",
            command=lambda: self.activate_zeno_defense(),
            font=("Helvetica", 11, "bold"),
            bg="#cc9900",
            fg="white",
            activebackground="#dd9900",
            activeforeground="white",
            relief="raised",
            bd=4,
            padx=12,
            pady=10,
            width=20,
            height=3
        )
        self.zeno_btn.pack()
        
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
        
    def on_player_board_click(self, event):
        """Handle clicks on player's board (ship placement or Zeno defense)."""
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        
        if row >= self.grid_size or col >= self.grid_size:
            return
            
        # Ship placement mode
        if self.game_phase == "ship_placement":
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
        
        # Zeno defense mode  
        elif self.game_phase == "battle" and self.player_turn and self.zeno_mode:
            self.highlight_defense_region(row, col)
        
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
        
        # Get new region based on targeting mode
        if self.selection_mode == "classical":
            # Classical mode: single square
            self.selected_region = [(row, col)]
        else:
            # Quantum modes: use controller to get region
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
                    
    def highlight_defense_region(self, row, col):
        """Highlight the selected defense region on player board."""
        # Clear previous selection
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if hasattr(self, 'defense_highlights') and (i, j) in self.defense_highlights:
                    if self.defense_highlights[(i, j)]:
                        self.player_canvas.delete(self.defense_highlights[(i, j)])
        
        # Initialize defense highlights dict if not exists
        if not hasattr(self, 'defense_highlights'):
            self.defense_highlights = {}
        
        # Get new region for defense - SINGLE SQUARE ONLY for Zeno defense
        candidate_pos = (row, col)

        # Filter to only include positions where the player actually has ships
        own_ships = set(self.player_controller.game.ship_positions)
        
        if candidate_pos not in own_ships:
            messagebox.showwarning("Invalid Zeno Placement", "Zeno Defense must be placed on one of your ship squares.", parent=self.root)
            self.selected_region = []
            return

        # Single square selection only
        self.selected_region = [candidate_pos]

        # Highlight with blue overlay (defense) - single square
        rr, cc = candidate_pos
        if 0 <= rr < self.grid_size and 0 <= cc < self.grid_size:
            cx = cc * self.cell_size + self.cell_size // 2
            cy = rr * self.cell_size + self.cell_size // 2
            highlight = self.player_canvas.create_rectangle(
                cc * self.cell_size + 5, rr * self.cell_size + 5,
                (cc + 1) * self.cell_size - 5, (rr + 1) * self.cell_size - 5,
                fill="#0088ff", outline="#0044aa", width=2, stipple="gray50"
            )
            self.defense_highlights[(rr, cc)] = highlight
                
    def select_weapon(self, weapon_type):
        """Select a weapon and set up the appropriate targeting mode."""
        self.current_weapon = weapon_type
        # Reset all button backgrounds
        self.grover_btn.config(bg="#cc3333")
        self.ev_scan_btn.config(bg="#3366cc") 
        self.zeno_btn.config(bg="#cc9900")
        
        # Highlight selected weapon
        if weapon_type == "grover":
            self.grover_btn.config(bg="#ff4444")
            self.zeno_mode = False
            messagebox.showinfo("Grover Shot Selected", "📡 Select target region on enemy board and click to fire quantum shot!", parent=self.root)
        elif weapon_type == "ev_scan":
            self.ev_scan_btn.config(bg="#4488ff")
            self.zeno_mode = False
            messagebox.showinfo("EV Scan Selected", "🔍 Select target region on enemy board to perform stealth reconnaissance!", parent=self.root)
        elif weapon_type == "zeno_defense":
            self.zeno_btn.config(bg="#ffcc00")
            self.zeno_mode = True
            messagebox.showinfo("Zeno Defense Selected", "🛡️ Select region on YOUR board to protect with quantum shield!", parent=self.root)
            
        # Clear any existing selections
        self.selected_region = []
    
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
                    
    def fire_quantum_weapon(self, weapon_type):
        """Execute player's quantum weapon attack."""
        print(f"DEBUG: fire_quantum_weapon called with weapon: {weapon_type}")
        
        # Check if it's player's turn
        if not self.player_turn:
            messagebox.showwarning("Not Your Turn", "Wait for your turn!", parent=self.root)
            return
        
        # Check target selection for offensive weapons
        if weapon_type != "zeno_defense":
            if not self.selected_region:
                messagebox.showwarning("No Target Selected", "Please select a target region on the enemy board first!", parent=self.root)
                return
                
            # Validate targeting mode compatibility with weapon type
            if hasattr(self, 'selection_mode'):
                if weapon_type in ["grover", "ev_scan"] and self.selection_mode == "classical":
                    messagebox.showwarning("Invalid Targeting", f"{weapon_type.upper()} requires a 2x2 region target, not single square. Switch to 'Square' targeting mode.", parent=self.root)
                    return
                elif weapon_type == "classical" and self.selection_mode != "classical":
                    messagebox.showwarning("Invalid Targeting", "Classical shot requires single square targeting mode. Switch to 'Classical' targeting mode.", parent=self.root)
                    return
        
        # Handle classical shot
        if weapon_type == "classical":
            if len(self.selected_region) != 1:
                messagebox.showwarning("Invalid Selection", "Classical shot requires exactly one target square!", parent=self.root)
                return
            
            target = self.selected_region[0]
            # Check if there's a ship at the target
            ai_ships = self.ai_controller.get_ship_positions()
            if target in ai_ships:
                # Hit!
                result = {
                    "type": "hit",
                    "coords": target,
                    "message": f"Classical shot hit enemy ship at {target}!",
                    "method": "classical"
                }
                # Remove ship from AI controller
                self.ai_controller.receive_hit(target[0], target[1])
            else:
                # Miss
                result = {
                    "type": "miss",
                    "coords": target,
                    "message": f"Classical shot missed at {target}.",
                    "method": "classical"
                }
            
            # Show result
            self.show_player_targeting_animation(result)
            return
        
        # Handle Zeno defense differently - it protects your own ships
        if weapon_type == "zeno_defense":
            if not self.selected_region:
                messagebox.showwarning("No Target Selected", "Please select squares on your own board to protect!", parent=self.root)
                return
            
            print(f"DEBUG: Using Zeno defense")
            result = self.quantum_state.use_weapon("zeno_defense", self.selected_region, self.player_controller)
            if "error" in result:
                messagebox.showwarning("Error", result["error"], parent=self.root)
                return
            messagebox.showinfo("Zeno Defense Activated!", f"🛡️ Quantum shield activated! Selected region is now protected.\n\n{result.get('message', '')}", parent=self.root)
            self.clear_selections()
            # End turn after using Zeno defense
            self.player_turn = False
            self.ai_turn()
            return
            
        # For quantum weapons (Grover and EV scan)
        print(f"DEBUG: Using quantum weapon: {weapon_type}")
        # Clear selection highlights first
        if hasattr(self, 'target_highlights'):
            for highlight in self.target_highlights.values():
                if highlight:
                    self.ai_canvas.delete(highlight)
            self.target_highlights = {}
            
        # Get AI ship positions for quantum weapons
        ai_ships = self.ai_controller.get_ship_positions()
        
        # Use quantum weapons system
        print(f"DEBUG: Calling quantum_state.execute_attack")
        result = self.quantum_state.execute_attack(weapon_type, self.selected_region, ai_ships)
        print(f"DEBUG: Got result: {result}")
        
        if "error" in result:
            messagebox.showwarning("Error", result["error"], parent=self.root)
            return
            
        # Show player targeting animation before displaying result
        self.show_player_targeting_animation(result)
        
    def activate_zeno_defense(self):
        """Activate Zeno defense mode to protect your own ships."""
        if not self.player_turn:
            messagebox.showwarning("Not Your Turn", "Wait for your turn!", parent=self.root)
            return
        # If we're already in Zeno selection mode and have a selection, apply protection
        if self.zeno_mode and self.selected_region:
            # Use only squares that belong to player's ships (defense selection already enforces this)
            result = self.quantum_state.use_weapon("zeno_defense", self.selected_region, self.player_controller)
            if "error" in result:
                messagebox.showwarning("Error", result["error"], parent=self.root)
                return
                
            # Show visual protection indicators
            for coords in self.selected_region:
                self.show_zeno_protection_visual(coords)
                
            messagebox.showinfo("Zeno Defense Activated!", f"🛡️ Quantum shield activated! Selected region is now protected.\n\n{result.get('message', '')}", parent=self.root)
            self.clear_selections()
            # End turn after using Zeno defense
            self.player_turn = False
            self.ai_turn()
            return

        # Otherwise enter selection mode
        self.zeno_mode = True
        self.selected_region = []

        # Clear any existing highlights
        if hasattr(self, 'defense_highlights'):
            for highlight in self.defense_highlights.values():
                if highlight:
                    self.player_canvas.delete(highlight)
            self.defense_highlights = {}

        messagebox.showinfo("Zeno Defense Mode", "Click on your own ships (left board) to protect them with quantum shielding.\nClick the Zeno Defense button again when ready to activate protection.", parent=self.root)
        
    def show_zeno_protection_visual(self, coords):
        """Show visual indication of Zeno protection on player's ship."""
        row, col = coords
        cx = col * self.cell_size + self.cell_size // 2
        cy = row * self.cell_size + self.cell_size // 2
        
        # Create a golden shield overlay on player's board
        shield = self.player_canvas.create_oval(
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
            try:
                self.player_canvas.delete(self.protection_visuals[coords])
            except:
                pass
            del self.protection_visuals[coords]
        
    def clear_selections(self):
        """Clear all visual selections and reset weapon mode."""
        # Clear target highlights
        if hasattr(self, 'target_highlights'):
            for highlight in self.target_highlights.values():
                if highlight:
                    self.ai_canvas.delete(highlight)
            self.target_highlights = {}
            
        # Clear defense highlights  
        if hasattr(self, 'defense_highlights'):
            for highlight in self.defense_highlights.values():
                if highlight:
                    self.player_canvas.delete(highlight)
            self.defense_highlights = {}
            
        # Reset selections
        self.selected_region = []
        self.current_weapon = None
        self.zeno_mode = False
        
        # Reset button colors
        self.grover_btn.config(bg="#cc3333")
        self.ev_scan_btn.config(bg="#3366cc") 
        self.zeno_btn.config(bg="#cc9900")
        
    def show_player_targeting_animation(self, shot_result):
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
        self.animate_player_targeting_pattern(self.selection_mode, target_row, target_col, shot_result)
        
    def animate_player_targeting_pattern(self, pattern, target_row, target_col, shot_result):
        """Animate the player's targeting pattern on AI's board."""
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
        
        # Create red pulse animation for player shots
        self.player_animation_overlays = []
        for row, col in animation_cells:
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                cx = col * self.cell_size + self.cell_size // 2
                cy = row * self.cell_size + self.cell_size // 2
                
                # Create pulsing red overlay for player targeting
                overlay = self.ai_canvas.create_rectangle(
                    cx - 20, cy - 20, cx + 20, cy + 20,
                    fill="#cc3333", outline="#ff0000", width=2, stipple="gray25"
                )
                self.player_animation_overlays.append(overlay)
        
        # Start pulsing animation
        self.player_animation_step = 0
        self.player_pulse_animation(shot_result)
    
    def player_pulse_animation(self, shot_result):
        """Create pulsing effect for player targeting animation."""
        if self.player_animation_step < 6:  # Pulse 3 times
            # Alternate visibility
            if self.player_animation_step % 2 == 0:
                # Show overlays
                for overlay in self.player_animation_overlays:
                    self.ai_canvas.itemconfig(overlay, state="normal")
            else:
                # Hide overlays
                for overlay in self.player_animation_overlays:
                    self.ai_canvas.itemconfig(overlay, state="hidden")
            
            self.player_animation_step += 1
            # Continue animation after 300ms
            self.root.after(300, lambda: self.player_pulse_animation(shot_result))
        else:
            # Animation complete - clean up and show result
            for overlay in self.player_animation_overlays:
                self.ai_canvas.delete(overlay)
            self.player_animation_overlays = []
            
            # Show the actual result after animation
            self.complete_player_shot(shot_result)
    
    def complete_player_shot(self, result):
        """Complete the player's shot after animation."""
        # Handle different quantum weapon results
        result_type = result.get("type", "miss")
        weapon_method = result.get("method", "unknown")
        
        if result_type == "hit":
            # Standard Grover hit
            coords_info = f"at {result['coords']}" if result.get("coords") else ""
            messagebox.showinfo("Grover Hit!", f"🎯 DIRECT HIT! Enemy ship destroyed {coords_info}!\n\n{result.get('message', '')}", parent=self.root)
            self.show_hit_result(result)
            
        elif result_type == "detected":
            # EV scan successful detection - region only, no specific coordinates
            region_info = f"Region: {len(result.get('region', []))} squares scanned"
            ship_count = result.get('ship_count', 'unknown')
            messagebox.showinfo("EV Detection!", f"🔍 SHIPS DETECTED! EV scan found {ship_count} ship(s) in region!\n{region_info}\n\n{result.get('message', '')}", parent=self.root)
            self.show_detection_result(result)
            
        elif result_type == "interaction":
            # EV scan with interaction - region affected, no specific coordinates  
            region_info = f"Region: {len(result.get('region', []))} squares affected"
            ship_count = result.get('ship_count', 'unknown')
            messagebox.showinfo("EV Interaction!", f"⚡ REGION INTERACTION! EV scan affected {ship_count} ship(s) in region!\n{region_info}\n\n{result.get('message', '')}", parent=self.root)
            self.show_interaction_result(result)
            
        elif result_type == "clear":
            # EV scan - no ships detected
            region_info = f"Region: {len(result.get('region', []))} squares scanned"
            messagebox.showinfo("EV Clear!", f"✅ REGION CLEAR! EV scan confirmed no ships in scanned area.\n{region_info}\n\n{result.get('message', '')}", parent=self.root)
            
        elif result_type == "inconclusive":
            # EV scan - inconclusive result
            region_info = f"Region: {len(result.get('region', []))} squares scanned"
            messagebox.showinfo("EV Inconclusive", f"❓ INCONCLUSIVE! EV scan could not determine ship presence in region.\n{region_info}\n\n{result.get('message', '')}", parent=self.root)
            
        elif result_type == "noise":
            # EV scan - false positive  
            region_info = f"Region: {len(result.get('region', []))} squares scanned"
            messagebox.showinfo("EV Noise", f"📡 QUANTUM NOISE! EV scan detected interference in region.\n{region_info}\n\n{result.get('message', '')}", parent=self.root)
            self.show_noise_result(result)
            
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
            self.show_miss_result(result)
        
        # Ensure window focus after dialog
        self.root.lift()
        self.root.focus_force()
        
        # Clear selection
        self.selected_region = []
        
        # Check if player won (only for destructive hits)
        if result_type in ["hit", "interaction"] and self.ai_controller.is_game_won():
            messagebox.showinfo("VICTORY!", "🏆 You destroyed the enemy fleet! YOU WIN!", parent=self.root)
            self.player_turn = False
            return
            
        # End turn for ALL quantum weapon uses (EV scan, Grover, etc.)
        # EV scan should always count as a move, regardless of result
        self.player_turn = False
        self.status_label.config(text="AI IS THINKING...")
        self.root.after(1000, self.ai_turn)
    
    def show_hit_result(self, result):
        """Show visual result for a direct hit."""
        if "coords" in result and self.ship_img:
            hit_row, hit_col = result["coords"]
            cx = hit_col * self.cell_size + self.cell_size // 2
            cy = hit_row * self.cell_size + self.cell_size // 2
            ship_overlay = self.ai_canvas.create_image(cx, cy, image=self.ship_img)
            self.ai_overlays[hit_row][hit_col] = ship_overlay
            
            # Add red X over the hit ship
            x_size = 20
            x_mark1 = self.ai_canvas.create_line(
                cx - x_size, cy - x_size, cx + x_size, cy + x_size,
                fill="#ff0000", width=4
            )
            x_mark2 = self.ai_canvas.create_line(
                cx - x_size, cy + x_size, cx + x_size, cy - x_size,
                fill="#ff0000", width=4
            )
    
    def show_detection_result(self, result):
        """Show visual result for EV detection (no specific coordinates - region detection only)."""
        # EV scans now only detect presence in region, not specific coordinates
        # Show region-wide detection indicators instead of pinpoint markers
        if "region" in result:
            region = result["region"]
            for row, col in region:
                cx = col * self.cell_size + self.cell_size // 2
                cy = row * self.cell_size + self.cell_size // 2
                
                # Show region scan indicator (not specific ship location)
                detection_marker = self.ai_canvas.create_rectangle(
                    cx - 20, cy - 20, cx + 20, cy + 20,
                    outline="#00ff00", width=2, fill="", stipple="gray75"
                )
                
                # Store for cleanup
                if not hasattr(self, 'detection_markers'):
                    self.detection_markers = []
                self.detection_markers.append(detection_marker)
    
    def show_interaction_result(self, result):
        """Show visual result for EV interaction (region affected, not specific ships)."""
        # EV interaction affects region but doesn't pinpoint exact ship locations
        if "region" in result:
            region = result["region"]
            for row, col in region:
                cx = col * self.cell_size + self.cell_size // 2
                cy = row * self.cell_size + self.cell_size // 2
                
                # Show interaction effect on region
                interaction_mark = self.ai_canvas.create_oval(
                    cx - 15, cy - 15, cx + 15, cy + 15,
                    outline="#ffaa00", width=2, fill="", stipple="gray50"
                )
                
                # Store for cleanup
                if not hasattr(self, 'interaction_markers'):
                    self.interaction_markers = []
                self.interaction_markers.append(interaction_mark)
    
    def show_noise_result(self, result):
        """Show visual result for quantum noise in scanned region."""
        # EV noise affects entire scanned region, not specific coordinates
        if "region" in result:
            region = result["region"]
            for row, col in region:
                cx = col * self.cell_size + self.cell_size // 2
                cy = row * self.cell_size + self.cell_size // 2
                
                # Show noise/static indicator across region
                noise_marker = self.ai_canvas.create_rectangle(
                    cx - 8, cy - 8, cx + 8, cy + 8,
                    outline="#888888", width=1, fill="", stipple="gray25"
                )
                
                # Store for cleanup
                if not hasattr(self, 'noise_markers'):
                    self.noise_markers = []
                self.noise_markers.append(noise_marker)
    
    def show_miss_result(self, result):
        """Show visual result for a miss."""
        if "coords" in result and self.splash_img:
            miss_row, miss_col = result["coords"]
            if 0 <= miss_row < self.grid_size and 0 <= miss_col < self.grid_size:
                if not self.ai_overlays[miss_row][miss_col]:
                    cx = miss_col * self.cell_size + self.cell_size // 2
                    cy = miss_row * self.cell_size + self.cell_size // 2
                    splash_overlay = self.ai_canvas.create_image(cx, cy, image=self.splash_img)
                    self.ai_overlays[miss_row][miss_col] = splash_overlay
        
    def ai_turn(self):
        """Execute AI's turn."""
        # Handle quantum protection expiration at start of AI turn
        if hasattr(self, 'quantum_state'):
            expired_positions = self.quantum_state.end_turn()
            if expired_positions:
                # Remove visual protection indicators for expired positions
                for coords in expired_positions:
                    self.remove_zeno_protection_visual(coords)
        
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
        if "row targeting" in ai_message.lower() or "quantum row" in ai_message.lower():
            pattern = "row"
        elif "column targeting" in ai_message.lower() or "quantum column" in ai_message.lower():
            pattern = "column"
        elif "square targeting" in ai_message.lower() or "quantum square" in ai_message.lower():
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