"""clipe-domingo, versão cortejo: um único passeio encadeado pela rua do bairro.

    python3 movies/clipe-domingo/cortejo.py      # -> scripts/cortejo-v1.yaml

A v1 (roteiro.yaml, cenas independentes do dialogo.py) não tinha cara de clipe:
17 cortes secos, cada um num frame diferente. Esta versão segue a receita dos
vídeos da Josy (~/moviemakr-workspace, josy-disco-dream): a cadeia inteira com
overlap, uma ação por cena, a câmera recuando à frente do grupo, e cada cena
terminando no quadro que a próxima herda.

O cortejo: a Lurdes sai do portão e começa a descer a rua; a cada cena um
amigo entra no quadro pela lateral e passa a andar com o grupo (Tião, Cida,
José, Renato, Paçoca, Pretinha). Os sete param, se juntam como no frame
cenario-clipe-todos.png e cantam o refrão (refrao-{1,2}.wav = melodia).

Referências (a regra da Josy: uma foto só vai para a cena em que ela é verdade):
  - nenhum anchor: nenhuma foto vale para as 10 cenas;
  - a cena 1 abre no frame cenario-clipe-lurdes-acao.png;
  - o close de branco de cada um (cenario-clipe-<pet>-close.png) entra como
    referência de identidade a partir da cena em que ele aparece, e só pelo
    rosto, pela pelagem e pela roupa;
  - o frame dos sete juntos só entra quando eles já pararam (cenas 8 a 10).
No comfy o encadeamento não ocupa índice: <Picture N> segue ref_images.

Elenco e figurino vêm do tools/dialogo.py (ELENCO, CENARIOS["clipe"]), palavra
por palavra. Não edite o YAML gerado: mude este arquivo e rode de novo.
"""

import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent.parent / "tools"))
from dialogo import CENARIOS, ELENCO, ENGINE, FECHO, ele, o  # noqa: E402

VERSAO = "v1"
SEED = 2510
ORDEM = ["lurdes", "tiao", "cida", "jose", "renato", "pacoca", "pretinha"]
# de que lado do quadro cada um entra (alterna para o grupo não pender)
LADO = {"tiao": "right", "cida": "left", "jose": "right", "renato": "left", "pacoca": "right",
        "pretinha": "left"}
TODOS = "cenario-clipe-todos.png"
# frame de abertura: o portão num muro paralelo à rua, na calçada da direita
# (o cenario-clipe-lurdes-acao punha o muro no meio da pista).
# Opções em movies/cenarios/scripts/clipe-cortejo.yaml.
ABERTURA = "cenario-clipe-lurdes-abertura.png"
# O node gasta um tempo enorme codificando referências antes de gerar, e o tempo
# cresce com cada imagem: 19 min com 1, 34 com 2, 46 com 3, ~70 com 4 (24/10).
# Até a cena SO_NOVO vão os closes de todos; depois, só o de quem chega (os
# outros vêm pela cadeia), e no fim só o frame dos sete juntos.
SO_NOVO = 4
# seed por cena: com a seed padrão a cena 5 inclinou a câmera para o céu duas
# vezes (o texto sozinho não mudou o movimento).
SEEDS = {"05-renato": 7311, "07-pretinha": 4242}
# o modelo duplicou cachorros na cena 7 (v1) e no frame do grupo (1ª rodada)
SETE = ("There are exactly seven dogs in the whole shot, one of each, and no other dog ever appears: only one "
        "English bulldog, only one cocker spaniel, only one French bulldog.")
NIVEL = ("The camera stays level at the height of the dogs' heads the whole time and never tilts up towards the "
         "sky: the dogs fill the lower half of the frame and only a narrow band of sky shows at the very top.")
# cenas que abrem num corte seco em vez de encadear
# O refrão abre num corte seco no frame do grupo: a cena 7 (v1) saiu com nove
# cachorros (dois Renatos, duas Lurdes) e a câmera para o céu (25/10, 14h30).
CORTES = {"05-renato", "08-refrao-1"}
# O grupo reunido (Erika, 25/10): mais aberto que o cenario-clipe-todos, que
# cortava a Pretinha na borda, e com ela no centro da fileira da frente.
# movies/cenarios/scripts/clipe-cortejo-grupo2.yaml, opção centro-a. A cena 7
# (a entrada da Pretinha, com destaque) termina nessa arrumação e o refrão
# encadeia dela; o encontro (antiga cena 8, corte seco) saiu.
GRUPO = "cenario-clipe-grupo.png"
ARRUMACAO = ("in the front row, sitting, from left to right: {pacoca}, {pretinha} in the centre, {cida} and "
             "{lurdes}; in the back row, standing behind them, from left to right: {jose}, {tiao} and {renato}")
