"""
Estados do jogo (início, jogando, pausa, vitória e derrota), teclado, mouse,
câmeras e luzes.
"""
from enum import Enum

import glfw
import glm
import moderngl
import numpy as np

from camera import CameraOrbital, CameraPerseguicao
from config import (
    ANGULO_SETA, ATENUACAO_LUZ_NAVE, AVANCO_LUZ_NAVE, COR_LUZ_NAVE, COR_SOL, DIRECAO_SOL, META,
    MODOS_DE_ILUMINACAO, NOME_JOGO, TEXTURAS_TERRA,
)
from material import Luz
from partida import Partida
from placar import Placar
from renderizador import Renderizador


class Estado(Enum):
    INICIO = "início"
    JOGANDO = "jogando"
    PAUSADO = "pausado"
    VITORIA = "vitória"
    DERROTA = "derrota"


# P só alterna entre jogando e pausado; nos outros estados não faz nada.
PAUSA = {Estado.JOGANDO: Estado.PAUSADO, Estado.PAUSADO: Estado.JOGANDO}
FIM = (Estado.VITORIA, Estado.DERROTA)

# Fontes acesas em cada modo da tecla L: (nome, Sol, luz da nave).
MODOS_DE_LUZ = (("sol + nave", True, True), ("só sol", True, False), ("só nave", False, True))
APAGADA = glm.vec3(0.0)

TECLAS_DIREITA = (glfw.KEY_RIGHT, glfw.KEY_D)
TECLAS_ESQUERDA = (glfw.KEY_LEFT, glfw.KEY_A)


