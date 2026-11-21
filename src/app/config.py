"""
Constantes ajustáveis do jogo.

Distâncias em unidades do mundo (o raio da Terra é 1), ângulos em radianos e
velocidades por segundo. Os pares (início, fim) são interpolados pelo progresso
da partida. As cores das luzes e dos materiais estão em luz linear; as do
placar e do fundo são cores de tela.
"""
from pathlib import Path

import numpy as np

Par = tuple[float, float]
Cor = tuple[float, float, float]

NOME_JOGO = "Defesa do Planeta"
LARGURA_JANELA, ALTURA_JANELA = 1280, 720
DT_MAXIMO = 0.05

PASTA = Path(__file__).parent
PASTA_SHADERS = PASTA / "shaders"
PASTA_MODELOS = PASTA / "assets" / "modelos"
PASTA_TEXTURAS = PASTA / "assets" / "texturas"

VIDAS = 3
META = 20   # asteroides destruídos para vencer

RAIO_TERRA = 1.0
INCLINACAO_TERRA = np.radians(23.5)
VEL_ROTACAO_TERRA = 0.08
VEL_NUVENS = 0.012   # voltas por segundo sobre a superfície
PARALELOS_TERRA, MERIDIANOS_TERRA = 48, 96

RAIO_ORBITA = 2.4
VEL_NAVE = 1.7
RAIO_NAVE = 0.35

VEL_TIRO = 12.0
RAIO_TIRO = 0.12
TAMANHO_TIRO = (0.55, 0.05, 0.05)
INTERVALO_TIRO = 0.28
SAIDA_TIRO = 0.6   # distância do centro da nave em que o tiro nasce

RAIO_SURGIMENTO = 12.0
ALCANCE_TIRO = RAIO_SURGIMENTO + 1.0
PRIMEIRO_ASTEROIDE = 1.0
INTERVALO_ASTEROIDE = (2.4, 1.0)
VEL_ASTEROIDE = (1.3, 2.2)
VARIACAO_VEL_ASTEROIDE = 0.15   # cada asteroide sai até 15% mais lento ou mais rápido
RAIO_ASTEROIDE = (0.40, 0.65)   # sorteado entre os dois
ACHATAMENTO_ASTEROIDE = (0.60, 0.95)
VEL_GIRO_ASTEROIDE = (0.4, 1.6)
REPETICOES_ROCHA = (3.0, 2.0)
TEMPO_SURGIR = 0.6   # o asteroide cresce até o tamanho final
TEMPO_SUMIR = 0.2    # e encolhe depois de atingido
# Resistentes aguentam um tiro a mais. Surgem a partir da metade da META, com chance crescente.
PONTOS_RESISTENTE = META // 2
CHANCE_RESISTENTE = (0.15, 0.5)

FOVY = np.radians(45.0)
RAIO_CENA = RAIO_SURGIMENTO + 1.5   # esfera em volta da Terra que contém tudo que é desenhado
RECUO_CAMERA, ALTURA_CAMERA, MIRA_CAMERA = 4.4, 3.2, 1.0
NEAR_MINIMO = 0.25
DISTANCIA_ORBITAL = 13.0
LIMITES_ORBITAL = (5.0, 36.0)
PASSO_ZOOM = 1.5
INCLINACAO_ORBITAL = np.radians(40.0)
ANGULO_SETA = 0.6   # um asteroide mais longe que isso da frente da nave está fora da vista

LUZ_AMBIENTE = (1.0, 1.0, 1.0)
DIRECAO_SOL = (0.6, 0.7, 0.35)   # da cena para o Sol
COR_SOL = (1.0, 0.96, 0.88)
COR_LUZ_NAVE = (0.35, 0.75, 1.6)
ATENUACAO_LUZ_NAVE = (1.0, 0.15, 0.08)   # kc, kl, kq
AVANCO_LUZ_NAVE = 0.55   # a luz fica no bico, à frente do centro da nave

# Tecla I. A posição de cada modo é o u_modo de cena.frag.
MODOS_DE_ILUMINACAO = ("Blinn-Phong", "Phong", "cartoon", "normais")
# Tecla T. As nuvens só vão sobre a primeira, a foto da Terra.
TEXTURAS_TERRA = ("terra.jpg", "pattern.png", "brick_base.jpg")

FUNDO = (0.0, 0.004, 0.012)
COR_ESTRELAS = (0.55, 0.58, 0.68)
QUANTIDADE_ESTRELAS = 1500

COR_PONTO = (1.0, 0.82, 0.16)
COR_VIDA = (0.95, 0.25, 0.22)
COR_MOLDURA = (0.85, 0.87, 0.90)
COR_CAIXA = (0.03, 0.04, 0.07)
COR_ICONE = (0.92, 0.94, 0.97)
COR_VITORIA = (0.30, 0.90, 0.45)
COR_DERROTA = (0.95, 0.25, 0.22)

# Sem tunelamento: no pior caso (tiro e asteroide de frente) o passo é menor que a faixa de contato.
assert (VEL_TIRO + VEL_ASTEROIDE[1] * (1.0 + VARIACAO_VEL_ASTEROIDE)) * DT_MAXIMO \
    < 2.0 * (RAIO_TIRO + RAIO_ASTEROIDE[0])