# A cena 5 encadeada deu o Renato gigante, de pernas compridas, da altura do
# Tião (Erika, 25/10). Ela agora abre num corte seco num frame nivelado
# (movies/cenarios/scripts/clipe-cortejo-5.yaml) e o tamanho dele é dito.
ABERTURA5 = "cenario-clipe-renato-abertura.png"
ALTURA_RENATO = ("He is short, low to the ground and broad, with short thick bowed legs and a deep wide chest close "
                 "to the ground: his back is no higher than Lurdes's back and his head only reaches the height of "
                 "Tião's chest; Tião and José are the tallest of the friends.")
# Nas cenas 5-7 (v1) o Tião virou Renato: os dois são brancos com manchas e só
# ia o close do Renato (Erika, 25/10). Agora o close do Tião vai junto e a
# diferença entre os dois é dita.
TIAO_NAO_RENATO = ("He is not a bulldog and looks nothing like Renato: he has a long, narrow muzzle, a slim head, "
                   "tall straight legs and semi-floppy ears, and no jowls, wrinkles or pushed-in face.")
TIAO = "cenario-clipe-tiao-close.png"
NUM = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}

CLIPE = CENARIOS["clipe"]
RUA = ("a quiet, tidy residential street of a middle-class Brazilian neighbourhood on a sunny Sunday morning: "
       "single-storey houses in soft colours with low front walls, iron gates and small gardens, trees along the "
       "sidewalk, a blooming yellow ipê tree, and strings of small green, yellow and a few red paper bunting flags "
       "across the street")

ESTILO = ("The target video is photorealistic live-action footage, outdoors on a residential street on a bright "
          "Sunday morning, in soft, warm sunlight and vibrant but natural colours, cinematic and joyful, like a "
          "music video. The camera glides smoothly on a dolly, perfectly steady, with no shake and no handheld "
          "wobble.")

TRAVELLING = ("The camera glides slowly backwards down the middle of the street ahead of the walking friends, at "
              "exactly their slow walking pace and at the height of their heads, so they never get closer and never "
              "get further away. It stays far enough back that every walking dog fits in the frame from ears to "
              "paws, the group in the lower half of the vertical frame and the street, the houses, the yellow ipê "
              "and the bunting above and behind them.")

# A v1 saiu com cara neutra: os closes de referência são neutros e o modelo
# copia. A expressão é negada na retention_analysis e o sorriso, descrito pela
# boca e pelos olhos, se repete em toda cena.
SORRISO = ("a big, happy dog smile: the mouth open and relaxed, the corners of the mouth pulled up, the pink tongue "
           "showing, the eyes bright, soft and crinkled with joy")
FELIZ = f"Every one of them is visibly happy and beaming the whole time, with {SORRISO}, from the first frame to the last."
NAO_NEUTRO = "the neutral expression of that picture is not retained: here {ele} beams with " + SORRISO + "."

# A Erika achou a Lurdes da cena 1 correndo: é "andar com fé", um passeio lento.
PASSO = ("a slow, calm, unhurried stroll, one deliberate step at a time, like a peaceful Sunday procession; never "
         "trotting, hurrying or running")
# Da cena 3 em diante: a câmera recua um pouco mais rápido que o grupo, para o
# plano abrir aos poucos enquanto o grupo cresce.
TRAVELLING_ABRE = ("The camera glides slowly backwards down the middle of the street ahead of the walking friends, "
                   "at the height of their heads, a little faster than their slow walking pace, so the shot "
                   "gradually widens and they grow slightly smaller in the frame, never closer to the lens.")

ANDAR = (f"They walk at {PASSO}, heads up, looking ahead and now and then at each other, each one walking on four "
         f"legs. " + FELIZ)

