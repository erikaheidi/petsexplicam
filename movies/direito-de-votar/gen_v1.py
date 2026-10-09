"""Gera movies/direito-de-votar/scripts/v1.yaml: só texto, um plano contínuo encadeado."""
import sys

PRETINHA = ("Pretinha, a small female French bulldog: compact and muscular, a short black coat with faint darker "
            "brindle striping, a white blaze covering the centre of her chest, large upright bat ears set high and "
            "wide, round dark brown eyes, and a short deeply wrinkled muzzle with a flat black nose. She wears no "
            "collar and no harness")
PACOCA = ("Paçoca, a male pug, the opposite build to her: stocky and round, a short fawn-yellow coat, a jet-black mask "
          "over his muzzle and around his eyes, small black folded ears, large round glossy dark eyes, deep wrinkles "
          "on his forehead, and a tightly curled tail. He wears no collar and no harness")
ROOM = ("the dining area of a modest, traditional Brazilian family home: a worn honey-coloured wooden parquet floor "
        "laid in a herringbone pattern, walls painted bright turquoise, an open green-painted wooden shutter window, "
        "a square wooden dining table covered with a white crocheted tablecloth, simple wooden chairs, and a "
        "blue-painted wooden front door off to the right, with warm late-afternoon sunlight falling through the "
        "shutters in soft stripes across the floor")

STYLE = ("The target video is photorealistic live-action footage with warm, natural late-afternoon light and vibrant "
         "but natural colours, shot from a locked-off static camera on a heavy tripod: the picture is perfectly steady "
         "for the whole video, with no camera shake, no handheld movement and no drift.")

# O enquadramento único, idêntico em todas as cenas - é ele que segura o plano.
FRAME = ("The camera is completely static on a tripod at table height, facing the table straight on in a medium "
         "shot, close enough that the dogs fill the upper half of the frame, and it never moves, pans or zooms. The "
         "near edge of the square wooden dining table with the white crocheted tablecloth runs along the bottom of the "
         "frame. <Subject 1> sits upright on a wooden chair behind the table, just left of centre, her head and chest "
         "large in the frame, a plain black laptop with a matte black lid open on the tablecloth in front of her "
         "with its lid facing the camera, so its screen is never visible. A second wooden chair stands behind the "
         "table just right of centre, beside hers. Close behind them, softly out of focus, is the bright turquoise "
         "wall of <Subject 3> with the open green shutter window on the left.")
PACOCA_AT_CHAIR = ("<Subject 2> stands on the seat of the second wooden chair just right of centre, beside her, with "
                   "his front paws resting on the edge of the table, so his head is level with hers.")

VOICE = {
    "pretinha": "an adult female voice, low and calm, with precise diction and an unhurried pace, dry and slightly weary",
    "pacoca": "a young male voice, bright and slightly nasal, fast and excitable, his words tumbling over each other",
}

CLOSER = ("Each dog's mouth moves only while that dog speaks. No humans appear at any point, and no text, lettering, "
          "watermark, letterboxing or black bars appear anywhere in the frame.")

SOUNDSCAPE = ("Quiet indoor room tone, with faint neighbourhood ambience drifting in through the open shutters: distant "
              "voices, birdsong and a far-off motorbike. No barking, whining or growling at any point.")

RET_ROOM = ("<Subject 3> (appears in [Shot 1]): fully_preserved - the room, the table, the laptop and the late-afternoon "
            "light stay exactly as they are, and the camera framing does not change.")

