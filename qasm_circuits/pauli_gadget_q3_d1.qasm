OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
h q[0];
h q[1];
gate v vq0 {
u3(0.5*pi,1.5*pi,0.5*pi) vq0;
}
v q[2];
cx q[2],q[1];
cx q[1],q[0];
rz(0.7889739724463758*pi) q[0];
cx q[1],q[0];
h q[0];
cx q[2],q[1];
h q[1];
gate vdg vdgq0 {
u3(3.5*pi,1.5*pi,0.5*pi) vdgq0;
}
vdg q[2];
