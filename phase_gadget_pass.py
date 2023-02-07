"""Script to apply the Hidden inverse technique to Phase gadget circuits."""
from pytket.circuit import Circuit, OpType
from pytket.circuit.display import view_browser
from pytket.passes import CustomPass
from pytket.predicates import GateSetPredicate
from pytket.utils import compare_unitaries


def get_phase_gadget(rz_angle: float, n_qubits: int) -> Circuit:
    """
    Creates a phase gadget circuit for a given Rz angle and number of qubits.
    """

    assert n_qubits > 1
    circ = Circuit(n_qubits)

    for qubit in range(n_qubits - 1):
        circ.CX(qubit, qubit + 1)

    circ.Rz(rz_angle, n_qubits - 1)

    for qubit in reversed(range(n_qubits - 1)):
        circ.CX(qubit, qubit + 1)

    return circ


def compile_cx(circ: Circuit) -> Circuit:
    """
    Function that takes a circuit and decomposes CNOT gates using the H-series gateset.
    Used to define the cx_decomp_pass.
    """
    circ_prime = Circuit(circ.n_qubits)
    for cmd in circ.get_commands():
        if cmd.op.type == OpType.CX:
            circ_prime.add_gate(OpType.PhasedX, [0.5, -0.5], [cmd.qubits[-1]])
            circ_prime.add_gate(OpType.ZZPhase, [1 / 2], cmd.qubits)
            circ_prime.add_gate(OpType.PhasedX, [-0.5, 0], [cmd.qubits[-1]])
            circ_prime.add_gate(OpType.Rz, [3 / 2], [cmd.qubits[1]])
            circ_prime.add_gate(OpType.Rz, [7 / 2], [cmd.qubits[0]])
        else:
            circ_prime.add_gate(cmd.op.type, cmd.op.params, cmd.qubits)

    return circ_prime


def compile_cx_conj(circ: Circuit) -> Circuit:
    """
    Function that takes a circuit and decomposes CNOT-dagger gates using the H-series gateset.
    Used to define the cxdg_decomp_pass.
    """
    circ_prime = Circuit(circ.n_qubits)
    for cmd in circ.get_commands():
        if cmd.op.type == OpType.CX:
            circ_prime.add_gate(OpType.Rz, [-3 / 2], [cmd.qubits[1]])
            circ_prime.add_gate(OpType.Rz, [-7 / 2], [cmd.qubits[0]])
            circ_prime.add_gate(OpType.PhasedX, [0.5, 0], [cmd.qubits[-1]])
            circ_prime.add_gate(OpType.ZZPhase, [-1 / 2], cmd.qubits)
            circ_prime.add_gate(OpType.PhasedX, [-0.5, -0.5], [cmd.qubits[-1]])
        else:
            circ_prime.add_gate(cmd.op.type, cmd.op.params, cmd.qubits)

    return circ_prime


cx_decomp_pass = CustomPass(compile_cx)
cxdg_decomp_pass = CustomPass(compile_cx_conj)

phase_gadget_predicate = GateSetPredicate({OpType.Rz, OpType.CX})


def partition_phase_gadget(circ: Circuit) -> list[Circuit]:
    """
    Helper function: Given a phase gadget circuit returns a list of three circuits.
    The first circuit is the CNOT ladder before the Rz gate, the second circuit is
    the Rz gate itself. The third circuit is the CNOT ladder after the Rz gate.
    """
    circuit_list = []
    command_list = circ.get_commands()
    n_qubits = circ.n_qubits

    assert len(command_list) == 2 * n_qubits - 1
    assert phase_gadget_predicate.verify(circ)

    circ1 = Circuit(n_qubits)
    for cmd in command_list[: n_qubits - 1]:
        circ1.add_gate(OpType.CX, cmd.qubits)
    circuit_list.append(circ1)

    central_rz_angle = command_list[n_qubits - 1].op.params[0]
    circ2 = Circuit(1).Rz(central_rz_angle, 0)
    circuit_list.append(circ2)

    circ3 = Circuit(n_qubits)
    for cmd in command_list[n_qubits:]:
        circ3.add_gate(OpType.CX, cmd.qubits)
    circuit_list.append(circ3)

    assert len(circuit_list) == 3

    return circuit_list


def compile_phase_gadget(circ: Circuit) -> Circuit:
    """
    Function that takes a phase gadget circuit and compiles the first
    CNOT ladder with the standard CNOT decomposition and the second with the CNOT-dg decomposition.
    """
    circuit_list = partition_phase_gadget(circ)

    circ_prime = Circuit(circ.n_qubits)

    cx_decomp_pass.apply(circuit_list[0])

    cxdg_decomp_pass.apply(circuit_list[2])

    circ_prime.append(circuit_list[0])
    circ_prime.add_circuit(circuit_list[1], [circ_prime.qubits[-1]])
    circ_prime.append(circuit_list[2])

    return circ_prime


# Define a CustomPass
phase_gadget_hi_pass = CustomPass(compile_phase_gadget)

# Try a testcase and check circuit unitary before and after HI compilation.
testcase1 = get_phase_gadget(0.9, 2)
u_before = testcase1.get_unitary()

phase_gadget_hi_pass.apply(testcase1)
u_after = testcase1.get_unitary()

# print(compare_unitaries(u_before, u_after))

# view_browser(testcase1)