# (id, frames, estado no frame 0 para o retention, resumo, ação+fala)
SCENES = [
    ("entrada", 124, None,
     "<Subject 1> works at the laptop while <Subject 2> comes in, complaining, and climbs onto the chair beside her; once he has settled she turns her head to look at him.",
     "For the first second <Subject 1> is alone in frame, typing with one front paw on the laptop keyboard, "
     "her head tilted down and her eyes lowered to the laptop screen just below her chin, and the second chair is empty. The front door is heard opening off-screen to the right. <Subject 2> "
     "trots in from the right edge of the frame, hops up onto the seat of the empty second chair beside her and "
     "plants his front paws on the edge of the table, complaining loudly as he arrives. <Subject 2> (S1), in "
     "{pacoca}, says: <d>[Portuguese] Poxa vida, todo dia uma regra nova aqui na comunidade!</d> From then until "
     "the last frame he stays standing on that chair beside her, his head level with hers. <Subject 1> keeps her "
     "head down over the laptop while he talks. As soon as he settles beside her, she turns her head towards the right "
     "of the frame and looks straight at him, and she is still looking at him in the last frame."),
    ("reclama", 124, "settled",
     "<Subject 2> keeps complaining; <Subject 1> listens for a moment, then turns back to her laptop.",
     "<Subject 2> turns his head towards <Subject 1>, his forehead wrinkled in frustration, and talks fast with "
     "exaggerated indignation. <Subject 2> (S1), on screen, in the voice referenced from <Audio 1> ({pacoca}), his mouth visibly opening and closing in sync with every syllable, says: <d>[Portuguese] Eu só queria jogar futebol, mas "
     "agora a quadra só está liberada nos finais de semana.</d> He huffs once through his nose. <Subject 1> starts "
     "the shot looking at him, then slowly turns her head back to the laptop, her face still turned towards the camera and only her eyes lowered to the laptop screen just below her chin, so her mouth stays clearly visible, mouth closed."),
    ("estranho", 107, "reading",
     "<Subject 1> answers without taking her eyes off the laptop.",
     "<Subject 1> keeps her face still turned towards the camera and only her eyes lowered to the laptop screen just below her chin, so her mouth stays clearly visible the whole time, one front paw resting on the "
     "keyboard, and never looks up. <Subject 1> (S1), on screen, in {pretinha}, her mouth visibly opening and closing in sync with every syllable, says: <d>[Portuguese] Que "
     "estranho! Essas coisas geralmente são decididas por uma votação.</d> <Subject 2> watches her with his mouth "
     "closed."),
    ("reuniao", 90, "reading",
     "<Subject 1> looks up from the laptop and questions <Subject 2>.",
     "<Subject 1> slowly lifts her eyes from the laptop and turns her head towards the right of the frame, looking straight at "
     "<Subject 2> with a level, knowing stare. <Subject 1> (S1), on screen, in the voice referenced from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, asks: <d>[Portuguese] Você foi na "
     "última reunião, né?</d> She holds the stare until the end. <Subject 2> freezes, mouth closed."),
    ("desconversa", 124, "staring",
     "<Subject 2> dodges the question.",
     "<Subject 2> glances away from her, up at the ceiling and back, avoiding eye contact. <Subject 2> (S1), on screen, in the voice referenced from <Audio 1> "
     "({pacoca}), his mouth visibly opening and closing in sync with every syllable, answers with forced nonchalance: <d>[Portuguese] Reunião? Eu não. Não vou perder tempo com essas "
     "coisas, sou muito ocupado.</d> He ends with an awkward, too-wide grin. <Subject 1> keeps staring at him, "
     "unimpressed, mouth closed."),
    ("whatsapp-1", 90, "staring",
     "<Subject 1> turns back to the laptop to check the neighbourhood group chat.",
     "<Subject 1> turns her head back towards the laptop, her face still turned towards the camera and only her eyes "
     "lowered to the screen, and taps the touchpad twice with one front paw. <Subject 1> (S1), on screen, "
     "in the voice referenced from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, says flatly: <d>[Portuguese] Deixa eu ver aqui no grupo do WhatsApp.</d> <Subject 2> keeps his "
     "mouth closed."),
    ("whatsapp-2", 90, "reading",
     "<Subject 1> reads from the laptop.",
     "<Subject 1> reads from the laptop screen, her face still turned towards the camera and only her eyes lowered to the laptop screen just below her chin, so her mouth stays clearly visible, her eyes moving slightly as she scrolls with one front paw on the "
     "touchpad. <Subject 1> (S1), on screen, in the voice referenced from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, says: <d>[Portuguese] A última reunião foi há dois dias atrás.</d> "
     "<Subject 2> keeps his mouth closed."),
    ("whatsapp-3", 124, "reading",
     "<Subject 1> keeps reading while <Subject 2> leans in.",
     "<Subject 1> keeps reading from the laptop screen, her eyebrows rising very slightly. <Subject 2> leans in "
     "closer, his head tilted. <Subject 1> (S1), on screen, in the voice referenced from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, reads out: <d>[Portuguese] Estou vendo que votaram "
     "sobre fechar a quadra nos dias de semana,</d> <Subject 2> keeps his mouth closed."),
    ("whatsapp-4", 90, "reading",
     "<Subject 1> finishes reading the decision.",
     "<Subject 1> reads on, her face still turned towards the camera and only her eyes lowered to the laptop screen just below her chin, so her mouth stays clearly visible, while <Subject 2> listens with his head tilted. <Subject 1> (S1), on screen, in the voice referenced "
     "from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, continues: <d>[Portuguese] pra diminuir custos com limpeza e manutenção.</d> <Subject 2> keeps his "
     "mouth closed."),
    ("whatsapp-5", 90, "reading",
     "<Subject 1> looks up at the camera for a deadpan beat.",
     "<Subject 1> lifts her eyes from the screen and looks straight into the lens for a dry, deadpan beat before "
     "speaking. <Subject 1> (S1), on screen, in the voice referenced from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, says: <d>[Portuguese] Mas só quatro pessoas foram e votaram:</d> "
     "She lets the pause hang. <Subject 2> looks from her to the laptop, mouth closed."),
    ("nomes", 107, "lens",
     "<Subject 1> reads out four names while <Subject 2> grows more alarmed.",
     "<Subject 1> looks back down at the laptop and counts off names in a slow, even rhythm, a short pause after "
     "each. <Subject 2> listens, his eyes widening a little more with every name. <Subject 1> (S1), on screen, in the voice referenced from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, "
     "reads: <d>[Portuguese] Marcleide, Jeremias, Seu José e Irmã Maria.</d> <Subject 2> keeps his mouth closed."),
    ("protesto", 124, "reading",
     "<Subject 2> protests.",
     "<Subject 2> rears back in outrage with his ears pinned, then leans forward towards <Subject 1>, talking fast. "
     "<Subject 2> (S1), on screen, in the voice referenced from <Audio 1> ({pacoca}), his mouth visibly opening and closing in sync with every syllable, protests: <d>[Portuguese] Mas esse pessoal odeia futebol, sempre reclamam do "
     "barulho, e eles não têm filhos.</d> <Subject 1> keeps her face still turned towards the camera and only her eyes lowered to the laptop screen just below her chin, so her mouth stays clearly visible, mouth closed."),
    ("nao-deveriam", 90, "reading",
     "<Subject 2> insists, and <Subject 1> turns to him.",
     "<Subject 2> bounces his front paws on the edge of the table in indignation. <Subject 2> (S1), on screen, in the voice referenced from <Audio 1> ({pacoca}), his mouth visibly opening and closing in sync with every syllable, exclaims: "
     "<d>[Portuguese] Eles não deveriam decidir!</d> <Subject 1> turns her head slowly from the laptop to look at him, "
     "unimpressed, mouth closed."),
    ("licao-1", 90, "facing",
     "<Subject 1> starts explaining to <Subject 2>.",
     "<Subject 1> lets out a small, patient sigh through her nose and looks at <Subject 2>. <Subject 1> (S1), on screen, in the voice referenced "
     "from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, says: <d>[Portuguese] Bom, infelizmente é isso que acontece,</d> <Subject 2> listens, mouth closed."),
    ("licao-2", 107, "facing",
     "<Subject 1> continues while <Subject 2> deflates.",
     "<Subject 1> speaks to <Subject 2> calmly, while his ears slowly lower. <Subject 1> (S1), on screen, in the voice referenced from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, "
     "continues: <d>[Portuguese] quando você abre mão do seu direito de votar.</d> <Subject 2> keeps his mouth "
     "closed."),
    ("licao-3", 107, "facing",
     "<Subject 1> drives the point home.",
     "<Subject 1> holds a steady look at <Subject 2>, completely composed. <Subject 1> (S1), on screen, in the voice referenced from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, says: "
     "<d>[Portuguese] Você deixa a decisão na mão de outras pessoas.</d> <Subject 2> stares back, mouth closed."),
    ("shrug", 90, "facing",
     "<Subject 1> shrugs and goes back to work.",
     "<Subject 1> looks back at the laptop and, while saying the line, lifts both front shoulders in a small, "
     "deliberate shrug and lowers them again. <Subject 1> (S1), on screen, in the voice referenced from <Audio 1> ({pretinha}), her mouth visibly opening and closing in sync with every syllable, says: <d>[Portuguese] Depois, não "
     "adianta reclamar.</d> <Subject 2> stares at her with his mouth closed."),
    ("decepcao", 90, "reading",
     "<Subject 2> sinks into disappointment while <Subject 1> keeps working.",
     "Neither dog speaks. <Subject 2>'s ears droop, his forehead wrinkles deepen, and his head sinks slowly until his "
     "chin rests on the edge of the table between his front paws. His big glossy eyes look up at <Subject 1> with a crushed, "
     "disappointed expression, and he lets out one long, deflated sigh through his nose. <Subject 1> types calmly on "
     "the laptop. Both stay completely still for the last second."),
]

