"""Trackball virtual: arrastar o mouse gira uma orientação guardada num quatérnio."""
import glm


class Trackball:
    def __init__(self, orientacao: glm.quat) -> None:
        self.orientacao = orientacao
        self.arrastando = False
        self.ultimo = glm.vec3(0.0)
        self.largura = self.altura = 1.0

    def redimensionar(self, largura: int, altura: int) -> None:
        self.largura, self.altura = float(max(1, largura)), float(max(1, altura))

    def _na_esfera(self, x: float, y: float) -> glm.vec3:
        """Leva o cursor à esfera unitária. Fora do círculo, o ponto fica na borda (z = 0)."""
        p = glm.vec3(2.0 * x / self.largura - 1.0, 1.0 - 2.0 * y / self.altura, 0.0)
        quadrado = p.x * p.x + p.y * p.y
        if quadrado >= 1.0:
            return glm.normalize(p)
        p.z = glm.sqrt(1.0 - quadrado)
        return p

    def pressionar(self, x: float, y: float) -> None:
        self.arrastando = True
        self.ultimo = self._na_esfera(x, y)

    def mover(self, x: float, y: float) -> None:
        if not self.arrastando:
            return
        atual = self._na_esfera(x, y)
        # |p1 x p2| = sen(ângulo), que entre dois eventos seguidos vale quase o ângulo.
        eixo = glm.cross(self.ultimo, atual)
        angulo = glm.length(eixo)
        if angulo > 1e-9:
            self.orientacao = glm.normalize(glm.angleAxis(angulo, eixo / angulo) * self.orientacao)
        self.ultimo = atual

    def soltar(self) -> None:
        self.arrastando = False
