"""Tudo que fala com a GPU fica aqui: shaders, malhas (VBO/VAO/EBO), texturas e draw calls."""
import glm
import moderngl
import numpy as np

import geometria
import material
import texturas
from camera import Camera
from config import (
    COR_ESTRELAS, FUNDO, LUZ_AMBIENTE, MERIDIANOS_TERRA, MODOS_DE_ILUMINACAO, PARALELOS_TERRA,
    PASTA_MODELOS, PASTA_SHADERS, PASTA_TEXTURAS, QUANTIDADE_ESTRELAS, REPETICOES_ROCHA,
    TEXTURAS_TERRA, Cor, Par,
)
from malha import Malha
from material import Luz, Material

# Estado do OpenGL que o moderngl não tem pelo nome: codifica em sRGB o que o shader grava.
GL_FRAMEBUFFER_SRGB = 0x8DB9

TIPOS_GLM = (glm.mat3, glm.mat4, glm.vec2, glm.vec3, glm.vec4)
EIXO_Z = glm.vec3(0.0, 0.0, 1.0)


def enviar(programa: moderngl.Program, **uniformes) -> None:
    """Envia os uniformes que o programa declara (o linker descarta os que o shader não usa)."""
    for nome, valor in uniformes.items():
        if nome not in programa:
            continue
        if isinstance(valor, TIPOS_GLM):
            programa[nome].write(valor.to_bytes())
        else:
            programa[nome].value = valor


def matriz_normal(modelo: glm.mat4) -> glm.mat3:
    """Inversa transposta da parte linear: mantém a normal perpendicular com escala não uniforme."""
    return glm.transpose(glm.inverse(glm.mat3(modelo)))


