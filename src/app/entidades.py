"""
Tudo que aparece no mundo: a Terra, a nave, os asteroides e os tiros. Cada um se
atualiza e se desenha; quem decide quando é a Partida.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

import glm
import numpy as np

import material
from config import (
    INCLINACAO_TERRA, RAIO_NAVE, RAIO_ORBITA, RAIO_SURGIMENTO, RAIO_TERRA, RAIO_TIRO,
    TAMANHO_TIRO, TEMPO_SUMIR, TEMPO_SURGIR, VEL_NAVE, VEL_NUVENS, VEL_ROTACAO_TERRA, VEL_TIRO,
)

if TYPE_CHECKING:
    from renderizador import Renderizador

EIXO_Y = glm.vec3(0.0, 1.0, 0.0)
EIXO_Z = glm.vec3(0.0, 0.0, 1.0)

# Peças da nave, todas o mesmo cubo: (centro, tamanho, material). O bico aponta para +x.
PECAS_NAVE = (
    ((0.00, 0.00, 0.00), (0.62, 0.12, 0.16), material.CASCO),
    ((0.38, 0.00, 0.00), (0.18, 0.08, 0.10), material.CASCO),
    ((-0.10, -0.01, 0.00), (0.22, 0.03, 0.72), material.ASA),
    ((-0.24, 0.10, 0.00), (0.14, 0.12, 0.02), material.ASA),
    ((0.10, 0.08, 0.00), (0.20, 0.07, 0.10), material.CABINE),
    ((-0.34, 0.00, 0.10), (0.08, 0.08, 0.08), material.MOTOR),
    ((-0.34, 0.00, -0.10), (0.08, 0.08, 0.08), material.MOTOR),
)


def direcao(angulo: float) -> glm.vec3:
    """Vetor unitário do plano da órbita (xz) que faz esse ângulo com o eixo x."""
    return glm.vec3(np.cos(angulo), 0.0, np.sin(angulo))


def girar_para(angulo: float) -> glm.mat4:
    """Rotação em torno de y que leva o eixo x para direcao(angulo)."""
    return glm.rotate(-angulo, EIXO_Y)


@dataclass(eq=False)
class Terra:
    tempo: float = 0.0
    posicao: ClassVar[glm.vec3] = glm.vec3(0.0)
    raio: ClassVar[float] = RAIO_TERRA

    def atualizar(self, dt: float) -> None:
        self.tempo += dt

    def desenhar(self, render: Renderizador) -> None:
        modelo = (glm.rotate(INCLINACAO_TERRA, EIXO_Z)
                  * glm.rotate(VEL_ROTACAO_TERRA * self.tempo, EIXO_Y)
                  * glm.scale(glm.vec3(RAIO_TERRA)))
        render.terra(modelo, (VEL_NUVENS * self.tempo) % 1.0)


@dataclass(eq=False)
class Nave:
    angulo: float = 0.0   # onde ela está na órbita
    raio: ClassVar[float] = RAIO_NAVE

    @property
    def frente(self) -> glm.vec3:
        return direcao(self.angulo)

    @property
    def posicao(self) -> glm.vec3:
        return RAIO_ORBITA * self.frente

    def atualizar(self, dt: float, sentido: float) -> None:
        self.angulo += sentido * VEL_NAVE * dt

    def desenhar(self, render: Renderizador) -> None:
        base = glm.translate(self.posicao) * girar_para(self.angulo)
        for centro, tamanho, mat in PECAS_NAVE:
            render.cubo(base * glm.translate(glm.vec3(centro)) * glm.scale(glm.vec3(tamanho)), mat)


@dataclass(eq=False)
class Asteroide:
    angulo: float         # de que lado ele vem, no plano da órbita
    velocidade: float
    raio: float           # da esfera de colisão: o maior semieixo
    tamanho: glm.vec3     # os três semieixos (escala não uniforme)
    eixo: glm.vec3        # do giro próprio
    vel_giro: float
    distancia: float = RAIO_SURGIMENTO   # até o centro da Terra
    giro: float = 0.0
    idade: float = 0.0
    atingido: bool = False
    sumindo: float = 0.0   # tempo desde que foi atingido

    @property
    def posicao(self) -> glm.vec3:
        return self.distancia * direcao(self.angulo)

    @property
    def sumiu(self) -> bool:
        return self.sumindo >= TEMPO_SUMIR

    def atualizar(self, dt: float) -> None:
        self.idade += dt
        self.giro += self.vel_giro * dt
        if self.atingido:
            self.sumindo += dt
        else:
            self.distancia -= self.velocidade * dt

    def desenhar(self, render: Renderizador) -> None:
        # Cresce ao surgir e encolhe depois de atingido.
        fator = min(1.0, self.idade / TEMPO_SURGIR) * max(0.0, 1.0 - self.sumindo / TEMPO_SUMIR)
        modelo = (glm.translate(self.posicao)
                  * glm.rotate(self.giro, self.eixo)
                  * glm.scale(self.tamanho * fator))
        render.asteroide(modelo)


@dataclass(eq=False)
class Tiro:
    angulo: float
    distancia: float
    gasto: bool = False   # já acertou um asteroide
    raio: ClassVar[float] = RAIO_TIRO

    @property
    def posicao(self) -> glm.vec3:
        return self.distancia * direcao(self.angulo)

    def atualizar(self, dt: float) -> None:
        self.distancia += VEL_TIRO * dt

    def desenhar(self, render: Renderizador) -> None:
        modelo = (glm.translate(self.posicao) * girar_para(self.angulo)
                  * glm.scale(glm.vec3(TAMANHO_TIRO)))
        render.cubo(modelo, material.TIRO)
