"""Script to generate H-Series decompositions for any two qubit unitary with a hidden inverse"""
import numpy as np
from pytket.circuit import OpType, Circuit, Unitary2qBox
from pytket.predicates import GateSetPredicate
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

hseries_rebase = auto_rebase_pass({OpType.ZZPhase, OpType.Rz, OpType.PhasedX})
hseries_squash = auto_squash_pass({OpType.PhasedX, OpType.Rz})

h_series_seq_pass = SequencePass(
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
h_series_gateset_predicate = GateSetPredicate(
    {OpType.ZZPhase, OpType.ZZMax, OpType.Rz, OpType.PhasedX}
)


cnot_circ = Circuit(2).CX(0, 1)

h_series_seq_pass.apply(cnot_circ)

# view_browser(cnot_circ)  # Look at the CNOT decomposition circuit

# view_browser(cnot_circ.dagger())  # Look at the CNOT-Dagger decomposition circuit


# The function below should generate pairs of Hidden inverses for any two qubit unitary
#  that is self-adjoint. The decompositions are given in the H-Series gateset.
def get_hidden_inverse_circuits(unitary: np.array) -> tuple([Circuit, Circuit]):
    """
    Given a 2 qubit unitary A that is self-adjoint returns the decomposition of A as well as the
    decomposition of A^. Both decompositions are in the H-series gateset.
    """
    assert np.allclose(
        unitary, unitary.conj().T
    )  # assert that 2q unitary is self-adjoint
    u_box = Unitary2qBox(unitary)
    circ = Circuit(2)
    circ.add_unitary2qbox(u_box, 0, 1)
    h_series_seq_pass.apply(circ)
    assert h_series_gateset_predicate.verify(circ)
    return (circ, circ.dagger())


cz_matrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]])

c1, c2 = get_hidden_inverse_circuits(cz_matrix)

# print(np.round(c1.get_unitary(), 3), np.round(c2.get_unitary(), 3))
# view_browser(c1)
# view_browser(c2)
