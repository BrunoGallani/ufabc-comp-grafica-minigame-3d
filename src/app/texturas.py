"""Leitura de imagens e criação de texturas na GPU."""
from pathlib import Path

import moderngl
import numpy as np
from PIL import Image

# Formatos internos do OpenGL que o moderngl não tem pelo nome.
GL_SRGB8_ALPHA8 = 0x8C43   # cor: o OpenGL decodifica os texels para luz linear na leitura
GL_RGBA8 = 0x8058          # dado (máscara): os valores chegam ao shader como estão no arquivo

ANISOTROPIA_MAX = 8.0


def carregar(ctx: moderngl.Context, caminho: Path, srgb: bool) -> moderngl.Texture:
    """Envia a imagem para a GPU com repetição, mipmaps e filtro trilinear."""
    imagem = np.asarray(Image.open(caminho).convert("RGBA"), dtype='u1')
    altura, largura = imagem.shape[:2]
    # A imagem vem com a linha 0 em cima; a primeira linha enviada é a de v = 0, a de baixo.
    textura = ctx.texture((largura, altura), 4, np.ascontiguousarray(imagem[::-1]).tobytes(),
                          internal_format=GL_SRGB8_ALPHA8 if srgb else GL_RGBA8)
    textura.repeat_x = textura.repeat_y = True
    textura.build_mipmaps()
    textura.filter = (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)
    textura.anisotropy = min(ANISOTROPIA_MAX, ctx.max_anisotropy)
    return textura
