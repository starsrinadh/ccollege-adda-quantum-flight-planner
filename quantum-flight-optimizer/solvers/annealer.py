"""
Quantum Annealer Emulation Solver for AeroQ-Route.
==================================================
Uses dimod and dwave-neal (SimulatedAnnealingSampler) to emulate quantum annealing locally.

For First-Year B.Tech Students:
- Physical Quantum Annealers (like D-Wave Advantage) utilize transverse-field quantum tunneling
  to traverse rugged energy barriers and find the global minimum energy state of an Ising model.
- Neal emulates this process classically on CPU using simulated annealing (Metropolis-Hastings
  transitions with an inverse temperature schedule beta_0 -> beta_1).
- This solver builds the Route-Conflict QUBO, converts it into a Binary Quadratic Model (BQM),
  samples low-energy states, and decodes the optimal deconflicted flight assignments.
"""

import time
from typing import Dict, List
import dimod
import neal
import networkx as nx
import numpy as np

from .base import BaseSolver
from .classical import DijkstraSolver
from models.qubo_model import (
    generate_candidate_paths,
    build_route_conflict_qubo,
)


class AnnealerSolver(BaseSolver):
    """
    Quantum Annealer Emulator using dwave-neal.
    Finds ground state of the Route-Conflict Airspace QUBO.
    """

    def __init__(self):
        super().__init__(name="Sim Annealer (Neal)")

    def solve(
        self,
        G: nx.Graph,
        flights: List[Dict],
        P_path: float = 5000.0,
        P_cap: float = 2000.0,
        num_reads: int = 150,
        num_sweeps: int = 500,
        **kwargs
    ) -> Dict:
        start_time = time.time()

        # 1. Generate candidate paths (K=2 or K=3 alternatives per flight)
        candidate_paths = generate_candidate_paths(G, flights, k_paths=2)

        # 2. Build Route-Conflict QUBO Matrix
        Q, var_list, conflicts = build_route_conflict_qubo(
            G, flights, candidate_paths,
            P_one=P_path, P_conflict=P_cap
        )

        if len(var_list) == 0:
            return DijkstraSolver().solve(G, flights)

        # 3. Convert QUBO matrix to dimod BinaryQuadraticModel (BQM)
        qubo_dict = {}
        N = Q.shape[0]
        for i in range(N):
            for j in range(i, N):
                val = float(Q[i, j])
                if abs(val) > 1e-6:
                    qubo_dict[(i, j)] = val

        bqm = dimod.BinaryQuadraticModel.from_qubo(qubo_dict)

        # 4. Sample ground states via Neal Simulated Annealing
        sampler = neal.SimulatedAnnealingSampler()
        sampleset = sampler.sample(
            bqm,
            num_reads=num_reads,
            num_sweeps=num_sweeps,
            seed=42
        )

        best_sample = sampleset.first.sample
        best_energy = sampleset.first.energy

        # 5. Decode sample bitstrings into flight path assignments
        assignments = {}
        for flight in flights:
            f_id = flight['id']
            # Find which candidate paths have bit 1
            active_ks = []
            for k in range(len(candidate_paths[f_id])):
                var_idx = var_list.index((f_id, k))
                # Support both integer index and variable tuple key from sampler
                val = best_sample.get(var_idx, best_sample.get((f_id, k), 0))
                if val == 1:
                    active_ks.append(k)

            # If exactly one bit is set, select it; if multiple, pick the one with lowest fuel; if none, default to 0
            if len(active_ks) == 1:
                chosen_k = active_ks[0]
            elif len(active_ks) > 1:
                chosen_k = active_ks[0]
            else:
                chosen_k = 0

            assignments[f_id] = candidate_paths[f_id][chosen_k]

        # 6. Evaluate actual physical metrics
        total_fuel, total_co2, violations, edge_usage = self.evaluate_solution(G, flights, assignments)
        runtime = time.time() - start_time

        return {
            'solver_name': self.name,
            'assignments': assignments,
            'total_fuel': total_fuel,
            'total_co2': total_co2,
            'violations': violations,
            'runtime_sec': round(runtime, 4),
            'edge_usage': edge_usage,
            'details': {
                'qubo_energy': round(best_energy, 2),
                'qubo_variables': N,
                'conflicts_modeled': len(conflicts),
                'num_reads': num_reads,
                'num_sweeps': num_sweeps
            }
        }