class Renderizador:
    """
    Cada geometria e cada textura vai para a VRAM uma vez só, aqui. Depois, cada
    objeto é desenhado com a sua matriz de modelo, enviada como uniforme.
    """

    def __init__(self, ctx: moderngl.Context) -> None:
        self.ctx = ctx
        self.aspecto = 1.0
        self._recursos: list = []   # liberados em ordem inversa no fim
        self.cena = self._programa("cena")
        self.ceu = self._programa("estrelas")
        self.tela = self._programa("placar")
        ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        atributos = ('vPosition', 'vNormal', 'vTexCoord')
        self._terra = self._malha(self.cena, '3f 3f 2f', atributos,
                                  *geometria.esfera(PARALELOS_TERRA, MERIDIANOS_TERRA))
        asteroide = Malha(PASTA_MODELOS / "asteroide.off")
        self._enquadramento = asteroide.matriz_enquadramento()
        self._asteroide = self._malha(self.cena, '3f 3f 2f', atributos, *asteroide.texturada())
        # O cubo tem cantos vivos: uma normal por face, sem índices.
        cubo = Malha(PASTA_MODELOS / "cubo.off")
        self._cubo = self._malha(self.cena, '3f 3f', atributos[:2], cubo.facetada())
        self._estrelas = self._malha(self.ceu, '3f', ('vPosition',),
                                     geometria.estrelas(QUANTIDADE_ESTRELAS))
        self._quadrado = self._malha(self.tela, '2f', ('vPosition',), geometria.QUADRADO)
        self._seta = self._malha(self.tela, '2f', ('vPosition',), geometria.SETA)

        self._texturas_terra = [self._textura(nome, srgb=True) for nome in TEXTURAS_TERRA]
        self._textura_terra = 0   # qual delas, escolhida a cada quadro em iniciar_cena
        self._tex_nuvens = self._textura("nuvem.jpg", srgb=False)   # máscara: dado, não cor
        self._tex_rocha = self._textura("rocha.png", srgb=True)
        enviar(self.cena, u_base=0, u_camada=1)   # as unidades de textura de cada amostrador

    # ---------------------------------------------------------------- recursos
    def _programa(self, nome: str) -> moderngl.Program:
        programa = self.ctx.program(
            vertex_shader=(PASTA_SHADERS / f"{nome}.vert").read_text(encoding="utf-8"),
            fragment_shader=(PASTA_SHADERS / f"{nome}.frag").read_text(encoding="utf-8"),
        )
        self._recursos.append(programa)
        return programa

    def _buffer(self, dados: np.ndarray) -> moderngl.Buffer:
        buffer = self.ctx.buffer(dados.tobytes())
        self._recursos.append(buffer)
        return buffer

    def _malha(self, programa: moderngl.Program, formato: str, atributos: tuple[str, ...],
               vertices: np.ndarray, indices: np.ndarray | None = None) -> moderngl.VertexArray:
        vbo = self._buffer(vertices)
        ebo = self._buffer(indices) if indices is not None else None
        vao = self.ctx.vertex_array(programa, [(vbo, formato, *atributos)], index_buffer=ebo)
        self._recursos.append(vao)
        return vao

    def _textura(self, arquivo: str, srgb: bool) -> moderngl.Texture:
        textura = texturas.carregar(self.ctx, PASTA_TEXTURAS / arquivo, srgb)
        self._recursos.append(textura)
        return textura

    def ajustar_viewport(self, largura: int, altura: int) -> None:
        if largura == 0 or altura == 0:   # janela minimizada
            return
        self.ctx.viewport = (0, 0, largura, altura)
        self.aspecto = largura / altura

    # ------------------------------------------------------ primeira passada: 3D
    def iniciar_cena(self, camera: Camera, sol: Luz, luz_nave: Luz, modo: int,
                     textura_terra: int) -> None:
        """Limpa a tela e envia a câmera, as luzes (já no espaço da câmera) e o modo de iluminação."""
        # A cor do fundo já é uma cor de tela: limpa sem codificar.
        self.ctx.disable_direct(GL_FRAMEBUFFER_SRGB)
        self.ctx.clear(*FUNDO, depth=1.0)
        # As normais são dados mostrados como cor: também ficam sem codificar.
        if MODOS_DE_ILUMINACAO[modo] != "normais":
            self.ctx.enable_direct(GL_FRAMEBUFFER_SRGB)
        self.ctx.enable(moderngl.DEPTH_TEST)

        self._textura_terra = textura_terra
        self._visao, self._projecao = camera.visao(), camera.projecao()
        enviar(self.cena, u_visao=self._visao, u_projecao=self._projecao, u_modo=modo,
               u_ambiente=LUZ_AMBIENTE,
               u_sol=self._visao * sol.posicao, u_cor_sol=sol.cor,
               u_luz=self._visao * luz_nave.posicao, u_cor_luz=luz_nave.cor,
               u_atenuacao=luz_nave.atenuacao)

    def _desenhar(self, vao: moderngl.VertexArray, modelo: glm.mat4, mat: Material,
                  textura: moderngl.Texture | None = None, repeticoes: Par = (1.0, 1.0),
                  camada: moderngl.Texture | None = None, deslocamento: float = 0.0) -> None:
        if textura is not None:
            textura.use(0)
        if camada is not None:
            camada.use(1)
        enviar(self.cena, u_modelo=modelo, u_normal=matriz_normal(modelo),
               u_ka=mat.ka, u_kd=mat.kd, u_ks=mat.ks, u_alfa=mat.alfa,
               u_usar_textura=textura is not None, u_repeticoes=repeticoes,
               u_usar_camada=camada is not None, u_deslocamento=deslocamento)
        vao.render(moderngl.TRIANGLES)

    def cubo(self, modelo: glm.mat4, mat: Material) -> None:
        self._desenhar(self._cubo, modelo, mat)

    def asteroide(self, modelo: glm.mat4) -> None:
        # O enquadramento vem primeiro: leva a malha do arquivo para o raio 1 na origem.
        self._desenhar(self._asteroide, modelo * self._enquadramento, material.ROCHA,
                       self._tex_rocha, REPETICOES_ROCHA)

    def terra(self, modelo: glm.mat4, deslocamento_nuvens: float) -> None:
        nuvens = self._tex_nuvens if self._textura_terra == 0 else None   # só sobre a foto
        self._desenhar(self._terra, modelo, material.TERRA,
                       self._texturas_terra[self._textura_terra],
                       camada=nuvens, deslocamento=deslocamento_nuvens)

    def estrelas(self) -> None:
        """Por último na passada 3D: só aparecem onde nada foi desenhado."""
        enviar(self.ceu, u_visao_rot=glm.mat4(glm.mat3(self._visao)), u_projecao=self._projecao,
               u_cor=COR_ESTRELAS)
        # As estrelas têm profundidade 1, o valor da limpeza: o teste precisa aceitar a igualdade.
        self.ctx.depth_func = '<='
        self._estrelas.render(moderngl.POINTS)
        self.ctx.depth_func = '<'

    # ---------------------------------------------------- segunda passada: placar
    def iniciar_placar(self) -> None:
        """Formas 2D por cima da cena: sem profundidade, em projeção ortográfica e em cores de tela."""
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.disable_direct(GL_FRAMEBUFFER_SRGB)
        # A tela vai de -1 a 1 na vertical e de -aspecto a aspecto na horizontal.
        enviar(self.tela, u_projecao=glm.ortho(-self.aspecto, self.aspecto, -1.0, 1.0, -1.0, 1.0))

    def _forma(self, vao: moderngl.VertexArray, primitiva: int, centro: Par, tamanho: Par,
               cor: Cor, angulo: float) -> None:
        modelo = (glm.translate(glm.vec3(*centro, 0.0)) * glm.rotate(angulo, EIXO_Z)
                  * glm.scale(glm.vec3(*tamanho, 1.0)))
        enviar(self.tela, u_modelo=modelo, u_cor=cor)
        vao.render(primitiva)

    # O mesmo VAO do quadrado é preenchido (TRIANGLE_FAN) ou contornado (LINE_LOOP).
    def retangulo(self, centro: Par, tamanho: Par, cor: Cor, angulo: float = 0.0) -> None:
        self._forma(self._quadrado, moderngl.TRIANGLE_FAN, centro, tamanho, cor, angulo)

    def contorno(self, centro: Par, tamanho: Par, cor: Cor) -> None:
        self._forma(self._quadrado, moderngl.LINE_LOOP, centro, tamanho, cor, 0.0)

    def triangulo(self, centro: Par, tamanho: float, cor: Cor, angulo: float = 0.0) -> None:
        self._forma(self._seta, moderngl.TRIANGLES, centro, (tamanho, tamanho), cor, angulo)

    def liberar(self) -> None:
        # Ordem inversa da criação: cada VAO sai antes dos buffers que ele usa.
        for recurso in reversed(self._recursos):
            recurso.release()
