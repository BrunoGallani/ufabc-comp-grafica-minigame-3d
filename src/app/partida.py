"""
Uma partida: a Terra, a nave, os asteroides que surgem em volta, os tiros, as
colisões e a contagem de pontos e de vidas.
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

import glm
import numpy as np

from colisao import esferas_colidem
from config import (
    ACHATAMENTO_ASTEROIDE, ALCANCE_TIRO, CHANCE_RESISTENTE, INTERVALO_ASTEROIDE, INTERVALO_TIRO,
    META, PONTOS_RESISTENTE, Par, PRIMEIRO_ASTEROIDE, RAIO_ASTEROIDE, RAIO_ORBITA, SAIDA_TIRO,
    VARIACAO_VEL_ASTEROIDE, VEL_ASTEROIDE, VEL_GIRO_ASTEROIDE, VIDAS,
)
from entidades import Asteroide, Nave, Terra, Tiro

if TYPE_CHECKING:
    from renderizador import Renderizador


def interpolar(par: Par, t: float) -> float:
    """Valor entre o (início, fim) do par; t vai de 0 a 1."""
    inicio, fim = par
    return inicio + (fim - inicio) * t


class Partida:
    def __init__(self) -> None:
        self.pontos = 0
        self.vidas = VIDAS
        self.terra = Terra()
        self.nave = Nave()
        self.asteroides: list[Asteroide] = []
        self.tiros: list[Tiro] = []
        self.espera_asteroide = PRIMEIRO_ASTEROIDE
        self.espera_tiro = 0.0

    @property
    def venceu(self) -> bool:
        return self.pontos >= META

    @property
    def perdeu(self) -> bool:
        return self.vidas <= 0

    def ameaca(self) -> Asteroide | None:
        """O asteroide que chega primeiro à Terra, entre os que ainda não foram atingidos."""
        vivos = [a for a in self.asteroides if not a.atingido]
        return min(vivos, key=lambda a: a.distancia / a.velocidade, default=None)

    def atirar(self) -> None:
        if self.espera_tiro > 0.0:
            return
        self.tiros.append(Tiro(self.nave.angulo, RAIO_ORBITA + SAIDA_TIRO))
        self.espera_tiro = INTERVALO_TIRO

    def atualizar(self, dt: float, sentido: float) -> None:
        self.espera_tiro = max(0.0, self.espera_tiro - dt)
        self.terra.atualizar(dt)
        self.nave.atualizar(dt, sentido)
        for objeto in (*self.asteroides, *self.tiros):
            objeto.atualizar(dt)

        self._surgir(dt)
        self._colidir()
        self.tiros = [t for t in self.tiros if not t.gasto and t.distancia < ALCANCE_TIRO]
        self.asteroides = [a for a in self.asteroides if not a.sumiu]

    def _surgir(self, dt: float) -> None:
        """De tempos em tempos, um asteroide novo; mais rápidos e mais frequentes com os pontos."""
        self.espera_asteroide -= dt
        if self.espera_asteroide > 0.0:
            return
        progresso = self.pontos / META
        self.espera_asteroide = interpolar(INTERVALO_ASTEROIDE, progresso)

        sortear = random.uniform
        raio = sortear(*RAIO_ASTEROIDE)
        tamanho = raio * glm.vec3(1.0, sortear(*ACHATAMENTO_ASTEROIDE),
                                  sortear(*ACHATAMENTO_ASTEROIDE))
        eixo = glm.normalize(glm.vec3(*(random.gauss(0.0, 1.0) for _ in range(3))))
        velocidade = interpolar(VEL_ASTEROIDE, progresso) \
            * sortear(1.0 - VARIACAO_VEL_ASTEROIDE, 1.0 + VARIACAO_VEL_ASTEROIDE)
        resistente = random.random() < self._chance_resistente()
        self.asteroides.append(Asteroide(sortear(0.0, 2.0 * np.pi), velocidade, raio, tamanho,
                                         eixo, sortear(*VEL_GIRO_ASTEROIDE), resistente=resistente))

    def _chance_resistente(self) -> float:
        """Zero até PONTOS_RESISTENTE; depois cresce com os pontos, de CHANCE_RESISTENTE[0] a [1]."""
        if self.pontos < PONTOS_RESISTENTE:
            return 0.0
        return interpolar(CHANCE_RESISTENTE,
                          (self.pontos - PONTOS_RESISTENTE) / (META - PONTOS_RESISTENTE))

    def _colidir(self) -> None:
        for asteroide in self.asteroides:
            if asteroide.atingido:
                continue
            for tiro in self.tiros:
                if not tiro.gasto and self._tocam(asteroide, tiro):
                    tiro.gasto = True
                    asteroide.levar_tiro()
                    if asteroide.atingido:
                        self.pontos = min(META, self.pontos + 1)
                    break
            else:
                if self._tocam(asteroide, self.terra) or self._tocam(asteroide, self.nave):
                    asteroide.atingido = True
                    self.vidas = max(0, self.vidas - 1)

    @staticmethod
    def _tocam(a, b) -> bool:
        return esferas_colidem(a.posicao, a.raio, b.posicao, b.raio)

    def desenhar(self, render: Renderizador) -> None:
        for objeto in (self.terra, self.nave, *self.asteroides, *self.tiros):
            objeto.desenhar(render)