SOM = ("Gentle Sunday-morning street ambience: birdsong, a light breeze, the soft flutter of the paper bunting, "
       "distant church bells and the soft patter of paws on the asphalt. No music and no barking, whining or "
       "growling at any point.")


def nome(k: str) -> str:
    return ELENCO[k]["nome"]


def definicao(k: str, rotulo: str, pic: int | None) -> str:
    e = ELENCO[k]
    # o cardigã colorido das senhoras brigaria com o branco do figurino
    aparencia = re.sub(r"\. She wears a plain \w+(-\w+)? hand-knitted cardigan[^.]*", "", e["aparencia"])
    onde = f"in <Picture {pic}>" if pic else "already walking with the group at the end of the previous shot"
    return (f"{rotulo} is {e['nome']}, {e['quem_e']} {onde}: {aparencia}. "
            f"{CLIPE['figurino'][k]}")


def retencao_close(k: str, rotulo: str, pic: int) -> str:
    return (f"{rotulo} (appears in [Shot 1]): partially_preserved - the same dog as in <Picture {pic}>: "
            f"{ELENCO[k]['pron']} face, coat, markings, proportions and white outfit are retained. The low camera "
            f"angle and the close framing of <Picture {pic}> are not: here {ele(k)} is seen full body, walking "
            f"with the others. Also, {NAO_NEUTRO.format(ele=ele(k))}")


def quadro(n: int, fim: bool = False) -> str:
    """Quanto do quadro o grupo ocupa: abre conforme o grupo cresce."""
    if n >= 5:
        # Na cena 5 (v1) "the lower third" fez a câmera inclinar para o céu, com
        # o grupo cortado na borda de baixo. Daqui em diante: câmera nivelada,
        # patas no quadro, faixa de rua embaixo e pouco céu.
        nivel = ("The camera stays level at the height of the dogs' heads and never tilts up towards the sky. "
                 f"All {NUM[n]} dogs are fully inside the frame, none cut off at the edges, every one visible "
                 "from ears to paws with a strip of asphalt below their paws; the group fills the lower half "
                 "of the vertical frame, the houses and the bunting above them, and only a narrow band of sky "
                 "at the very top.")
        return nivel if not fim else f"every face clearly visible. {nivel}"
    alt = {3: "the lower half", 4: "the lower half"}[n]
    if fim:
        return (f"small enough that all {NUM[n]} fit across the frame from ears to paws, in {alt} of the vertical "
                f"frame, with a little open street on both sides of the group and every face clearly visible.")
    return (f"The shot is wider than before: the camera keeps well back, so the whole group fits across the frame "
            f"from ears to paws in {alt} of the vertical frame, with open street on both sides.")


def lista(ks: list[str], rot: dict) -> str:
    r = [rot[k] for k in ks]
    return r[0] if len(r) == 1 else ", ".join(r[:-1]) + " and " + r[-1]


