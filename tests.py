from phase_gadget_pass import get_phase_gadget, phase_gadget_hi_pass
from pauli_gadget_pass import get_pauli_gadget, pauli_gadget_hi_pass
from pytket.utils import compare_unitaries

# from pytket.circuit.display import view_browser
# TODO write more tests - and better ones!


def compare_phase_and_pauli_unitaries() -> None:
    circ_phase = get_phase_gadget(0.9, 2)
    circ_pauli = get_pauli_gadget("ZZ", 0.9)
    u1_phase = circ_phase.get_unitary()
    u1_pauli = circ_pauli.get_unitary()
    phase_gadget_hi_pass.apply(circ_phase)
    pauli_gadget_hi_pass.apply(circ_pauli)
    # view_browser(circ1)
    # view_browser(circ2)
    assert compare_unitaries(circ_phase.get_unitary(), circ_pauli.get_unitary())
    assert compare_unitaries(circ_phase.get_unitary(), u1_phase)
    assert compare_unitaries(circ_pauli.get_unitary(), u1_pauli)


if __name__ == "__main__":
    compare_phase_and_pauli_unitaries()