# O que já é verdade no frame 0 de uma cena encadeada.
STATE = {
    "settled": "she is already seated at the laptop and already turned towards him, looking at him, and he has already come in and already stands on the second chair "
               "beside her with his front paws on the table when the shot opens. He does not walk in again.",
    "staring": "she is already seated, already turned towards him and staring, and he is already standing on the second chair "
               "beside her when the shot opens.",
    "reading": "she is already seated with her face still turned towards the camera and only her eyes lowered to the laptop screen just below her chin, so her mouth stays clearly visible, and he is already standing on the second chair "
               "beside her when the shot opens.",
    "lens": "she is already seated, already looking into the lens, and he is already standing on the second chair "
              "beside her when the shot opens.",
    "facing": "she is already seated and already turned towards him, and he is already standing on the second chair "
              "beside her when the shot opens.",
}


# Quem fala em cada cena com referência de voz. Cada cena leva só a voz de quem
# fala nela, sempre como <Audio 1>. As cenas 1-3 ficam de fora: estão aprovadas,
# e são a origem das duas vozes (Paçoca na 1, Pretinha na 3).
PACOCA_SCENES = {"reclama", "desconversa", "protesto", "nao-deveriam"}
PRETINHA_SCENES = {"reuniao", "whatsapp-1", "whatsapp-2", "whatsapp-3", "whatsapp-4",
                   "whatsapp-5", "nomes", "licao-1", "licao-2", "licao-3", "shrug"}
