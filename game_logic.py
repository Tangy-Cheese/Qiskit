# game_logic.py
import math
import random
from grovershot import grover_shot


class QuantumBattleshipGame:
    """
    Game logic and state management for Quantum Battleship.
    Handles ship placement, coordinate conversions, game rules, and quantum shots.
    """
    
    def __init__(self, grid_size=8, num_ships=8, auto_place_ships=True):
        self.grid_size = grid_size
        self.num_ships = num_ships
        self.found_ships = set()
        
        if auto_place_ships:
            self.ship_positions = self.generate_random_ships()
        else:
            self.ship_positions = set()  # Will be set manually
        
    def generate_random_ships(self):
        """Generate random ship positions ensuring no duplicates."""
        ships = set()
        max_attempts = self.grid_size * self.grid_size * 2
        attempts = 0
        
        while len(ships) < self.num_ships and attempts < max_attempts:
            row = random.randint(0, self.grid_size - 1)
            col = random.randint(0, self.grid_size - 1)
            ships.add((row, col))
            attempts += 1
        
        if len(ships) < self.num_ships:
            print(f"Warning: Could only place {len(ships)} ships out of {self.num_ships} requested")
        
        return list(ships)
    
    def coords_to_index(self, x, y):
        """Convert (row, col) coordinates to linear index."""
        return x * self.grid_size + y
    
    def index_to_coords(self, index):
        """Convert linear index back to (row, col) coordinates."""
        return divmod(index, self.grid_size)
    
    def coords_to_indices(self, coords):
        """Convert list of coordinates to list of indices."""
        return [
            self.coords_to_index(x, y)
            for x, y in coords
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size
        ]
    
    def get_region_coords(self, row, col, selection_mode, region_size=2):
        """Get all coordinates for a selected region based on mode."""
        region = []
        
        if selection_mode == "classical":
            # Classical mode - single square only
            if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
                region.append((row, col))
        
        elif selection_mode == "square":
            for dx in range(region_size):
                for dy in range(region_size):
                    rr, cc = row + dx, col + dy
                    if 0 <= rr < self.grid_size and 0 <= cc < self.grid_size:
                        region.append((rr, cc))
        
        elif selection_mode == "row":
            for cc in range(self.grid_size):
                region.append((row, cc))
        
        elif selection_mode == "column":
            for rr in range(self.grid_size):
                region.append((rr, col))
        
        return region
    
    def fire_quantum_shot(self, selected_region):
        """
        Execute a quantum shot using Grover's algorithm.
        Returns result dictionary with hit info and measured position.
        """
        if not selected_region:
            return {"error": "No region selected"}
        
        # Check if region only contains already-found ships
        if all(cell in self.found_ships for cell in selected_region):
            return {"error": "Region already contains discovered ships"}
        
        # Convert to indices and filter out found ships
        region_indices = self.coords_to_indices(selected_region)
        # Find which ships (if any) are in the target region
        remaining_ships = [s for s in self.ship_positions if s not in self.found_ships]
        ship_indices = self.coords_to_indices(remaining_ships)
        ships_in_region = [s for s in ship_indices if s in region_indices]
        
        # Remove already found ships from search space
        region_indices = [
            idx for idx in region_indices
            if self.index_to_coords(idx) not in self.found_ships
        ]
        
        if not region_indices:
            return {"error": "You already scanned this area"}
        
        n_qubits = math.ceil(math.log2(self.grid_size * self.grid_size))
        
        # Execute quantum shot
        if ships_in_region:
            # Normal Grover search with real targets
            result = grover_shot(n_qubits, ships_in_region)
        else:
            # No ships in region - quantum system still measures randomly
            random_index = random.choice(region_indices)
            result = {
                "hit": False,
                "measured_index": random_index,
                "measured_state": format(random_index, f'0{n_qubits}b'),
                "iterations": 1,
                "counts": {format(random_index, f'0{n_qubits}b'): 1}
            }
        
        # Process result
        hit = result["hit"]
        measured = result["measured_index"]
        
        if hit and measured is not None:
            coords = self.index_to_coords(measured)
            if coords not in self.found_ships:
                self.found_ships.add(coords)
                return {
                    "type": "hit",
                    "coords": coords,
                    "message": f"HIT! Ship detected at cell index {measured}!",
                    "result": result
                }
            else:
                return {
                    "type": "already_found",
                    "coords": coords,
                    "message": f"Ship at index {measured} was already found.",
                    "result": result
                }
        else:
            coords = self.index_to_coords(measured) if measured is not None else None
            message = f"MISS! Quantum scan measured cell {measured} but no ship found." if measured is not None else "MISS! No ship detected in this region."
            return {
                "type": "miss",
                "coords": coords,
                "message": message,
                "result": result
            }
    
    def is_game_won(self):
        """Check if all ships have been found."""
        return set(self.ship_positions) == self.found_ships
    
    def get_game_stats(self):
        """Get current game statistics."""
        return {
            "ships_found": len(self.found_ships),
            "total_ships": len(self.ship_positions),
            "ships_remaining": len(self.ship_positions) - len(self.found_ships),
            "grid_size": f"{self.grid_size}x{self.grid_size}",
            "total_cells": self.grid_size * self.grid_size,
            "qubits_needed": math.ceil(math.log2(self.grid_size * self.grid_size))
        }
    
    def print_debug_info(self):
        """Print debug information about ship placement and game state."""
        stats = self.get_game_stats()
        print(f"Ships placed at: {self.ship_positions}")
        print(f"Grid size: {stats['grid_size']} = {stats['total_cells']} cells")
        print(f"Qubits needed: {stats['qubits_needed']}")
        print(f"Ships found: {stats['ships_found']}/{stats['total_ships']}")