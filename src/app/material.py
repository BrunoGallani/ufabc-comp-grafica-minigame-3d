"""Materiais e fontes de luz do modelo de Blinn-Phong, com as cores em luz linear."""
from dataclasses import dataclass

import glm

from config import Cor


class Material:
    def __init__(self, ka: Cor, kd: Cor, ks: Cor, alfa: float) -> None:
        self.ka, self.kd, self.ks = glm.vec3(ka), glm.vec3(kd), glm.vec3(ks)
        self.alfa = alfa


@dataclass(frozen=True)
class Luz:
    """Com w = 1, `posicao` é o ponto de uma fonte pontual; com w = 0, a direção até uma fonte direcional."""
    posicao: glm.vec4
    cor: glm.vec3
    atenuacao: glm.vec3   # kc, kl, kq; só vale para a pontual


BRANCO, PRETO = (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)

# Nos objetos com textura, a imagem é multiplicada por kd: com kd branco, fica a imagem pura.
TERRA = Material((0.03, 0.03, 0.04), BRANCO, (0.22, 0.22, 0.22), 24.0)
ROCHA = Material((0.035, 0.035, 0.04), BRANCO, (0.03, 0.03, 0.03), 6.0)
# Asteroide resistente: a mesma rocha, tingida de vermelho pelo kd. Depois do 1º tiro, fica em
# brasa: o ka alto brilha mesmo no lado sem luz.
ROCHA_RESISTENTE = Material((0.035, 0.02, 0.02), (1.00, 0.45, 0.35), (0.05, 0.05, 0.05), 10.0)
ROCHA_RACHADA = Material((0.40, 0.13, 0.02), (1.00, 0.65, 0.40), (0.30, 0.30, 0.30), 40.0)

CASCO = Material((0.03, 0.03, 0.04), (0.55, 0.57, 0.62), (0.25, 0.25, 0.25), 40.0)
ASA = Material((0.03, 0.01, 0.01), (0.55, 0.08, 0.06), (0.12, 0.12, 0.12), 32.0)
CABINE = Material((0.00, 0.02, 0.04), (0.04, 0.30, 0.55), (1.00, 1.00, 1.00), 160.0)

# "Acesos": só o termo ambiente, que não depende das fontes de luz.
MOTOR = Material((0.25, 0.75, 1.00), PRETO, PRETO, 1.0)
TIRO = Material((1.00, 0.22, 0.10), PRETO, PRETO, 1.0)
