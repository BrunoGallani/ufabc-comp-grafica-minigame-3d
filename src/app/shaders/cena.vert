#version 400 core

// Leva a posicao e a normal para o espaco da camera, onde a
// iluminacao e calculada por fragmento.

layout(location = 0) in vec4 vPosition;
layout(location = 1) in vec3 vNormal;
layout(location = 2) in vec2 vTexCoord;

uniform mat4 u_modelo, u_visao, u_projecao;
uniform mat3 u_normal;       // inversa transposta de u_modelo

out vec3 fP;
out vec3 fN;
out vec2 fTexCoord;

void main() {
    vec4 pos_camera = u_visao * u_modelo * vPosition;
    gl_Position = u_projecao * pos_camera;
    fP = pos_camera.xyz;
    fN = mat3(u_visao) * u_normal * vNormal;
    fTexCoord = vTexCoord;
}
