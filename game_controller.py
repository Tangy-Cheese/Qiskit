# game_controller.py
from game_logic import QuantumBattleshipGame


class GameController:
    """
    Controller that connects the UI and game logic.
    Handles communication between the visual interface and game state.
    """
    
    def __init__(self, grid_size=8, num_ships=8, auto_place_ships=True):
        self.game = QuantumBattleshipGame(grid_size, num_ships, auto_place_ships)
        if auto_place_ships:
            self.game.print_debug_info()
    
    def get_found_ships(self):
        """Get the set of found ship coordinates."""
        return self.game.found_ships
    
    def get_region_coords(self, row, col, selection_mode, region_size=2):
        """Get coordinates for a selected region."""
        return self.game.get_region_coords(row, col, selection_mode, region_size)
    
    def fire_shot(self, selected_region):
        """Execute a quantum shot and return the result."""
        return self.game.fire_quantum_shot(selected_region)
    
    def is_game_won(self):
        """Check if the game has been won."""
        return self.game.is_game_won()
    
    def get_game_stats(self):
        """Get current game statistics."""
        return self.game.get_game_stats()
    
    def get_ship_positions(self):
        """Get all ship positions (for debugging)."""
        return self.game.ship_positions
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.game = QuantumBattleshipGame(self.game.grid_size, self.game.num_ships)
        self.game.print_debug_info()