def cena(i: int) -> dict:
    """Cenas 1-7: o cortejo cresce. A cena i tem os i primeiros de ORDEM."""
    grupo = ORDEM[:i]
    novo = grupo[-1]
    antigos = grupo[:-1]
    if i == 1:
        refs = [ABERTURA]
        pic = {"lurdes": 1}
    elif f"{i:02d}-{novo}" in CORTES:
        refs = [ABERTURA5, f"cenario-clipe-{novo}-close.png", TIAO]
        pic = {k: 1 for k in antigos} | {novo: 2, "tiao": 3}
    elif i <= SO_NOVO:
        refs = [f"cenario-clipe-{k}-close.png" for k in grupo]
        pic = {k: n for n, k in enumerate(grupo, 1)}
    else:
        # só o close de quem chega: os outros vêm pela cadeia (ver SO_NOVO)
        refs = [f"cenario-clipe-{novo}-close.png", TIAO]
        pic = {k: None for k in antigos} | {novo: 1, "tiao": 2}
    rot = {k: f"<Subject {n}>" for n, k in enumerate(grupo, 1)}
    lugar = f"<Subject {len(grupo) + 1}>"

    defs = [definicao(k, rot[k], pic[k]) for k in grupo]
    if "renato" in grupo:
        n = grupo.index("renato")
        defs[n] += " " + ALTURA_RENATO.replace("Lurdes", rot["lurdes"]).replace("Tião", rot["tiao"]).replace(
            "José", rot["jose"])
    if "renato" in grupo:
        defs[grupo.index("tiao")] += " " + TIAO_NAO_RENATO.replace("Renato", rot["renato"])
    defs.append(f"{lugar} is {RUA}.")
    corte = f"{i:02d}-{novo}" in CORTES

    if i == 1:
        k = "lurdes"
        resumo = (f"[reference generation] The music video's opening shot. {rot[k]} steps out of her front gate "
                  f"onto {lugar} and sets off walking down the street towards the camera, which starts gliding "
                  f"backwards ahead of her. <Picture 1> supplies the dog, the gate, the street and the opening "
                  f"framing.")
        ret = [f"<Picture 1> ([Shot 1] opening frame): partially_preserved - the shot opens on exactly this "
               f"composition: the street running away through the middle of the frame, and {rot[k]} on the right-hand "
               f"sidewalk at the open gate of her low front wall, in her white cardigan; as she walks out the camera "
               f"starts to glide backwards, so the framing does not stay fixed.",
               f"{rot[k]} (appears in [Shot 1]): fully_preserved - the same dog as in <Picture 1>, in the same "
               f"white cardigan, from the first frame to the last; only her expression changes, as {NAO_NEUTRO.format(ele='she')}"]
        acao = (f"[Shot 1] The shot opens on the composition of <Picture 1>: the street of {lugar} running "
                f"straight away through the middle of the frame, and {rot[k]} on the right-hand sidewalk at the "
                f"open iron gate in her low front wall, beaming with {SORRISO}. She lowers her raised paw, steps "
                f"off the kerb into the street and turns to walk down the middle of it towards the camera at {PASSO}, "
                f"her long ears swaying gently with each step. The camera begins to glide slowly backwards ahead of her, at the "
                f"height of her head, a little faster than she walks, so she never comes closer than in the first "
                f"frame. In the last frame she walks alone down the middle of the street towards the camera, small "
                f"in the frame: her whole body, from ears to paws, in the lower third of the vertical frame, with "
                f"plenty of open street on both sides of her, and the houses, the yellow ipê and the bunting above "
                f"and behind her. She is visibly happy and beaming the whole time, with {SORRISO}, "
                f"from the first frame to the last.")
    elif corte:
        lado = LADO[novo]
        resumo = (f"[reference generation] After a cut, the music video picks up the walk: {lista(antigos, rot)} "
                  f"walk side by side down {lugar} towards the camera, which glides backwards ahead of them, and "
                  f"{rot[novo]}, waiting at his gate, joins them. <Picture 1> supplies the opening framing, the "
                  f"four walkers and {rot[novo]} at his gate; <Picture 2> supplies {rot[novo]}'s face.")
        ret = [f"<Picture 1> ([Shot 1] opening frame): fully_preserved - the shot opens on exactly this "
               f"composition: the level camera at the height of the dogs' heads, the four friends walking side by "
               f"side, {rot[novo]} at his gate on the {lado}-hand sidewalk, and the sizes of all five dogs relative "
               f"to each other.",
               *[f"{rot[k]} (appears in [Shot 1]): fully_preserved - the same dog as in <Picture 1>, unchanged, "
                 f"beaming with {SORRISO}." for k in antigos if k != "tiao"],
               f"{rot['tiao']} (appears in [Shot 1]): fully_preserved - the same dog as in <Picture 1>, with the "
               f"long-muzzled face of <Picture 3>, unchanged, beaming with {SORRISO}; <Picture 3> only adds the "
               f"detail of his face.",
               f"{rot[novo]} (appears in [Shot 1]): fully_preserved - the same dog as in <Picture 1>, at the same "
               f"size relative to the others; <Picture 2> only adds the detail of his face, and its low angle, "
               f"close framing and neutral expression are not retained: here he beams with {SORRISO}."]
        acao = (f"[Shot 1] The shot opens on the composition of <Picture 1>, after a cut: {lista(antigos, rot)} "
                f"walk side by side down the middle of {lugar} towards the camera, and {rot[novo]} stands at the "
                f"open gate of his house on the {lado}-hand sidewalk, just beside their path. {TRAVELLING} "
                f"{quadro(len(grupo))} {rot[novo]} waves one front paw as they come alongside, and the others turn "
                f"their heads towards him and smile. He steps off the kerb with his short legs and falls into step "
                f"on the {lado} side of the group, staying low and broad beside them, his head at the height of "
                f"{rot['tiao']}'s chest, and all five walk on together. {ANDAR} In the last frame the "
                f"five friends walk side by side towards the camera, {quadro(len(grupo), fim=True)}")
    else:
        lado = LADO[novo]
        resumo = (f"[reference generation] The music video continues without a cut from the previous shot: "
                  f"{lista(antigos, rot)} {"walks" if len(antigos) == 1 else "walk"} down {lugar} towards the camera, which glides backwards ahead of "
                  f"them, and {rot[novo]} steps into the frame from the {lado} and joins them, so {NUM[len(grupo)]} "
                  f"friends walk on together. The pictures supply the dogs' faces, coats and white outfits.")
        ret = [retencao_close(k, rot[k], pic[k]) if pic[k] else
               (f"{rot[k]} (appears in [Shot 1]): fully_preserved - the same dog as at the end of the previous "
                f"shot, with the same face, coat, markings and white outfit, still beaming with {SORRISO}.")
               for k in grupo]
        sozinha = "walks" if len(antigos) == 1 else "walk side by side"
        if i == 2:  # já renderizada e aprovada: o texto não muda
            acao = (f"[Shot 1] Continuing without a cut from the previous shot, {lista(antigos, rot)} {sozinha} down "
                    f"the middle of {lugar} towards the camera. {TRAVELLING} At about one second, {rot[novo]} walks "
                    f"calmly into the frame from the sidewalk on the {lado} edge, waving one front paw in greeting, and the "
                    f"others turn their heads towards {o(novo)} and smile. {rot[novo]} falls into step on the {lado} "
                    f"side of the group, and {"both" if len(grupo) == 2 else "all " + NUM[len(grupo)]} walk on together. {ANDAR} In the last frame the "
                    f"{NUM[len(grupo)]} friends walk side by side towards the camera, every face clearly visible.")
        else:
            # Na cena 2 o Tião entrou rente à lente e tapou meio quadro. Daqui em
            # diante quem chega já está no quadro desde o início, ao lado do
            # caminho, na mesma distância do grupo; e o plano abre a cada cena.
            acao = (f"[Shot 1] Continuing without a cut from the previous shot, {lista(antigos, rot)} {sozinha} "
                    f"down the middle of {lugar} towards the camera. {TRAVELLING_ABRE} {quadro(len(grupo))} From the "
                    f"first frame, {rot[novo]} is already in the picture, standing on the {lado}-hand sidewalk "
                    f"at the open gate of {ELENCO[novo]['pron']} house, just beside the group's path, at the same "
                    f"distance from the camera as the group and the same size as them in the frame, never closer "
                    f"to the lens than the others. {ele(novo).capitalize()} waves one front paw as they come "
                    f"alongside, and the others turn their heads towards {o(novo)} and smile. {rot[novo]} steps "
                    f"off the kerb and falls into step on the {lado} side of the group, and all "
                    f"{NUM[len(grupo)]} walk on together. {ANDAR} In the last frame the {NUM[len(grupo)]} friends "
                    f"walk side by side towards the camera, {quadro(len(grupo), fim=True)}")
    return {"id": f"{i:02d}-{novo}", "refs": refs, "defs": defs, "resumo": resumo, "ret": ret,
            "acao": acao, "som": SOM}


