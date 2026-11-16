"""
O placar na cena, feito só de geometria: os pontos no canto de cima à esquerda,
as vidas à direita e, no centro, o ícone do estado do jogo.
"""
import numpy as np

from config import (
    COR_CAIXA, COR_DERROTA, COR_ICONE, COR_MOLDURA, COR_PONTO, COR_VIDA, COR_VITORIA, META,
    VIDAS, Cor, Par,
)
from renderizador import Renderizador

MARGEM = 0.07       # das bordas da tela
LADO_MARCA = 0.046
PASSO_MARCA = 0.062
FOLGA_MOLDURA = 0.028
ALTURA_MOLDURA = LADO_MARCA + 2.0 * FOLGA_MOLDURA
Y_PLACAR = 1.0 - MARGEM - ALTURA_MOLDURA / 2.0
LADO_CAIXA = 0.52
Y_ICONE = 0.36   # acima da nave, que fica no meio da tela
ESPESSURA = 0.07   # das barras dos ícones


def largura_fileira(marcas: int) -> float:
    return (marcas - 1) * PASSO_MARCA + LADO_MARCA + 2.0 * FOLGA_MOLDURA


class Placar:
    def __init__(self, render: Renderizador) -> None:
        self.render = render

    def desenhar(self, pontos: int, vidas: int) -> None:
        """Uma marca por ponto e uma por vida, cada fileira dentro da sua moldura."""
        aspecto = self.render.aspecto
        self._fileira(-aspecto + MARGEM, META, pontos, COR_PONTO)
        self._fileira(aspecto - MARGEM - largura_fileira(VIDAS), VIDAS, vidas, COR_VIDA)

    def _fileira(self, esquerda: float, total: int, cheias: int, cor: Cor) -> None:
        largura = largura_fileira(total)
        centro = (esquerda + largura / 2.0, Y_PLACAR)
        self.render.retangulo(centro, (largura, ALTURA_MOLDURA), COR_CAIXA)
        self.render.contorno(centro, (largura, ALTURA_MOLDURA), COR_MOLDURA)
        primeira = esquerda + FOLGA_MOLDURA + LADO_MARCA / 2.0
        for i in range(min(cheias, total)):
            self.render.retangulo((primeira + i * PASSO_MARCA, Y_PLACAR),
                                  (LADO_MARCA, LADO_MARCA), cor)

    def _caixa(self, cor: Cor) -> None:
        """Fundo escuro com moldura, para o ícone não se perder na cena."""
        self.render.retangulo((0.0, Y_ICONE), (LADO_CAIXA, LADO_CAIXA), COR_CAIXA)
        self.render.contorno((0.0, Y_ICONE), (LADO_CAIXA, LADO_CAIXA), cor)

    def _barra(self, inicio: Par, comprimento: float, angulo: float, cor: Cor) -> None:
        """Barra que sai de `inicio` na direção do ângulo."""
        centro = (inicio[0] + 0.5 * comprimento * np.cos(angulo),
                  inicio[1] + 0.5 * comprimento * np.sin(angulo))
        self.render.retangulo(centro, (comprimento, ESPESSURA), cor, angulo)

    def seta(self, lado: float) -> None:
        """Na borda da tela, aponta o lado (-1 esquerda, 1 direita) de um asteroide fora da vista."""
        x = lado * (self.render.aspecto - MARGEM - 0.08)
        self.render.triangulo((x, 0.0), 0.16, COR_VIDA, 0.0 if lado > 0.0 else np.pi)

    def icone_inicio(self) -> None:
        self._caixa(COR_ICONE)
        self.render.triangulo((0.0, Y_ICONE), 0.28, COR_ICONE)

    def icone_pausa(self) -> None:
        self._caixa(COR_ICONE)
        for lado in (-1.0, 1.0):
            self.render.retangulo((0.07 * lado, Y_ICONE), (ESPESSURA, 0.28), COR_ICONE)

    def icone_derrota(self) -> None:
        self._caixa(COR_DERROTA)
        for angulo in (np.pi / 4.0, -np.pi / 4.0):
            self.render.retangulo((0.0, Y_ICONE), (0.36, ESPESSURA), COR_DERROTA, angulo)

    def icone_vitoria(self) -> None:
        self._caixa(COR_VITORIA)
        quina = (-0.05, Y_ICONE - 0.12)   # o ponto de baixo do "certo"
        self._barra(quina, 0.16, np.radians(135.0), COR_VITORIA)
        self._barra(quina, 0.34, np.radians(50.0), COR_VITORIA)
