# Quantum Battleships using IBM's library QISKIT

A custom-made battleship game that demonstrates quantum computing principles through interactive gameplay. Experience quantum mechanics concepts like Grover's algorithm, Elitzur-Vaidman bomb testing, and the quantum Zeno effect in this strategic game.

**Authors: Adam Tang, Qasim Bedford and Yann Janssen**

##  Overview

Quantum Battleships transforms the classic game by incorporating three fundamental quantum mechanics principles as weapons/utlities:

- **Grover Shot**: Quantum search algorithm for high-accuracy targeting
- **EV Scan**: Interaction-free measurement for non-destructive wavefuctions  
- **Zeno Defense**: Quantum Zeno effect for measurement-based protection

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Required packages: `qiskit`, `qiskit-aer`, `tkinter`, `PIL` (Pillow), `numpy`

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/Tangy-Cheese/Quantum-Battleships.git
   cd Quantum-Battleships
   ```

2. **Install dependencies:**
   ```bash
   pip install qiskit qiskit-aer pillow numpy
   ```

3. **Run the game:**
   ```bash
   python main.py
   ```

## How to Play

### Game Modes

Choose between two game modes from the main menu:

- **Single Player**: Play against an AI with varying difficulty levels
- **Local Multiplayer**: Two players take turns on the same computer

### Set up

1. **Ship Placement**: Each player places 8 ships on their 8×8 grid
   - Click squares to place or remove ships
   - Use "Random Ships" for a randomised placement
   - Click "Ready for Battle" when finished to confirm the grid

2. **Turn Structure**: Players alternate turns, with one action per turn

### Battle 

#### Targeting Modes

There are four targetting modes to choose from before confirming an attack:

- **Classical**: Single square targeting (1×1)
- **2x2 Grid**: Quantum targeting region using Grover's algorithm (2×2) 
- **Full Row**: Quantum target entire horizontal row using Grover's algorithm
- **Full Column**: Quantum target entire vertical column using Grover's algorithm

#### Quantum Weapons

**Grover Shot**
- **Targeting**: Requires the given target selection
- **Effect**: 85% hit probability when ships are in target 
- **Physics**: Uses Grover's algorithm for amplitude amplification
- **Strategy**: High-accuracy weapon for scattered targets

**EV Scan**
- **Targeting**: Requires the given target selection
- **Effect**: Detects ship presence without destroying them
- **Physics**: Elitzur-Vaidman bomb tester for interaction-free measurement
- **Results**:
  - `Clear`: No ships detected in region (high confidence)
  - `Detected`: Ships present somewhere in region (exact location unknown)
  - `Interaction`: Ships damaged but survive
  - `Inconclusive`: Quantum interference prevented clear detection

**Zeno Defense**
- **Targeting**: Select ships on your own board
- **Effect**: Protects ships from enemy quantum attacks by reducing the amplitude amplification from Grover Shot.
- **Physics**: Quantum Zeno effect freezes evolution through frequent measurements
- **Duration**: Protection lasts 1 round
- **Effectiveness**: 90% (maximum) or 60% (partial) protection

**Classical Shot**
- **Targeting**: Single square selection
- **Effect**: Standard battleship mechanics
- **Strategy**: Reliable and choice based but limited to one target

### Game Flow

1. **Targeting selection**: Choose appropriate targeting pattern
2. **Select Target**: Click on enemy board to highlight target region
3. **Choose Weapon**: Click weapon button to fire
4. **View Results**: See attack outcome and effects
5. **Pass Turn**: Click "PASS TO PLAYER X" to end your turn. Singleplayer automatically switches to AI.

### Winning Conditions

- **Victory**: Destroy all enemy ships
- **Strategy**: Balance offensive attacks with defensive protection when number of ships are low
- **Resource Management**: Each quantum weapon has strategic trade-offs

## Quantum Physics Concepts

### Grover's Algorithm
- **Principle**: Quantum search providing quadratic speedup over classical algorithms
- **Implementation**: Amplitude amplification increases probability of finding ship positions
- **Game Mechanic**: Higher hit probability when targeting regions containing ships

### Elitzur-Vaidman Bomb Tester
- **Principle**: Interaction-free measurement allows detection without direct interaction
- **Implementation**: Quantum interference patterns reveal object presence
- **Game Mechanic**: Non-destructive ship detection with region-level information

### Quantum Zeno Effect
- **Principle**: Frequent quantum measurements freeze system evolution
- **Implementation**: Repeated weak measurements prevent state changes
- **Game Mechanic**: Measurement-based protection against quantum attacks

## Technical Details

### Architecture
- **Frontend**: Tkinter-based GUI with scrollable interface
- **Backend**: Qiskit quantum circuit simulation
- **Quantum Simulator**: AerSimulator for realistic quantum behavior
- **Game Engine**: Turn-based state management with quantum weapon integration

#### ***Note that this was programmed on WSL subsystem of Linux x64. This program will run with no issues on a Linux based operating system. Please beware MacOS removes the colours of the buttons.***

### Circuit Implementation
- **3-qubit Grover circuits**: Superposition of states across rows/columns
- **2-qubit Grover circuits**: Superposition of states on a 2x2 mini-grid
- **2-qubit EV circuits**: Model detection-free interaction
- **1-qubit Zeno circuits**: Simulate evolution-freezing
- **Real quantum mechanics**: All probability calculations follow quantum mechanical principles

### Directory Structure
```
Qiskit/
├── main.py                   # Game launcher
├── multiplayer_ui.py         # Multiplayer interface
├── single_player_ui.py       # Single player interface 
├── grovershot.py             # Grover's algorithm 
├── quantum_weapons.py        # Quantum mechanics implementation
├── game_controller.py        # Game logic controller
├── game_logic.py             # Core mechanics
├── ai_player.py              # AI opponent
├── assets/                   # Game graphics
│   ├── water.png
│   ├── ship.png
│   └── splash.png
└── README.md                 # This file
```

## Troubleshooting

### Common Issues

**"No Target" Error**
- Solution: Click on enemy board to select target region first
- Ensure correct targeting mode is selected

**Quantum Shot Won't Fire**
- Check: Are you in battle phase? (not ship placement)
- Check: Have you already taken your shot this turn?
- Check: Is targeting mode compatible with weapon?

**Game Won't Start**
- Ensure Python 3.8+ is installed
- Install required packages: `pip install qiskit qiskit-aer pillow numpy`
- Check that all game files are present

## Contributing

We welcome contributions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Quantum Team UCL**: Thank you for providing this Hackathon opportunity, and shout out to the president: Daniel Aliev!
- **IBM Quantum**: For making quantum computing accessible
- **Quantum Computing Community**: For inspiration and educational resources
- **Authors: Adam Tang, Qasim Bedford and Yann Janssen**

---

**Experience quantum mechanics through gaming - where physics meets strategy.** 

*"In the quantum realm, observation changes reality - use this power wisely in battle."*
