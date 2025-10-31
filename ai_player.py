# ai_player.py
import random
import math
from typing import List, Tuple, Dict


class AIPlayer:
    """
    AI opponent for Quantum Battleship.
    Uses different strategies based on difficulty level.
    """
    
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.shots_taken = set()  # Use set for O(1) lookup
        self.hits_found = []
        self.hunting_mode = False
        self.target_queue = []  # For smart hunting around hits
        
    def make_move(self, game_controller) -> Dict:
        """
        Make an AI move based on difficulty level.
        Returns result dictionary with move information.
        """
        if self.difficulty == "easy":
            return self._make_random_move(game_controller)
        elif self.difficulty == "medium":
            return self._make_smart_move(game_controller)
        elif self.difficulty == "hard":
            return self._make_quantum_move(game_controller)
        else:
            return self._make_random_move(game_controller)
    
    def _make_random_move(self, game_controller) -> Dict:
        """Easy AI: Random shots."""
        grid_size = game_controller.game.grid_size
        
        # Find available cells
        available_cells = []
        for row in range(grid_size):
            for col in range(grid_size):
                if (row, col) not in self.shots_taken:
                    available_cells.append((row, col))
        
        if not available_cells:
            return {"message": "AI has no moves left!"}
        
        # Random selection
        target_cell = random.choice(available_cells)
        
        # Execute shot
        result = self._execute_shot(game_controller, [target_cell])
        
        return {
            "message": f"AI randomly targeted {target_cell}: {result['message']}",
            "result": result
        }
    
    def _make_smart_move(self, game_controller) -> Dict:
        """Medium AI: Hunt mode after hits."""
        grid_size = game_controller.game.grid_size
        
        # If we have targets to hunt, use
        if self.target_queue:
            target_cell = self.target_queue.pop(0)
            if target_cell not in self.shots_taken:
                result = self._execute_shot(game_controller, [target_cell])
                
                if result["type"] == "hit":
                    self._add_adjacent_targets(target_cell, grid_size)
                
                return {
                    "message": f"AI hunted around previous hit at {target_cell}: {result['message']}",
                    "result": result
                }
        
        # Otherwise, use probability-based targeting
        target_cell = self._get_probability_target(game_controller)
        result = self._execute_shot(game_controller, [target_cell])
        
        if result["type"] == "hit":
            self.hunting_mode = True
            self._add_adjacent_targets(target_cell, grid_size)
        
        return {
            "message": f"AI used probability analysis to target {target_cell}: {result['message']}",
            "result": result
        }
    
    def _make_quantum_move(self, game_controller) -> Dict:
        """Hard AI: Advanced targeting strategies with quantum weapons."""
        grid_size = game_controller.game.grid_size
        
        # AI can choose between different strategies
        strategies = ["advanced_targeting", "ev_scan", "defensive"]
        weights = [0.6, 0.3, 0.1]  # Most likely to use advanced targeting
        strategy = random.choices(strategies, weights=weights)[0]
        
        if strategy == "ev_scan":
            # Use EV scan on a promising area
            return self._use_ev_scan(game_controller)
        elif strategy == "defensive":
            # Use Zeno defense (if AI has ships to protect)
            return self._use_zeno_defense(game_controller)
        else:
            # Advanced targeting with classical weapons
            return self._use_advanced_targeting(game_controller)
    
    def _use_ev_scan(self, game_controller) -> Dict:
        """AI uses EV scan to detect ships without destroying them."""
        grid_size = game_controller.game.grid_size
        
        # Choose a 2x2 region to scan
        row = random.randint(0, grid_size - 2)
        col = random.randint(0, grid_size - 2)
        region = []
        for dr in range(2):
            for dc in range(2):
                r, c = row + dr, col + dc
                if 0 <= r < grid_size and 0 <= c < grid_size:
                    region.append((r, c))
        
        # Filter out already shot cells
        region = [cell for cell in region if cell not in self.shots_taken]
        if not region:
            return self._use_advanced_targeting(game_controller)
        
        # Use the quantum weapons system
        from quantum_weapons import QuantumGameState
        quantum_state = QuantumGameState()
        
        # Get player ship positions for EV scan
        player_ships = game_controller.game.ship_positions
        result = quantum_state.execute_attack("ev_scan", region, player_ships)
        
        # Record the region as shot
        for cell in region:
            self.shots_taken.add(cell)
        
        return {
            "message": f"AI used EV scan on region starting at {(row, col)}: {result.get('message', '')}",
            "result": result
        }
    
    def _use_zeno_defense(self, game_controller) -> Dict:
        """AI uses Zeno defense to protect its own ships."""
        # For simplicity, AI will just make a regular shot instead of using defense
        # (Zeno defense would require AI ship management which is complex)
        return self._use_advanced_targeting(game_controller)
    
    def _use_advanced_targeting(self, game_controller) -> Dict:
        """Use advanced targeting patterns."""
        grid_size = game_controller.game.grid_size
        
        # Use advanced targeting modes
        targeting_modes = ["square", "row", "column"]
        weights = [0.3, 0.35, 0.35]
        mode = random.choices(targeting_modes, weights=weights)[0]
        
        if mode == "row":
            row = self._get_best_row(game_controller)
            region = [(row, col) for col in range(grid_size)]
        elif mode == "column":
            col = self._get_best_column(game_controller)
            region = [(row, col) for row in range(grid_size)]
        else:
            top_left = self._get_best_square_position(game_controller)
            region = []
            for dr in range(2):
                for dc in range(2):
                    r, c = top_left[0] + dr, top_left[1] + dc
                    if 0 <= r < grid_size and 0 <= c < grid_size:
                        region.append((r, c))
        
        # Filter out already shot cells
        region = [cell for cell in region if cell not in self.shots_taken]
        if not region:
            return self._make_random_move(game_controller)
            
        result = self._execute_shot(game_controller, region)
        
        return {
            "message": f"AI used advanced {mode} targeting: {result.get('message', '')}",
            "result": result
        }
    
    def _execute_shot(self, game_controller, region: List[Tuple[int, int]]) -> Dict:
        """Execute a shot on the given region using quantum weapons."""
        # Import quantum weapons system
        from quantum_weapons import QuantumGameState
        
        # Filter out already shot cells from region
        available_region = [cell for cell in region if cell not in self.shots_taken]
        
        if not available_region:
            return {"error": "No available cells in region", "type": "error"}
        
        # Record all cells in region as attempted (since quantum weapons target regions)
        for cell in available_region:
            self.shots_taken.add(cell)
        
        # Use the REAL quantum weapons system that the player uses
        quantum_state = QuantumGameState()
        
        # Get player ship positions for quantum targeting
        player_ships = game_controller.game.ship_positions
        
        # Use Grover shot (same as player's quantum weapon)
        result = quantum_state.execute_attack("grover", available_region, player_ships)
        
        # Track hits for AI strategy
        if result.get("type") == "hit" and result.get("coords"):
            self.hits_found.append(result["coords"])
            
        return result
    
    def _get_best_row(self, game_controller) -> int:
        """Get the row with highest ship probability."""
        grid_size = game_controller.game.grid_size
        
        # Score each row based on unshot cells
        row_scores = []
        for row in range(grid_size):
            unshot_count = sum(1 for col in range(grid_size) 
                             if (row, col) not in self.shots_taken)
            row_scores.append(unshot_count)
        
        # Choose row with highest score
        best_row = row_scores.index(max(row_scores))
        return best_row
    
    def _get_best_column(self, game_controller) -> int:
        """Get the column with highest ship probability."""
        grid_size = game_controller.game.grid_size
        
        # Score each column based on unshot cells
        col_scores = []
        for col in range(grid_size):
            unshot_count = sum(1 for row in range(grid_size) 
                             if (row, col) not in self.shots_taken)
            col_scores.append(unshot_count)
        
        # Choose column with highest score
        best_col = col_scores.index(max(col_scores))
        return best_col
    
    def _get_best_square_position(self, game_controller) -> Tuple[int, int]:
        """Get the best 2x2 square position."""
        grid_size = game_controller.game.grid_size
        
        best_score = -1
        best_pos = (0, 0)
        
        for row in range(grid_size - 1):
            for col in range(grid_size - 1):
                # Count unshot cells in this 2x2 square
                score = 0
                for dr in range(2):
                    for dc in range(2):
                        if (row + dr, col + dc) not in self.shots_taken:
                            score += 1
                
                if score > best_score:
                    best_score = score
                    best_pos = (row, col)
        
        return best_pos
    
    def reset(self):
        """Reset AI state for a new game."""
        self.shots_taken = set()
        self.hits_found = []
        self.hunting_mode = False
        self.target_queue = []