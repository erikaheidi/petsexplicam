"""Roteiro de diálogo -> script do moviemakr, com a receita validada embutida.

    ./dialogo novo   <filme> [--vlog pacoca]  cria movies/<filme>/ com um roteiro.yaml de exemplo
    ./dialogo gerar  <filme> [--versao v2]  roteiro.yaml -> scripts/v1.yaml (ou v2...)
    ./dialogo cenas  <filme>              tabela de cenas: quem fala, palavras, duração

O roteiro diz só o que muda de um vídeo para outro (quem fala, o quê, e a ação).
Tudo que precisa se repetir PALAVRA POR PALAVRA em todas as cenas - elenco,
cenário, enquadramento, postura, regras de fala - mora aqui. Foi essa repetição
que segurou a consistência no direito-de-votar; editar os textos à mão, cena a
cena, é o jeito mais rápido de perder a dupla e o enquadramento.

A receita (o que o direito-de-votar ensinou, ver ELENCO.md e CLAUDE.md):
  - Câmera por cena (`camera:` no roteiro): `dupla`, ou o close de um dos dois
    quando o cenário tiver. Sem `camera:`, a cena vai no close de quem fala.
    Cada câmera tem seu frame de referência; quem está fora do plano é citado
    por descrição, não por rótulo.
  - Cenas INDEPENDENTES, sem chain: um chain longo degrada (a câmera sobe, a
    imagem estranha, uma pose ruim se propaga). Cada cena abre na composição de
    um frame de referência do cenário (<Picture 1>), que segura dupla e câmera.
  - Voz de referência por personagem (<Audio 1>, só a de quem fala na cena), e
    a descrição da voz em texto CONCORDANDO com a gravação - "young male voice"
    derrubou o Paçoca uma oitava.
  - Fala visível: "on screen ... mouth visibly opening and closing"; a Pretinha
    nunca afunda atrás do notebook.
  - Duração pela fala: 90/107/124 frames (3,75/4,46/5,17 s). Fala que não cabe
    em 124 é erro - divida em duas cenas.
  - 8 passos com sol_attn start 0.2 / end 1.0: com 4 passos a câmera treme.

Modo vlog (`vlog: pacoca` ou `vlog: pretinha` no roteiro, ou
`./dialogo novo <filme> --vlog pacoca`): um pet sozinho falando para a lente,
como num vídeo-diário. Toda cena vai na câmera `vlog-<pet>` do cenário, com o
pet olhando direto para a câmera. Uma fala do outro pet sai "heard off-screen",
com a voz de referência dele - dá para o outro interromper de fora do quadro.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
EXEMPLO = Path(__file__).resolve().parent / "roteiro-exemplo.yaml"
EXEMPLO_VLOG = Path(__file__).resolve().parent / "roteiro-vlog-exemplo.yaml"

# --------------------------------------------------------------------------
# elenco - os textos canônicos do ELENCO.md
# --------------------------------------------------------------------------

ELENCO = {
    "pretinha": {
        "nome": "Pretinha",
        "quem_e": "the small female French bulldog",
        "aparencia": ("compact and muscular, a short black coat with faint darker brindle striping, a white blaze "
                      "covering the centre of her chest, large upright bat ears set high and wide, round dark brown "
                      "eyes, and a short deeply wrinkled muzzle with a flat black nose. She wears no collar and no "
                      "harness"),
        "fora": "the French bulldog off-screen",
        "voz_ref": "pretinha-voz.wav",
        # ~258 Hz na referência
        "voz": "an adult female voice, low and calm, with precise diction and an unhurried pace, dry and slightly "
               "weary",
        "pron": "her",
        "palavras_por_s": 2.6,
    },
    "pacoca": {
        "nome": "Paçoca",
        "quem_e": "the male pug",
        "aparencia": ("stocky and round, a short fawn-yellow coat, a jet-black mask over his muzzle and around his "
                      "eyes, small black folded ears, large round glossy dark eyes, deep wrinkles on his forehead, "
                      "and a tightly curled tail. He wears no collar and no harness"),
        "fora": "the pug off-screen",
        "voz_ref": "pacoca-voz.wav",
        # ~296 Hz na referência: aguda, de menino. "young male voice" dava ~157 Hz.
        "voz": "a high-pitched, boyish voice, like an excited young boy, bright and slightly nasal, fast, his words "
               "tumbling over each other",
        "pron": "his",
        "palavras_por_s": 3.0,
    },
}
F0_REF = {"pretinha": 258, "pacoca": 296}  # Hz, para o QC de voz

# --------------------------------------------------------------------------
# cenários - cada câmera com seu frame de referência em assets/
#
# Uma câmera diz quem aparece (`visiveis`, na ordem dos <Subject N>; onde cada
# um está em <Picture 1> vai em `onde`), o texto do quadro e a pose de abertura.
# Nos textos, {P}/{C} viram o rótulo da Pretinha/do Paçoca naquele plano e {L}
# o do lugar. Quem não está no plano é citado por descrição ("the pug
# off-screen"), nunca por rótulo - senão o modelo tenta pôr os dois no close.
# --------------------------------------------------------------------------

ESTILO_CASA = ("The target video is photorealistic live-action footage with warm, natural late-afternoon light and "
               "vibrant but natural colours, shot from a locked-off static camera on a heavy tripod: the picture is "
               "perfectly steady for the whole video, with no camera shake, no handheld movement and no drift.")
SOM_CASA = ("Quiet indoor room tone, with faint neighbourhood ambience drifting in through the open window: distant "
            "voices, birdsong and a far-off motorbike. No barking, whining or growling at any point.")


def camera_vlog(quem: str, ref: str, fundo: str, lugar: str | None = None, plano: str | None = None) -> dict:
    """Câmera de vlog: `quem` sozinho, de frente, olhando para a lente.

    `fundo` é o que se vê atrás dele em <Picture 1>, escrito olhando a imagem
    aprovada ("{L}" vira o rótulo do lugar). `lugar`, se o fundo do close for
    só um lado do cenário (ver o terraço). `plano`, se a imagem não for um
    close: o tamanho do pet no quadro, como se vê nela.
    """
    e = ELENCO[quem]
    eu = "{P}" if quem == "pretinha" else "{C}"
    ele = "she" if quem == "pretinha" else "he"
    plano = plano or (f"in a medium close-up of {eu} alone, and it never moves, pans or zooms. {eu} faces the "
                      f"camera straight on and looks directly into the lens, talking to the viewer; {e['pron']} whole "
                      f"face, muzzle and chest are sharp and centred, {e['pron']} head in the upper half of the frame.")
    cam = {
        "ref": ref,
        "visiveis": [quem],
        "onde": {quem: ""},
        "quadro": (
            f"The camera is completely static on a small tripod at {e['pron']} eye level, like a phone set up to "
            f"record a video diary, {plano.format(P='{P}', C='{C}')} Behind {'her' if quem == 'pretinha' else 'him'}, softly out of focus, {fundo}"),
        "abertura": (f"as the shot opens {ele} is framed exactly as in <Picture 1>, facing the lens, "
                     f"{e['pron']} whole face visible, looking straight into the camera."),
    }
    if lugar:
        cam["lugar"] = lugar
    return cam

CENARIOS = {
    "sala": {
        "lugar": ("the dining area shown in <Picture 1>, a modest, traditional Brazilian family home: a worn "
                  "honey-coloured wooden parquet floor laid in a herringbone pattern, walls painted bright turquoise, "
                  "an open green-painted wooden shutter window, a square wooden dining table covered with a white "
                  "crocheted tablecloth, simple wooden chairs, and a blue-painted wooden front door off to the right, "
                  "with warm late-afternoon sunlight falling through the shutters in soft stripes across the floor"),
        "estilo": ESTILO_CASA,
        "som": SOM_CASA,
        "cameras": {
            "dupla": {
                "ref": "cenario-sala.png",
                "visiveis": ["pretinha", "pacoca"],
                "onde": {"pretinha": "on the left", "pacoca": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at table height, facing the table straight on in "
                    "a medium shot, close enough that the dogs fill the upper half of the frame, and it never moves, "
                    "pans or zooms. The near edge of the square wooden dining table with the white crocheted "
                    "tablecloth runs along the bottom of the frame. {P} sits upright on a wooden chair behind the "
                    "table, just left of centre, her head and chest large in the frame, a plain black laptop with a "
                    "matte black lid open on the tablecloth in front of her with its lid facing the camera, so its "
                    "screen is never visible. A second wooden chair stands behind the table just right of centre, "
                    "beside hers. Close behind them, softly out of focus, is the bright turquoise wall of {L} with "
                    "the open green shutter window on the left. {C} stands on the seat of the second wooden chair "
                    "just right of centre, beside her, with his front paws resting on the edge of the table, so his "
                    "head is level with hers. {P} sits up tall the whole time with her chin above the top of the "
                    "laptop lid, so her whole face and mouth stay visible; she never sinks down behind the laptop."),
                "abertura": ("as the shot opens they are posed exactly as in <Picture 1>: she sits upright with her "
                             "chin above the top of the laptop lid and her whole face visible, and he stands on the "
                             "second chair beside her with his front paws on the table."),
            },
        },
    },
    "sofa": {
        "lugar": ("the living room shown in <Picture 1>, in a modest, traditional Brazilian family home: an old, soft "
                  "dark-green fabric sofa with a white crocheted throw draped over its back, a bright turquoise wall, "
                  "a green-painted wooden shutter window on the left letting in warm late-afternoon light, and a "
                  "small wooden side table with a lamp"),
        "estilo": ESTILO_CASA,
        "som": SOM_CASA,
        "cameras": {
            "dupla": {
                "ref": "cenario-sofa.png",
                "visiveis": ["pretinha", "pacoca"],
                "onde": {"pretinha": "on the left", "pacoca": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the sofa seat, straight on, in a "
                    "medium shot, and it never moves, pans or zooms. {P} sits upright on the left half of the green "
                    "sofa seat and {C} sits close beside her on the right half, both seen from their front paws on "
                    "the seat up to the tips of their ears, their heads in the upper half of the frame. The white "
                    "crocheted throw hangs over the sofa back behind them, and behind it, softly out of focus, the "
                    "bright turquoise wall of {L}, the green shutter window on the left and the lamp on the side "
                    "table at the right edge."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>, side by side on the sofa, both "
                             "faces fully visible."),
            },
            "pretinha": {
                "ref": "cenario-sofa-pretinha.png",
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "quadro": (
                    "The camera is completely static on a tripod at her eye level, in a medium close-up of {P} "
                    "alone, and it never moves, pans or zooms. Her head and upper chest fill most of the frame, her "
                    "head in the upper half. The pug sits just out of frame to the right. Behind her, softly out of "
                    "focus, the white crocheted throw on the green sofa, the bright turquoise wall and the green "
                    "shutter window of {L} with warm light."),
                "abertura": ("as the shot opens she is framed exactly as in <Picture 1>, her whole face visible, "
                             "turned slightly towards the right of the frame, where the pug sits out of view."),
            },
            "pacoca": {
                "ref": "cenario-sofa-pacoca.png",
                "visiveis": ["pacoca"],
                "onde": {"pacoca": ""},
                "quadro": (
                    "The camera is completely static on a tripod at his eye level, in a tight close-up of {C} "
                    "alone, and it never moves, pans or zooms. His big round head fills most of the width of the "
                    "frame, in the upper half, with his chest below it. The French bulldog sits just out of frame to the left. Behind him, "
                    "softly out of focus, the green sofa back, the bright turquoise wall of {L} and the wooden side "
                    "table with its lamp in warm light."),
                "abertura": ("as the shot opens he is framed exactly as in <Picture 1>, his whole face visible, "
                             "turned slightly towards the left of the frame, where the French bulldog sits out of "
                             "view."),
            },
        },
    },
    # Os dois de frente um para o outro: conversa, não fala para a câmera.
    # Closes por cima do ombro de quem escuta (desfocado em primeiro plano).
    "sofa-frente": {
        "lugar": ("the living room shown in <Picture 1>, in a modest, traditional Brazilian family home: an old, soft "
                  "dark-green fabric sofa with a white crocheted throw draped over its back, a bright turquoise wall, "
                  "a green-painted wooden shutter window on the left letting in warm late-afternoon light, and a "
                  "small wooden side table with a lamp"),
        "estilo": ESTILO_CASA,
        "som": SOM_CASA,
        "cameras": {
            "dupla": {
                "ref": "cenario-sofafrente.png",
                "visiveis": ["pretinha", "pacoca"],
                "onde": {"pretinha": "on the left", "pacoca": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the sofa seat, straight on, in a "
                    "medium-wide shot, and it never moves, pans or zooms. {P} sits at the left end of the green sofa "
                    "seat, her body and head turned to the right, seen in profile, looking at {C}; {C} sits at the "
                    "right end of the seat, turned to the left, seen in profile, looking back at her, with a stretch "
                    "of sofa between them. Both are seen whole, from their paws on the seat to the tips of their "
                    "ears. Their mouths face each other in profile, so every movement of each mouth stands out "
                    "against the turquoise wall. The white crocheted throw hangs over the sofa back behind them, and "
                    "behind it, softly out of focus, the bright turquoise wall of {L}, the green shutter window on "
                    "the left and the lamp at the right edge."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>, facing each other in profile at "
                             "the two ends of the sofa."),
            },
            "pretinha": {
                "ref": "cenario-sofafrente-pretinha.png",
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the pug's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "right, out of focus, are the pug's fawn back and shoulder and the back of his small black ear, "
                    "turned away from the camera; his face is never seen. {P} sits facing the camera at a "
                    "three-quarter angle, turned towards the pug and looking at him, just to the right of the lens; "
                    "her face, whole muzzle and chest are sharp and fill the left two thirds of the frame. Behind "
                    "her, softly out of focus, the white crocheted throw on the green sofa, the turquoise wall and "
                    "the green shutter window of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the pug's out-of-focus back "
                             "and ear in the lower-right foreground, and her face sharp, turned towards him."),
            },
            "pacoca": {
                "ref": "cenario-sofafrente-pacoca.png",
                "visiveis": ["pacoca"],
                "onde": {"pacoca": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the French bulldog's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "left, out of focus, are the French bulldog's black back and shoulder and the back of her tall "
                    "upright bat ear, turned away from the camera; her face is never seen. {C} sits facing the "
                    "camera at a three-quarter angle, turned towards her and looking at her, just to the left of the "
                    "lens; his face, whole muzzle and chest are sharp and fill the right two thirds of the frame. "
                    "Behind him, softly out of focus, the green sofa back, the turquoise wall of {L} and the wooden "
                    "side table with its lamp."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the French bulldog's "
                             "out-of-focus back and ear in the lower-left foreground, and his face sharp, turned "
                             "towards her."),
            },
        },
    },
    # A laje no pôr do sol. Geografia do campo/contracampo: atrás do Paçoca (e
    # da dupla) a mureta, a caixa d'água, o varal, o morro e o sol; atrás da
    # Pretinha o lado oposto - portinha da escada, vasos, céu já anoitecendo.
    "terraco-frente": {
        "lugar": ("the flat concrete rooftop terrace shown in <Picture 1>, on top of a modest Brazilian house at "
                  "sunset: a rough grey concrete floor, low walls of exposed red bricks, a blue water tank, a "
                  "clothesline with colourful clothes, and a sweeping view of a hillside neighbourhood of "
                  "unplastered red-brick houses under a warm orange and pink sky"),
        "estilo": ("The target video is photorealistic live-action footage at sunset, with warm golden light and "
                   "vibrant but natural colours, shot from a locked-off static camera on a heavy tripod: the "
                   "picture is perfectly steady for the whole video, with no camera shake, no handheld movement "
                   "and no drift."),
        "som": ("Open-air rooftop ambience at dusk: a light breeze, distant neighbourhood sounds - voices, a "
                "radio far away, a motorbike, a dog barking in the distance - and birds settling for the night. "
                "Neither of the two dogs barks, whines or growls at any point."),
        "cameras": {
            "dupla": {
                "ref": "cenario-terraco.png",
                "visiveis": ["pretinha", "pacoca"],
                "onde": {"pretinha": "on the left", "pacoca": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the bench, straight on, in a "
                    "medium-wide shot, and it never moves, pans or zooms. {P} sits at the left end of a low, "
                    "weathered wooden bench, her body and head turned to the right, seen in profile, looking at "
                    "{C}; {C} sits at the right end, turned to the left, seen in profile, looking back at her. "
                    "Both are seen whole. Their mouths face each other in profile, so every movement of each mouth "
                    "stands out against the sky. Behind them, on {L}: the low brick wall, the blue water tank, the "
                    "clothesline on the left, the hillside of brick houses and the sunset sky."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>, facing each other in profile at "
                             "the two ends of the bench."),
            },
            "pretinha": {
                "ref": "cenario-terraco-pretinha.png",
                "lugar": ("the far side of the flat concrete rooftop terrace shown in <Picture 1>, on top of a modest "
                          "Brazilian house at dusk: a rough grey concrete floor, a low wall of exposed red bricks "
                          "with a small green metal door at the top of the stairs, terracotta pots with plants, and "
                          "neighbouring rooftops under a deep blue and violet sky with the first lights coming on. "
                          "There is no water tank and no clothesline on this side"),
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the pug's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "right, out of focus, are the pug's fawn back and shoulder and the back of his small black ear, "
                    "turned away from the camera; his face is never seen. {P} faces the camera at a three-quarter "
                    "angle, turned towards the pug and looking at him, just to the right of the lens; her face, "
                    "whole muzzle and chest are sharp, lit straight on by the warm sunset light. Behind her, softly "
                    "out of focus, the opposite side of {L}: a low brick wall with the small green metal door to the "
                    "stairs, potted plants and neighbouring rooftops under a blue and violet dusk sky."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the pug's out-of-focus back "
                             "and ear in the lower-right foreground, and her face sharp, turned towards him."),
            },
            "pacoca": {
                "ref": "cenario-terraco-pacoca.png",
                "visiveis": ["pacoca"],
                "onde": {"pacoca": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the French bulldog's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "left, out of focus, are the French bulldog's black back and shoulder and the back of her tall "
                    "upright bat ear, turned away from the camera; her face is never seen. {C} faces the camera at "
                    "a three-quarter angle, turned towards her and looking at her, just to the left of the lens; "
                    "his face, whole muzzle and chest are sharp. Behind him, softly out of focus, {L}: the brick "
                    "wall, the blue water tank, the clothesline and the hillside of brick houses under the sunset."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the French bulldog's "
                             "out-of-focus back and ear in the lower-left foreground, and his face sharp, turned "
                             "towards her."),
            },
        },
    },
    # A cozinha: os dois nas duas pontas da mesa, frente a frente. No fundo da
    # dupla, a pia do lado dela e o fogão/geladeira do lado dele - o mesmo que
    # aparece atrás de cada um nos closes.
    "cozinha-frente": {
        "lugar": ("the kitchen shown in <Picture 1>, in a modest, traditional Brazilian family home: pale yellow "
                  "square wall tiles, an old white four-burner gas stove with an aluminium pot, an old white "
                  "refrigerator, a window letting in warm late-afternoon light, and a small table covered with a "
                  "red-and-white checked oilcloth"),
        "estilo": ESTILO_CASA,
        "som": ("Quiet kitchen room tone, the faint hum of an old refrigerator and a soft simmer from the pot on "
                "the stove, with distant neighbourhood voices through the window. No barking, whining or growling "
                "at any point."),
        "cameras": {
            "dupla": {
                "ref": "cenario-cozinhafrente.png",
                "visiveis": ["pretinha", "pacoca"],
                "onde": {"pretinha": "on the left", "pacoca": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at table height, facing the long side of the "
                    "table, in a medium-wide shot, and it never moves, pans or zooms. The table with the "
                    "red-and-white checked oilcloth runs left to right across the frame. {P} sits on a wooden chair "
                    "at the left end of the table, turned to the right, seen in profile, looking at {C}; {C} sits on "
                    "a wooden chair at the right end, turned to the left, seen in profile, looking back at her, the "
                    "whole length of the table between them, as at lunch. Their mouths face each other in profile, "
                    "so every movement of each mouth is clearly visible. On the far wall of {L}, softly out of "
                    "focus: the sink and the shelf of jars on the left behind her, the window in the middle, and "
                    "the stove with its pot and the refrigerator on the right behind him."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>, facing each other in profile at "
                             "the two ends of the table."),
            },
            "pretinha": {
                "ref": "cenario-cozinhafrente-pretinha.png",
                "lugar": ("the sink corner of the kitchen shown in <Picture 1>, in a modest, traditional "
                          "Brazilian family home: pale yellow square wall tiles, a window with warm light, a white "
                          "corner sink with a dish rack full of white plates, a small shelf of jars, and the side of "
                          "the white gas stove with its pot at the edge. There is no door and no refrigerator on "
                          "this side"),
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the pug's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "right, out of focus, are the pug's fawn back and shoulder and the back of his small black ear, "
                    "turned away from the camera; his face is never seen. {P} faces the camera at a three-quarter "
                    "angle, turned towards the pug and looking at him, just to the right of the lens; her face, "
                    "whole muzzle and chest are sharp. Behind her, softly out of focus, {L}: the window, the corner "
                    "sink with its dish rack of white plates, the small shelf of jars, and the side of the stove "
                    "with its pot at the right edge."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the pug's out-of-focus back "
                             "and ear in the lower-right foreground, and her face sharp, turned towards him."),
            },
            "pacoca": {
                "ref": "cenario-cozinhafrente-pacoca.png",
                "visiveis": ["pacoca"],
                "onde": {"pacoca": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the French bulldog's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "left, out of focus, are the French bulldog's black back and shoulder and the back of her tall "
                    "upright bat ear, turned away from the camera; her face is never seen. {C} faces the camera at "
                    "a three-quarter angle, turned towards her and looking at her, just to the left of the lens; "
                    "his face, whole muzzle and chest are sharp. Behind him, softly out of focus, {L}: the stove "
                    "with its aluminium pot, the refrigerator and the yellow tiles."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the French bulldog's "
                             "out-of-focus back and ear in the lower-left foreground, and his face sharp, turned "
                             "towards her."),
            },
        },
    },
    # A varanda da frente, de onde se vê a rua do bairro (movies/cenarios/scripts/frente-varanda.yaml:
    # dupla-b, pretinha-a, pacoca-a). No plano da dupla o Paçoca fica a três quartos, não de perfil puro.
    "varanda-frente": {
        "lugar": ("the narrow front veranda shown in <Picture 1>, of a modest house on a quiet Brazilian street in "
                  "the late afternoon: a terracotta tiled floor, a white wall on the left, a green metal railing "
                  "with potted plants, and beyond it a street of small colourful single-storey houses - pink, "
                  "pale green, white - with utility poles and overhead wires against a pale golden sky"),
        "estilo": ("The target video is photorealistic live-action footage in warm late-afternoon light, with "
                   "vibrant but natural colours, shot from a locked-off static camera on a heavy tripod: the "
                   "picture is perfectly steady for the whole video, with no camera shake, no handheld movement "
                   "and no drift."),
        # Sem moto no som: "a motorbike passing" pôs um motoqueiro na rua ao fundo (direita-nao-e-golpe v1).
        "som": ("Quiet street ambience in the late afternoon: a light breeze, faint distant voices, a radio far "
                "away and birds in the trees. The street behind them stays empty, with no people and no vehicles. "
                "Neither of the two dogs barks, whines or growls at any point."),
        "cameras": {
            "dupla": {
                "ref": "cenario-varandafrente.png",
                "visiveis": ["pretinha", "pacoca"],
                "onde": {"pretinha": "on the left", "pacoca": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod a little above the bench, straight on, in a "
                    "medium-wide shot, and it never moves, pans or zooms. {P} sits on the left half of a low "
                    "wooden bench on the tiled floor, her body and head turned to the right, seen in profile, "
                    "looking at {C}; {C} sits on the right half, turned to the left at a three-quarter angle, "
                    "looking back at her. Both are seen whole. Their mouths face each other, so every movement of "
                    "each mouth is clearly visible. Behind them, on {L}: the white wall on the left, the green "
                    "railing with potted plants, and the street of colourful houses with utility poles and wires."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>, facing each other on the "
                             "bench, she in profile and he at three-quarters."),
            },
            "pretinha": {
                "ref": "cenario-varandafrente-pretinha.png",
                "lugar": ("the end of the front veranda shown in <Picture 1>, of a modest house on a quiet "
                          "Brazilian street in the late afternoon: the corner of a white wall, a large terracotta "
                          "pot with a plant, the green metal railing and, across the street, a pink house with "
                          "white window frames. There are no utility poles on this side"),
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the pug's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "right, out of focus, are the pug's fawn back and shoulder and the back of his small black ear, "
                    "turned away from the camera; his face is never seen. {P} faces the camera at a three-quarter "
                    "angle, turned towards the pug and looking at him, just to the right of the lens; her face, "
                    "whole muzzle and chest are sharp, lit by the warm afternoon light. Behind her, softly out of "
                    "focus, {L}: the white wall, the terracotta pot, the green railing and the pink house across "
                    "the street."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the pug's out-of-focus back "
                             "and ear in the lower-right foreground, and her face sharp, turned towards him."),
            },
            "pacoca": {
                "ref": "cenario-varandafrente-pacoca.png",
                "visiveis": ["pacoca"],
                "onde": {"pacoca": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the French bulldog's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "left, out of focus, are the French bulldog's black back and shoulder and the back of her tall "
                    "upright bat ear, turned away from the camera; her face is never seen. {C} faces the camera at "
                    "a three-quarter angle, turned towards her and looking at her, just to the left of the lens; "
                    "his face, whole muzzle and chest are sharp. Behind him, softly out of focus, {L}: the green "
                    "railing and the street of pink and pale green houses with utility poles and wires under the "
                    "golden sky."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the French bulldog's "
                             "out-of-focus back and ear in the lower-left foreground, and his face sharp, turned "
                             "towards her."),
            },
        },
    },
    # O quartinho do Paçoca: só vlog dele (vlog-quarto-pacoca-c). Rubro-negro
    # pelas cores, sem escudo: marca registrada, e o modelo deforma brasão.
    "quarto-pacoca": {
        "lugar": ("the pug's small bedroom shown in <Picture 1>, in a modest, traditional Brazilian family home: a "
                  "bed with a colourful crocheted patchwork bedspread, a wall painted warm peach-orange, a small "
                  "wooden window with a floral cotton curtain on the left letting in warm late-afternoon light, a "
                  "long knitted scarf in plain red and black stripes hung across the wall, a black-and-white "
                  "football on a low wooden shelf, a round plush dog bed beside the bed, and a yellow rubber "
                  "chicken toy on the bedspread"),
        "estilo": ESTILO_CASA,
        "som": ("Quiet bedroom room tone, with faint neighbourhood ambience drifting in through the window: distant "
                "voices, birdsong and a far-off motorbike. No barking, whining or growling at any point."),
        "cameras": {
            "vlog-pacoca": camera_vlog(
                "pacoca", "cenario-quarto-pacoca.png",
                "{L}: the warm peach-orange wall with the red-and-black striped scarf hung across it, one end "
                "hanging down on the left, the window with its floral curtain at the left edge, the football on the "
                "low shelf and the plush dog bed on the right. The yellow rubber chicken toy lies on the bedspread "
                "in the lower right corner.",
                plano=("in a medium shot of {C} alone, and it never moves, pans or zooms. {C} sits on the colourful "
                       "patchwork bedspread facing the camera straight on and looks directly into the lens, talking "
                       "to the viewer; he is seen whole, from his front paws on the bedspread to the tips of his "
                       "ears, his face sharp and centred just above the middle of the frame.")),
            # Ele já deitado (tio-renato): deitar dentro do vídeo saiu torto.
            "vlog-pacoca-deitado": camera_vlog(
                "pacoca", "cenario-quarto-pacoca-deitado.png",
                "{L}: the warm peach-orange wall with the red-and-black striped scarf hung across it, one end "
                "hanging down on the left, the window with its floral curtain at the left edge, the football on the "
                "low shelf and the plush dog bed on the right. The yellow rubber chicken toy lies on the bedspread "
                "at the right edge.",
                plano=("in a medium shot of {C} alone, and it never moves, pans or zooms. {C} lies on his belly "
                       "on the colourful patchwork bedspread, facing the camera, his front paws stretched forward "
                       "and his chin resting low between them; his face is fully visible and sharp in the middle "
                       "of the frame, his sad round eyes looking up into the lens.")),
        },
    },
}

# Câmeras de vlog dos cenários de diálogo (movies/cenarios/scripts/vlog.yaml,
# edições dos closes aprovados). Quando o fundo é só um lado do cenário, o
# vlog reusa o `lugar` do close daquele lado.
_cams = {n: CENARIOS[n]["cameras"] for n in ("sofa", "cozinha-frente", "terraco-frente", "varanda-frente")}
_cams["sofa"]["vlog-pacoca"] = camera_vlog(
    "pacoca", "cenario-sofa-vlog-pacoca.png",
    "the green sofa back beside him, the bright turquoise wall of {L} and the lamp on the wooden side table at "
    "the upper right.")
_cams["sofa"]["vlog-pretinha"] = camera_vlog(
    "pretinha", "cenario-sofa-vlog-pretinha.png",
    "the white crocheted throw on the green sofa behind her, the bright turquoise wall of {L} and the green "
    "shutter window with warm light at the upper left.")
_cams["cozinha-frente"]["vlog-pacoca"] = camera_vlog(
    "pacoca", "cenario-cozinha-vlog-pacoca.png",
    "the wooden back of the chair he sits on, and in {L} the old white gas stove with its aluminium pot and the "
    "old white refrigerator against the pale yellow tiles.")
_cams["cozinha-frente"]["vlog-pretinha"] = camera_vlog(
    "pretinha", "cenario-cozinha-vlog-pretinha.png",
    "{L}: the window with warm light at the upper left, the corner sink with its dish rack of white plates, the "
    "small shelf with jars and a kettle, and the white gas stove with its pot on the right.",
    lugar=_cams["cozinha-frente"]["pretinha"]["lugar"],
    plano=("in a medium shot of {P} alone, and it never moves, pans or zooms. {P} sits on a wooden chair behind "
           "the table, the red-and-white checked oilcloth running along the bottom of the frame, her head and "
           "chest above the table edge; she faces the camera straight on and looks directly into the lens, "
           "talking to the viewer, her whole face and muzzle sharp and centred."))
_cams["terraco-frente"]["vlog-pacoca"] = camera_vlog(
    "pacoca", "cenario-terraco-vlog-pacoca.png",
    "{L}: the low brick wall, the blue water tank on its concrete base, the clothesline with colourful clothes "
    "on the left, and the hillside of brick houses under the warm sunset sky.",
    plano=("in a medium shot of {C} alone, and it never moves, pans or zooms. {C} sits on the rough concrete "
           "floor facing the camera straight on and looks directly into the lens, talking to the viewer; he is "
           "seen whole, from his front paws to the tips of his ears, his face sharp and centred in the upper "
           "half of the frame."))
_cams["terraco-frente"]["vlog-pretinha"] = camera_vlog(
    "pretinha", "cenario-terraco-vlog-pretinha.png",
    "{L}: the low brick wall with the small green metal door at the top of a few steps, terracotta pots with "
    "plants on the left, and neighbouring rooftops with the first lights coming on under a deep blue and violet "
    "dusk sky.",
    lugar=_cams["terraco-frente"]["pretinha"]["lugar"],
    plano=("in a medium shot of {P} alone, and it never moves, pans or zooms. {P} sits on the rough concrete "
           "floor facing the camera straight on and looks directly into the lens, talking to the viewer; she is "
           "seen whole, from her front paws to the tips of her ears, her face sharp and centred in the upper "
           "half of the frame."))
_cams["varanda-frente"]["vlog-pretinha"] = camera_vlog(
    "pretinha", "cenario-varanda-vlog-pretinha.png",
    "{L}: the white wall on the left, a terracotta pot with a plant, the green metal railing running along the "
    "terracotta tiled floor on the right, and the pink house across the street in the warm afternoon light.",
    lugar=_cams["varanda-frente"]["pretinha"]["lugar"],
    plano=("in a medium shot of {P} alone, and it never moves, pans or zooms. {P} sits on the veranda facing the "
           "camera straight on and looks directly into the lens, talking to the viewer; she is seen from her "
           "chest to the tips of her ears, her face sharp and centred in the upper half of the frame."))
del _cams

FECHO = ("No humans appear at any point, and no text, lettering, watermark, letterboxing or black bars appear "
         "anywhere in the frame.")
FECHO_DUPLA = "Each dog's mouth moves only while that dog speaks. "

# Na grade 17n+5 do modelo; mais longo que 124 nunca foi testado aqui.
FRAMES = (90, 107, 124)
FPS = 24
FOLGA_S = 0.9  # respiro antes/depois da fala

# Grafia -> como a voz deve ler. Só o prompt recebe a forma falada; o
# `legendas` desfaz a troca, e a legenda mostra a grafia certa. "Cleide" saiu
# "Cléidi" (é aberto); o circunflexo pede o ê fechado. "vinte e dois" saiu
# truncado (tio-renato): o roteiro escreve "22", a voz lê "vintedois" e a
# legenda mostra o número da urna.
PRONUNCIA = {"Cleide": "Clêide", "22": "vintedois"}


def pronuncia(texto: str) -> str:
    for escrita, falada in PRONUNCIA.items():
        texto = re.sub(rf"\b{escrita}\b", falada, texto)
    return texto

ENGINE = """\
backend: comfy
comfy:
  url: http://127.0.0.1:8188
  input_dir: /home/erika/Projects/rocm-comfyui/data/input
  output_dir: /home/erika/Projects/rocm-comfyui/data/output
  diffusion_model: minimax_h3_fastvideo_vsa_datafree_1300step_4step_int8_convrot.safetensors
  text_encoder: qwen3vl_32b_minimax_h3_bf16.safetensors
  video_vae: minimax_h3_video_vae_int8_convrot.safetensors
  audio_vae: minimax_h3_audio_vae_fp32.safetensors
  # 8 passos, start 0.2 / end 1.0: com 4 passos e atenção esparsa desde o
  # primeiro passo a câmera treme.
  steps: 8
  ref_image_size: match
  sol_attn:
    mode: vsa
    keep_percent: 20.0
    min_tokens: 4096
    start_percent: 0.2
    end_percent: 1.0
    verbose: true