def cena_pretinha() -> dict:
    """Cena 7: os seis param e a Pretinha entra com destaque, indo para o centro do grupo."""
    rot = {k: f"<Subject {n}>" for n, k in enumerate(ORDEM, 1)}
    lugar = f"<Subject {len(ORDEM) + 1}>"
    pic = {k: 1 for k in ORDEM} | {"pretinha": 2}
    defs = [definicao(k, rot[k], pic[k]) for k in ORDEM]
    defs[ORDEM.index("renato")] += " " + ALTURA_RENATO.replace("Lurdes", rot["lurdes"]).replace(
        "Tião", rot["tiao"]).replace("José", rot["jose"])
    defs[ORDEM.index("tiao")] += " " + TIAO_NAO_RENATO.replace("Renato", rot["renato"])
    defs.append(f"{lugar} is {RUA}, as in <Picture 1>.")
    seis = [k for k in ORDEM if k != "pretinha"]
    arr = ARRUMACAO.format(**rot)
    P = rot["pretinha"]
    resumo = (f"[reference generation] The music video continues without a cut: the six friends walking down "
              f"{lugar} come to a stop, and {P}, the star, steps out of her gate and walks to the centre of the "
              f"group; the others gather around her and the shot ends on the group of <Picture 1>. <Picture 1> "
              f"supplies the final composition and the seven dogs; <Picture 2> supplies {P}'s face.")
    ret = [f"<Picture 1> ([Shot 1] final composition): fully_preserved in the last frame - the shot ENDS on this "
           f"composition: the seven friends gathered in the middle of the street, {arr}, the level camera at the "
           f"height of the dogs' heads, the wide framing with all seven fully inside and open street on both sides.",
           f"{lista(seis, rot)} (appear in [Shot 1]): fully_preserved - the same dogs as at the end of the "
           f"previous shot and as in <Picture 1>, with the same faces, coats, sizes and white outfits, beaming "
           f"with {SORRISO}.",
           f"{P} (appears in [Shot 1]): partially_preserved - the same dog as in <Picture 1> and <Picture 2>: her "
           f"face, coat, markings and white t-shirt are retained; the low angle, close framing and neutral "
           f"expression of <Picture 2> are not: here she beams with {SORRISO}."]
    acao = (f"[Shot 1] Continuing without a cut from the previous shot, {lista(seis, rot)} walk side by side down "
            f"the middle of {lugar} towards the camera. The camera glides slowly backwards ahead of them, level at "
            f"the height of the dogs' heads, and gently slows to a stop; the six friends slow down with it at "
            f"{PASSO} and come to a halt in the middle of the street, then turn their heads to the left-hand "
            f"sidewalk, beaming. There, {P} steps out of the open gate of her house: the last and most awaited "
            f"of the friends, the star of the video. She walks calmly and proudly into the middle of the street, "
            f"head high, beaming with {SORRISO}, and every one of the others turns to watch her, delighted, their "
            f"tails wagging. She takes her place in the very centre of the front row, and the others gather "
            f"close around her and settle: {arr}. In the last frame the camera is still and level, in a wide "
            f"shot exactly like <Picture 1>, all seven fully inside the frame from ears to paws, with open street "
            f"on both sides of the group, every face clearly visible. {FELIZ} {NIVEL} {SETE}")
    return {"id": "07-pretinha", "refs": [GRUPO, "cenario-clipe-pretinha-close.png"], "defs": defs,
            "resumo": resumo, "ret": ret, "acao": acao, "som": SOM, "frames": 124}


