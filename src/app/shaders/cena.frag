#version 400 core

// Blinn-Phong por fragmento, no espaco da camera, com duas fontes:
// o Sol (direcional) e a luz da nave (pontual, com atenuacao).
// A saida e luz linear; o OpenGL a codifica em sRGB ao gravar.

in vec3 fP;
in vec3 fN;
in vec2 fTexCoord;

uniform vec3 u_ka, u_kd, u_ks;
uniform float u_alfa;

uniform vec3 u_ambiente;
uniform vec4 u_sol;           // w = 0: direcao ate a fonte
uniform vec3 u_cor_sol;
uniform vec4 u_luz;           // w = 1: posicao da fonte
uniform vec3 u_cor_luz;
uniform vec3 u_atenuacao;     // kc, kl, kq

uniform bool u_usar_textura;
uniform sampler2D u_base;     // cor, no lugar de kd
uniform vec2 u_repeticoes;
uniform bool u_usar_camada;
uniform sampler2D u_camada;   // mascara das nuvens: 0 ceu limpo, 1 nuvem
uniform float u_deslocamento; // das nuvens, em u

out vec4 outfragcolor;

// Parcelas difusa e especular de uma fonte.
vec3 fonte(vec4 luz, vec3 cor, vec3 N, vec3 V, vec3 kd) {
    vec3 L = normalize(luz.xyz);
    float atenuacao = 1.0;
    if (luz.w == 1.0) {
        vec3 ate_a_fonte = luz.xyz - fP;
        float d = length(ate_a_fonte);
        L = ate_a_fonte / d;
        atenuacao = 1.0 / (u_atenuacao.x + u_atenuacao.y * d + u_atenuacao.z * d * d);
    }
    float NdotL = max(dot(N, L), 0.0);

    // sem brilho especular onde a luz nao chega
    float brilho = 0.0;
    if (NdotL > 0.0) {
        vec3 H = normalize(L + V);
        brilho = pow(max(dot(N, H), 0.0), u_alfa);
    }
    return atenuacao * cor * (kd * NdotL + u_ks * brilho);
}

void main() {
    vec3 kd = u_kd;
    if (u_usar_textura) kd = texture(u_base, fTexCoord * u_repeticoes).rgb;
    if (u_usar_camada) {
        float nuvem = texture(u_camada, fTexCoord + vec2(u_deslocamento, 0.0)).r;
        kd = mix(kd, vec3(1.0), nuvem);
    }

    vec3 N = normalize(fN);    // a interpolacao encurta a normal
    vec3 V = normalize(-fP);   // a camera esta na origem
    vec3 cor = u_ka * u_ambiente
             + fonte(u_sol, u_cor_sol, N, V, kd)
             + fonte(u_luz, u_cor_luz, N, V, kd);
    outfragcolor = vec4(cor, 1.0);
}
