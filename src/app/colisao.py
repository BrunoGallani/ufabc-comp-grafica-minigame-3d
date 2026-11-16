"""Teste de colisão do jogo, em função pura (sem estado, fácil de testar)."""
import glm


def esferas_colidem(centro1: glm.vec3, raio1: float, centro2: glm.vec3, raio2: float) -> bool:
    """A distância entre os centros é menor que a soma dos raios? Compara os quadrados, sem raiz."""
    d = centro1 - centro2
    soma = raio1 + raio2
    return glm.dot(d, d) < soma * soma
