# AeroQ-Route Workspace

This workspace contains **AeroQ-Route**, a quantum-assisted aviation emissions and flight trajectory optimization system.

---

## Projects in this Workspace

### 🛫 [quantum-flight-optimizer](./quantum-flight-optimizer)
The core research, optimization, and benchmarking suite. Formulates commercial airspace corridor deconfliction as a **QUBO (Quadratic Unconstrained Binary Optimization)** problem and benchmarks:
- **Classical Greedy Dijkstra Baseline**
- **Exact Mixed-Integer Linear Programming (MILP / Branch-and-Bound)**
- **Simulated Quantum Annealing (D-Wave Neal)**
- **Gate-Based QAOA (Qiskit 2.x)**

---

## Quick Start

```bash
# Navigate to the project directory
cd "quantum-flight-optimizer"

# Run the benchmark across all four solvers
python main.py

# Run the automated test suite
pytest tests/ -v
```

For complete documentation on mathematical derivations, architecture, configuration, and solver details, see:
- [quantum-flight-optimizer/README.md](./quantum-flight-optimizer/README.md)
- [quantum-flight-optimizer/data_gen/README.md](./quantum-flight-optimizer/data_gen/README.md)
- [quantum-flight-optimizer/models/README.md](./quantum-flight-optimizer/models/README.md)
- [quantum-flight-optimizer/solvers/README.md](./quantum-flight-optimizer/solvers/README.md)
- [quantum-flight-optimizer/tests/README.md](./quantum-flight-optimizer/tests/README.md)