def cena_todos(i: int, cid: str, acao: str, resumo: str, audio: str | None = None) -> dict:
    refs = [GRUPO]
    pic = {k: 1 for k in ORDEM}
    pt = 1
    rot = {k: f"<Subject {n}>" for n, k in enumerate(ORDEM, 1)}
    lugar = f"<Subject {len(ORDEM) + 1}>"
    defs = [definicao(k, rot[k], pic[k]) for k in ORDEM]
    defs.append(f"{lugar} is {RUA}, as in <Picture {pt}>.")
    if audio:
        defs.append("<Audio 1> is the melody and rhythm reference for the singing.")
    antes = "" if cid in CORTES else " and at the end of the previous shot"
    ret = [f"{lista(ORDEM, rot)} (appear in [Shot 1]): partially_preserved - the same seven dogs as in "
           f"<Picture 1>{antes}, with their faces, coats, markings and white outfits; "
           f"only the neutral expressions of <Picture 1> are not retained: here every one of them beams with "
           f"{SORRISO}.",
           f"<Picture {pt}> (group composition for [Shot 1]): the seven friends gathered in the middle of the "
           f"street - {ARRUMACAO.format(**rot)} - in a wide, level shot with all seven fully inside the frame and "
           f"open street on both sides."]
    if audio:
        ret.append("<Audio 1>: reference - the dogs sing the words with the same melody, rhythm and timing as "
                   "<Audio 1>, in their own dog voices, without copying the original signal or its timbre.")
    return {"id": cid, "refs": refs, "audio": audio, "defs": defs,
            "resumo": f"[reference generation{' + audio reference' if audio else ''}] {resumo}",
            "ret": ret, "acao": acao.format(L=lugar, P=pt, **{k: rot[k] for k in ORDEM}), "som": SOM}