defaults:
  width: 544
  height: 960
  fps: 24
  video_frames: 107
  seed: {seed}
  style_suffix: ""
continuity:
  anchors: []
  chain_from_previous: false
output:
  container: mp4
  audio: keep
  music: null
"""


class RoteiroError(Exception):
    pass


AVISOS: list[str] = []


class Plano:
    """Uma câmera de um cenário, com os rótulos de quem aparece nela."""

    def __init__(self, cenario: dict, camera: str):
        self.cenario = cenario
        self.cam = cenario["cameras"][camera]
        self.rotulo = {k: f"<Subject {i}>" for i, k in enumerate(self.cam["visiveis"], 1)}
        self.lugar = f"<Subject {len(self.rotulo) + 1}>"

    def texto(self, t: str) -> str:
        """Nomes -> rótulos de quem está no plano; quem está fora vira descrição."""
        for k, e in ELENCO.items():
            alvo = self.rotulo.get(k, e["fora"])
            for nome in {e["nome"], e["nome"].replace("ç", "c")}:
                t = re.sub(rf"\b{nome}\b", alvo, t)
        return t

    def formata(self, t: str) -> str:
        return t.format(P=self.rotulo.get("pretinha", ELENCO["pretinha"]["fora"]),
                        C=self.rotulo.get("pacoca", ELENCO["pacoca"]["fora"]), L=self.lugar)


def palavras(fala: str) -> int:
    return len(re.findall(r"[\wÀ-ÿ]+", fala))


def duracao(cena: dict) -> int:
    if "frames" in cena:
        return int(cena["frames"])
    fala = cena.get("fala")
    if not fala:
        return FRAMES[0]
    quem = ELENCO[fala["quem"]]
    precisa = (palavras(fala["texto"]) / quem["palavras_por_s"] + FOLGA_S) * FPS
    for f in FRAMES:
        if precisa <= f:
            return f
    raise RoteiroError(
        f"cena '{cena['id']}': {palavras(fala['texto'])} palavras não cabem em {FRAMES[-1]} frames "
        f"({FRAMES[-1] / FPS:.2f} s) - divida a fala em duas cenas.")


def camera_da_cena(cena: dict, cenario: dict, vlog: str | None = None) -> str:
    """A pedida; no vlog, a do vlogueiro; senão o close de quem fala, se o
    cenário tiver; senão a dupla."""
    if cena.get("camera"):
        return cena["camera"]
    if vlog:
        return f"vlog-{vlog}"
    fala = cena.get("fala")
    if fala and fala["quem"] in cenario["cameras"]:
        return fala["quem"]
    return "dupla"


def frase_da_fala(fala: dict, plano: Plano) -> str:
    quem = ELENCO[fala["quem"]]
    texto = fala["texto"].strip()
    if texto[-1] not in ".?!,:":
        texto += "."
    if fala["quem"] in plano.rotulo:
        falante = (f"{plano.rotulo[fala['quem']]} (S1), on screen, in the voice referenced from <Audio 1> "
                   f"({quem['voz']}), {quem['pron']} mouth visibly opening and closing in sync with every syllable,")
    else:
        falante = f"{quem['fora'].capitalize()} (S1), heard off-screen in the voice referenced from <Audio 1> ({quem['voz']}),"
    frase = f"{falante} says: <d>[Portuguese] {pronuncia(texto)}</d>"
    outros = [k for k in plano.rotulo if k != fala["quem"]]
    for k in outros:
        frase += f" {plano.rotulo[k]} keeps {ELENCO[k]['pron']} mouth closed."
    return frase


def prompt(cena: dict, cenario: dict) -> str:
    plano = Plano(cenario, camera_da_cena(cena, cenario))
    cam = plano.cam
    fala = cena.get("fala")
    defs = [f"{plano.rotulo[k]} is {ELENCO[k]['nome']}, {ELENCO[k]['quem_e']}"
            f"{(' ' + cam['onde'][k]) if cam['onde'][k] else ''} in <Picture 1>: {ELENCO[k]['aparencia']}."
            for k in cam["visiveis"]]
    # Uma câmera pode ter o próprio "lugar": no close do contracampo, o lugar do
    # cenário citaria o que está atrás do OUTRO (a caixa d'água, o fogão) e o
    # modelo põe de volta, por cima da referência.
    defs.append(f"{plano.lugar} is {cam.get('lugar', cenario['lugar'])}.")
    prefixo = "[reference generation]"
    ret_voz = []
    if fala:
        quem = ELENCO[fala["quem"]]
        alvo = plano.rotulo.get(fala["quem"], quem["fora"])
        defs.append(f"<Audio 1> is the voice-timbre reference for {alvo}.")
        prefixo = "[reference generation + audio reference]"
        ret_voz = [f"<Audio 1>: reference - {alvo}'s voice follows the timbre, pitch and delivery of <Audio 1> "
                   "without copying the original signal or its words."]
    visiveis = " and ".join(plano.rotulo.values())
    um = len(plano.rotulo) == 1
    acao = " ".join(p for p in (
        plano.texto(cena.get("antes", "")).strip(),
        frase_da_fala(fala, plano) if fala else ("Nobody speaks." if um else "Neither dog speaks."),
        plano.texto(cena.get("depois", "")).strip(),
    ) if p)
    quem_ret = (f"{visiveis} (appears in [Shot 1]): fully_preserved - the same dog as in <Picture 1>" if um else
                f"{visiveis} (appear in [Shot 1]): fully_preserved - the same two dogs as in <Picture 1>")
    return "\n".join([
        "subject_definitions:", *defs,
        "summary:",
        f"{prefixo} {plano.texto(cena.get('resumo', '')).strip()} <Picture 1> supplies "
        f"{'the dog' if um else 'the two dogs'}, the room and the framing.",
        "retention_analysis:",
        f"{quem_ret}, unchanged from the first frame to the last; {cam['abertura']}",
        f"{plano.lugar} (appears in [Shot 1]): fully_preserved - the room, the furniture and the light stay exactly "
        "as they are, and the camera framing does not change.",
        "<Picture 1> (composition and subject reference for [Shot 1]): fully_preserved - the shot opens on exactly "
        f"this composition: the same camera position, framing and scale, the same furniture, and "
        f"{'the dog' if um else 'both dogs'} in the same place and at the same size. The framing never widens, "
        "tilts or drifts.",
        *ret_voz,
        "detailed_description:",
        cenario["estilo"],
        f"[Shot 1] The shot opens on the composition of <Picture 1>. {plano.formata(cam['quadro'])} {acao} "
        f"{'' if um else FECHO_DUPLA}{FECHO}",
        f"overall_soundscape: {cenario['som']}",
        "non_diegetic_music: N/A",
    ])


def carregar(filme: str, cenario: str | None = None) -> tuple[Path, dict]:
    pasta = ROOT / "movies" / filme
    arq = pasta / "roteiro.yaml"
    if not arq.is_file():
        raise RoteiroError(f"{arq} não existe - comece com ./dialogo novo {filme}")
    rot = yaml.safe_load(arq.read_text()) or {}
    if cenario:
        rot["cenario"] = cenario
    cenas = rot.get("cenas") or []
    if not cenas:
        raise RoteiroError("roteiro sem cenas")
    vistos = set()
    for i, c in enumerate(cenas, 1):
        if not c.get("id"):
            raise RoteiroError(f"cena {i}: falta 'id'")
        if c["id"] in vistos:
            raise RoteiroError(f"id repetido: {c['id']}")
        vistos.add(c["id"])
        f = c.get("fala")
        if f and (f.get("quem") not in ELENCO or not f.get("texto")):
            raise RoteiroError(f"cena '{c['id']}': fala precisa de quem ({'/'.join(ELENCO)}) e texto")
        c["frames"] = duracao(c)
    nome = rot.get("cenario", "sala")
    if nome not in CENARIOS:
        raise RoteiroError(f"cenário desconhecido: {nome} (há: {', '.join(CENARIOS)})")
    vlog = rot.get("vlog")
    if vlog and vlog not in ELENCO:
        raise RoteiroError(f"vlog: {vlog}? (é {' ou '.join(ELENCO)})")
    cams = CENARIOS[nome]["cameras"]
    for c in cenas:
        cam = camera_da_cena(c, CENARIOS[nome], vlog)
        if cam not in cams:
            com_vlog = [n for n, ce in CENARIOS.items() if cam in ce["cameras"]]
            raise RoteiroError(f"cena '{c['id']}': o cenário {nome} não tem a câmera {cam} "
                               f"(tem: {', '.join(cams)})"
                               + (f" - cenários com {cam}: {', '.join(com_vlog)}" if com_vlog else ""))
        c["camera"] = cam
        ref = cams[cam]["ref"]
        if not (ROOT / "assets" / ref).is_file():
            AVISOS.append(f"câmera {cam}: falta assets/{ref} (frame de referência ainda não aprovado)")
        visiveis = CENARIOS[nome]["cameras"][cam]["visiveis"]
        for k, e in ELENCO.items():
            if k in visiveis:
                continue
            for campo in ("antes", "depois"):
                # Só quando ele é o SUJEITO de uma frase ("Paçoca's ears droop"): ser
                # para onde o outro olha ("looks at Paçoca") é legítimo.
                nomes = f"{e['nome']}|{e['nome'].replace('ç', 'c')}"
                if re.search(rf"(^|[.!?]\s+)({nomes})\b", c.get(campo, "").strip()):
                    AVISOS.append(f"cena '{c['id']}': em '{campo}', {e['nome']} faz algo, mas está fora do "
                                  f"plano ({cam}) - o modelo não pode mostrar isso e tende a pôr os dois no quadro")
    return pasta, rot


def gerar(filme: str, versao: str, cenario: str | None = None) -> Path:
    pasta, rot = carregar(filme, cenario)
    cenario = CENARIOS[rot.get("cenario", "sala")]
    nome = rot.get("nome") or (filme if versao == "v1" else f"{filme}-{versao}")
    partes = [
        f"# {filme} {versao} - GERADO por tools/dialogo.py a partir de movies/{filme}/roteiro.yaml.\n"
        f"# Não edite à mão: mude o roteiro (ou a receita em tools/dialogo.py) e rode\n"
        f"#   ./dialogo gerar {filme}{'' if versao == 'v1' else ' --versao ' + versao}\n"
        f"# Cada cena é independente: dá para refazer uma só com --only N.\n",
        f"name: {nome}\n",
        ENGINE.format(seed=int(rot.get("seed", 2026))),
        "scenes:\n",
    ]
    for c in rot["cenas"]:
        partes.append(f"  - id: {c['id']}\n")
        if c["frames"] != 107:
            partes.append(f"    video_frames: {c['frames']}\n")
        if "seed" in c:
            partes.append(f"    seed: {int(c['seed'])}\n")
        partes.append(f"    ref_images: [{cenario['cameras'][c['camera']]['ref']}]\n")
        if c.get("fala"):
            partes.append(f"    ref_audios: [{ELENCO[c['fala']['quem']]['voz_ref']}]\n")
        partes.append("    prompt: |-\n")
        partes.extend(f"      {linha}\n" for linha in prompt(c, cenario).split("\n"))
    destino = pasta / "scripts" / f"{versao}.yaml"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("".join(partes))
    return destino


def tabela(filme: str, cenario: str | None = None) -> None:
    _, rot = carregar(filme, cenario)
    total = 0
    print(f"{'#':>3}  {'cena':16} {'câmera':13} {'quem':9} {'pal':>3} {'dur':>6}  fala")
    for i, c in enumerate(rot["cenas"], 1):
        f = c.get("fala") or {}
        total += c["frames"]
        print(f"{i:>3}  {c['id']:16} {c['camera']:13} {f.get('quem', '-'):9} {palavras(f.get('texto', '')):>3} "
              f"{c['frames'] / FPS:5.2f}s  {f.get('texto', '')[:55]}")
    print(f"     total {total / FPS:.1f} s em {len(rot['cenas'])} cenas")
    for aviso in dict.fromkeys(AVISOS):
        print(f"aviso: {aviso}")


def novo(filme: str, vlog: str | None = None) -> None:
    pasta = ROOT / "movies" / filme
    if pasta.exists():
        raise RoteiroError(f"{pasta} já existe")
    if vlog and vlog not in ELENCO:
        raise RoteiroError(f"--vlog {vlog}? (é {' ou '.join(ELENCO)})")
    subprocess.run([str(ROOT / "mm"), "new", filme, "--template", "none"], check=True)
    if vlog:
        # O exemplo é do Paçoca no quarto dele; para a Pretinha, troque o pet e
        # ponha um cenário que tenha a câmera vlog-pretinha.
        texto = EXEMPLO_VLOG.read_text()
        if vlog == "pretinha":
            texto = texto.replace("vlog: pacoca", "vlog: pretinha").replace("cenario: quarto-pacoca", "cenario: sofa")
        (pasta / "roteiro.yaml").write_text(texto)
    else:
        shutil.copyfile(EXEMPLO, pasta / "roteiro.yaml")
    print(f"roteiro: {pasta / 'roteiro.yaml'}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("novo")
    n.add_argument("filme")
    n.add_argument("--vlog", help="pacoca | pretinha: um pet sozinho falando para a câmera")
    g = sub.add_parser("gerar")
    g.add_argument("filme")
    g.add_argument("--versao", default="v1")
    g.add_argument("--cenario", help="outro cenário para este roteiro (ex.: uma v2 em outro lugar)")
    c = sub.add_parser("cenas")
    c.add_argument("filme")
    c.add_argument("--cenario")
    args = ap.parse_args()
    try:
        if args.cmd == "novo":
            novo(args.filme, args.vlog)
        elif args.cmd == "gerar":
            print(gerar(args.filme, args.versao, args.cenario))
            tabela(args.filme, args.cenario)
        else:
            tabela(args.filme, args.cenario)
    except RoteiroError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
