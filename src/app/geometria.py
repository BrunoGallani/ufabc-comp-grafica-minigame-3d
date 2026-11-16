"""Geometrias geradas em numpy (nada aqui fala com a GPU)."""
import numpy as np

# Formas do placar, centradas na origem e com tamanho 1.
QUADRADO = np.array([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)], dtype='f4')
TRIANGULOS_QUADRADO = np.array([0, 1, 2, 2, 3, 0], dtype='u4')
CONTORNO_QUADRADO = np.array([0, 1, 2, 3], dtype='u4')
SETA = np.array([(-0.4, -0.5), (0.6, 0.0), (-0.4, 0.5)], dtype='f4')   # aponta para a direita


def esfera(paralelos: int, meridianos: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Esfera de raio 1 com as coordenadas de textura geradas junto: linhas
    (posição, normal, u, v) e os índices dos triângulos. u dá a volta em torno
    do eixo y e v sobe do polo sul ao norte. A coluna de u = 1 repete a de
    u = 0 para a textura fechar a volta sem costura.
    """
    u, v = np.meshgrid(np.linspace(0.0, 1.0, meridianos + 1), np.linspace(0.0, 1.0, paralelos + 1))
    longitude, latitude = 2.0 * np.pi * (u - 0.5), np.pi * (v - 0.5)
    posicao = np.stack([np.cos(latitude) * np.sin(longitude),
                        np.sin(latitude),
                        np.cos(latitude) * np.cos(longitude)], axis=-1).reshape(-1, 3)
    # Na esfera unitária, a normal é a própria posição.
    dados = np.hstack([posicao, posicao, u.reshape(-1, 1), v.reshape(-1, 1)]).astype('f4')

    # Cada quadrilátero a-b-c-d vira dois triângulos anti-horários vistos de fora.
    i, j = np.meshgrid(np.arange(paralelos), np.arange(meridianos), indexing='ij')
    a = (i * (meridianos + 1) + j).ravel()
    b, d = a + 1, a + meridianos + 1
    c = d + 1
    return dados, np.column_stack([a, b, c, a, c, d]).astype('u4')


def estrelas(quantidade: int, semente: int = 7) -> np.ndarray:
    """Direções espalhadas por igual na esfera de raio 1, uma por estrela."""
    p = np.random.default_rng(semente).normal(size=(quantidade, 3))
    return (p / np.linalg.norm(p, axis=1, keepdims=True)).astype('f4')