def finais() -> list[dict]:
    grupo = "{jose}, {tiao}, {renato}, {pretinha}, {pacoca}, {cida} and {lurdes}"
    fila = ARRUMACAO + ", as in <Picture {P}>"
    plano = ("[Shot 1] {ABRE} the camera is completely still and level "
             "at the height of the dogs' heads, in a wide shot of the seven friends gathered in the middle of {L}, "
             "all in white: " + fila + ". All seven are fully inside the frame, with open street on both sides "
             "of the group, and every face and mouth is clearly visible. ")
    canto = (grupo + " (S1), all on screen, sing together in chorus, in their own different voices at the same "
             "moment, joyfully, like a choir of friends, every mouth visibly opening and closing in sync with "
             "every syllable, says: ")
    return [
        cena_todos(8, "08-refrao-1",
                   plano.replace("{ABRE}", "The shot opens on the composition of <Picture 1>, after a cut:") + canto + "<d>[Portuguese] Andar com fé eu vou,</d> They sway gently from side to side as "
                   "they sing, every face beaming with joy, the eyes bright and crinkled with happiness.",
                   "All seven sing the first half of the chorus together, gathered like <Picture 1>.",
                   audio="refrao-1.wav"),
        cena_todos(9, "09-refrao-2",
                   plano.replace("{ABRE}", "Continuing without a cut from the previous shot,") + canto + "<d>[Portuguese] que a fé não costuma faiá!</d> On the last word they lean in "
                   "towards each other, their heads close together. " + FELIZ,
                   "All seven sing the end of the chorus together, gathered like <Picture 1>.",
                   audio="refrao-2.wav"),
    ]


def yaml_cena(c: dict, primeira: bool) -> str:
    estilo = ESTILO if not c["id"].startswith(("08", "09", "10")) else ESTILO.replace(
        "The camera glides smoothly on a dolly, perfectly steady, with no shake and no handheld wobble.",
        "The camera is locked off on a tripod for the whole video: perfectly steady, with no shake, no "
        "handheld movement and no drift; only the dogs move.")
    corpo = ["subject_definitions:", *c["defs"], "", "summary:", c["resumo"], "", "retention_analysis:",
             *c["ret"], "", "detailed_description:", estilo, c["acao"] + " " + FECHO.strip(), "",
             f"overall_soundscape: {c['som']}", "", "non_diegetic_music: N/A"]
    linhas = [f"  - id: {c['id']}"]
    if primeira:
        linhas.append("    chain_from_previous: false")
    if c["id"] in SEEDS:
        linhas.append(f"    seed: {SEEDS[c['id']]}")
    if c.get("frames"):
        linhas.append(f"    video_frames: {c['frames']}")
    linhas.append(f"    ref_images: [{', '.join(c['refs'])}]")
    if c.get("audio"):
        linhas.append(f"    ref_audios: [{c['audio']}]")
    linhas.append("    prompt: |-")
    linhas += [("      " + l) if l else "" for l in corpo]
    return "\n".join(linhas)


def main() -> None:
    cenas = [cena(i) for i in range(1, 7)] + [cena_pretinha()] + finais()
    engine = ENGINE.format(seed=SEED).replace(
        "  style_suffix: \"\"\n", "  style_suffix: \"\"\n  overlap_frames: 5\n").replace(
        "  chain_from_previous: false", "  chain_from_previous: true")
    topo = (f"# clipe-domingo cortejo {VERSAO} - GERADO por movies/clipe-domingo/cortejo.py.\n"
            f"# Não edite à mão: mude o cortejo.py e rode de novo.\n"
            f"# Cadeia inteira (overlap 5): refazer a cena N exige refazer as seguintes.\n"
            f"name: clipe-domingo-cortejo\n")
    saida = AQUI / "scripts" / f"cortejo-{VERSAO}.yaml"
    saida.write_text(topo + engine + "scenes:\n" + "\n".join(yaml_cena(c, n == 0 or c["id"] in CORTES) for n, c in enumerate(cenas))
                     + "\n")
    print(saida)


if __name__ == "__main__":
    main()
