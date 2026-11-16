"""As duas câmeras do jogo: visão LookAt e projeção perspectiva."""
import glm
import numpy as np

from config import (
    ALTURA_CAMERA, DISTANCIA_ORBITAL, FOVY, INCLINACAO_ORBITAL, LIMITES_ORBITAL, MIRA_CAMERA,
    NEAR_MINIMO, PASSO_ZOOM, RAIO_CENA, RAIO_ORBITA, RECUO_CAMERA,
)
from trackball import Trackball

CIMA = glm.vec3(0.0, 1.0, 0.0)
CENTRO = glm.vec3(0.0)


class Camera:
    nome = ""
    near = NEAR_MINIMO
    far = 2.0 * RAIO_CENA

    def __init__(self) -> None:
        self.aspecto = 1.0

    def visao(self) -> glm.mat4:
        raise NotImplementedError

    def projecao(self) -> glm.mat4:
        return glm.perspective(FOVY, self.aspecto, self.near, self.far)


class CameraPerseguicao(Camera):
    """Atrás e acima da nave, olhando para o espaço à frente dela."""
    nome = "segue a nave"
    # Ela fica sempre à mesma distância do centro, e o far alcança o outro lado da cena.
    far = float(np.hypot(RAIO_ORBITA - RECUO_CAMERA, ALTURA_CAMERA)) + RAIO_CENA

    def __init__(self) -> None:
        super().__init__()
        self.olho = glm.vec3(0.0, 0.0, 1.0)
        self.alvo = glm.vec3(0.0)

    def seguir(self, posicao: glm.vec3, frente: glm.vec3) -> None:
        self.olho = posicao - RECUO_CAMERA * frente + ALTURA_CAMERA * CIMA
        self.alvo = posicao + MIRA_CAMERA * frente

    def visao(self) -> glm.mat4:
        return glm.lookAt(self.olho, self.alvo, CIMA)


class CameraOrbital(Camera):
    """Visão geral: gira em volta da Terra com o trackball e se aproxima com a roda do mouse."""
    nome = "visão geral"

    def __init__(self) -> None:
        super().__init__()
        self.distancia = DISTANCIA_ORBITAL
        self.trackball = Trackball(glm.angleAxis(INCLINACAO_ORBITAL, glm.vec3(1.0, 0.0, 0.0)))

    # Os planos envolvem a esfera da cena, com o near o mais longe possível da câmera.
    @property
    def near(self) -> float:
        return max(NEAR_MINIMO, self.distancia - RAIO_CENA)

    @property
    def far(self) -> float:
        return self.distancia + RAIO_CENA

    def aproximar(self, passos: float) -> None:
        self.distancia = float(np.clip(self.distancia - passos * PASSO_ZOOM, *LIMITES_ORBITAL))

    def visao(self) -> glm.mat4:
        # O trackball gira a cena; para a câmera, é o giro contrário aplicado ao olho e ao "para cima".
        giro = glm.inverse(self.trackball.orientacao)
        return glm.lookAt(giro * glm.vec3(0.0, 0.0, self.distancia), CENTRO, giro * CIMA)
