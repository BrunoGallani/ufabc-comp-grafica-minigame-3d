"""Materiais e fontes de luz do modelo de Blinn-Phong, com as cores em luz linear."""
from dataclasses import dataclass

import glm

from config import Cor


@dataclass(frozen=True)
class Material:
    ka: glm.vec3
    kd: glm.vec3
    ks: glm.vec3
    alfa: float


@dataclass(frozen=True)
class Luz:
    """Com w = 1, `posicao` é o ponto de uma fonte pontual; com w = 0, a direção até uma fonte direcional."""
    posicao: glm.vec4
    cor: glm.vec3
    atenuacao: glm.vec3   # kc, kl, kq; só vale para a pontual


def material(ka: Cor, kd: Cor, ks: Cor, alfa: float) -> Material:
    return Material(glm.vec3(ka), glm.vec3(kd), glm.vec3(ks), alfa)


BRANCO, PRETO = (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)

# Nos objetos com textura, a imagem faz o papel de kd.
TERRA = material((0.03, 0.03, 0.04), BRANCO, (0.22, 0.22, 0.22), 24.0)
ROCHA = material((0.035, 0.035, 0.04), BRANCO, (0.03, 0.03, 0.03), 6.0)

CASCO = material((0.03, 0.03, 0.04), (0.55, 0.57, 0.62), (0.25, 0.25, 0.25), 40.0)
ASA = material((0.03, 0.01, 0.01), (0.55, 0.08, 0.06), (0.12, 0.12, 0.12), 32.0)
CABINE = material((0.00, 0.02, 0.04), (0.04, 0.30, 0.55), (1.00, 1.00, 1.00), 160.0)

# "Acesos": só o termo ambiente, que não depende das fontes de luz.
MOTOR = material((0.25, 0.75, 1.00), PRETO, PRETO, 1.0)
TIRO = material((1.00, 0.22, 0.10), PRETO, PRETO, 1.0)
