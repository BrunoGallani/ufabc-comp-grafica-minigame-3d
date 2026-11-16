#version 400 core

layout(location = 0) in vec3 vPosition;

uniform mat4 u_visao_rot;    // visao sem a translacao: as estrelas ficam no infinito
uniform mat4 u_projecao;

void main() {
    vec4 p = u_projecao * u_visao_rot * vec4(vPosition, 1.0);
    gl_Position = p.xyww;    // z/w = 1: no plano far, atras de tudo
}