VOICE_REF = {"pacoca": "pacoca-voz.wav", "pretinha": "pretinha-voz.wav"}


# Nova tentativa de uma cena: outra seed. (nao-deveriam saiu com o Paçoca a
# 381 Hz e o QC reprovou, mas a Erika ouviu e aprovou - fica a original.)
SEEDS = {}


def speaker(sid):
    return "pacoca" if sid in PACOCA_SCENES else "pretinha" if sid in PRETINHA_SCENES else None


# A voz do Paçoca nas cenas independentes. "a young male voice" puxava o modelo
# para um registro de homem adulto (~157 Hz na primeira cena 5) e ele ignorava
# <Audio 1>, que é aguda (~296 Hz). Texto e referência precisam concordar. As
# cenas 1-4 mantêm o texto antigo: estão aprovadas.
VOICE_SA = dict(VOICE, pacoca="a high-pitched, boyish voice, like an excited young boy, bright and slightly "
                              "nasal, fast, his words tumbling over each other")

# As cenas 1-3 são encadeadas e congeladas. Da 4 em diante cada cena é
# independente: abre na composição de REF_FRAME (um frame da cena 3) em vez de
# na cauda da anterior, para os defeitos não se acumularem pelo chain.
CHAINED = {"entrada", "reclama", "estranho"}
REF_FRAME = "dupla-referencia.png"

PRETINHA_P = PRETINHA.replace("Pretinha, a small female French bulldog:",
                              "Pretinha, the small female French bulldog on the left in <Picture 1>:")
PACOCA_P = PACOCA.replace("Paçoca, a male pug, the opposite build to her:",
                          "Paçoca, the male pug on the right in <Picture 1>, the opposite build to her:")
