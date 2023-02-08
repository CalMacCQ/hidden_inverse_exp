OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
h q[0];
h q[1];
cx q[0],q[1];
rz(1.5608260216382743*pi) q[1];
cx q[0],q[1];
h q[0];
h q[1];
