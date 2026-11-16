#version 400 core

// Segunda passada: formas 2D sobre a cena, em projecao ortografica.

layout(location = 0) in vec2 vPosition;

uniform mat4 u_modelo, u_projecao;

void main() {
    gl_Position = u_projecao * u_modelo * vec4(vPosition, 0.0, 1.0);
}