ROOM_P = ROOM.replace("the dining area of", "the dining area shown in <Picture 1>,", 1).replace(
    "<Picture 1>, a modest", "<Picture 1>, a modest")
POSTURE = ("<Subject 1> sits up tall the whole time with her chin above the top of the laptop lid, so her whole "
           "face and mouth stay visible; she never sinks down behind the laptop.")
RET_PICTURE = ("<Picture 1> (composition and subject reference for [Shot 1]): fully_preserved - the shot opens on "
               "exactly this composition: the same camera position, framing and scale, the same table, laptop, "
               "chairs, window and door, and both dogs in the same places and at the same size. The framing never "
               "widens, tilts or drifts.")


# A cena 4 foi aprovada com a abertura antiga (o estado vindo do roteiro
# encadeado, que fazia a Pretinha abrir de cabeça baixa atrás do notebook) e
# fica congelada assim. Da 5 em diante a cena abre exatamente na pose de
# <Picture 1>; olhar para a tela ou para ele vira ação dentro da cena.
OPEN_AS_PICTURE = ("as the shot opens they are posed exactly as in <Picture 1>: she sits upright with her chin above "
                   "the top of the laptop lid and her whole face visible, and he stands on the second chair beside "
                   "her with his front paws on the table.")
LEGACY_OPENING = {"reuniao"}


def standalone_prompt(state, summary, body, voiced=None, sid=None) -> str:
    defs = [f"<Subject 1> is {PRETINHA_P}.", f"<Subject 2> is {PACOCA_P}.", f"<Subject 3> is {ROOM_P}."]
    prefix = "[reference generation]"
    if voiced:
        who = "<Subject 2>" if voiced == "pacoca" else "<Subject 1>"
        defs.append(f"<Audio 1> is the voice-timbre reference for {who}.")
        prefix = "[reference generation + audio reference]"
    summary = f"{prefix} {summary} <Picture 1> supplies the two dogs, the room and the framing."
    ret = [f"<Subject 1> and <Subject 2> (appear in [Shot 1]): fully_preserved - the same two dogs as in "
           f"<Picture 1>, unchanged from the first frame to the last; "
           f"{STATE[state] if sid in LEGACY_OPENING else OPEN_AS_PICTURE}",
           RET_ROOM, RET_PICTURE]
    if voiced:
        ret.append(f"<Audio 1>: reference - {'<Subject 2>' if voiced == 'pacoca' else '<Subject 1>'}'s voice "
                   "follows the timbre, pitch and delivery of <Audio 1> without copying the original signal or "
                   "its words.")
    shot = f"[Shot 1] The shot opens on the composition of <Picture 1>. {FRAME} {PACOCA_AT_CHAIR} {POSTURE}"
    return "\n".join([
        "subject_definitions:", *defs,
        "summary:", summary,
        "retention_analysis:", *ret,
        "detailed_description:", STYLE, f"{shot} {body.format(**VOICE_SA)} {CLOSER}",
        f"overall_soundscape: {SOUNDSCAPE}",
        "non_diegetic_music: N/A",
    ])


def prompt(state, summary, body, voiced=None) -> str:
    defs = [f"<Subject 1> is {PRETINHA}.", f"<Subject 2> is {PACOCA}.", f"<Subject 3> is {ROOM}."]
    if voiced:
        who = "<Subject 2>" if voiced == "pacoca" else "<Subject 1>"
        defs.append(f"<Audio 1> is the voice-timbre reference for {who}.")
        summary = f"[audio reference] {summary}"
    if state is None:
        ret = ["<Subject 1> (appears in [Shot 1]): fully_preserved - her build, black brindle coat, white chest "
               "blaze, upright bat ears and dark eyes stay the same from the first frame to the last.",
               "<Subject 2> (appears in [Shot 1]): fully_preserved - his round build, fawn coat, black mask, folded "
               "ears and forehead wrinkles stay the same from his entrance to the last frame.",
               RET_ROOM]
        shot = f"[Shot 1] {FRAME}"
    else:
        ret = [f"<Subject 1> and <Subject 2> (appear in [Shot 1]): fully_preserved - the same two dogs as the previous "
               f"shot; {STATE[state]}",
               RET_ROOM]
        shot = f"[Shot 1] The same static shot continues without a cut. {FRAME} {PACOCA_AT_CHAIR}"
    return "\n".join([
        "subject_definitions:", *defs,
        "summary:", summary,
        "retention_analysis:", *ret,
        *([f"<Audio 1>: reference - {'<Subject 2>' if voiced == 'pacoca' else '<Subject 1>'}'s voice follows "
           "the timbre, pitch and delivery of <Audio 1> without copying the original signal or its words."]
          if voiced else []),
        "detailed_description:", STYLE, f"{shot} {body.format(**VOICE)} {CLOSER}",
        f"overall_soundscape: {SOUNDSCAPE}",
        "non_diegetic_music: N/A",
    ])


