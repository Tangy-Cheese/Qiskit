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
        self.shots_taken = []
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
        
        # If we have targets to hunt, use them
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
        """Hard AI: Quantum-inspired strategies with region targeting."""
        grid_size = game_controller.game.grid_size
        
        # Use quantum region targeting (rows/columns)
        targeting_modes = ["square", "row", "column"]
        weights = [0.3, 0.35, 0.35]  # Prefer lines for better coverage
        
        mode = random.choices(targeting_modes, weights=weights)[0]
        
        if mode == "row":
            # Target entire row
            row = self._get_best_row(game_controller)
            region = [(row, col) for col in range(grid_size)]
        elif mode == "column":
            # Target entire column
            col = self._get_best_column(game_controller)
            region = [(row, col) for row in range(grid_size)]
        else:
            # Target 2x2 square
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
            # Fallback to random
            return self._make_random_move(game_controller)
        
        result = self._execute_shot(game_controller, region)
        
        return {
            "message": f"AI used quantum {mode} targeting: {result['message']}",
            "result": result
        }
    
    def _execute_shot(self, game_controller, region: List[Tuple[int, int]]) -> Dict:
        """Execute a shot on the given region."""
        # Record shots
        self.shots_taken.extend(region)
        
        # Use game controller to fire shot
        result = game_controller.fire_shot(region)
        
        # Track hits
        if result.get("type") == "hit" and result.get("coords"):
            self.hits_found.append(result["coords"])
        
        return result
    
    def _add_adjacent_targets(self, hit_cell: Tuple[int, int], grid_size: int):
        """Add adjacent cells to target queue for hunting."""
        row, col = hit_cell
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # right, left, down, up
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < grid_size and 0 <= new_col < grid_size and
                (new_row, new_col) not in self.shots_taken and
                (new_row, new_col) not in self.target_queue):
                self.target_queue.append((new_row, new_col))
    
    def _get_probability_target(self, game_controller) -> Tuple[int, int]:
        """Get target based on probability analysis."""
        grid_size = game_controller.game.grid_size
        
        # Simple probability: avoid edges, prefer center
        available_cells = []
        for row in range(grid_size):
            for col in range(grid_size):
                if (row, col) not in self.shots_taken:
                    # Weight center cells higher
                    center_distance = abs(row - grid_size//2) + abs(col - grid_size//2)
                    weight = max(1, grid_size - center_distance)
                    available_cells.extend([(row, col)] * weight)
        
        return random.choice(available_cells) if available_cells else (0, 0)
    
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
        self.shots_taken = []
        self.hits_found = []
        self.hunting_mode = False
        self.target_queue = []