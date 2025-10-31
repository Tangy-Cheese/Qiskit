# Quantum Battleship 🚢⚛️

A revolutionary battleship game that demonstrates real quantum computing principles through interactive gameplay. Experience quantum mechanics concepts like Grover's algorithm, Elitzur-Vaidman bomb testing, and the quantum Zeno effect in an engaging strategic game.

## 🎯 Overview

Quantum Battleship transforms the classic naval strategy game by incorporating three fundamental quantum mechanics principles as weapons:

- **Grover Shot**: Quantum search algorithm for high-accuracy targeting
- **EV Scan**: Interaction-free measurement for non-destructive reconnaissance  
- **Zeno Defense**: Quantum Zeno effect for measurement-based protection

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Required packages: `qiskit`, `qiskit-aer`, `tkinter`, `PIL` (Pillow), `numpy`

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Tangy-Cheese/Qiskit.git
   cd Qiskit
   ```

2. **Install dependencies:**
   ```bash
   pip install qiskit qiskit-aer pillow numpy
   ```

3. **Run the game:**
   ```bash
   python main.py
   ```

## 🎮 How to Play

### Game Modes

Choose between two game modes from the main menu:

- **Single Player**: Play against an AI opponent with adjustable difficulty
- **Local Multiplayer**: Two players take turns on the same computer

### Setup Phase

1. **Ship Placement**: Each player places 8 ships on their 8×8 grid
   - Click squares to place/remove ships manually
   - Use "Random Ships" for automatic placement
   - Click "Ready for Battle" when finished

2. **Turn Structure**: Players alternate turns, each getting one action per turn

### Battle Phase

#### Targeting Modes

Select your targeting pattern before attacking:

- **Classical**: Single square targeting (1×1)
- **2x2 Grid**: Quantum targeting region (2×2) 
- **Full Row**: Target entire horizontal row
- **Full Column**: Target entire vertical column

#### Quantum Weapons

**🎯 Grover Shot (Direct Attack)**
- **Targeting**: Requires 2×2 region selection
- **Effect**: 85% hit probability when ships are in target region
- **Physics**: Uses Grover's algorithm for quantum amplitude amplification
- **Strategy**: High-accuracy weapon for confirmed targets

**🔍 EV Scan (Stealth Reconnaissance)**
- **Targeting**: Requires 2×2 region selection
- **Effect**: Detects ship presence without destroying them
- **Physics**: Elitzur-Vaidman bomb tester for interaction-free measurement
- **Results**:
  - `Clear`: No ships detected in region (high confidence)
  - `Detected`: Ships present somewhere in region (exact location unknown)
  - `Interaction`: Ships damaged but survive
  - `Inconclusive`: Quantum interference prevented clear detection

**🛡️ Zeno Defense (Quantum Protection)**
- **Targeting**: Select squares on your own board
- **Effect**: Protects ships from enemy quantum attacks
- **Physics**: Quantum Zeno effect freezes quantum evolution through frequent measurement
- **Duration**: Protection lasts 1 round
- **Effectiveness**: 90% (maximum) or 60% (partial) protection

**⚔️ Classical Shot (Traditional Attack)**
- **Targeting**: Single square selection
- **Effect**: Standard hit/miss mechanics
- **Strategy**: Reliable but limited to one target

### Game Flow

1. **Select Targeting Mode**: Choose appropriate targeting pattern
2. **Select Target**: Click on enemy board to highlight target region
3. **Choose Weapon**: Click weapon button to fire
4. **View Results**: See attack outcome and effects
5. **Pass Turn**: Click "PASS TO PLAYER X" to end your turn

### Winning Conditions

- **Victory**: Destroy all enemy ships
- **Strategy**: Balance offensive attacks with defensive protection
- **Resource Management**: Each quantum weapon has strategic trade-offs

## ⚛️ Quantum Physics Concepts

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

## 🎛️ Controls

### Mouse Controls
- **Left Click**: Select grid squares, place ships, activate buttons
- **Mouse Wheel**: Scroll up/down through interface (both game modes)
- **Scrollbar**: Drag for precise navigation

### Keyboard Shortcuts
- **ESC**: Cancel current selection
- **Space**: Random ship placement (during setup)

## 🔧 Technical Details

### Architecture
- **Frontend**: Tkinter-based GUI with scrollable interface
- **Backend**: Qiskit quantum circuit simulation
- **Quantum Simulator**: AerSimulator for realistic quantum behavior
- **Game Engine**: Turn-based state management with quantum weapon integration

### Circuit Implementation
- **3-qubit Grover circuits**: Represent 8 possible grid positions
- **2-qubit EV circuits**: Model photon-ship interaction
- **1-qubit Zeno circuits**: Simulate measurement-induced protection
- **Real quantum mechanics**: All probability calculations follow quantum mechanical principles

### File Structure
```
Qiskit/
├── main.py                    # Game launcher
├── multiplayer_ui.py          # Multiplayer interface
├── single_player_ui.py        # Single player interface  
├── quantum_weapons.py         # Quantum mechanics implementation
├── game_controller.py         # Game logic controller
├── game_logic.py             # Core mechanics
├── ai_player.py              # AI opponent
├── assets/                   # Game graphics
│   ├── water.png
│   ├── ship.png
│   └── splash.png
└── README.md                 # This file
```

## 🧠 Strategy Guide

### Beginner Tips
1. **Start with EV Scans**: Use reconnaissance to locate enemy ship clusters
2. **Combine Weapons**: EV Scan → Grover Shot for maximum efficiency
3. **Protect Valuable Ships**: Use Zeno Defense on ships in exposed positions
4. **Targeting Modes**: Match targeting mode to weapon type

### Advanced Strategies
1. **Quantum Chains**: Chain EV scans to map enemy positions
2. **Defensive Timing**: Apply Zeno protection before enemy discovers your ships
3. **Resource Management**: Balance offensive and defensive quantum operations
4. **Pattern Recognition**: Learn enemy placement and targeting patterns

### Weapon Interactions
- **Grover vs Zeno**: Zeno defense reduces Grover hit probability (85% → 8.5%)
- **EV vs Zeno**: Zeno protection can obfuscate EV scan results
- **Classical shots**: Unaffected by quantum interference

## 🐛 Troubleshooting

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

### Performance Tips
- Close other applications for smoother quantum simulation
- Use smaller grid sizes on slower computers
- Reduce visual effects if experiencing lag

## 📚 Educational Value

This game serves as an interactive introduction to quantum computing concepts:

- **Quantum Algorithms**: Experience Grover's search advantage
- **Quantum Measurement**: Understand interaction-free measurement principles
- **Quantum Effects**: See how measurement affects quantum systems
- **Practical Applications**: Connect theory to interactive examples

Perfect for students, educators, and anyone curious about quantum mechanics!

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- Additional quantum algorithms (quantum teleportation, error correction)
- Enhanced AI with quantum strategies
- Network multiplayer support
- Mobile interface adaptation
- Educational mode with step-by-step explanations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Qiskit Team**: For the excellent quantum computing framework
- **IBM Quantum**: For making quantum computing accessible
- **Quantum Computing Community**: For inspiration and educational resources

## 📞 Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Review the game documentation
3. Open an issue on GitHub
4. Contact the development team

---

**Experience quantum mechanics through gaming - where physics meets strategy!** ⚛️🎮

*"In the quantum realm, observation changes reality - use this power wisely in battle!"*