HEADER = """\
# direito-de-votar - Pretinha explica ao Paçoca o que acontece quando você abre
# mão do seu direito de votar. Rascunho em drafts/direito-de-votar.md; elenco
# em ELENCO.md.
#
#   ./mm render movies/direito-de-votar/scripts/v1.yaml --dry-run
#   ./mm render movies/direito-de-votar/scripts/v1.yaml --only 1
#   ./mm render movies/direito-de-votar/scripts/v1.yaml
#
# SÓ TEXTO, UM PLANO CONTÍNUO. Nenhuma ref_image e nenhum anchor: as refs
# passam por todo passo de amostragem e encareciam cada cena. A dupla nasce da
# descrição na cena 1 e o chain (overlap_frames: 5, vídeo E som) a carrega pelas
# 17 seguintes. Mesmo esquema do josy-hangover-dream no workspace pessoal.
#
# Consequências:
#   - A Pretinha NÃO vai sair igual à Josy, nem o Paçoca igual à foto de perfil.
#     Se a identidade importar, o atalho é pôr refs só na cena 1.
#   - Uma câmera só, estática, a mesma frase de enquadramento em toda cena. Um
#     movimento de câmera liberado alargaria todas as cenas seguintes.
#   - Re-renderizar a cena N invalida N+1 em diante (o chain usa o conteúdo).
#   - Formato H3: as seis seções Ref2VA, mas só com <Subject N> - sem
#     <Picture N> (não há imagem para resolver) e sem o prefixo [task type].
#     Nas cenas encadeadas, retention_analysis diz o que JÁ é verdade no frame
#     0, para a cena não repetir a ação anterior (o Paçoca entrar de novo).
#
# FALAS: literais do rascunho, uma frase (ou meia) por cena para caber no tempo
# - 90 frames = 3,75 s (até ~9 palavras), 107 = 4,46 s (~11), 124 = 5,17 s
# (~13; o Paçoca fala mais rápido). Normalizações em relação ao rascunho:
# "reuniãom" -> "reunião", "4" -> "quatro" (o modelo fala o que lê), "tem" ->
# "têm", "WhatsApp", e reticências viraram ponto (o guia H3 só aceita , . ? !).
# O speaker ID (S1) é por cena: o primeiro a falar NAQUELE clipe.
#
# POSIÇÕES: Pretinha na cadeira atrás da mesa, à esquerda do centro; Paçoca em
# pé na segunda cadeira, à direita, patas na mesa. Olhar para a tela é descrito
# pela cabeça ("head tilted down, eyes lowered to the laptop screen just below
# her chin") - "eyes on the laptop" sozinho fazia ela encarar a câmera. Olhar
# para o Paçoca = virar a cabeça para a direita do quadro.
#
# A PARTIR DA CENA 4, SEM CHAIN. A primeira passada encadeou as 18 cenas e a
# qualidade degradou a cada elo: a câmera foi subindo (teto e luminária entraram
# no quadro na 6-7), a imagem ficou estranha, e a Pretinha terminava escondida
# atrás do notebook - a cena seguinte herdava isso e ela falava sem mostrar a
# boca. Agora as cenas 1-3 (aprovadas) seguem encadeadas e da 4 em diante cada
# cena é independente: abre na composição de assets/dupla-referencia.png
# (<Picture 1>, o frame 90 da cena 3: os dois de boca fechada, ela com o queixo
# acima da tampa, enquadramento original). Cada cena pode ser refeita sozinha.
#
# VOZES: assets/pacoca-voz.wav (recortada da cena 1) e assets/pretinha-voz.wav
# (recortada da cena 3), as duas aprovadas, entram como ref_audios em toda cena
# em que aquele personagem fala - sempre <Audio 1>, porque cada cena leva só a
# voz de quem fala nela. O chain só carrega ~0,2 s de som, pouco para segurar um
# timbre.
# Precisa do moviemakr com suporte a ref_audios (branch ref-audios).
#
# AS CENAS 1-3 ESTÃO CONGELADAS: o texto delas é o que foi renderizado e aprovado.
# Mudar qualquer frase compartilhada que apareça nela (descrições, cenário,
# enquadramento) a invalida - e, pelo chain, todas as seguintes.
#
# FALA VISÍVEL: toda fala diz "on screen ... her/his mouth visibly opening and
# closing in sync with every syllable", e olhar para a tela é "face still turned
# towards the camera and only her eyes lowered" - com a cabeça baixa a Pretinha
# virava narradora fora de quadro (cena 3 da primeira passada).
#
# MÚSICA: N/A em todas as cenas. Para pôr trilha, coloque um arquivo em
# assets/ e aponte output.music para ele: é mixado na montagem.
"""

