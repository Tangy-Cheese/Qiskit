"""
Quantum Weapons Implementation for Quantum Battleship
Implements three quantum mechanics-based weapons:
1. Grover Shot - Direct attack with high accuracy
2. EV Scan - Elitzur-Vaidman interaction-free measurement
3. Zeno Defense - Quantum Zeno effect protection
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector
import random


class QuantumWeapons:
    """Quantum weapons implementation using Qiskit."""
    
    def __init__(self):
        self.simulator = AerSimulator()
        
    def grover_shot(self, selected_region, ship_positions, excluded_squares=None, protected_positions=None):
        """
        Grover's algorithm implementation - high accuracy ship targeting.
        This is the existing implementation from grovershot.py
        
        Args:
            selected_region: List of coordinates in the target region
            ship_positions: List of ship coordinates
            excluded_squares: Set of coordinates that have already been targeted in this region
            protected_positions: Dict of positions with Zeno protection {coord: strength}
        """
        if excluded_squares is None:
            excluded_squares = set()
        if protected_positions is None:
            protected_positions = {}
            
        # For now, using simplified Grover logic
        # This should integrate with the existing grovershot.py implementation
        region_size = len(selected_region)
        if region_size == 0:
            return {"error": "No target region selected"}
        
        # Filter out already targeted squares from the region
        available_squares = [pos for pos in selected_region if pos not in excluded_squares]
        
        if not available_squares:
            return {"error": "All squares in this region have already been targeted"}
            
        # Check if any ships are in the FULL selected region (not just available squares)
        # Grover algorithm should detect ships anywhere in the target region
        ships_in_region = [pos for pos in ship_positions if pos in selected_region]
        
        if ships_in_region:
            # Ships detected in region - now target an unshot position
            # Check which ships are at unshot positions (can actually be hit)
            hittable_ships = [pos for pos in ships_in_region if pos in available_squares]
            
            if hittable_ships:
                # Choose target ship from hittable ones (prefer unprotected)
                unprotected_ships = [pos for pos in hittable_ships if pos not in protected_positions]
                
                if unprotected_ships:
                    # Target unprotected ship with high probability
                    hit_probability = 0.85 + (0.1 * len(ships_in_region) / len(selected_region))
                    if random.random() < hit_probability:
                        target_ship = random.choice(unprotected_ships)
                        return {
                            "type": "hit",
                            "coords": target_ship,
                            "message": f"Grover algorithm amplified target probability. Ship destroyed at {target_ship}!",
                            "method": "grover"
                        }
                else:
                    # All hittable ships are protected - test Zeno defense
                    target_ship = random.choice(hittable_ships)
                    protection_strength = protected_positions.get(target_ship, 0)
                    
                    base_probability = 0.85 + (0.1 * len(ships_in_region) / len(selected_region))
                    reduced_probability = base_probability * (1.0 - (protection_strength * 0.3))
                    
                    if random.random() < reduced_probability:
                        return {
                            "type": "hit",
                            "coords": target_ship,
                            "message": f"Grover shot overcame Zeno defense! Ship destroyed at {target_ship}!",
                            "method": "grover"
                        }
                    else:
                        return {
                            "type": "blocked",
                            "coords": target_ship,
                            "message": f"Zeno quantum defense deflected Grover attack at {target_ship}!",
                            "method": "grover"
                        }
            
            # Ships detected in region but all already shot - quantum measurement reveals miss
            miss_coords = random.choice(available_squares)
            return {
                "type": "miss",
                "coords": miss_coords,
                "message": f"Grover detected ships in region but quantum measurement collapsed to empty space at {miss_coords}",
                "method": "grover"
            }
        
        # Miss - return random position from available squares
        miss_coords = random.choice(available_squares)
        return {
            "type": "miss",
            "coords": miss_coords,
            "message": f"Grover search found no ships in quantum superposition. Measured position: {miss_coords}",
            "method": "grover"
        }
    
    def ev_scan(self, selected_region, ship_positions):
        """
        Elitzur-Vaidman bomb tester implementation.
        Interaction-free measurement that can detect ships without destroying them.
        """
        # Create quantum circuit for EV bomb tester
        qc = QuantumCircuit(2, 2)
        
        # Check if there are any ships in the region (live bombs)
        ships_in_region = [pos for pos in ship_positions if pos in selected_region]
        has_ship = len(ships_in_region) > 0
        
        # EV bomb tester circuit
        # Photon starts in superposition
        qc.h(0)  # Hadamard gate creates superposition
        
        if has_ship:
            # Ship presence affects the quantum interference
            # This simulates the bomb interaction
            qc.cz(0, 1)  # Controlled-Z represents ship interaction
        
        # Second Hadamard for interference
        qc.h(0)
        
        # Measure both qubits
        qc.measure_all()
        
        # Execute circuit
        job = self.simulator.run(transpile(qc, self.simulator), shots=1)
        result = job.result()
        counts = result.get_counts()
        measurement = list(counts.keys())[0]
        
        # Interpret results based on EV bomb tester logic
        if has_ship:
            # Ship detected case
            if measurement in ['01', '10']:
                # Successful interaction-free detection (~25% chance)
                # EV can only detect presence in region, not exact location
                return {
                    "type": "detected",
                    "coords": None,  # No specific coordinates - EV limitation
                    "region": selected_region,
                    "ship_count": len(ships_in_region),
                    "message": f"EV scan detected {len(ships_in_region)} ship(s) somewhere in selected region. Exact location unknown.",
                    "method": "ev_scan",
                    "confidence": "high"
                }
            elif measurement == '11':
                # Interaction occurred (~25% chance) - general region affected
                return {
                    "type": "interaction",
                    "coords": None,  # No specific coordinates
                    "region": selected_region,
                    "ship_count": len(ships_in_region),
                    "message": f"EV scan interacted with region containing {len(ships_in_region)} ship(s). Ships damaged but survive!",
                    "method": "ev_scan",
                    "confidence": "medium"
                }
            else:
                # No conclusive result (~50% chance)
                return {
                    "type": "inconclusive",
                    "coords": None,
                    "region": selected_region,
                    "message": "EV scan inconclusive. Quantum interference prevented clear detection of region.",
                    "method": "ev_scan",
                    "confidence": "low"
                }
        else:
            # No ship - perfect interference
            if measurement == '00':
                return {
                    "type": "clear",
                    "coords": None,
                    "region": selected_region,
                    "ship_count": 0,
                    "message": "EV scan shows perfect interference. No ships detected anywhere in selected region.",
                    "method": "ev_scan",
                    "confidence": "high"
                }
            else:
                # Noise/false positive
                return {
                    "type": "noise",
                    "coords": None,
                    "region": selected_region,
                    "message": f"EV scan detected quantum noise in region. Possible false positive - region may be empty.",
                    "method": "ev_scan",
                    "confidence": "low"
                }
    
    def zeno_defense(self, target_coords, protection_strength=3):
        """
        Quantum Zeno effect implementation.
        Frequent measurements freeze quantum evolution, making ships harder to detect.
        """
        # Create circuit with repeated weak measurements
        qc = QuantumCircuit(1, 1)
        
        # Initial state preparation
        qc.h(0)  # Start in superposition
        
        # Apply Zeno effect through repeated measurements and corrections
        for i in range(protection_strength):
            # Small rotation (weak interaction)
            qc.ry(0.2, 0)
            
            # Measurement and immediate correction (simulating Zeno effect)
            # In real implementation, this would be multiple weak measurements
            qc.ry(-0.1, 0)  # Partial correction
        
        # Final measurement
        qc.measure_all()
        
        # Execute circuit
        job = self.simulator.run(transpile(qc, self.simulator), shots=1)
        result = job.result()
        counts = result.get_counts()
        measurement = list(counts.keys())[0]
        
        # Zeno protection effectiveness based on measurement
        if measurement == '0':
            protection_level = "maximum"
            effectiveness = 0.9  # 90% protection
        else:
            protection_level = "partial"
            effectiveness = 0.6  # 60% protection
        
        return {
            "type": "protection_active",
            "coords": target_coords,
            "effectiveness": effectiveness,
            "protection_level": protection_level,
            "message": f"Zeno defense activated at {target_coords}. Protection level: {protection_level}",
            "method": "zeno_defense"
        }
    
    def apply_zeno_protection(self, attack_result, protected_coords, protection_effectiveness):
        """
        Apply Zeno protection to incoming attacks.
        Reduces effectiveness of both Grover shots and EV scans.
        """
        if attack_result.get("coords") == protected_coords:
            # Zeno protection interferes with attack
            if random.random() < protection_effectiveness:
                # Attack blocked or reduced
                if attack_result["type"] == "hit":
                    return {
                        "type": "blocked",
                        "coords": protected_coords,
                        "message": f"Zeno defense blocked attack on {protected_coords}! Quantum state frozen.",
                        "original_attack": attack_result["method"]
                    }
                elif attack_result["type"] == "detected":
                    return {
                        "type": "obfuscated", 
                        "coords": None,
                        "message": f"Zeno defense obfuscated EV scan of {protected_coords}. Detection prevented.",
                        "original_attack": attack_result["method"]
                    }
        
        # No protection or protection failed
        return attack_result


class QuantumGameState:
    """Manages quantum state and protection effects for the game."""
    
    def __init__(self):
        self.protected_positions = {}  # pos -> protection_strength
        self.protection_rounds = {}   # pos -> rounds_remaining
        self.quantum_weapons = QuantumWeapons()
        
    def add_zeno_protection(self, coords, strength=3, duration=1):
        """Add temporary Zeno protection to a position."""
        result = self.quantum_weapons.zeno_defense(coords, strength)
        self.protected_positions[coords] = result["effectiveness"]
        self.protection_rounds[coords] = duration  # Default 1 round
        return result
        
    def remove_protection(self, coords):
        """Remove Zeno protection from a position."""
        if coords in self.protected_positions:
            del self.protected_positions[coords]
        if coords in self.protection_rounds:
            del self.protection_rounds[coords]
            
    def end_turn(self):
        """Called at end of turn - decrements protection durations."""
        expired_positions = []
        for coords in list(self.protection_rounds.keys()):
            self.protection_rounds[coords] -= 1
            if self.protection_rounds[coords] <= 0:
                expired_positions.append(coords)
        
        # Remove expired protections
        for coords in expired_positions:
            self.remove_protection(coords)
            
        return expired_positions  # Return list of positions that lost protection
            
    def execute_attack(self, attack_type, selected_region, ship_positions, excluded_squares=None):
        """Execute a quantum attack and apply any active protections."""
        weapons = self.quantum_weapons
        if attack_type == "grover":
            result = weapons.grover_shot(selected_region, ship_positions, excluded_squares, self.protected_positions)
        elif attack_type == "ev_scan":
            result = weapons.ev_scan(selected_region, ship_positions)
        else:
            return {"error": f"Unknown attack type: {attack_type}"}
        # If weapon method returns None, treat as error
        if result is None:
            return {"error": "Quantum weapon returned no result."}
        # Protection is now handled inside the weapon methods
        return result
    
    def use_weapon(self, weapon_type, selected_region, controller):
        """Unified interface for firing quantum weapons or activating Zeno defense."""
        if weapon_type == "zeno_defense":
            # Zeno defense: protect selected squares on player's board
            results = []
            for coords in selected_region:
                result = self.add_zeno_protection(coords, strength=3, duration=1)
                results.append(result)
            # Return summary for UI
            return {
                "type": "protection_active",
                "coords": selected_region,
                "message": f"Zeno defense activated for {len(selected_region)} squares.",
                "details": results,
                "method": "zeno_defense"
            }
        elif weapon_type in ["grover", "ev_scan"]:
            # Offensive weapons: attack enemy board
            ship_positions = controller.game.ship_positions if hasattr(controller, "game") else []
            return self.execute_attack(weapon_type, selected_region, ship_positions)
        else:
            return {"error": f"Unknown weapon type: {weapon_type}"}