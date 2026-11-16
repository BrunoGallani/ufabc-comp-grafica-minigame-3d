"""
Gera o modelo e a textura dos asteroides. Não faz parte do jogo: roda uma vez, e
os dois arquivos gerados ficam guardados com os outros modelos e texturas.

Executar:
    python src/app/gerar_assets.py
"""
import numpy as np
from PIL import Image

from config import PASTA_MODELOS, PASTA_TEXTURAS

SEMENTE = 2026
SUBDIVISOES = 3   # 20 faces * 4^3 = 1280
RELEVOS = 16
LADO_TEXTURA = 512
OITAVAS = ((4, 1.0), (8, 0.5), (16, 0.25), (32, 0.125), (64, 0.0625))   # (células, peso)
ROCHA_ESCURA, ROCHA_CLARA = (70.0, 60.0, 52.0), (175.0, 162.0, 148.0)


def icosaedro() -> tuple[np.ndarray, list[tuple[int, int, int]]]:
    """Os 12 vértices na esfera de raio 1 e as 20 faces, anti-horárias vistas de fora."""
    t = (1.0 + np.sqrt(5.0)) / 2.0
    vertices = np.array([(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0),
                         (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
                         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)], dtype='f8')
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
             (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
             (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
             (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    return vertices / np.linalg.norm(vertices, axis=1, keepdims=True), faces


def subdividir(vertices: np.ndarray, faces: list) -> tuple[np.ndarray, list]:
    """Cada triângulo vira quatro; os pontos médios das arestas são levados à esfera."""
    pontos = list(vertices)
    meio: dict[tuple[int, int], int] = {}

    def ponto_medio(i: int, j: int) -> int:
        aresta = (min(i, j), max(i, j))
        if aresta not in meio:   # a aresta é de dois triângulos: o ponto é criado uma vez só
            soma = pontos[i] + pontos[j]
            pontos.append(soma / np.linalg.norm(soma))
            meio[aresta] = len(pontos) - 1
        return meio[aresta]

    novas = []
    for a, b, c in faces:
        ab, bc, ca = ponto_medio(a, b), ponto_medio(b, c), ponto_medio(c, a)
        novas += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
    return np.array(pontos), novas


def deformar(vertices: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Afasta ou aproxima cada vértice do centro: calombos e crateras largos e uma aspereza fina."""
    raio = np.ones(len(vertices))
    for _ in range(RELEVOS):
        centro = rng.normal(size=3)
        centro /= np.linalg.norm(centro)
        altura, largura = rng.uniform(-0.22, 0.22), rng.uniform(0.08, 0.5)
        # Vale `altura` no centro do relevo e cai com o ângulo até ele.
        raio += altura * np.exp((vertices @ centro - 1.0) / largura)
    raio += rng.normal(scale=0.008, size=len(vertices))
    return vertices * raio[:, None]


def volume_com_sinal(vertices: np.ndarray, faces: list) -> float:
    """Positivo quando as faces são anti-horárias vistas de fora."""
    a, b, c = (vertices[np.array(faces)[:, i]] for i in range(3))
    return float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6.0)


def gravar_off(caminho, vertices: np.ndarray, faces: list) -> None:
    linhas = ["OFF", f"{len(vertices)} {len(faces)} 0"]
    linhas += [f"{x:.6f} {y:.6f} {z:.6f}" for x, y, z in vertices]
    linhas += [f"3 {a} {b} {c}" for a, b, c in faces]
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def ruido(celulas: int, rng: np.random.Generator) -> np.ndarray:
    """Ruído suave que se repete nas bordas: uma grade aleatória ampliada com interpolação."""
    grade = (rng.random((celulas, celulas)) * 255.0).astype('u1')
    # Amplia a grade repetida 3 x 3 e fica com o miolo: assim as bordas casam.
    lado = 3 * LADO_TEXTURA
    ampliada = Image.fromarray(np.tile(grade, (3, 3))).resize((lado, lado),
                                                              Image.Resampling.BICUBIC)
    miolo = slice(LADO_TEXTURA, 2 * LADO_TEXTURA)
    return np.asarray(ampliada, dtype='f4')[miolo, miolo] / 255.0


def textura_de_rocha(rng: np.random.Generator) -> Image.Image:
    """Soma de ruídos cada vez mais finos e mais fracos, pintada entre dois tons de rocha."""
    n = sum(peso * ruido(celulas, rng) for celulas, peso in OITAVAS)
    n = (n - n.min()) / (n.max() - n.min())
    escura, clara = np.array(ROCHA_ESCURA), np.array(ROCHA_CLARA)
    return Image.fromarray((escura + (clara - escura) * n[..., None]).astype('u1'), "RGB")


def main() -> None:
    rng = np.random.default_rng(SEMENTE)
    vertices, faces = icosaedro()
    for _ in range(SUBDIVISOES):
        vertices, faces = subdividir(vertices, faces)
    vertices = deformar(vertices, rng)
    assert volume_com_sinal(vertices, faces) > 0.0

    gravar_off(PASTA_MODELOS / "asteroide.off", vertices, faces)
    textura_de_rocha(rng).save(PASTA_TEXTURAS / "rocha.png")
    print(f"asteroide.off: {len(vertices)} vértices, {len(faces)} faces")
    print(f"rocha.png: {LADO_TEXTURA} x {LADO_TEXTURA}")


if __name__ == "__main__":
    main()