ENGINE = """\
name: direito-de-votar
backend: comfy
comfy:
  url: http://127.0.0.1:8188
  input_dir: /home/erika/Projects/rocm-comfyui/data/input
  output_dir: /home/erika/Projects/rocm-comfyui/data/output
  diffusion_model: minimax_h3_fastvideo_vsa_datafree_1300step_4step_int8_convrot.safetensors
  text_encoder: qwen3vl_32b_minimax_h3_bf16.safetensors
  video_vae: minimax_h3_video_vae_int8_convrot.safetensors
  audio_vae: minimax_h3_audio_vae_fp32.safetensors
  # 8 passos com start_percent 0.2 / end_percent 1.0 - a config estável do
  # josy-gamer v6 e do josy-hangover-dream. Com 4 passos e a atenção esparsa
  # ligada desde o primeiro passo a câmera TREME (medido com vidstabdetect:
  # ~0,6-1,8 px/frame de tremor vertical contra ~0,02 nesta config). Os primeiros
  # 20% em atenção densa fixam a estrutura global, câmera inclusive.
  steps: 8
  sol_attn:
    mode: vsa
    keep_percent: 20.0
    min_tokens: 4096     # o default 12288 do node é um crossover de CUDA
    start_percent: 0.2
    end_percent: 1.0
    verbose: true        # sem isso, toda falha deste node é silenciosa
defaults:
  # 9:16 vertical - o formato de Reels.
  width: 544
  height: 960
  fps: 24
  video_frames: 107
  seed: 2026
  style_suffix: ""
  overlap_frames: 5
continuity:
  anchors: []
  chain_from_previous: true
output:
  container: mp4
  audio: keep
  music: null
scenes:
"""


def main(out: str) -> None:
    parts = [HEADER, ENGINE]
    for sid, frames, state, summary, body in SCENES:
        parts.append(f"  - id: {sid}\n")
        if state is None:
            parts.append("    chain_from_previous: false\n")
        if frames != 107:
            parts.append(f"    video_frames: {frames}\n")
        if sid not in CHAINED:
            parts.append("    chain_from_previous: false\n")
            parts.append(f"    ref_images: [{REF_FRAME}]\n")
        if sid in SEEDS:
            parts.append(f"    seed: {SEEDS[sid]}\n")
        if speaker(sid):
            parts.append(f"    ref_audios: [{VOICE_REF[speaker(sid)]}]\n")
        parts.append("    prompt: |-\n")
        parts.extend(f"      {line}\n" for line in (prompt(state, summary, body, speaker(sid)) if sid in CHAINED
                                    else standalone_prompt(state, summary, body, speaker(sid), sid)).split("\n"))
    with open(out, "w") as f:
        f.write("".join(parts))


main(sys.argv[1])
