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
        # Era "dry and slightly weary": saía séria demais, brava até no "Tô!"
        # feliz (corrida-6x1). Mantém "low" - o texto tem que bater com a referência.
        "voz": "an adult female voice, low and warm, with precise diction and an unhurried pace, firm but "
               "friendly",
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
    # O primo José (terras-raras). A voz de referência sai recortada da primeira
    # cena boa dele: enquanto assets/jose-voz.wav não existe, as falas dele vão
    # sem <Audio 1> e o modelo inventa a voz pela descrição.
    "jose": {
        "nome": "José",
        "quem_e": "the male caramel mixed-breed dog",
        "aparencia": ("a male Brazilian caramelo mixed-breed dog (vira-lata caramelo): medium-sized and lean, a short "
                      "smooth caramel-golden coat, slightly paler cream fur on his muzzle, throat and chest, medium "
                      "triangular ears that stand up at the base and fold forward at the tips, warm amber-brown eyes, "
                      "a longish muzzle with a black nose, and a long tail that curves up in a loose sickle. He wears "
                      "no collar and no harness"),
        "fora": "the caramel dog off-screen",
        "voz_ref": "jose-voz.wav",
        # ~134 Hz na referência (terras-raras v1 cena 2, aprovada).
        "voz": ("a young adult male voice, a guy of about twenty-three, light and warm, relaxed and friendly, "
                "clear, at a steady explaining pace"),
        "pron": "his",
        "palavras_por_s": 2.8,
    },
    # Seu Tião, o motorista de aplicativo (cenário uber). Ficha em
    # movies/ficha-tiao/ (par A). Voz recortada da cena 3 do corrida-6x1 v1
    # (aprovada pela Erika).
    "tiao": {
        "nome": "Tião",
        "quem_e": "the male white dog with black patches",
        "aparencia": ("a male Brazilian mixed-breed dog (vira-lata malhado): medium-sized and sturdy, a short white "
                      "coat with large irregular black patches - one black patch covering his left ear and the area "
                      "around his left eye, and a large black patch across his back - tan-brown markings on his "
                      "cheeks and above his eyes, a greying muzzle with white hairs around the mouth, semi-floppy "
                      "ears that stand up at the base and fold over halfway, kind, slightly tired brown eyes, a "
                      "medium-length muzzle with a black nose, and a long tail. He wears no collar and no harness"),
        "fora": "the driver dog off-screen",
        "voz_ref": "tiao-voz.wav",
        # ~167 Hz na referência.
        "voz": ("a middle-aged male voice, a man of about fifty, deep and slightly hoarse, relaxed and unhurried, "
                "plain-spoken, a little tired but friendly"),
        "pron": "his",
        "palavras_por_s": 2.6,
    },
    # As senhoras do supermercado (secao-mudou), vizinhas da Pretinha. Ficha em
    # movies/ficha-senhoras/. Sem voz de referência até a primeira cena boa de
    # cada uma: aí a voz sai recortada dela, como a do José.
    "cida": {
        "nome": "Cida",
        "quem_e": "the elderly female poodle",
        "aparencia": ("small and slender, a soft curly coat of off-white fur gone slightly "
                      "creamy with age, a greying muzzle, long curly ears hanging down beside her face, gentle dark "
                      "brown eyes a little cloudy with age, a narrow muzzle with a black nose. She wears a plain "
                      "lilac hand-knitted cardigan with no pattern, buttoned at the chest, her front legs through the "
                      "sleeves, and no collar"),
        "fora": "the old poodle off-screen",
        "voz_ref": "cida-voz.wav",
        # ~258 Hz na referência (secao-mudou v1 cena 1, aprovada).
        "voz": ("an elderly female voice, a woman of about seventy-five, thin and slightly quavering, sweet and "
                "chatty, a little breathless"),
        "pron": "her",
        "palavras_por_s": 2.4,
    },
    "lurdes": {
        "nome": "Lurdes",
        "quem_e": "the elderly female cocker spaniel",
        "aparencia": ("medium-sized and plump, a wavy golden-red coat, a muzzle and "
                      "eyebrows gone white with age, long silky wavy ears hanging below her jaw, warm, slightly "
                      "droopy brown eyes, a broad muzzle with a brown nose. She wears a plain sea-green "
                      "hand-knitted cardigan with no pattern, buttoned at the chest, her front legs through the "
                      "sleeves, and no collar"),
        "fora": "the old spaniel off-screen",
        "voz_ref": "lurdes-voz.wav",
        # ~143 Hz na referência (secao-mudou v1 cena 5, aprovada de ouvido).
        "voz": ("an elderly female voice, a woman of about seventy, low and a little husky, warm and motherly, at an "
                "unhurried pace"),
        "pron": "her",
        "palavras_por_s": 2.4,
    },
    # Tio Renato, o tio do Paçoca que votava 22 (tio-renato-muda). Buldogue
    # inglês, escolha da Erika. Ficha em movies/ficha-renato/. A voz_ref sai
    # recortada da primeira cena boa dele, como a do José e a do Tião.
    "renato": {
        "nome": "Renato",
        "quem_e": "the male English bulldog",
        "aparencia": ("a male English bulldog of about sixty: heavy and low-set, with a broad deep chest and thick "
                      "shoulders, a short smooth white coat with large fawn-brindle patches over both ears, around "
                      "his eyes and across his back, a massive wrinkled head with deep folds over a short pushed-in "
                      "muzzle, heavy drooping jowls, a slight underbite with two lower teeth just showing, small "
                      "rose ears folded back, dark, serious eyes under a heavy brow, a greying muzzle with white "
                      "hairs around the mouth, and a short tail. He wears no collar and no harness"),
        "fora": "the old bulldog off-screen",
        "voz_ref": "renato-voz.wav",
        # A voz da v1 (~93 Hz, grave e solene) ficou "sorumbática" (Erika,
        # 22/10): guardada no pacote tio-renato-muda (ARQUIVO.md), em assets/renato-voz-v1-solene.wav.
        # 1ª tentativa leve (v2a, ~108 Hz) ainda soou igual à solene: o modelo
        # puxa "buldogue de 65 anos, rouco" para o grave. Agora o tom é dito com
        # todas as letras (tenor, agudo, fino), sem "deep" nem "raspy": ~186 Hz na
        # referência (v2, cena 2, 0-4,4 s), aprovada de ouvido pela Erika.
        "voz": ("a light, rather high-pitched elderly man's voice in the tenor range, thin, bright and a little "
                "nasal, with a slight old-age creak, quick and chatty like a cheerful grandpa telling a story at the "
                "bakery, playful and teasing, never deep, never booming, never solemn"),
        "pron": "his",
        "palavras_por_s": 2.6,  # v2: voz mais leve e conversadora
    },
}
F0_REF = {"pretinha": 258, "pacoca": 296, "jose": 134, "tiao": 167, "cida": 258, "lurdes": 143}  # Hz, para o QC de voz
# Rótulo de cada um nos textos de câmera: {P}, {C}, {J}, {T}.
MARCA = {"pretinha": "P", "pacoca": "C", "jose": "J", "tiao": "T", "cida": "I", "lurdes": "U", "renato": "R"}


def ele(quem: str) -> str:
    return "she" if ELENCO[quem]["pron"] == "her" else "he"


def o(quem: str) -> str:
    return "her" if ELENCO[quem]["pron"] == "her" else "him"


def tem_voz(quem: str) -> bool:
    if quem == CORO:
        return False
    return (ROOT / "assets" / ELENCO[quem]["voz_ref"]).is_file()


# `quem: todos` - todos os que estão no quadro falam juntos, em coro (o fecho do
# todos-perdem). Sem voz de referência: o node aceita no máximo 3 áudios.
CORO = "todos"

