import os
from glob import glob
from phase_gadget_pass import get_phase_gadget, phase_gadget_hi_pass
from pauli_gadget_pass import (
    get_pauli_gadget,
    single_pauli_gadget_hi_pass,
)
from pytket import Circuit
from alternating_cnot_decomposition import hidden_inverse_alternating_cnots

# from pauli_gadget_pass import _partition_pauli_gadget,
# )
from pytket.utils import compare_unitaries
from pytket.qasm import circuit_from_qasm

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
CIRCUITS_FOLDER = f"{PROJECT_FOLDER}/qasm_circuits"
circuit_files = glob(f"{CIRCUITS_FOLDER}/*.qasm")

# from pytket.circuit.display import view_browser

# TODO write more tests - and better ones!


def compare_phase_and_pauli_unitaries() -> None:
    circ_phase = get_phase_gadget(0.9, 2)
    circ_pauli = get_pauli_gadget("ZZ", 0.9)
    u1_phase = circ_phase.get_unitary()
    u1_pauli = circ_pauli.get_unitary()
    phase_gadget_hi_pass.apply(circ_phase)
    single_pauli_gadget_hi_pass.apply(circ_pauli)
    # view_browser(circ1)
    # view_browser(circ2)
    assert compare_unitaries(circ_phase.get_unitary(), circ_pauli.get_unitary())
    assert compare_unitaries(circ_phase.get_unitary(), u1_phase)
    assert compare_unitaries(circ_pauli.get_unitary(), u1_pauli)


def test_specific_pauli_gadget_circuits() -> None:
    pauli_yz = get_pauli_gadget("YZ", 0.7)
    pauli_xyyz = get_pauli_gadget("XYYZ", 0.65)

    u1_yz = pauli_yz.get_unitary()
    single_pauli_gadget_hi_pass.apply(pauli_yz)
    u2_yz = pauli_yz.get_unitary()
    assert compare_unitaries(u1_yz, u2_yz)

    u1_xyyz = pauli_xyyz.get_unitary()
    single_pauli_gadget_hi_pass.apply(pauli_xyyz)
    u2_xyyz = pauli_xyyz.get_unitary()
    assert compare_unitaries(u1_xyyz, u2_xyyz)


def test_depth1_pauli_gadget_qasm_circuits() -> None:
    counter = 1
    for circuit_file in circuit_files:
        print(f"Testing circuit: ({counter}/{len(circuit_files)})", circuit_file)
        pauli_circuit = circuit_from_qasm(circuit_file)
        # cut_circuit_list = _partition_pauli_gadget(pauli_circuit)
        # for circ in cut_circuit_list:
        #    view_browser(circ)
        u1 = pauli_circuit.get_unitary()
        # view_browser(pauli_circuit)
        single_pauli_gadget_hi_pass.apply(pauli_circuit)
        u2 = pauli_circuit.get_unitary()
        # view_browser(pauli_circuit)
        assert compare_unitaries(u1, u2)
        counter += 1


def test_alternating_cnot_decomposition():
    circuit = (
        Circuit(4)
        .H(0)
        .CX(0, 1)
        .H(1)
        .CX(1, 2)
        .H(3)
        .CX(2, 3)
        .H(3)
        .CX(0, 1)
        .H(1)
        .CX(1, 2)
        .CX(0, 1)
        .H(0)
        .H(1)
    )
    u1 = circuit.get_unitary()
    # view_browser(circuit)
    hidden_inverse_alternating_cnots.apply(circuit)

    u2 = circuit.get_unitary()
    # view_browser(circuit)

    assert compare_unitaries(u1, u2)


if __name__ == "__main__":
    compare_phase_and_pauli_unitaries()
    test_specific_pauli_gadget_circuits()
    test_depth1_pauli_gadget_qasm_circuits()
    test_alternating_cnot_decomposition()
    print("tests passed")