class Jogo:
    def __init__(self, ctx: moderngl.Context, janela: 'glfw._GLFWwindowPointerT') -> None:
        self.janela = janela
        self.render = Renderizador(ctx)
        self.placar = Placar(self.render)
        self.perseguicao = CameraPerseguicao()
        self.orbital = CameraOrbital()
        self.camera = self.perseguicao
        self.modo_de_luz = 0
        self.modo_de_iluminacao = 0
        self.textura_terra = 0
        self.vsync = True
        self.partida = Partida()
        self.estado = Estado.INICIO

        # Tecla nova = um método + uma linha aqui.
        self.acoes = {
            glfw.KEY_ESCAPE: self.sair,
            glfw.KEY_ENTER: self.iniciar,
            glfw.KEY_KP_ENTER: self.iniciar,
            glfw.KEY_SPACE: self.atirar,
            glfw.KEY_P: self.alternar_pausa,
            glfw.KEY_R: self.reiniciar,
            glfw.KEY_C: self.trocar_camera,
            glfw.KEY_L: self.trocar_luz,
            glfw.KEY_I: self.trocar_iluminacao,
            glfw.KEY_T: self.trocar_textura,
            glfw.KEY_V: self.alternar_vsync,
        }

    # ------------------------------------------------------------------ teclado
    def tecla(self, janela: 'glfw._GLFWwindowPointerT', key: int, scancode: int,
              action: int, mods: int) -> None:
        """Callback de teclado do GLFW. Só o PRESS conta: segurar não repete a ação."""
        if action == glfw.PRESS and (acao := self.acoes.get(key)):
            acao()

    def iniciar(self) -> None:
        """ENTER: começa a partida; no fim de jogo, começa outra."""
        if self.estado in FIM:
            self.partida = Partida()
        if self.estado is Estado.INICIO or self.estado in FIM:
            self.estado = Estado.JOGANDO

    def reiniciar(self) -> None:
        """R: outra partida na hora. Só troca a Partida; a GPU não é tocada."""
        if self.estado is not Estado.INICIO:
            self.partida = Partida()
            self.estado = Estado.JOGANDO

    def atirar(self) -> None:
        if self.estado is Estado.JOGANDO:
            self.partida.atirar()

    def alternar_pausa(self) -> None:
        self.estado = PAUSA.get(self.estado, self.estado)

    def trocar_camera(self) -> None:
        self.orbital.trackball.soltar()
        self.camera = self.orbital if self.camera is self.perseguicao else self.perseguicao

    def trocar_luz(self) -> None:
        self.modo_de_luz = (self.modo_de_luz + 1) % len(MODOS_DE_LUZ)

    def trocar_iluminacao(self) -> None:
        self.modo_de_iluminacao = (self.modo_de_iluminacao + 1) % len(MODOS_DE_ILUMINACAO)

    def trocar_textura(self) -> None:
        self.textura_terra = (self.textura_terra + 1) % len(TEXTURAS_TERRA)

    def alternar_vsync(self) -> None:
        self.vsync = not self.vsync
        glfw.swap_interval(int(self.vsync))

    def sair(self) -> None:
        glfw.set_window_should_close(self.janela, True)

    def _apertada(self, teclas: tuple[int, ...]) -> bool:
        return any(glfw.get_key(self.janela, t) == glfw.PRESS for t in teclas)

    def sentido(self) -> float:
        """-1 (esquerda), 0 ou 1 (direita). Lido a cada quadro, não pelo callback."""
        return float(self._apertada(TECLAS_DIREITA)) - float(self._apertada(TECLAS_ESQUERDA))

    # -------------------------------------------------------------------- mouse
    def botao_do_mouse(self, janela: 'glfw._GLFWwindowPointerT', botao: int, action: int,
                       mods: int) -> None:
        """Callback do GLFW. O botão esquerdo segura e solta a visão geral."""
        if botao != glfw.MOUSE_BUTTON_LEFT:
            return
        if action == glfw.PRESS and self.camera is self.orbital:
            self.orbital.trackball.pressionar(*glfw.get_cursor_pos(janela))
        elif action == glfw.RELEASE:
            self.orbital.trackball.soltar()

    def cursor(self, janela: 'glfw._GLFWwindowPointerT', x: float, y: float) -> None:
        """Callback do GLFW. Com o botão esquerdo segurado, arrastar gira a visão geral."""
        self.orbital.trackball.mover(x, y)

    def roda(self, janela: 'glfw._GLFWwindowPointerT', dx: float, dy: float) -> None:
        """Callback do GLFW. A roda aproxima e afasta a visão geral."""
        if self.camera is self.orbital:
            self.orbital.aproximar(dy)

    # ------------------------------------------------------------------- janela
    def redimensionar(self, janela: 'glfw._GLFWwindowPointerT', largura: int,
                      altura: int) -> None:
        """Callback do GLFW quando a área de desenho muda de tamanho (em pixels)."""
        self.render.ajustar_viewport(largura, altura)
        self.perseguicao.aspecto = self.orbital.aspecto = self.render.aspecto
        # O cursor vem em coordenadas da janela, que em telas densas não são pixels.
        self.orbital.trackball.redimensionar(*glfw.get_window_size(janela))

    # -------------------------------------------------------------- cada quadro
    def atualizar(self, dt: float) -> None:
        if self.estado is Estado.INICIO:
            self.partida.terra.atualizar(dt)   # antes da partida, só o planeta gira
        elif self.estado is Estado.JOGANDO:
            self.partida.atualizar(dt, self.sentido())
            if self.partida.venceu:
                self.estado = Estado.VITORIA
            elif self.partida.perdeu:
                self.estado = Estado.DERROTA
        nave = self.partida.nave
        self.perseguicao.seguir(nave.posicao, nave.frente)

    def _luzes(self) -> tuple[Luz, Luz]:
        """O Sol (direcional) e a luz presa ao bico da nave (pontual), conforme o modo da tecla L."""
        _, sol_aceso, nave_acesa = MODOS_DE_LUZ[self.modo_de_luz]
        nave = self.partida.nave
        sol = Luz(glm.vec4(*DIRECAO_SOL, 0.0), glm.vec3(COR_SOL) if sol_aceso else APAGADA,
                  glm.vec3(1.0, 0.0, 0.0))
        luz_nave = Luz(glm.vec4(nave.posicao + AVANCO_LUZ_NAVE * nave.frente, 1.0),
                       glm.vec3(COR_LUZ_NAVE) if nave_acesa else APAGADA,
                       glm.vec3(ATENUACAO_LUZ_NAVE))
        return sol, luz_nave

    def _lado_da_ameaca(self) -> float:
        """-1 ou 1 se o asteroide mais urgente está fora da vista da câmera que segue a nave; senão 0."""
        ameaca = self.partida.ameaca()
        if ameaca is None or self.camera is not self.perseguicao:
            return 0.0
        # Diferença de ângulo levada para [-pi, pi): positiva é à direita da nave.
        diferenca = (ameaca.angulo - self.partida.nave.angulo + np.pi) % (2.0 * np.pi) - np.pi
        return float(np.sign(diferenca)) if abs(diferenca) > ANGULO_SETA else 0.0

    def desenhar(self) -> None:
        self.render.iniciar_cena(self.camera, *self._luzes(), self.modo_de_iluminacao,
                                 self.textura_terra)
        self.partida.desenhar(self.render)
        self.render.estrelas()

        self.render.iniciar_placar()
        self.placar.desenhar(self.partida.pontos, self.partida.vidas)
        match self.estado:
            case Estado.JOGANDO:
                if lado := self._lado_da_ameaca():
                    self.placar.seta(lado)
            case Estado.INICIO:
                self.placar.icone_inicio()
            case Estado.PAUSADO:
                self.placar.icone_pausa()
            case Estado.VITORIA:
                self.placar.icone_vitoria()
            case Estado.DERROTA:
                self.placar.icone_derrota()

    def titulo(self, fps: float) -> str:
        return (f"{NOME_JOGO} - {self.estado.value} - {self.partida.pontos}/{META} pontos - "
                f"{self.partida.vidas} vidas - câmera: {self.camera.nome} - "
                f"luz: {MODOS_DE_LUZ[self.modo_de_luz][0]} - "
                f"iluminação: {MODOS_DE_ILUMINACAO[self.modo_de_iluminacao]} - "
                f"Terra: {TEXTURAS_TERRA[self.textura_terra]} - "
                f"vsync {'on' if self.vsync else 'OFF'} - {fps:5.1f} fps")

    def liberar(self) -> None:
        self.render.liberar()