# --------------------------------------------------------------------------
# cenários - cada câmera com seu frame de referência em assets/
#
# Uma câmera diz quem aparece (`visiveis`, na ordem dos <Subject N>; onde cada
# um está em <Picture 1> vai em `onde`), o texto do quadro e a pose de abertura.
# Nos textos, {P}/{C}/{J}/{T}/{I}/{U} viram o rótulo da Pretinha/do Paçoca/do José/do Tião/da Cida/da Lurdes naquele
# plano e {L} o do lugar. `figurino` (opcional, por cenário) veste alguém só
# ali: entra depois da aparência canônica. Quem não está no plano é citado por descrição ("the pug
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
    eu = "{" + MARCA[quem] + "}"
    plano = plano or (f"in a medium close-up of {eu} alone, and it never moves, pans or zooms. {eu} faces the "
                      f"camera straight on and looks directly into the lens, talking to the viewer; {e['pron']} whole "
                      f"face, muzzle and chest are sharp and centred, {e['pron']} head in the upper half of the frame.")
    cam = {
        "ref": ref,
        "visiveis": [quem],
        "onde": {quem: ""},
        "quadro": (
            f"The camera is completely static on a small tripod at {e['pron']} eye level, like a phone set up to "
            f"record a video diary, {plano.format(**{m: "{" + m + "}" for m in MARCA.values()})} Behind {o(quem)}, softly out of focus, "
            f"{fundo}"),
        "abertura": (f"as the shot opens {ele(quem)} is framed exactly as in <Picture 1>, facing the lens, "
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
    # O boteco da esquina, depois da pelada: Paçoca e o primo José (terras-raras).
    # Primeiro cenário externo. Frames em movies/cenarios/scripts/lanchonete.yaml
    # (dupla = vertical-b, closes jose-a / pacoca-a). Os dois de camiseta do time.
    # Sem carro nem moto no `som`: o modelo desenha o que ouve.
    "lanchonete": {
        "lugar": ("the street corner outside the small Brazilian corner snack bar (a boteco) shown in <Picture 1>: a "
                  "red plastic table and red plastic chairs on the grey concrete pavement, the open front of the "
                  "snack bar with a raised green metal roll-up door, white wall tiles with a band of blue tiles, a "
                  "glass display case of golden fried snacks on the counter inside, and a weathered pale wall, all "
                  "in warm late-afternoon light"),
        "estilo": ("The target video is photorealistic live-action footage, outdoors on a street corner in warm, "
                   "golden late-afternoon light with soft long shadows and vibrant but natural colours, shot from a "
                   "locked-off static camera on a heavy tripod: the picture is perfectly steady for the whole video, "
                   "with no camera shake, no handheld movement and no drift."),
        "som": ("Calm street-corner ambience on a quiet afternoon: distant voices from down the street, birdsong, and "
                "now and then the soft clink of a glass bottle from the snack bar counter. No barking, whining or "
                "growling at any point."),
        "figurino": {
            "pacoca": ("Here he wears a short-sleeved football shirt of an amateur neighbourhood team, green with "
                       "white vertical stripes, plain, with no crest, no number and no lettering, his front legs "
                       "through the sleeves."),
            "jose": ("Here he wears the same short-sleeved football shirt of the amateur neighbourhood team, green "
                     "with white vertical stripes, plain, with no crest, no number and no lettering, his front legs "
                     "through the sleeves."),
        },
        "cameras": {
            "dupla": {
                "ref": "cenario-lanchonete.png",
                "visiveis": ["pacoca", "jose"],
                "onde": {"pacoca": "on the left", "jose": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the table top, straight on, in a "
                    "medium-wide shot, and it never moves, pans or zooms. {C} sits up on the seat of a red plastic "
                    "chair on the left, turned to the right in a three-quarter profile, looking at {J}; {J} sits up "
                    "on the seat of a red plastic chair on the right, turned to the left in a three-quarter profile, "
                    "looking back at him. Between them stands the red plastic table with a plate of two golden "
                    "coxinhas and two glass bottles of dark soft drink with no labels, and a black-and-white football "
                    "rests on the pavement by the pug's chair. Both are seen whole, from their paws on the chair "
                    "seats to the tips of their ears, their faces and mouths clearly visible. Behind them, softly "
                    "out of focus, the open front of {L} under the raised green roll-up door, the counter with the "
                    "display case of fried snacks and the white tiles with the blue band."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>, on the two red chairs on either "
                             "side of the table, turned towards each other."),
            },
            "jose": {
                "ref": "cenario-lanchonete-jose.png",
                "visiveis": ["jose"],
                "onde": {"jose": ""},
                "lugar": ("the street corner outside the small Brazilian corner snack bar shown in <Picture 1>: the "
                          "raised green metal roll-up door, the white wall tiles with a band of blue tiles at the side "
                          "of the opening and a weathered pale wall, in warm late-afternoon light"),
                "quadro": (
                    "The camera is completely static on a tripod just behind the pug's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "left, out of focus, are the pug's fawn back in the green-and-white striped shirt and the back of "
                    "his small black folded ear, turned away from the camera; his face is never seen. {J} sits "
                    "facing the camera at a three-quarter angle, turned towards the pug and looking at him, just to "
                    "the left of the lens; his face, whole muzzle and chest in the striped shirt are sharp and fill "
                    "the right two thirds of the frame. Behind him, softly out of focus, the raised green roll-up "
                    "door, the white tiles with the blue band and the weathered wall of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the pug's out-of-focus back "
                             "and ear in the lower-left foreground, and his face sharp, turned towards the pug."),
            },
            "pacoca": {
                "ref": "cenario-lanchonete-pacoca.png",
                "visiveis": ["pacoca"],
                "onde": {"pacoca": ""},
                "lugar": ("the open front of the small Brazilian corner snack bar shown in <Picture 1>: the counter "
                          "with a glass display case of golden fried snacks, white wall tiles with a band of blue "
                          "tiles and the green frame of the roll-up door, in warm late-afternoon light"),
                "quadro": (
                    "The camera is completely static on a tripod just behind the caramel dog's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "right, out of focus, are the caramel dog's back in the green-and-white striped shirt and the "
                    "back of his folded ear, turned away from the camera; his face is never seen. {C} sits facing "
                    "the camera at a three-quarter angle, turned towards the caramel dog and looking up at him, just "
                    "to the right of the lens; his face, whole muzzle and chest in the striped shirt are sharp and "
                    "fill the left two thirds of the frame. Behind him, softly out of focus, the display case of "
                    "fried snacks on the counter and the white tiles with the blue band of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the caramel dog's "
                             "out-of-focus back and ear in the lower-right foreground, and his face sharp, turned "
                             "towards him."),
            },
        },
    },
    # A barraca de pastel da feira de manhã cedo, ainda vazia: Paçoca e o primo
    # José (pix-ameaca, refeito fora da lanchonete). Frames em
    # movies/cenarios/scripts/feira-vazia.yaml (vazia-a) e feira-closes.yaml.
    # Camiseta lisa (sem a do time das terras raras). Rua vazia de propósito:
    # com cachorros fazendo papel de gente, todos encaravam a câmera.
    "feira": {
        "lugar": ("the pastel stall of the Brazilian street market shown in <Picture 1>, very early in the morning "
                  "before any shoppers arrive: a weathered wooden counter with two golden pastéis on paper napkins "
                  "and two plastic cups of orange juice, a big frying pan behind them, a striped yellow-and-blue "
                  "awning overhead, and an empty street between the stalls with crates of fruit and vegetables under "
                  "coloured awnings, in soft early sunlight with long shadows"),
        "estilo": ("The target video is photorealistic live-action footage, outdoors at a street market early in "
                   "the morning, in soft early sunlight with long shadows and vibrant but natural colours, shot from "
                   "a locked-off static camera on a heavy tripod: the picture is perfectly steady for the whole "
                   "video, with no camera shake, no handheld movement and no drift."),
        # Sem "vozes" nem "feirantes": o modelo desenha o que ouve.
        "som": ("Quiet early-morning street market ambience: birdsong, the soft rustle of the awnings in a light "
                "breeze and the faint sizzle of oil in the frying pan. The street stays empty. No music, no voices "
                "other than the dogs', and no barking, whining or growling at any point."),
        "figurino": {
            "pacoca": ("Here he wears a plain mustard-yellow short-sleeved t-shirt with no print, no logo and no "
                       "lettering, his front legs through the sleeves."),
            "jose": ("Here he wears a plain red short-sleeved t-shirt with no print, no logo and no lettering, his "
                     "front legs through the sleeves."),
        },
        "cameras": {
            "dupla": {
                "ref": "cenario-feira.png",
                "visiveis": ["pacoca", "jose"],
                "onde": {"pacoca": "on the left", "jose": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the counter, straight on, in a "
                    "medium shot, and it never moves, pans or zooms. {C} sits up on a low wooden stool on the left, "
                    "turned to the right in a three-quarter profile, looking at {J}; {J} sits up on a low wooden "
                    "stool on the right, turned to the left in a three-quarter profile, looking back at him. Between "
                    "them, on the wooden counter, are two golden pastéis on paper napkins and two plastic cups of "
                    "orange juice, with the big frying pan behind. Both are seen from their paws on the stools to "
                    "the tips of their ears, their faces and mouths clearly visible. Above them hangs the striped "
                    "yellow-and-blue awning, and behind them, softly out of focus, the empty street of {L}."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>, on the two wooden stools on "
                             "either side of the counter, turned towards each other."),
            },
            "jose": {
                "ref": "cenario-feira-jose.png",
                "visiveis": ["jose"],
                "onde": {"jose": ""},
                "lugar": ("the pastel stall of the Brazilian street market shown in <Picture 1>, very early in the "
                          "morning: a wooden counter and the stall's wooden wall, and the empty street between the "
                          "stalls with coloured awnings, in soft early sunlight"),
                "quadro": (
                    "The camera is completely static on a tripod just behind the pug's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "left, out of focus, are the pug's fawn shoulder in the mustard-yellow t-shirt and the back of "
                    "his small black folded ear, turned away from the camera; his face is never seen. {J} sits "
                    "facing the camera at a three-quarter angle, turned towards the pug and looking at him, just to "
                    "the left of the lens; his face, whole muzzle and chest in the red t-shirt are sharp and fill "
                    "the right two thirds of the frame. Behind him, softly out of focus, the wooden counter and the "
                    "green-and-blue awnings of {L}, with the street empty."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the pug's out-of-focus "
                             "yellow shoulder and ear in the lower-left foreground, and his face sharp, turned "
                             "towards the pug."),
            },
            # pacoca-a da feira-closes: no frame ele olha quase para a lente; o
            # quadro pede o olhar no José, à direita.
            "pacoca": {
                "ref": "cenario-feira-pacoca.png",
                "visiveis": ["pacoca"],
                "onde": {"pacoca": ""},
                "lugar": ("the pastel stall of the Brazilian street market shown in <Picture 1>, very early in the "
                          "morning: the wooden counter with a cup of orange juice and a pastel, and the empty street "
                          "between the stalls with crates of fruit under coloured awnings, in soft early sunlight"),
                "quadro": (
                    "The camera is completely static on a tripod just behind the caramel dog's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "right, out of focus, are the caramel dog's shoulder in the red t-shirt and the back of his "
                    "folded ear, turned away from the camera; his face is never seen. {C} sits up on his wooden "
                    "stool facing the camera at a three-quarter angle, his head turned to the right of the frame "
                    "and tilted up towards the caramel dog, looking at him and never into the lens; his face, whole "
                    "muzzle and chest in the mustard-yellow t-shirt are sharp and fill the left two thirds of the "
                    "frame. Behind him, softly out of focus, the striped yellow-and-blue awning and the empty street "
                    "of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the caramel dog's "
                             "out-of-focus red shoulder and ear in the lower-right foreground, and the pug sharp on "
                             "his stool."),
            },
        },
    },
    # A lotérica no dia do pagamento: a Pretinha e as vizinhas, Dona Cida e Dona
    # Lurdes, na fileira de cadeiras de espera (aposentadoria-subiu, refeito
    # fora do supermercado). Frames em movies/cenarios/scripts/loterica-4.yaml
    # (cadeira-a) e loterica-closes.yaml. Os três sentados na mesma altura: com
    # a Pretinha no chão os olhares não se encontravam. Pretinha de vermelho.
    "loterica": {
        # Sem "casa lotérica" no texto: o modelo escreveu "lotérica" num
        # letreiro, e pôs gente atrás dos guichês (aposentadoria-subiu v2).
        "lugar": ("the small, busy Brazilian bill-payment shop shown in <Picture 1>: a long counter of service "
                  "windows with thick glass panels and round metal speaking grilles in bright blue and orange, with "
                  "nobody behind the glass, a plain blue and orange wall above them with no sign, no logo and no "
                  "writing, a row of beige moulded plastic waiting chairs, pale floor tiles, a fan on the wall and "
                  "a short queue of dogs waiting at the windows, under bright white ceiling lights"),
        "estilo": ("The target video is photorealistic live-action footage inside a lottery shop in the morning, in "
                   "bright, even white overhead light and vibrant but natural colours, shot from a locked-off static "
                   "camera on a low tripod: the picture is perfectly steady for the whole video, with no camera "
                   "shake, no handheld movement and no drift."),
        # Sem "vozes" nem "fila conversando": o modelo poria gente no fundo.
        "som": ("Soft indoor ambience of a small shop: the steady whir of the wall fan, the faint hum of the "
                "ceiling lights and now and then the soft thud of a rubber stamp at a service window. No music, no "
                "announcements, no voices other than the three dogs', and no barking, whining or growling at any "
                "point."),
        "figurino": {
            "pretinha": ("Here she wears a plain red short-sleeved t-shirt with no print, no logo and no lettering, "
                         "her front legs through the sleeves."),
        },
        "cameras": {
            "dupla": {
                "ref": "cenario-loterica.png",
                "visiveis": ["pretinha", "cida", "lurdes"],
                "onde": {"pretinha": "on the left", "cida": "in the middle", "lurdes": "on the right"},
                "quadro": (
                    "The camera is completely static on a low tripod at the height of the dogs' heads, in a medium "
                    "shot, and it never moves, pans or zooms. The three sit in a row on the beige plastic waiting "
                    "chairs, their heads level with each other: {P} on the left, turned to the right in a "
                    "three-quarter profile, looking at the two ladies; {I} in the middle with a small brown leather "
                    "handbag on her lap and {U} beside her on the right, both turned to the left in a three-quarter "
                    "profile, looking back at {P}. All three are seen from their paws on the chair seats to the tips "
                    "of their ears, their faces and mouths clearly visible, and none of them looks into the lens. "
                    "Behind them, softly out of focus, the blue and orange service windows of {L} and the short "
                    "queue of dogs."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>: the French bulldog in the red "
                             "t-shirt on the left facing right, and the two old ladies side by side on the right, "
                             "facing her."),
            },
            "pretinha": {
                "ref": "cenario-loterica-pretinha.png",
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "lugar": ("the small Brazilian lottery shop shown in <Picture 1>: the blue and orange service windows "
                          "with thick glass, the orange wall and the beige plastic waiting chairs, under bright white "
                          "ceiling lights"),
                "quadro": (
                    "The camera is completely static on a low tripod just behind the old poodle's shoulder, in an "
                    "over-the-shoulder shot, and it never moves, pans or zooms. Along the right edge of the frame, "
                    "out of focus, are the back of the poodle's curly off-white head and her shoulder in the lilac "
                    "knitted cardigan, turned away from the camera; her face is never seen. {P} sits on a beige "
                    "plastic waiting chair in the left two thirds of the frame, her head turned to the right of the "
                    "frame in a three-quarter view, towards the old poodle at the right edge, and she keeps looking "
                    "at her the whole time, never into the lens; her face, whole muzzle and chest in the red t-shirt "
                    "are sharp, her head in the upper half of the frame. Behind her, softly out of focus, the blue "
                    "and orange service windows of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the old poodle's "
                             "out-of-focus head and lilac shoulder along the right edge, and her face sharp, turned "
                             "towards the ladies."),
            },
            "senhoras": {
                "ref": "cenario-loterica-senhoras.png",
                "visiveis": ["cida", "lurdes"],
                "onde": {"cida": "in the middle", "lurdes": "on the right"},
                "quadro": (
                    "The camera is completely static on a low tripod just behind the French bulldog's shoulder, in "
                    "an over-the-shoulder shot, and it never moves, pans or zooms. Along the left edge of the frame, "
                    "out of focus, are the French bulldog's black back in the red t-shirt and the back of her large "
                    "upright black bat ear, turned away from the camera; her face is never seen. {I} sits on a beige "
                    "plastic waiting chair in the middle of the frame with a small brown leather handbag on her lap, "
                    "and {U} beside her on the right, both facing the camera at a three-quarter angle, turned to the "
                    "left towards the French bulldog and looking at her; their faces, muzzles and chests in the "
                    "knitted cardigans are sharp, their heads in the upper half of the frame. Behind them, softly "
                    "out of focus, the blue and orange service windows of {L} with their round metal speaking "
                    "grilles."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the French bulldog's "
                             "out-of-focus black back and red t-shirt along the left edge, and the two old ladies "
                             "side by side, sharp, turned towards her."),
            },
        },
    },
    # A cozinha da Dona Lurdes no almoço de domingo, com um prato vazio para o
    # neto: a Pretinha e as vizinhas à mesa (neto-6x1, refeito fora do
    # supermercado). Frames em movies/cenarios/scripts/cozinha-lurdes.yaml
    # (trio-a, vestido em vestir.yaml -a) e cozinha-lurdes-closes.yaml
    # (pretinha-a, senhoras-b). Aqui a cocker (Lurdes) fica no meio e a poodle
    # (Cida) na ponta direita - o contrário da lotérica.
    "cozinha-lurdes": {
        "lugar": ("the kitchen of an old, modest Brazilian house shown in <Picture 1>, at Sunday lunch: a square "
                  "table with a red-and-white checked oilcloth set with plates, glasses, a pot of rice, a pot of "
                  "black beans and a dish of roast chicken, one empty place with a clean plate, pale yellow wall "
                  "tiles, an old white enamel stove with a steaming pan, a window with a lace curtain and plants on "
                  "the sill, and a round wall clock, in warm midday light"),
        "estilo": ("The target video is photorealistic live-action footage in a home kitchen at midday, in warm, "
                   "natural light from the window and vibrant but natural colours, shot from a locked-off static "
                   "camera on a heavy tripod: the picture is perfectly steady for the whole video, with no camera "
                   "shake, no handheld movement and no drift."),
        "som": ("Quiet kitchen ambience at Sunday lunch: the soft bubbling of a pan on the stove, the slow tick of "
                "the wall clock and faint birdsong through the window. No music, no voices other than the three "
                "dogs', and no barking, whining or growling at any point."),
        "figurino": {
            "pretinha": ("Here she wears a plain red short-sleeved t-shirt with no print, no logo and no lettering, "
                         "her front legs through the sleeves."),
        },
        "cameras": {
            "dupla": {
                "ref": "cenario-cozinha-lurdes.png",
                "visiveis": ["pretinha", "lurdes", "cida"],
                "onde": {"pretinha": "on the left", "lurdes": "in the middle", "cida": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the table top, in a medium shot, "
                    "and it never moves, pans or zooms. The three sit on wooden chairs at the kitchen table, their "
                    "heads and chests above the checked oilcloth: {P} on the left, turned to the right in a "
                    "three-quarter profile, looking at the two ladies; {U} in the middle and {I} beside her on the "
                    "right, both turned to the left in a three-quarter profile, looking back at {P}. Their faces "
                    "and mouths are clearly visible, and none of them looks into the lens. On the table in front of "
                    "them are the pots of rice and beans, the dish of roast chicken and the glasses. Behind them, "
                    "softly out of focus, the old white stove with the steaming pan and the window of {L}."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>: the French bulldog in the red "
                             "t-shirt on the left facing right, and the two old ladies side by side on the right, "
                             "facing her."),
            },
            "pretinha": {
                "ref": "cenario-cozinha-lurdes-pretinha.png",
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "lugar": ("the kitchen of an old, modest Brazilian house shown in <Picture 1>: the red-and-white "
                          "checked oilcloth, pale yellow wall tiles, the old white enamel stove with a steaming pan "
                          "and the window with plants on the sill, in warm midday light"),
                "quadro": (
                    "The camera is completely static on a tripod at the height of the table top just behind the "
                    "cocker spaniel's shoulder, in an over-the-shoulder shot, and it never moves, pans or zooms. "
                    "Along the right edge of the frame, out of focus, are the cocker spaniel's long wavy golden-red "
                    "ear and her shoulder in the sea-green knitted cardigan, turned away from the camera; her face "
                    "is never seen. {P} sits at the table in the left two thirds of the frame, her head turned to "
                    "the right of the frame in a three-quarter view, towards the cocker spaniel at the right edge, "
                    "and she keeps looking at her the whole time, never into the lens; her face, whole muzzle and "
                    "chest in the red t-shirt are sharp, her head in the upper half of the frame. Behind her, softly "
                    "out of focus, the old white stove with the steaming pan and the window of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the cocker spaniel's "
                             "out-of-focus ear and green shoulder along the right edge, and her face sharp, turned "
                             "towards the ladies."),
            },
            "senhoras": {
                "ref": "cenario-cozinha-lurdes-senhoras.png",
                "visiveis": ["lurdes", "cida"],
                "onde": {"lurdes": "on the left", "cida": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the table top just behind the "
                    "French bulldog's shoulder, in an over-the-shoulder shot, and it never moves, pans or zooms. "
                    "Along the left edge of the frame, out of focus, are the French bulldog's black head, the back "
                    "of her large upright bat ear and her shoulder in the red t-shirt, turned away from the camera; "
                    "her face is never seen. {U} sits at the table in the middle of the frame and {I} beside her on "
                    "the right, both facing the camera at a three-quarter angle, turned to the left towards the "
                    "French bulldog and looking at her; their faces, muzzles and chests in the knitted cardigans "
                    "are sharp, their heads in the upper half of the frame, above the pots of rice and beans and "
                    "the dish of roast chicken. Behind them, softly out of focus, the window with plants on the "
                    "sill, the wall clock and the stove of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the French bulldog's "
                             "out-of-focus head and red shoulder along the left edge, and the two old ladies side by "
                             "side, sharp, turned towards her."),
            },
        },
    },
    # O balcão da farmácia do bairro: o Seu Tião (de polo, como no uber) e a
    # Pretinha de vermelho (farmacia-popular, refeito fora do uber). Frames em
    # movies/cenarios/scripts/farmacia-olhar.yaml (olhar-a, vestido em
    # vestir.yaml -a) e farmacia-closes.yaml (pretinha-a, tiao-b). Prateleiras
    # sem rótulo legível; sem gente atrás do balcão.
    "farmacia": {
        "lugar": ("the counter of a small neighbourhood pharmacy in a Brazilian city shown in <Picture 1>: a white "
                  "counter with a small white paper bag on it, white shelves behind it with small boxes in plain "
                  "colours and nothing legible on them, a glowing green cross on the wall, and nobody behind the "
                  "counter, under bright white ceiling lights"),
        "estilo": ("The target video is photorealistic live-action footage inside a pharmacy in the daytime, in "
                   "bright, even white overhead light and clean, natural colours, shot from a locked-off static "
                   "camera on a tripod: the picture is perfectly steady for the whole video, with no camera shake, "
                   "no handheld movement and no drift."),
        "som": ("Quiet pharmacy ambience: the low hum of the ceiling lights and of a refrigerator, and now and then "
                "the soft rustle of a paper bag. No music, no announcements, no voices other than the two dogs', "
                "and no barking, whining or growling at any point."),
        "figurino": {
            "pretinha": ("Here she wears a plain red short-sleeved t-shirt with no print, no logo and no lettering, "
                         "her front legs through the sleeves."),
            "tiao": ("Here he wears a plain light-blue short-sleeved polo shirt with no logo, his front legs through "
                     "the sleeves."),
        },
        "cameras": {
            "dupla": {
                "ref": "cenario-farmacia.png",
                "visiveis": ["pretinha", "tiao"],
                "onde": {"pretinha": "on the left", "tiao": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the counter, in a medium shot, "
                    "and it never moves, pans or zooms. {P} sits up at the white counter on the left, in the "
                    "foreground, turned to the right in a three-quarter profile, looking up at {T}; {T} stands at "
                    "the counter on the right, a little taller, turned to the left in a three-quarter profile, "
                    "looking down at her. Their faces and mouths are clearly visible, and neither looks into the "
                    "lens. A small white paper bag rests on the counter at the lower right. Behind them, softly out "
                    "of focus, the white shelves of small boxes and the glowing green cross of {L}."),
                "abertura": ("as the shot opens they are exactly as in <Picture 1>: the French bulldog in the red "
                             "t-shirt on the left looking up, and the dog in the light-blue polo on the right "
                             "looking down at her."),
            },
            "pretinha": {
                "ref": "cenario-farmacia-pretinha.png",
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the shoulder of the dog in the "
                    "light-blue polo, in an over-the-shoulder close shot, and it never moves, pans or zooms. In the "
                    "foreground at the lower right, out of focus, are his light-blue polo shoulder and the back of "
                    "his black, half-folded ear, turned away from the camera; his face is never seen. {P} sits "
                    "facing the camera at a three-quarter angle, her head turned to the right of the frame and "
                    "tilted up towards him, and she keeps looking up at him the whole time, never into the lens; her "
                    "face, whole muzzle and chest in the red t-shirt are sharp and fill the left two thirds of the "
                    "frame. Behind her, softly out of focus, the white shelves of small boxes of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: his out-of-focus blue "
                             "shoulder and ear in the lower-right foreground, and her face sharp, looking up at "
                             "him."),
            },
            "tiao": {
                "ref": "cenario-farmacia-tiao.png",
                "visiveis": ["tiao"],
                "onde": {"tiao": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the French bulldog's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. Along the left edge of the "
                    "frame, out of focus, are the French bulldog's black head, the back of her large upright bat "
                    "ear and her shoulder in the red t-shirt, turned away from the camera; her face is never seen. "
                    "{T} stands at the white counter facing the camera at a three-quarter angle, his head turned "
                    "to the left of the frame and tilted down towards her, and he keeps looking down at her the "
                    "whole time, never into the lens; his face, whole muzzle and chest in the light-blue polo are "
                    "sharp and fill the right two thirds of the frame. Behind him, softly out of focus, the white "
                    "shelves of small boxes and the glowing green cross of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: her out-of-focus black "
                             "head and red shoulder along the left edge, and his face sharp, looking down at her."),
            },
        },
    },
    # A sala da casa do Tio Renato: ele no sofá, em chamada de vídeo com a
    # Pretinha, o celular num suporte na mesinha de centro (tio-renato-muda).
    # Frames em movies/cenarios/scripts/sala-renato.yaml (aberto-b) e
    # sala-renato-takes.yaml. Um personagem só, quatro takes para variar:
    # "frente" (de frente, ele olha para o celular), "lado",
    # "close" e "aberto". A tela do celular nunca aparece (a Pretinha não entra).
    "sala-renato": {
        "lugar": ("the living room of an older man's modest house in a Brazilian city shown in <Picture 1>: a worn "
                  "brown fabric sofa with a colourful crocheted throw over its back, a window with a lace curtain "
                  "letting in warm light, a potted fern on a wooden stand, a wooden sideboard with a doily and a "
                  "small plaster saint, an old round wall clock, a low wooden coffee table with a smartphone in a "
                  "small black stand, and a woven rug on a terracotta tile floor, in warm late-afternoon light"),
        "estilo": ESTILO_CASA,
        "som": ("Quiet living-room tone in an old house, the slow tick of the wall clock and faint neighbourhood "
                "ambience through the window: distant birdsong and a far-off motorbike. No music, no voices other "
                "than his, and no barking, whining or growling at any point."),
        "figurino": {
            "renato": ("Here he wears a traditional short-sleeved cotton button-up shirt in a small blue-and-white "
                       "check, with a pointed collar, a breast pocket and white buttons, neatly buttoned up, his front "
                       "legs through the sleeves."),
        },
        "cameras": {
            "aberto": {
                "ref": "cenario-sala-renato.png",
                "visiveis": ["renato"],
                "onde": {"renato": ""},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the sofa seat, in a wide shot of "
                    "the living room, and it never moves, pans or zooms. {R} sits on the sofa just left of centre, "
                    "turned to the right in a three-quarter profile, talking to the smartphone propped in its small "
                    "black stand on the coffee table in front of him; only the plain black back of the phone is "
                    "seen, never its screen. He is seen whole, from his paws on the sofa to the tips of his ears, "
                    "his face and mouth clearly visible, and he never looks into the lens. Around him {L}."),
                "abertura": ("as the shot opens he sits exactly as in <Picture 1>: on the sofa, turned "
                             "towards the phone on the coffee table."),
            },
            # O take do celular olhando para a lente não serviu (Erika): de frente,
            # mas ele olha para o celular, sentado direito, patas à mostra.
            "frente": {
                "ref": "cenario-sala-renato-frente.png",
                "visiveis": ["renato"],
                "onde": {"renato": ""},
                "lugar": ("the living room shown in <Picture 1>: the worn brown sofa with the colourful crocheted "
                          "throw, the window with the lace curtain, the fern and the wooden sideboard with the "
                          "small saint, in warm late-afternoon light"),
                "quadro": (
                    "The camera is completely static on a tripod in front of him, on the other side of the coffee "
                    "table, at the height of the sofa seat, in a medium shot, and it never moves, pans or zooms. "
                    "{R} sits upright on the front edge of the sofa cushion, his chest lifted and his two white "
                    "front paws resting on the cushion, his body facing the camera and his head turned a little "
                    "down and to the left of the frame, talking to the smartphone in its small black stand on the "
                    "coffee table at the lower left; only the plain black back of the phone is seen. He keeps "
                    "looking at the phone the whole time, never into the lens; his face, mouth, chest in the "
                    "checked shirt and front paws are sharp. Behind him, softly out of focus, {L}."),
                "abertura": ("as the shot opens he is framed exactly as in <Picture 1>: sitting up on the sofa, "
                             "his paws on the cushion, looking down at the phone."),
            },
            "lado": {
                "ref": "cenario-sala-renato-lado.png",
                "visiveis": ["renato"],
                "onde": {"renato": ""},
                "lugar": ("the living room shown in <Picture 1>: the worn brown sofa, the window with the lace "
                          "curtain and the fern, in warm late-afternoon light"),
                "quadro": (
                    "The camera is completely static on a tripod at the height of the sofa seat, at the end of the "
                    "sofa, in a medium side shot, and it never moves, pans or zooms. {R} sits on the sofa in "
                    "profile, turned to the right of the frame, talking to the smartphone in its small black stand "
                    "on the coffee table at the right edge; only the plain black back of the phone is seen. His "
                    "face, mouth and chest in the checked shirt are sharp, and he never looks into the lens. Behind "
                    "him, softly out of focus, {L}."),
                "abertura": ("as the shot opens he is framed exactly as in <Picture 1>: in profile on the sofa, "
                             "facing the phone at the right edge."),
            },
            "close": {
                "ref": "cenario-sala-renato-close.png",
                "visiveis": ["renato"],
                "onde": {"renato": ""},
                "lugar": ("the living room shown in <Picture 1>: the round wall clock and the wooden sideboard, in "
                          "warm late-afternoon light"),
                "quadro": (
                    "The camera is completely static on a tripod just beside the smartphone on the coffee table, in "
                    "a close-up of his face, and it never moves, pans or zooms. {R} faces the camera at a "
                    "three-quarter angle, his head turned a little to the right of the frame, talking to the phone "
                    "just beside the lens, never into the lens; his wrinkled face, heavy jowls and the collar of "
                    "the checked shirt are sharp and fill the frame. Behind him, softly out of focus, {L}."),
                "abertura": ("as the shot opens he is framed exactly as in <Picture 1>: his face in three-quarter "
                             "view, turned towards the phone beside the lens."),
            },
        },
    },
    # O salão de beleza do bairro: a Pretinha de vermelho no banquinho, a Cida e
    # a Lurdes nas cadeiras rosa sob os secadores de capacete
    # (voto-depois-dos-70). Frames em movies/cenarios/scripts/salao.yaml
    # (trio-a) e salao-closes.yaml (pretinha-a, senhoras-b). Sem espelho no quadro (reflexo vira
    # bagunça) e sem gente.
    "salao": {
        "lugar": ("the small neighbourhood beauty salon in a Brazilian city shown in <Picture 1>: pale pink walls, "
                  "pink leather salon chairs under cream hood hair dryers, a shelf with folded white towels, a few "
                  "plain bottles and a potted plant, a window letting in soft daylight, a ceiling fan and a beige "
                  "tiled floor, with no mirrors and nobody else in the room"),
        "estilo": ("The target video is photorealistic live-action footage inside a beauty salon in the morning, in "
                   "soft, even daylight and gentle pastel colours, shot from a locked-off static camera on a low "
                   "tripod: the picture is perfectly steady for the whole video, with no camera shake, no handheld "
                   "movement and no drift."),
        "som": ("Quiet beauty-salon ambience: the low whir of the hood hair dryers and the soft turning of the "
                "ceiling fan. No music, no radio, no voices other than the three dogs', and no barking, whining or "
                "growling at any point."),
        "figurino": {
            "pretinha": ("Here she wears a plain red short-sleeved t-shirt with no print, no logo and no lettering, "
                         "her front legs through the sleeves."),
        },
        "cameras": {
            "dupla": {
                "ref": "cenario-salao.png",
                "visiveis": ["pretinha", "cida", "lurdes"],
                "onde": {"pretinha": "on the left", "cida": "in the middle", "lurdes": "on the right"},
                "quadro": (
                    "The camera is completely static on a low tripod at the height of the dogs' heads, in a medium "
                    "shot, and it never moves, pans or zooms. {P} sits on a round beige stool at the left edge of "
                    "the frame, turned to the right in a three-quarter profile, looking at the two ladies; {I} sits "
                    "in the middle and {U} beside her on the right, on pink salon chairs under the cream hood "
                    "dryers, both turned to the left in a three-quarter profile, looking back at {P}. Their heads "
                    "are level with each other, their faces and mouths clearly visible, and none of them looks into "
                    "the lens. Behind them, softly out of focus, the pale pink wall, the shelf with folded towels "
                    "and the window of {L}."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>: the French bulldog in the red "
                             "t-shirt on her stool on the left facing right, and the two old ladies side by side on "
                             "the right under the dryers, facing her."),
            },
            "pretinha": {
                "ref": "cenario-salao-pretinha.png",
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "lugar": ("the small beauty salon shown in <Picture 1>: the pale pink wall, the window and the shelf "
                          "with folded towels and a potted plant, in soft daylight"),
                "quadro": (
                    "The camera is completely static on a low tripod just behind the old poodle's shoulder, in an "
                    "over-the-shoulder shot, and it never moves, pans or zooms. Along the right edge of the frame, "
                    "out of focus, are the back of the poodle's curly off-white head and her shoulder in the lilac "
                    "knitted cardigan, turned away from the camera; her face is never seen. {P} sits on her round "
                    "stool in the left two thirds of the frame, her head turned to the right of the frame in a "
                    "three-quarter view, towards the ladies, and she keeps looking at them the whole time, never "
                    "into the lens; her face, whole muzzle and chest in the red t-shirt are sharp, her head in the "
                    "upper half of the frame. Behind her, softly out of focus, {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the old poodle's "
                             "out-of-focus head and lilac shoulder along the right edge, and her face sharp, turned "
                             "towards the ladies."),
            },
            "senhoras": {
                "ref": "cenario-salao-senhoras.png",
                "visiveis": ["cida", "lurdes"],
                "onde": {"cida": "on the left", "lurdes": "on the right"},
                "lugar": ("the small beauty salon shown in <Picture 1>: the cream hood hair dryers over the pink "
                          "salon chairs and the pale pink wall, in soft daylight"),
                "quadro": (
                    "The camera is completely static on a low tripod just behind the French bulldog's shoulder, in "
                    "an over-the-shoulder shot, and it never moves, pans or zooms. Along the left edge of the frame, "
                    "out of focus, are the French bulldog's black head, the back of her large upright bat ear and "
                    "her shoulder in the red t-shirt, turned away from the camera; her face is never seen. {I} and "
                    "{U} sit side by side on the pink salon chairs under the cream hood dryers, {I} on the left and "
                    "{U} on the right, both facing the camera at a three-quarter angle, turned to the left towards "
                    "the French bulldog and looking at her; their faces, muzzles and chests in the knitted "
                    "cardigans are sharp, their heads in the upper half of the frame. Behind them, softly out of "
                    "focus, {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the French bulldog's "
                             "out-of-focus head and red shoulder along the left edge, and the two old ladies side by "
                             "side, sharp, turned towards her."),
            },
        },
    },
    # Uma rua de bairro residencial arrumado (não a de favela da rua-festa),
    # enfeitada de verde e amarelo com um pouco de vermelho: os 7 juntos, cada
    # um com a roupa de sempre (todos-perdem). Frame em
    # movies/cenarios/scripts/rua-bairro.yaml (todos-b). Uma câmera só, "todos".
    "rua-bairro": {
        "lugar": ("the quiet residential street of a middle-class Brazilian neighbourhood shown in <Picture 1>, on a "
                  "sunny late afternoon: tidy single-storey houses in soft colours with low front walls and iron "
                  "gates, a clean sidewalk lined with trees and a blooming yellow ipê tree, and strings of small "
                  "green, yellow and a few red paper bunting flags across the street overhead"),
        "estilo": ("The target video is photorealistic live-action footage, outdoors on a residential street in "
                   "warm, golden late-afternoon light with soft long shadows and vibrant but natural colours, shot "
                   "from a locked-off static camera on a heavy tripod: the picture is perfectly steady for the whole "
                   "video, with no camera shake, no handheld movement and no drift."),
        "som": ("Calm residential street ambience at the end of the afternoon: birdsong, leaves rustling in a light "
                "breeze and the soft flutter of the paper bunting. The street stays empty, with no people and no "
                "moving cars. No music, and no barking, whining or growling at any point."),
        "figurino": {
            "pretinha": "Here she wears a plain red short-sleeved t-shirt with no print.",
            "pacoca": "Here he wears a plain mustard-yellow short-sleeved t-shirt with no print.",
            "jose": "Here he wears a plain red short-sleeved t-shirt with no print.",
            "tiao": "Here he wears a plain light-blue short-sleeved polo shirt with no logo.",
            "renato": "Here he wears a short-sleeved light-blue button-up shirt with a collar.",
        },
        "cameras": {
            "todos": {
                "ref": "cenario-rua-bairro.png",
                "visiveis": ["pretinha", "pacoca", "cida", "lurdes", "jose", "tiao", "renato"],
                "onde": {"pretinha": "in the front row, on the left", "pacoca": "in the front row, second from the left",
                         "cida": "in the front row, second from the right", "lurdes": "in the front row, on the right",
                         "jose": "in the back row, on the left", "tiao": "in the back row, in the middle",
                         "renato": "in the back row, on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the dogs' heads, in a medium-wide "
                    "shot of the seven dogs together in the middle of the street, and it never moves, pans or "
                    "zooms. In the front row sit {P}, {C}, {I} and {U}, from left to right; in the back row, a "
                    "little higher behind them, stand {J}, {T} and {R}, from left to right. All seven face the "
                    "camera, close together, every face and mouth clearly visible. Behind them, {L}."),
                "abertura": ("as the shot opens the seven dogs are gathered exactly as in <Picture 1>, four in front "
                             "and three behind, facing the camera."),
            },
        },
    },
    # A varandinha do apartamento do primo José, de manhã cedo: só vlog dele
    # (checklist-domingo, refeito fora do home office). Frame em
    # movies/cenarios/scripts/varanda-jose.yaml (vlog-jose-a). Camiseta branca.
    "varanda-jose": {
        "lugar": ("the narrow balcony of the caramel dog's modest apartment in a Brazilian city shown in "
                  "<Picture 1>, early in the morning: a white balcony railing, a small potted basil plant and a "
                  "plain white coffee cup, and beyond it a view of low apartment buildings and red-tiled roofs "
                  "under a soft morning sky"),
        "estilo": ("The target video is photorealistic live-action footage on an apartment balcony early in the "
                   "morning, in soft, warm early sunlight and natural colours, shot from a locked-off static "
                   "camera on a small tripod: the picture is perfectly steady for the whole video, with no camera "
                   "shake, no handheld movement and no drift."),
        "sem_rabo": ["jose"],
        "som": ("Quiet early-morning city ambience from a balcony: birdsong, a light breeze and very faint "
                "distant traffic far below. No music, no voices other than his, and no barking, whining or "
                "growling at any point."),
        "figurino": {
            "jose": ("Here he wears a plain white short-sleeved t-shirt with no print and no logo, his front legs "
                     "through the sleeves."),
        },
        "cameras": {
            "vlog-jose": camera_vlog(
                "jose", "cenario-varanda-jose-vlog-jose.png",
                "{L}: the white railing behind him, the basil plant and the coffee cup at the lower left, and the "
                "low buildings and red-tiled roofs of the city in the distance.",
                plano=("in a medium shot of {J} alone, and it never moves, pans or zooms. {J} sits upright on a "
                       "small wooden stool, facing the camera straight on and looking directly into the lens, "
                       "talking to the viewer; his front paws rest on the stool in front of him, and his face is "
                       "sharp and centred in the upper half of the frame. He sits still the whole time.")),
        },
    },
    # O videoclipe de domingo ("Andar com Fé", Gilberto Gil; sem fala, só o
    # refrão em coro no fim): cada um sai de casa no bairro da rua-bairro, de
    # branco, e depois um close em contra-plongée; no fim, os 7 juntos. Frames
    # em movies/cenarios/scripts/clipe*.yaml -> assets/cenario-clipe-*.png.
    # Câmeras "<pet>-acao", "<pet>-close" e "todos" (montadas em _clipe()).
    "clipe": {
        "lugar": ("a quiet, tidy residential street of a middle-class Brazilian neighbourhood shown in <Picture 1>, "
                  "on a sunny Sunday morning: single-storey houses in soft colours with low front walls, iron gates "
                  "and small gardens, trees along the sidewalk, a blooming yellow ipê tree, and strings of small "
                  "green, yellow and a few red paper bunting flags across the street"),
        "estilo": ("The target video is photorealistic live-action footage, outdoors on a residential street on a "
                   "bright Sunday morning, in soft, warm sunlight and vibrant but natural colours, cinematic and "
                   "joyful, shot from a locked-off static camera on a tripod: the picture is perfectly steady for "
                   "the whole video, with no camera shake, no handheld movement and no drift; only the dogs move."),
        "som": ("Gentle Sunday-morning street ambience: birdsong, a light breeze, the soft flutter of the paper "
                "bunting and distant church bells. No music and no barking, whining or growling at any point."),
        "figurino": {
            "pretinha": "Here she wears a plain white short-sleeved t-shirt with no print.",
            "pacoca": "Here he wears a plain white short-sleeved t-shirt with no print.",
            "jose": "Here he wears a plain white short-sleeved t-shirt with no print.",
            "tiao": "Here he wears a plain white short-sleeved polo shirt with no logo.",
            "renato": "Here he wears a plain white short-sleeved button-up shirt with a collar.",
            "cida": "Here she wears a plain white knitted cardigan and carries nothing.",
            "lurdes": "Here she wears a plain white knitted cardigan.",
        },
        "cameras": {},
    },
    # O carro de aplicativo do Seu Tião, a Pretinha no banco de trás. Frames em
    # movies/cenarios/scripts/uber.yaml (dupla-a, pretinha-b, tiao-b). Câmera
    # presa ao painel: o quadro é fixo, a rua passa pelos vidros.
    "uber": {
        "lugar": ("the inside of the ride-hailing car shown in <Picture 1>: a clean grey fabric interior, grey front "
                  "seats with headrests, a grey back seat, a black steering wheel, a beige roof lining, and through "
                  "the windows a sunny Brazilian city street with trees and low buildings"),
        "estilo": ("The target video is photorealistic live-action footage inside a car on a bright afternoon, in "
                   "soft natural daylight coming through the windows and vibrant but natural colours, shot from a "
                   "camera rigidly mounted inside the car: the picture is perfectly steady for the whole video, with "
                   "no camera shake, no handheld movement and no drift. The car drives slowly and smoothly, and only "
                   "the street seen through the windows slides gently past."),
        "som": ("The low, steady hum of a car engine and the soft whoosh of tyres on asphalt, with muffled city "
                "traffic outside the closed windows. No music, no horns, and no barking, whining or growling at any "
                "point."),
        "figurino": {
            "tiao": ("Here he wears a plain light-blue short-sleeved polo shirt with no logo, his front legs through "
                     "the sleeves."),
        },
        "cameras": {
            "dupla": {
                "ref": "cenario-uber.png",
                "visiveis": ["pretinha", "tiao"],
                "onde": {"pretinha": "on the back seat, on the left", "tiao": "in the driver's seat, on the right"},
                "quadro": (
                    "The camera is rigidly mounted in the middle of the dashboard, pointing back into the car, in a "
                    "medium-wide shot, and it never moves, pans or zooms. {T} sits in the driver's seat on the right "
                    "of the frame, in the foreground, one white speckled front paw resting on the black steering "
                    "wheel at the lower right, his head turned towards the left of the frame, looking back at {P}; "
                    "his face and mouth are clearly visible. {P} sits upright on the grey back seat, to the left of "
                    "the centre of the frame, in the gap between the front seats, facing forward and looking at "
                    "{T}; she is seen from her front paws on the seat to the tips of her ears, her face and mouth "
                    "clearly visible. The empty grey front passenger seat fills the left edge of the frame, and a "
                    "small black phone holder with a dark, blank screen sits on the dashboard at the bottom. Behind "
                    "{P}, through the rear window, the sunny street of {L}, softly out of focus."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>: the driver at the wheel on the "
                             "right with his head turned back, and the French bulldog upright on the back seat, "
                             "looking at him."),
            },
            "pretinha": {
                "ref": "cenario-uber-pretinha.png",
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "lugar": ("the back seat of the ride-hailing car shown in <Picture 1>: grey fabric seats and "
                          "headrests, and through the rear window a sunny Brazilian city street with trees and low "
                          "buildings"),
                "quadro": (
                    "The camera is rigidly mounted between the two front seats, just behind the driver's shoulder, "
                    "in an over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the "
                    "right edge, out of focus, are the driver's shoulder in a light-blue polo shirt and the back of "
                    "his black, half-folded ear, turned away from the camera; his face is never seen. {P} sits "
                    "upright on the grey back seat, facing the camera at a three-quarter angle, turned towards the "
                    "driver and looking at him, just to the right of the lens; her face, whole muzzle and chest with "
                    "the white blaze are sharp and fill the centre of the frame. Behind her, softly out of focus, the "
                    "grey headrests and, through the rear window, the sunny street of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the driver's out-of-focus "
                             "shoulder and ear at the right edge, and her face sharp, turned towards him."),
            },
            "tiao": {
                "ref": "cenario-uber-tiao.png",
                "visiveis": ["tiao"],
                "onde": {"tiao": ""},
                "lugar": ("the driver's seat of the ride-hailing car shown in <Picture 1>: grey fabric seats, a "
                          "black steering wheel, a beige roof lining, and through the side window a sunny Brazilian "
                          "city street with trees and low buildings"),
                "quadro": (
                    "The camera is rigidly mounted on the dashboard in front of the empty passenger seat, angled "
                    "towards the driver, in a close shot, and it never moves, pans or zooms. {T} sits in the "
                    "driver's seat, one white speckled front paw on the black steering wheel at the lower right, "
                    "his head turned a little over his shoulder towards the back seat, talking to the passenger "
                    "behind him; his face, whole muzzle and chest in the polo shirt are sharp and fill the upper "
                    "two thirds of the frame, at a three-quarter angle. Behind him, softly out of focus, the grey "
                    "back seat and, through the side window, the sunny street of {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: his paw on the wheel and "
                             "his face sharp, turned a little towards the back seat."),
            },
        },
    },
    # O hortifrúti do supermercado do bairro: a Pretinha e as vizinhas, Dona
    # Cida e Dona Lurdes (secao-mudou). Frames em
    # movies/cenarios/scripts/supermercado.yaml (trio-a, closes da rodada 2).
    # A câmera "dupla" mostra os três; "senhoras", as duas juntas.
    "supermercado": {
        "lugar": ("the fruit and vegetable section of the small Brazilian neighbourhood supermarket shown in "
                  "<Picture 1>: pale floor tiles, slanted wooden crates heaped with oranges, tomatoes, green "
                  "lettuces, bananas and papayas, a red plastic shopping basket with oranges and bananas on the "
                  "floor, and bright white ceiling lights"),
        "estilo": ("The target video is photorealistic live-action footage inside a supermarket in the morning, in "
                   "bright, even white overhead light and vibrant but natural colours, shot from a locked-off static "
                   "camera on a low tripod: the picture is perfectly steady for the whole video, with no camera "
                   "shake, no handheld movement and no drift."),
        # Sem "vozes ao longe": na cena 2 do secao-mudou elas desenharam uma
        # pessoa no fundo.
        "som": ("Soft, empty supermarket ambience: the low steady hum of refrigerated produce counters and the "
                "faint buzz of the ceiling lights. No music, no announcements, no voices other than the dogs', and "
                "no barking, whining or growling at any point."),
        "cameras": {
            "dupla": {
                "ref": "cenario-supermercado.png",
                "visiveis": ["pretinha", "cida", "lurdes"],
                "onde": {"pretinha": "on the left", "cida": "in the middle", "lurdes": "on the right"},
                "quadro": (
                    "The camera is completely static on a low tripod at the dogs' eye level, in a medium shot, and "
                    "it never moves, pans or zooms. {P} sits on the pale floor tiles at the left edge of the frame, "
                    "turned to the right in a three-quarter profile, looking at the two ladies; {I} sits in the "
                    "middle and {U} beside her on the right, both turned to the left in a three-quarter profile, "
                    "looking back at {P}. All three are seen from their paws on the floor to the tips of their "
                    "ears, their faces and mouths clearly visible, their heads in the middle of the frame. A red "
                    "plastic shopping basket with oranges and bananas stands on the floor behind the gap between "
                    "{P} and {I}. Behind them, softly out of focus, the slanted wooden crates of oranges, tomatoes, "
                    "lettuces and bananas of {L} under the bright ceiling lights."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>: the French bulldog on the left "
                             "facing right, and the two old ladies side by side on the right, facing her."),
            },
            "pretinha": {
                "ref": "cenario-supermercado-pretinha.png",
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "quadro": (
                    "The camera is completely static on a low tripod just behind the old poodle's shoulder, in an "
                    "over-the-shoulder shot, and it never moves, pans or zooms. Along the right edge of the frame, "
                    "out of focus, are the back of the poodle's curly off-white head and long curly ear and her "
                    "shoulder in the lilac knitted cardigan, turned away from the camera; her face is never seen. "
                    "{P} sits on the pale floor tiles in the left two thirds of the frame, her head turned to the right "
                    "of the frame in a three-quarter view, towards the old poodle at the right edge, and she keeps "
                    "looking at her the whole time, never into the lens; her face, whole muzzle and chest with the "
                    "white blaze are sharp, her head in the upper half of the frame. "
                    "Behind her, softly out of focus, the wooden crates of oranges, tomatoes, lettuces and bananas "
                    "of {L} under the bright ceiling lights."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the old poodle's "
                             "out-of-focus head and lilac shoulder along the right edge, and her face sharp, turned "
                             "towards the ladies."),
            },
            "senhoras": {
                "ref": "cenario-supermercado-senhoras.png",
                "visiveis": ["cida", "lurdes"],
                "onde": {"cida": "in the middle", "lurdes": "on the right"},
                "quadro": (
                    "The camera is completely static on a low tripod just behind the French bulldog's shoulder, in "
                    "an over-the-shoulder shot, and it never moves, pans or zooms. Along the left edge of the frame, "
                    "out of focus, are the French bulldog's black back and the back of her large upright black bat "
                    "ear, turned away from the camera; her face is never seen. {I} sits on the pale floor tiles in "
                    "the middle of the frame and {U} beside her on the right, both facing the camera at a "
                    "three-quarter angle, turned to the left towards the French bulldog and looking at her; their "
                    "faces, muzzles and chests in the knitted cardigans are sharp, their heads in the upper half of "
                    "the frame. Behind them, softly out of focus, the red shopping basket on the floor and the "
                    "wooden crates of oranges, tomatoes, lettuces and bananas of {L} under the bright ceiling "
                    "lights."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the French bulldog's "
                             "out-of-focus black back and ear along the left edge, and the two old ladies side by "
                             "side, sharp, turned towards her."),
            },
        },
    },
    # O home office do primo José: só vlog dele, na webcam em cima do monitor
    # (jose-tutorial-secao). Frame em movies/cenarios/scripts/home-office.yaml
    # (vlog-jose-c). O monitor fica fora do quadro: só a traseira preta dele
    # aparece na borda esquerda. O rabo saiu estranho atrás da cadeira (cena 1
    # do jose-tutorial-secao), e "his tail stays out of sight" o fez abanar
    # mais: a palavra "tail" não pode aparecer. Descreva o que ocupa o espaço
    # (o encosto da cadeira) e ele quieto; a aparência vai sem rabo (sem_rabo).
    "home-office": {
        "lugar": ("the small home office corner of the caramel dog's modest apartment in a Brazilian city, shown in "
                  "<Picture 1>: a pale sage-green wall, a wooden shelf with a few books and a green trailing pothos "
                  "plant, a black-and-white football on top of a small black computer tower, a window on the right "
                  "with half-open blinds and apartment buildings outside, a dark desk with a black keyboard and a "
                  "plain cream coffee mug, in warm late-afternoon light"),
        "estilo": ESTILO_CASA,
        "sem_rabo": ["jose"],
        "som": ("Quiet room tone in a small apartment, the faint hum of a computer, and soft city ambience drifting "
                "in through the window: distant traffic and birdsong. No barking, whining or growling at any point."),
        "figurino": {
            "jose": ("Here he wears a plain heather-grey short-sleeved t-shirt with no print and no logo, his front "
                     "legs through the sleeves, and a pair of plain black over-ear headphones resting around his "
                     "neck."),
        },
        "cameras": {
            "vlog-jose": camera_vlog(
                "jose", "cenario-home-office-vlog-jose.png",
                "{L}: the sage-green wall, the wooden shelf with books and the trailing pothos plant at the upper "
                "left, the football on the black computer tower on the left, and the window with half-open blinds "
                "on the right. The out-of-focus black back of a monitor fills the left edge of the frame, the black "
                "keyboard runs along the bottom, and the cream coffee mug sits in the lower right corner.",
                plano=("in a medium shot of {J} alone, and it never "
                       "moves, pans or zooms. {J} sits on a black office chair at his desk, facing the camera "
                       "straight on and looking directly into the lens, talking to the viewer; his front paws rest "
                       "on the desk just behind the keyboard, and his face is sharp and centred just above the "
                       "middle of the frame. He sits still and upright, settled deep in the chair; the tall black "
                       "back of the office chair fills the space behind him on both sides.")),
        },
    },
    # A praça do bairro: só vlog do José (praca-vlog-jose-b, audio-falso v2).
    "praca": {
        "lugar": ("the small neighbourhood square in a Brazilian city shown in <Picture 1>: a green-painted wooden "
                  "bench, a wavy black-and-white Portuguese stone pavement, big leafy trees, low flower beds with "
                  "pink and red flowers, and low colourful houses across a quiet street, in warm golden "
                  "late-afternoon light through the leaves"),
        "estilo": ("The target video is photorealistic live-action footage, outdoors in a neighbourhood square in "
                   "warm, golden late-afternoon light filtering through the trees, with soft long shadows and "
                   "vibrant but natural colours, shot from a locked-off static camera on a heavy tripod: the "
                   "picture is perfectly steady for the whole video, with no camera shake, no handheld movement "
                   "and no drift."),
        "som": ("Calm open-air ambience in a quiet square at the end of the afternoon: leaves rustling in a light "
                "breeze, birdsong and faint distant voices. The square and the street behind him stay empty, with "
                "no people and no moving vehicles. No barking, whining or growling at any point."),
        "figurino": {
            "jose": ("Here he wears a plain navy-blue short-sleeved t-shirt with no print and no logo, his front "
                     "legs through the sleeves."),
        },
        "cameras": {
            "vlog-jose": camera_vlog(
                "jose", "cenario-praca-vlog-jose.png",
                "{L}: the big leafy trees framing the top of the picture, the wavy black-and-white stone pavement "
                "behind the bench, a flower bed on each side, and the low colourful houses across the empty street "
                "in the distance. The green wooden slats of the bench run along the bottom of the frame.",
                plano=("in a medium shot of {J} alone, and it never moves, pans or zooms. {J} sits upright on the "
                       "green wooden bench, facing the camera straight on and looking directly into the lens, "
                       "talking to the viewer; his front paws rest on the bench in front of him, and his face is "
                       "sharp and centred in the upper half of the frame. He sits still the whole time.")),
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
    # O ponto de ônibus da avenida no fim da tarde, na volta do trabalho
    # (tres-poderes, Erika 27/10). Frames em movies/cenarios/scripts/
    # ponto-onibus-closes.yaml (dupla-a sem o papel do contracheque,
    # pretinha-a, pacoca-a); o cenario-ponto-onibus.png com o papel fica para
    # o contracheque-ir. Ela à esquerda, de costas para o vidro do abrigo; ele
    # à direita, com a avenida atrás. O close dela tem o próprio `lugar`, só
    # com o vidro: a avenida é o fundo dele.
    "ponto-onibus": {
        "lugar": ("the bus stop shown in <Picture 1>, on a busy avenue in a Brazilian city at the end of the "
                  "afternoon: a dark wooden bench with a metal frame under a bus shelter with a clear glass back "
                  "panel in a dark green metal frame, with nothing on it, and beyond it the avenue with passing "
                  "cars, trees, utility poles and low buildings in warm golden light"),
        "estilo": ("The target video is photorealistic live-action footage outdoors at the end of the afternoon, "
                   "in warm, golden low sunlight with soft long shadows and vibrant but natural colours, shot from a "
                   "locked-off static camera on a heavy tripod: the picture is perfectly steady for the whole "
                   "video, with no camera shake, no handheld movement and no drift."),
        "som": ("Calm street ambience at a bus stop at the end of the afternoon: the low, steady hum of traffic on "
                "the avenue, a car passing now and then, and birds in the trees. No horns, no engines revving, no "
                "music, no voices other than the two dogs', and no barking, whining or growling at any point."),
        "figurino": {
            "pretinha": ("Here she wears a plain red short-sleeved t-shirt with no print, no logo and no "
                         "lettering, her front legs through the sleeves."),
            "pacoca": ("Here he wears a plain navy-blue work polo shirt with no logo, his front legs through the "
                       "sleeves."),
        },
        "cameras": {
            "dupla": {
                "ref": "cenario-pontoonibus.png",
                "visiveis": ["pretinha", "pacoca"],
                "onde": {"pretinha": "on the left", "pacoca": "on the right"},
                "quadro": (
                    "The camera is completely static on a tripod at the height of the bench, straight on, in a "
                    "medium shot, and it never moves, pans or zooms. {P} sits on the left of the bench in the red "
                    "t-shirt, turned to the right in a three-quarter profile, looking at {C}; {C} sits on the "
                    "right of the bench in the navy polo, turned to the left in a three-quarter profile, looking "
                    "back at her. Both are seen whole, from their paws on the bench to the tips of their ears, "
                    "and both faces and mouths are clearly visible. Behind them, softly out of focus, {L}: the "
                    "glass back panel of the shelter with its dark green frame behind her on the left, and the "
                    "avenue with its passing cars behind him on the right."),
                "abertura": ("as the shot opens they sit exactly as in <Picture 1>, side by side on the bench, "
                             "turned towards each other."),
            },
            "pretinha": {
                "ref": "cenario-pontoonibus-pretinha.png",
                "visiveis": ["pretinha"],
                "onde": {"pretinha": ""},
                "lugar": ("the bus shelter shown in <Picture 1>: the clear glass back panel in its dark green "
                          "metal frame, in warm golden late-afternoon light"),
                "quadro": (
                    "The camera is completely static on a tripod just behind the pug's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "right, out of focus, are the pug's fawn neck and shoulder in the navy-blue polo and the back of "
                    "his small black ear, turned away from the camera; his face is never seen. {P} sits on the "
                    "bench facing the camera at a three-quarter angle, turned towards the pug and looking at him, "
                    "just to the right of the lens; her face, whole muzzle and chest in the red t-shirt are sharp "
                    "and fill the left two thirds of the frame. Behind her, softly out of focus, {L}."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the pug's out-of-focus "
                             "shoulder and ear in the lower-right foreground, and her face sharp, turned towards "
                             "him."),
            },
            "pacoca": {
                "ref": "cenario-pontoonibus-pacoca.png",
                "visiveis": ["pacoca"],
                "onde": {"pacoca": ""},
                "quadro": (
                    "The camera is completely static on a tripod just behind the French bulldog's shoulder, in an "
                    "over-the-shoulder close shot, and it never moves, pans or zooms. In the foreground at the lower "
                    "left, out of focus, are the French bulldog's black shoulder in the red t-shirt and the back of "
                    "her tall upright bat ear, turned away from the camera; her face is never seen. {C} sits on "
                    "the bench facing the camera at a three-quarter angle, turned towards her and looking at her, "
                    "just to the left of the lens; his face, whole muzzle and chest in the navy polo are sharp and "
                    "fill the right two thirds of the frame. Behind him, softly out of focus, the avenue of {L} "
                    "in warm golden light: passing cars, trees, utility poles and low buildings."),
                "abertura": ("as the shot opens the framing is exactly as in <Picture 1>: the French bulldog's "
                             "out-of-focus shoulder and ear in the lower-left foreground, and his face sharp, "
                             "turned towards her."),
            },
        },
    },
}

# O sofa-frente de roupinha (democracia-todo-dia, Erika 26/10): Pretinha de
# camiseta vermelha, Paçoca com a camisa listrada do time da lanchonete.
# Frames em movies/cenarios/scripts/vestir-sofa.yaml (dupla-a, pretinha-a,
# pacoca-a: listras largas iguais nos três planos). O resto é o sofa-frente.
CENARIOS["sofa-frente-roupa"] = {
    **CENARIOS["sofa-frente"],
    "figurino": {
        "pretinha": ("Here she wears a plain red short-sleeved t-shirt with no print, no logo and no lettering, "
                     "her front legs through the sleeves."),
        "pacoca": ("Here he wears a short-sleeved football shirt of an amateur neighbourhood team, green with "
                   "white vertical stripes, plain, with no crest, no number and no lettering, his front legs "
                   "through the sleeves."),
    },
    "cameras": {
        nome: {**cam,
               "ref": cam["ref"].replace("cenario-sofafrente", "cenario-sofafrente-roupa"),
               "quadro": cam["quadro"]
               .replace("the pug's fawn back and shoulder",
                        "the pug's fawn back and shoulder in the green-and-white striped shirt")
               .replace("the French bulldog's black back and shoulder",
                        "the French bulldog's black back and shoulder in the red t-shirt")}
        for nome, cam in CENARIOS["sofa-frente"]["cameras"].items()
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
# A mesma varanda com a Pretinha de camiseta vermelha, como nos vídeos da
# última semana (recado-final, Erika 23/10). Frame: vestir-varanda.yaml.
_cams["varanda-frente"]["vlog-pretinha-vermelha"] = camera_vlog(
    "pretinha", "cenario-varanda-vlog-pretinha-vermelha.png",
    "{L}: the white wall on the left, a terracotta pot with a plant, the green metal railing running along the "
    "terracotta tiled floor on the right, and the pink house across the street in the warm afternoon light.",
    lugar=_cams["varanda-frente"]["pretinha"]["lugar"],
    # Frame recortado do peito para cima: no corpo inteiro, a mancha clara
    # entre as patas virou genitália no vídeo (recado-final, cena 1, 23/10).
    plano=("in a medium close-up of {P} alone, and it never moves, pans or zooms. {P}, a female dog, sits on the "
           "veranda facing the camera straight on and looks directly into the lens, talking to the viewer; she "
           "wears a plain red short-sleeved t-shirt with no print; the frame shows only her head and her chest "
           "in the red t-shirt, and everything below the t-shirt stays out of frame and is never seen; her face "
           "is sharp and fills the upper half of the frame."))
del _cams

# As câmeras do clipe: para cada pet, "<pet>-acao" (sai de casa, plano médio
# aberto, acena para um vizinho) e "<pet>-close" (contra-plongée, só ele);
# e "todos" (os 7 juntos, de branco).
def _clipe() -> None:
    cams = CENARIOS["clipe"]["cameras"]
    for k in ("lurdes", "tiao", "cida", "jose", "renato", "pacoca", "pretinha"):
        eu = "{" + MARCA[k] + "}"
        cams[f"{k}-acao"] = {
            "ref": f"cenario-clipe-{k}-acao.png",
            "visiveis": [k], "onde": {k: ""},
            "quadro": (f"The camera is completely static on a tripod at {ELENCO[k]['pron']} eye level, in a "
                       f"medium-wide shot, and it never moves, pans or zooms. {eu} is the only one of the "
                       f"seven friends in the picture, moving naturally along {{L}}; a friendly neighbour dog may "
                       f"be seen in the background. {eu}'s whole body and face stay clearly visible."),
            "abertura": f"as the shot opens {ele(k)} is exactly as in <Picture 1>.",
        }
        cams[f"{k}-close"] = {
            "ref": f"cenario-clipe-{k}-close.png",
            "visiveis": [k], "onde": {k: ""},
            "quadro": (f"The camera is completely static, low and below {ELENCO[k]['pron']} chin, looking up at "
                       f"{o(k)} in a low-angle close-up (contra-plongée), and it never moves, pans or zooms. "
                       f"{eu}'s head and shoulders fill the frame against the bright blue sky, the bunting and "
                       f"the yellow ipê of {{L}} softly out of focus above and behind; {ELENCO[k]['pron']} face is "
                       f"sharp, looking ahead down the street just beside the lens, never into it."),
            "abertura": f"as the shot opens {ele(k)} is framed exactly as in <Picture 1>, seen from below.",
        }
    cams["todos"] = {
        "ref": "cenario-clipe-todos.png",
        "visiveis": ["jose", "tiao", "renato", "pretinha", "pacoca", "cida", "lurdes"],
        "onde": {"jose": "in the back row, on the left", "tiao": "in the back row, in the middle",
                 "renato": "in the back row, on the right", "pretinha": "in the front row, on the left",
                 "pacoca": "in the front row, second from the left", "cida": "in the front row, second from the right",
                 "lurdes": "in the front row, on the right"},
        "quadro": ("The camera is completely static on a tripod at the height of the dogs' heads, in a medium-wide "
                   "shot of the seven friends together in the middle of {L}, all dressed in white, and it never "
                   "moves, pans or zooms. In the back row stand {J}, {T} and {R}; in the front row sit {P}, {C}, "
                   "{I} and {U}. Every face and mouth is clearly visible."),
        "abertura": "as the shot opens the seven friends are gathered exactly as in <Picture 1>.",
    }


_clipe()

FECHO = ("No humans appear at any point, and no text, lettering, watermark, letterboxing or black bars appear "
         "anywhere in the frame.")
FECHO_DUPLA = "Each dog's mouth moves only while that dog speaks. "
NUMERO = {2: "two", 3: "three"}

# Na grade 17n+5 do modelo; mais longo que 124 nunca foi testado aqui.
FRAMES = (90, 107, 124)
FPS = 24
FOLGA_S = 0.9  # respiro antes/depois da fala

# Grafia -> como a voz deve ler. Só o prompt recebe a forma falada; o
# `legendas` desfaz a troca, e a legenda mostra a grafia certa. "Cleide" saiu
# "Cléidi" (é aberto); o circunflexo pede o ê fechado. "vinte e dois" saiu
# truncado (tio-renato): o roteiro escreve "22", a voz lê "vintedois" e a
# legenda mostra o número da urna.
# O José (terras-raras) leu "Paçôca": o agudo abre o o.
# "e-Título" (secao-mudou): "ê Título", com espaço, saiu "é... título", com
# pausa; vai numa palavra só. "TSE" soletrado como
# "tê ésse é" saiu errado (secao-mudou cena 4): sigla não funciona, escreva
# por extenso no roteiro ("a Justiça Eleitoral").
# "TI" (jose-tutorial-secao): "têí", numa palavra só, pelo mesmo motivo.
# "CPF" e a URL (jose-tutorial-voz): a URL na forma que a Erika pediu saiu
# certa ("tê-ésse-é" dentro de uma frase com "ponto jus ponto BR" funcionou,
# ao contrário do "TSE" solto da Pretinha).
PRONUNCIA = {"Cleide": "Clêide", "22": "vintedois", "25": "vintecinco", "Paçoca": "Paçóca", "e-Título": "étítulo", "TI": "têí",
             "CPF": "cêpêéfe", "tse.jus.br": "tê-ésse-é ponto jus ponto BR"}


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
            for nome in {e["nome"], e["nome"].replace("ç", "c").replace("ã", "a")}:
                t = re.sub(rf"\b{nome}\b", alvo, t)
        return t

    def formata(self, t: str) -> str:
        return t.format(L=self.lugar, **{m: self.rotulo.get(k, ELENCO[k]["fora"]) for k, m in MARCA.items()})


def palavras(fala: str) -> int:
    return len(re.findall(r"[\wÀ-ÿ]+", fala))


def duracao(cena: dict) -> int:
    if "frames" in cena:
        return int(cena["frames"])
    fala = cena.get("fala")
    if not fala:
        return FRAMES[0]
    pps = 2.2 if fala["quem"] == CORO else ELENCO[fala["quem"]]["palavras_por_s"]
    precisa = (palavras(fala["texto"]) / pps + FOLGA_S) * FPS
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
    # Um close de mais de um (as duas senhoras no supermercado) serve a cada
    # um deles.
    for nome, cam in cenario["cameras"].items():
        if fala and nome != "dupla" and not nome.startswith("vlog-") and fala["quem"] in cam["visiveis"]:
            return nome
    return "dupla"


def frase_da_fala(fala: dict, plano: Plano) -> str:
    texto = fala["texto"].strip()
    if texto[-1] not in ".?!,:":
        texto += "."
    if fala["quem"] == CORO:
        todos = " and ".join(plano.rotulo.values())
        tom = f", {fala['tom'].strip().rstrip('.')}" if fala.get("tom") else ""
        return (f"{todos} (S1), all on screen, shout together in chorus, in their own different voices at the "
                f"same moment{tom}, every mouth visibly opening and closing in sync with every syllable, says: "
                f"<d>[Portuguese] {pronuncia(texto)}</d>")
    quem = ELENCO[fala["quem"]]
    voz = (f"in the voice referenced from <Audio 1> ({quem['voz']})" if tem_voz(fala["quem"])
           else f"in {quem['voz']}")
    # `tom:` (opcional, em inglês) muda só a emoção da fala, não o timbre: a
    # descrição canônica é seca e cansada, e um "Tô!" feliz saiu bravo
    # (corrida-6x1 v1, cena 2).
    if fala.get("tom"):
        voz += f", but on this line {ele(fala['quem'])} sounds {fala['tom'].strip().rstrip('.')}"
    if fala["quem"] in plano.rotulo:
        falante = (f"{plano.rotulo[fala['quem']]} (S1), on screen, {voz}, {quem['pron']} mouth visibly opening and "
                   f"closing in sync with every syllable,")
    else:
        falante = f"{quem['fora'].capitalize()} (S1), heard off-screen {voz},"
    frase = f"{falante} says: <d>[Portuguese] {pronuncia(texto)}</d>"
    # Só "keeps her mouth closed" não bastou: no close das duas senhoras lado a
    # lado as duas falaram a mesma frase juntas (aposentadoria-subiu v2, cena 2).
    outros = [k for k in plano.rotulo if k != fala["quem"]]
    for k in outros:
        pron = ELENCO[k]["pron"]
        frase += (f" {plano.rotulo[k]} does not speak at all: {'he' if pron == 'his' else 'she'} only listens, "
                  f"silent, {pron} lips pressed together and still for the whole shot.")
    if outros and fala["quem"] in plano.rotulo:
        frase += f" Only {plano.rotulo[fala['quem']]} speaks."
    return frase


def prompt(cena: dict, cenario: dict) -> str:
    plano = Plano(cenario, camera_da_cena(cena, cenario))
    cam = plano.cam
    fala = cena.get("fala")
    figurino = cenario.get("figurino", {})
    # `sem_rabo` (por cenário): sentado à mesa, o rabo da descrição canônica
    # aparece atrás da cadeira; ali a aparência vai sem a frase do rabo.
    def aparencia(k: str) -> str:
        a = ELENCO[k]["aparencia"]
        if k in cenario.get("sem_rabo", ()):
            a = re.sub(r",? and a (?:long |tightly curled )?tail[^.]*", "", a)
        return a
    defs = [f"{plano.rotulo[k]} is {ELENCO[k]['nome']}, {ELENCO[k]['quem_e']}"
            f"{(' ' + cam['onde'][k]) if cam['onde'][k] else ''} in <Picture 1>: {aparencia(k)}."
            f"{(' ' + figurino[k]) if k in figurino else ''}"
            for k in cam["visiveis"]]
    # Uma câmera pode ter o próprio "lugar": no close do contracampo, o lugar do
    # cenário citaria o que está atrás do OUTRO (a caixa d'água, o fogão) e o
    # modelo põe de volta, por cima da referência.
    defs.append(f"{plano.lugar} is {cam.get('lugar', cenario['lugar'])}.")
    prefixo = "[reference generation]"
    ret_voz = []
    if fala and tem_voz(fala["quem"]):
        quem = ELENCO[fala["quem"]]
        alvo = plano.rotulo.get(fala["quem"], quem["fora"])
        defs.append(f"<Audio 1> is the voice-timbre reference for {alvo}.")
        prefixo = "[reference generation + audio reference]"
        ret_voz = [f"<Audio 1>: reference - {alvo}'s voice follows the timbre, pitch and delivery of <Audio 1> "
                   "without copying the original signal or its words."]
    elif cena.get("audio"):
        # `audio:` numa cena = referência de melodia e ritmo (o refrão cantado do
        # clipe-domingo, na voz guia da Erika), não de timbre.
        defs.append("<Audio 1> is the melody and rhythm reference for the singing.")
        prefixo = "[reference generation + audio reference]"
        ret_voz = ["<Audio 1>: reference - the dogs sing the words with the same melody, rhythm and timing as "
                   "<Audio 1>, in their own dog voices, without copying the original signal or its timbre."]
    visiveis = " and ".join(plano.rotulo.values())
    um = len(plano.rotulo) == 1
    n = NUMERO.get(len(plano.rotulo), str(len(plano.rotulo)))
    acao = " ".join(p for p in (
        plano.texto(cena.get("antes", "")).strip(),
        frase_da_fala(fala, plano) if fala else ("Nobody speaks." if um else "Neither dog speaks." if n == "two" else "None of the dogs speaks."),
        plano.texto(cena.get("depois", "")).strip(),
    ) if p)
    quem_ret = (f"{visiveis} (appears in [Shot 1]): fully_preserved - the same dog as in <Picture 1>" if um else
                f"{visiveis} (appear in [Shot 1]): fully_preserved - the same {n} dogs as in <Picture 1>")
    return "\n".join([
        "subject_definitions:", *defs,
        "summary:",
        f"{prefixo} {plano.texto(cena.get('resumo', '')).strip()} <Picture 1> supplies "
        f"{'the dog' if um else f'the {n} dogs'}, the room and the framing.",
        "retention_analysis:",
        f"{quem_ret}, unchanged from the first frame to the last; {cam['abertura']}",
        f"{plano.lugar} (appears in [Shot 1]): fully_preserved - the room, the furniture and the light stay exactly "
        "as they are, and the camera framing does not change.",
        "<Picture 1> (composition and subject reference for [Shot 1]): fully_preserved - the shot opens on exactly "
        f"this composition: the same camera position, framing and scale, the same furniture, and "
        f"{'the dog' if um else 'both dogs' if n == 'two' else f'all {n} dogs'} in the same place and at the same size. The framing never widens, "
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
        if f and ((f.get("quem") not in ELENCO and f.get("quem") != CORO) or not f.get("texto")):
            raise RoteiroError(f"cena '{c['id']}': fala precisa de quem ({'/'.join(ELENCO)}) e texto")
        c["frames"] = duracao(c)
    nome = rot.get("cenario", "sala")
    if nome not in CENARIOS:
        raise RoteiroError(f"cenário desconhecido: {nome} (há: {', '.join(CENARIOS)})")
    vlog = rot.get("vlog")
    if vlog and vlog not in ELENCO:
        raise RoteiroError(f"vlog: {vlog}? (é {' ou '.join(ELENCO)})")
    for c in cenas:
        # `cenario:` numa cena troca o cenário só dela (todos-perdem: cada
        # coadjuvante no seu); sem ele, vale o do roteiro.
        cn = c.get("cenario", nome)
        if cn not in CENARIOS:
            raise RoteiroError(f"cena '{c['id']}': cenário desconhecido: {cn} (há: {', '.join(CENARIOS)})")
        c["_cenario"] = cn
        cams = CENARIOS[cn]["cameras"]
        cam = camera_da_cena(c, CENARIOS[cn], vlog)
        if cam not in cams:
            com_vlog = [n for n, ce in CENARIOS.items() if cam in ce["cameras"]]
            raise RoteiroError(f"cena '{c['id']}': o cenário {cn} não tem a câmera {cam} "
                               f"(tem: {', '.join(cams)})"
                               + (f" - cenários com {cam}: {', '.join(com_vlog)}" if com_vlog else ""))
        c["camera"] = cam
        if c.get("fala") and c["fala"]["quem"] != CORO and not tem_voz(c["fala"]["quem"]):
            AVISOS.append(f"{ELENCO[c['fala']['quem']]['nome']} ainda sem assets/"
                          f"{ELENCO[c['fala']['quem']]['voz_ref']}: as falas {'dela' if ELENCO[c['fala']['quem']]['pron'] == 'her' else 'dele'} saem sem voz de referência")
        ref = cams[cam]["ref"]
        if not (ROOT / "assets" / ref).is_file():
            AVISOS.append(f"câmera {cam}: falta assets/{ref} (frame de referência ainda não aprovado)")
        visiveis = cams[cam]["visiveis"]
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
        cenario = CENARIOS[c["_cenario"]]
        partes.append(f"  - id: {c['id']}\n")
        if c["frames"] != 107:
            partes.append(f"    video_frames: {c['frames']}\n")
        if "seed" in c:
            partes.append(f"    seed: {int(c['seed'])}\n")
        partes.append(f"    ref_images: [{cenario['cameras'][c['camera']]['ref']}]\n")
        if c.get("fala") and tem_voz(c["fala"]["quem"]):
            partes.append(f"    ref_audios: [{ELENCO[c['fala']['quem']]['voz_ref']}]\n")
        elif c.get("audio"):
            partes.append(f"    ref_audios: [{c['audio']}]\n")
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
