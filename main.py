# main.py
import math
import tkinter as tk
from visual import QuantumBattleshipGUI
from zeno import run_grover_with_zeno_qiskit

def main():
    grid_size = 5
    region_size = 2
    ships = [(0,0), (0,1), (1,2), (3,4)]  # Example ship positions

    root = tk.Tk()
    game = QuantumBattleshipGUI(root, grid_size=grid_size, region_size=region_size, ships=ships)

    # Helper: map (x,y) on the game grid to a linear basis index
    def coord_to_index(x, y):
        return x * game.grid_size + y

    # Attach a zeno_move to the game instance
    def zeno_move(x, y, zeno_strength=0.25, observations=4, iterations=None):
        """
        Defend cell (x,y) with a Zeno-style observation that weakens Grover amplitude amplification.
        - Maps the grid to the smallest power-of-two Hilbert space that fits all cells.
        - Runs run_grover_with_zeno_qiskit and updates the game's probability grid if available.
        """
        # compute cell index and total cells
        cell_index = coord_to_index(x, y)
        total_cells = game.grid_size * game.grid_size

        # embed into a Hilbert space sized to next power of two
        n_qubits = math.ceil(math.log2(max(1, total_cells)))
        dim = 2 ** n_qubits

        # If the cell index is out of range for some reason, abort
        if cell_index >= total_cells:
            return False

        # Run the Qiskit-based Grover+Zeno simulation in the dim-dimensional space,
        # marking only the single target basis state corresponding to our cell.
        probs = run_grover_with_zeno_qiskit(
            n=n_qubits,
            target_index=cell_index,
            iterations=iterations,
            zeno_strength=zeno_strength,
            observations_per_iteration=observations
        )

        # probs is length dim; take only the first total_cells entries that map to the grid
        grid_probs = probs[:total_cells].copy()

        # If the GUI exposes a probability_grid attribute, update it.
        # Accept either flat or 2D array shapes.
        if hasattr(game, "probability_grid"):
            pg = getattr(game, "probability_grid")
            try:
                # if shapes match, assign directly
                if pg.size == grid_probs.size:
                    # keep original shape
                    new_pg = grid_probs.reshape(pg.shape)
                    game.probability_grid = new_pg
                else:
                    # fallback: store flat vector
                    game.probability_grid = grid_probs
            except Exception:
                game.probability_grid = grid_probs

        # Track defended cells
        defended = getattr(game, "zeno_defended", None)
        if defended is None:
            game.zeno_defended = set()
        game.zeno_defended.add(cell_index)

        # If GUI has a refresh / redraw method, call it
        if hasattr(game, "refresh") and callable(game.refresh):
            try:
                game.refresh()
            except Exception:
                pass
        if hasattr(game, "redraw") and callable(game.redraw):
            try:
                game.redraw()
            except Exception:
                pass

        return True

    # expose the move on the game instance (user code can call game.zeno_move(x,y,...))
    game.zeno_move = zeno_move

    root.mainloop()

if __name__ == "__main__":
    main()
