# Minigame 3D: Defesa do Planeta

Projeto de minigame 3D desenvolvido em Python e OpenGL para a atividade 5 da disciplina de Computação Gráfica, cursada na UFABC no terceiro quadrimestre letivo do ano de 2026.

## O jogo (protótipo)

A Terra fica no centro da cena e a nave orbita o planeta. Asteroides surgem ao redor e vêm em linha reta na direção da Terra: a nave gira na órbita para ficar de frente para eles e atira. Cada asteroide destruído vale um ponto; cada um que atinge a Terra ou a nave tira uma vida. Vence quem completa a fileira de pontos do placar (20) e perde quem fica sem vidas (3). Os asteroides vêm cada vez mais rápidos e mais frequentes. Da metade da partida em diante surgem também asteroides resistentes, avermelhados, que aguentam dois tiros: o primeiro os deixa em brasa e o segundo os destrói. A chance de um asteroide vir resistente cresce com os pontos.

O placar é desenhado com geometria: os pontos no canto de cima à esquerda e as vidas à direita. Um ícone no meio da tela mostra o estado (jogar, pausa, vitória ou derrota), e uma seta vermelha na borda aponta o lado do asteroide mais urgente quando ele está fora da vista.

Há duas câmeras: uma segue a nave e a outra mostra a cena inteira, podendo ser girada e aproximada com o mouse. A cena é iluminada pelo Sol e por uma luz presa ao bico da nave.

## Como executar

Com Python 3.11, na raiz do repositório:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/app/main.py
```

Também dá para rodar pelo botão de executar do editor, com o arquivo `src/app/main.py` aberto.

## Teclas

| Tecla | Ação |
| --- | --- |
| ← / → ou A / D | giram a nave em torno do planeta |
| ESPAÇO | atira |
| ENTER | começa a partida (e, no fim de jogo, outra) |
| P | pausa e retoma |
| R | reinicia (começa outra partida na hora) |
| C | troca a câmera: segue a nave / visão geral |
| L | troca as luzes: Sol + nave / só o Sol / só a nave |
| I | troca a iluminação: Blinn-Phong / Phong / cartoon / normais |
| T | troca a textura da Terra: foto / padrão de teste / tijolos |
| V | liga e desliga o vsync (fps na barra de título) |
| ESC | sai |

## Mouse

Na câmera de visão geral:

| Ação | Efeito |
| --- | --- |
| arrastar com o botão esquerdo | gira a câmera em volta do planeta |
| roda | aproxima e afasta |

## Modelos e texturas

Ficam em `src/app/assets/`. O cubo e as imagens `terra.jpg`, `nuvem.jpg`, `pattern.png` e `brick_base.jpg` vêm do material da disciplina (as da Terra e das nuvens são da série Blue Marble, da NASA). O modelo e a textura dos asteroides foram gerados pelo script `src/app/gerar_assets.py`, que não precisa ser executado para jogar.
