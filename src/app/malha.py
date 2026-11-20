"""Malha triangular lida de um arquivo OFF: normais, esfera envolvente e coordenadas de textura."""
from pathlib import Path

import glm
import numpy as np

EPS = 1e-12        # evita divisão por zero ao normalizar
MEIA_VOLTA = 0.5   # em u; um triângulo comum cobre menos que isso


class Malha:
    def __init__(self, caminho: Path) -> None:
        self.vertices, self.faces = ler_off(caminho)
        minimo, maximo = self.vertices.min(axis=0), self.vertices.max(axis=0)
        # Esfera envolvente: centro da caixa e o vértice mais afastado dele.
        self.centro = 0.5 * (minimo + maximo)
        self.raio = float(np.linalg.norm(self.vertices - self.centro, axis=1).max())

    def matriz_enquadramento(self) -> glm.mat4:
        """
        S(1/r) T(-c): leva a esfera envolvente para a de raio 1 na origem. Entra
        na matriz de modelo; os vértices lidos do arquivo não são alterados.
        """
        return glm.scale(glm.vec3(1.0 / self.raio)) * glm.translate(glm.vec3(*(-self.centro)))

    def facetada(self) -> np.ndarray:
        """Sem índices: três vértices por face, com a normal da face. Linhas (posição, normal)."""
        posicoes = self.vertices[self.faces]
        normais = np.repeat(normais_de_face(self.vertices, self.faces)[:, None], 3, axis=1)
        return np.concatenate([posicoes, normais], axis=2).reshape(-1, 6).astype('f4')

    def texturada(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Indexada, com a normal de cada vértice e o (u, v) do mapeamento esférico.
        Devolve as linhas (posição, normal, u, v) e os índices das faces.
        """
        uv, faces, origem = self.costurar(self.coordenadas_esfericas())
        normais = normais_de_vertice(self.vertices, self.faces)
        # As cópias da costura herdam a posição e a normal do vértice original.
        vertices = np.vstack([self.vertices, self.vertices[origem]])
        normais = np.vstack([normais, normais[origem]])
        return np.hstack([vertices, normais, uv]).astype('f4'), faces.astype('u4')

    def coordenadas_esfericas(self) -> np.ndarray:
        """(u, v) de cada vértice: u é o ângulo em torno do eixo y e v, a elevação, ambos em [0, 1]."""
        p = self.vertices - self.centro
        u = np.arctan2(p[:, 0], p[:, 2]) / (2.0 * np.pi) + 0.5
        norma = np.maximum(np.linalg.norm(p, axis=1), EPS)
        v = np.arcsin(np.clip(p[:, 1] / norma, -1.0, 1.0)) / np.pi + 0.5
        return np.stack([u, v], axis=1).astype('f4')

    def costurar(self, uv: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Duplica os vértices da costura, onde u salta de 1 para 0. Num triângulo
        que a cruza, os vértices com u < 0,5 ganham uma cópia com u + 1, que a
        repetição da textura lê como u. Devolve (uv, faces, origem), em que
        origem[k] é o vértice original da k-ésima cópia.
        """
        faces = self.faces.copy()
        n = len(uv)
        copia: dict[int, int] = {}
        origem, uv_extra = [], []

        for f, face in enumerate(faces):
            u = uv[face, 0]
            if u.max() - u.min() <= MEIA_VOLTA:
                continue
            for k in range(3):
                i = int(face[k])
                if uv[i, 0] >= MEIA_VOLTA:
                    continue
                if i not in copia:
                    copia[i] = n + len(origem)
                    origem.append(i)
                    uv_extra.append((uv[i, 0] + 1.0, uv[i, 1]))
                faces[f, k] = copia[i]

        if origem:
            uv = np.vstack([uv, np.array(uv_extra, dtype='f4')])
        return uv, faces, np.array(origem, dtype='u4')


def normalizar(v: np.ndarray) -> np.ndarray:
    comprimento = np.linalg.norm(v, axis=1, keepdims=True)
    return (v / np.maximum(comprimento, EPS)).astype('f4')


def produto_das_arestas(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """(A - C) x (B - C) de cada face: tem a direção da normal e o dobro da área como norma."""
    a, b, c = (vertices[faces[:, i]] for i in range(3))
    return np.cross(a - c, b - c)


def normais_de_face(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    return normalizar(produto_das_arestas(vertices, faces))


def normais_de_vertice(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """Soma das normais das faces vizinhas, cada uma com o peso da sua área."""
    n = produto_das_arestas(vertices, faces)
    soma = np.zeros_like(vertices)
    # Em soma[indices] += n um índice repetido recebe só uma parcela; np.add.at soma todas.
    for i in range(3):
        np.add.at(soma, faces[:, i], n)
    return normalizar(soma)


def ler_off(caminho: Path) -> tuple[np.ndarray, np.ndarray]:
    """Lê um OFF de faces triangulares: vértices (V, 3) e índices das faces (F, 3)."""
    campos: list[str] = []
    for linha in Path(caminho).read_text(encoding="utf-8").splitlines():
        linha = linha.split("#")[0].strip()   # tira o comentário
        if linha:
            campos.extend(linha.split())

    if campos[0].upper() != "OFF":
        raise ValueError(f"{caminho}: não começa com OFF")

    n_vertices, n_faces = int(campos[1]), int(campos[2])
    p = 4   # campos[3] é o número de arestas, que não é usado

    vertices = np.array(campos[p:p + 3 * n_vertices], dtype='f4').reshape(n_vertices, 3)
    p += 3 * n_vertices

    # Cada face triangular ocupa 4 campos: o número de lados e os três índices.
    faces = np.array(campos[p:p + 4 * n_faces], dtype='u4').reshape(n_faces, 4)
    if not (faces[:, 0] == 3).all():
        raise ValueError(f"{caminho}: há faces que não são triângulos")
    return vertices, np.ascontiguousarray(faces[:, 1:])
