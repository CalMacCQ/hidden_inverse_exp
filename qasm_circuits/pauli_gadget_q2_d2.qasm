OPENQASM 2.0;
include "qelib1.inc";

qreg q[2];
h q[0];
h q[1];
cx q[1],q[0];
rz(2.4550484158149017*pi) q[0];
cx q[1],q[0];
h q[0];
h q[1];
h q[0];
h q[1];
cx q[1],q[0];
rz(2.7332219057844087*pi) q[0];
cx q[1],q[0];
h q[0];
h q[1];
