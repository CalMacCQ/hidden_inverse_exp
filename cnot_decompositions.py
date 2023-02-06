from pytket import Circuit, OpType
from pytket.passes import (
    SequencePass,
    DecomposeBoxes,
    FullPeepholeOptimise,
    NormaliseTK2,
    DecomposeTK2,
    auto_rebase_pass,
    RemoveRedundancies,
    auto_squash_pass,
)
from pytket.circuit.display import view_browser

cnot_circ = Circuit(2).CX(0, 1)

# Reproduce the default_compilation_pass for the QuantinuumBackend (Without contextual optimisation)
# This is used to get the CNOT and CNOT-dagger decompositions - ensure unitary is preserved (no SimplifyInitial)
hseries_rebase = auto_rebase_pass({OpType.ZZPhase, OpType.Rz, OpType.PhasedX})
hseries_squash = auto_squash_pass({OpType.PhasedX, OpType.Rz})

seq_pass = SequencePass(
    [
        DecomposeBoxes(),
        FullPeepholeOptimise(target_2qb_gate=OpType.TK2),
        NormaliseTK2(),
        DecomposeTK2(),
        hseries_rebase,
        RemoveRedundancies(),
        hseries_squash,
    ]
)

seq_pass.apply(cnot_circ)

view_browser(cnot_circ)  # Look at the CNOT decomposition circuit

view_browser(cnot_circ.dagger())  # Look at the CNOT-Dagger decomposition circuit
