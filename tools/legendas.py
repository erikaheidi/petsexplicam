"""Legendas em PT-BR a partir das falas do script, queimadas no vídeo.

    ./legendas movies/<filme>/scripts/v1.yaml            .ass + .srt + <filme>-legendado.mp4
    ./legendas movies/<filme>/scripts/v1.yaml --previa 4  só as 4 primeiras cenas, num vídeo de prévia

O texto vem de dentro de `<d>[Portuguese] ...</d>` de cada cena - a fala literal
que o modelo recebeu -, então serve para qualquer script, gerado pelo
./dialogo ou escrito à mão. Os tempos vêm dos clipes reais: a duração de cada
cena (menos o overlap cortado das encadeadas, como a montagem do moviemakr faz)
e, dentro da cena, o trecho em que há som de fala (silencedetect). Sem trecho
detectável, a legenda ocupa a cena inteira.

Cor por personagem, para quem assiste sem som saber quem fala: Pretinha branca,
Paçoca amarelo. Posição: acima do terço de baixo da tela, fora da área que a
interface do Reels cobre (legenda do post, botões à direita), e abaixo dos
rostos da dupla.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOVIEMAKR_HOME = Path(os.environ.get("MOVIEMAKR_HOME", Path.home() / "Projects/moviemakr"))
sys.path.insert(0, str(MOVIEMAKR_HOME))

from moviemakr.assemble import overlap_trim  # noqa: E402
from moviemakr.config import load_script  # noqa: E402
from moviemakr.layout import Workspace  # noqa: E402
from moviemakr.state import load_state  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dialogo import PRONUNCIA  # noqa: E402

FALA = re.compile(r"<d>\[[^\]]+\]\s*(.*?)</d>", re.S)
QUEM = re.compile(r"<Subject (\d)>[^<]{0,40}\(S\d\)")
QUEM_E = re.compile(r"<Subject (\d)> is ([^\s,]+),")
# Cor por personagem. Quem fala vem da voz de referência da cena (o rótulo
# <Subject N> não serve: num close do Paçoca, ele é o <Subject 1>); sem voz de
# referência, do nome que o prompt dá ao <Subject N> que fala.
COR = {"1": "&H00FFFFFF", "2": "&H0045D8FF", "3": "&H009AE98C", "4": "&H00F0C88A",
       "5": "&H00FFB4D8", "6": "&H0090C0FF"}  # ASS é &HAABBGGRR: branco, amarelo, verde-claro, azul-claro, lilás, laranja-claro
VOZ = {"pretinha-voz.wav": "1", "pacoca-voz.wav": "2", "jose-voz.wav": "3", "tiao-voz.wav": "4",
       "cida-voz.wav": "5", "lurdes-voz.wav": "6"}
NOME = {"Pretinha": "1", "Paçoca": "2", "José": "3", "Tião": "4", "Cida": "5", "Lurdes": "6"}


def grafia(texto: str) -> str:
    """Desfaz a troca de pronúncia do dialogo (Clêide -> Cleide)."""
    for escrita, falada in PRONUNCIA.items():
        texto = texto.replace(falada, escrita)
    return texto

LARGURA_LINHA = 24   # caracteres por linha: a 544 px, 30 já encostava nas bordas
MAX_LINHAS = 2
LIMIAR_DB = -30
MIN_SILENCIO = 0.12
MARGEM = 0.08        # antes/depois do trecho falado
# Distância da legenda ao pé da tela, em fração da altura. 0.30 fica abaixo
# dos rostos da dupla em plano médio; num close (recado-final) o rosto desce
# até ali - use --altura 0.20 (em cima da roupa, ainda acima da interface).
ALTURA = 0.30
RAJADA = 0.45        # som mais curto que isso nas pontas da cena não é fala (a porta na cena 1: 0,4 s)

ASS_CABECALHO = """\
[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Fala,DejaVu Sans,{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,{ol},1,2,{ml},{mr},{mv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def sh(*cmd: str) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stderr


def duracao(clip: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(clip)], capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def trecho_falado(clip: Path, inicio: float, fim: float) -> tuple[float, float] | None:
    """(início, fim) do som acima do limiar, relativo a `inicio` no clipe."""
    log = sh("ffmpeg", "-hide_banner", "-ss", f"{inicio:.3f}", "-to", f"{fim:.3f}", "-i", str(clip),
             "-af", f"silencedetect=n={LIMIAR_DB}dB:d={MIN_SILENCIO}", "-f", "null", "-")
    total = fim - inicio
    silencios, aberto = [], None
    for m in re.finditer(r"silence_(start|end): ([0-9.]+)", log):
        t = float(m.group(2))
        if m.group(1) == "start":
            aberto = t
        else:
            silencios.append((aberto or 0.0, t))
            aberto = None
    if aberto is not None:
        silencios.append((aberto, total))
    # Os trechos com som são o complemento dos silêncios. Rajadas curtas nas
    # pontas (a porta batendo antes da fala, um estalo no fim) não são fala.
    sons, cursor = [], 0.0
    for s0, s1 in silencios:
        if s0 > cursor:
            sons.append((cursor, s0))
        cursor = max(cursor, s1)
    if cursor < total:
        sons.append((cursor, total))
    while len(sons) > 1 and sons[0][1] - sons[0][0] < RAJADA:
        sons.pop(0)
    while len(sons) > 1 and sons[-1][1] - sons[-1][0] < RAJADA:
        sons.pop()
    if not sons or sons[-1][1] - sons[0][0] < 0.4:
        return None
    return max(0.0, sons[0][0] - MARGEM), min(total, sons[-1][1] + MARGEM)


def _linhas(texto: str) -> list[str]:
    """Quebra gulosa por palavra em linhas de até LARGURA_LINHA."""
    linhas, atual = [], ""
    for p in texto.split():
        if atual and len(atual) + 1 + len(p) > LARGURA_LINHA:
            linhas.append(atual)
            atual = p
        else:
            atual = f"{atual} {p}".strip()
    return linhas + ([atual] if atual else [])


def _equilibrar(bloco: str) -> str:
    """Um bloco que precisa de duas linhas, quebrado no ponto mais equilibrado."""
    ws = bloco.split()
    if len(_linhas(bloco)) < 2:
        return bloco
    k = min(range(1, len(ws)), key=lambda k: max(len(" ".join(ws[:k])), len(" ".join(ws[k:]))))
    return " ".join(ws[:k]) + "\\N" + " ".join(ws[k:])


def _partes_iguais(texto: str) -> list[str]:
    """Divide por palavra no menor número de blocos que cabem, de tamanhos
    parecidos - nunca "…nos finais" + "de semana." sobrando sozinho."""
    ws = texto.split()
    n = -(-len(_linhas(texto)) // MAX_LINHAS)
    while True:
        alvo = len(texto) / n
        partes, atual = [], []
        for w in ws:
            if atual and len(" ".join(atual + [w])) > alvo * 1.15 and len(partes) < n - 1:
                partes.append(" ".join(atual))
                atual = [w]
            else:
                atual.append(w)
        partes.append(" ".join(atual))
        if all(len(_linhas(p)) <= MAX_LINHAS for p in partes):
            return partes
        n += 1


def quebrar(texto: str) -> list[str]:
    """Em blocos de até MAX_LINHAS linhas, cortando na pontuação sempre que der.

    Primeiro em frases (. ! ?), depois em orações (, :) só quando uma frase não
    cabe num bloco, e por palavra só em último caso. Pedaços curtos vizinhos são
    juntados enquanto couberem - "Calma." sozinho na tela some antes de ser lido.
    """
    def cabe(t: str) -> bool:
        return len(_linhas(t)) <= MAX_LINHAS

    pedacos = []
    for frase in re.split(r"(?<=[.!?])\s+", texto.strip()):
        if cabe(frase):
            pedacos.append((frase, True))
            continue
        for oracao in re.split(r"(?<=[,:])\s+", frase):
            if cabe(oracao):
                pedacos.append((oracao, True))
            else:
                pedacos += [(p, False) for p in _partes_iguais(oracao)]
    # Só junta pedaços inteiros (frase ou oração completa): grudar "Que
    # estranho!" no começo de uma frase cortada ao meio piora a leitura.
    blocos: list[tuple[str, bool]] = []
    for p, inteiro in pedacos:
        if blocos and inteiro and blocos[-1][1] and cabe(f"{blocos[-1][0]} {p}"):
            blocos[-1] = (f"{blocos[-1][0]} {p}", True)
        else:
            blocos.append((p, inteiro))
    # Interjeição sozinha ("Ué,") some da tela antes de ser lida: gruda no
    # bloco seguinte se couber.
    i = 0
    while i < len(blocos) - 1:
        b, inteiro = blocos[i]
        if len(b) <= 8 and cabe(f"{b} {blocos[i + 1][0]}"):
            blocos[i:i + 2] = [(f"{b} {blocos[i + 1][0]}", blocos[i + 1][1])]
        else:
            i += 1
    return [_equilibrar(b) for b, _ in blocos]


def ts_ass(t: float) -> str:
    cs = round(t * 100)
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def ts_srt(t: float) -> str:
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def legendas(script, ate: int | None):
    """[(inicio, fim, quem, texto)] na linha do tempo do filme montado, e as cenas usadas."""
    state = load_state(script.layout.state_file)
    t = 0.0
    eventos, usadas = [], []
    for cena in script.scenes[:ate]:
        clip = script.layout.clip(cena.slug)
        if not clip.is_file():
            raise SystemExit(f"erro: falta o clipe da cena {cena.index} ({cena.slug}) - renderize antes")
        corte = overlap_trim(cena, state)
        dur = duracao(clip) - corte
        usadas.append((clip, corte))
        falas = [(grafia(m.group(1).strip()), m.start()) for m in FALA.finditer(cena.prompt)]
        if falas:
            span = trecho_falado(clip, corte, corte + dur) or (0.1, dur - 0.1)
            pesos = [len(f) for f, _ in falas]
            cursor = span[0]
            for (texto, pos), peso in zip(falas, pesos, strict=True):
                fatia = (span[1] - span[0]) * peso / sum(pesos)
                vozes = [VOZ[p.name] for p in cena.ref_audios if p.name in VOZ]
                if vozes:
                    quem = vozes[0]
                else:
                    rotulo = (QUEM.findall(cena.prompt[max(0, pos - 400):pos]) or ["1"])[-1]
                    nomes = dict(QUEM_E.findall(cena.prompt))
                    quem = NOME.get(nomes.get(rotulo, ""), "1")
                # Cada bloco fica na tela pelo tempo proporcional ao seu texto.
                blocos = quebrar(texto)
                # Peso mínimo: um "Ué," sozinho ainda precisa de ~0,7 s para ser lido.
                tamanhos = [max(14, len(b.replace("\\N", " "))) for b in blocos]
                a = cursor
                for bloco, tam in zip(blocos, tamanhos, strict=True):
                    b = a + fatia * tam / sum(tamanhos)
                    eventos.append((t + a, t + b, quem, bloco))
                    a = b
                cursor += fatia
        t += dur
    return eventos, usadas


def escrever(eventos, base: Path, w: int, h: int) -> tuple[Path, Path]:
    ass = base.with_suffix(".ass")
    linhas = [ASS_CABECALHO.format(w=w, h=h, fs=round(h * 0.036), ol=max(2, round(h * 0.0035)),
                                   ml=round(w * 0.07), mr=round(w * 0.13), mv=round(h * ALTURA))]
    for a, b, quem, texto in eventos:
        cor = COR.get(quem, COR["1"])
        linhas.append(f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},Fala,,0,0,0,,{{\\c{cor}}}{texto}\n")
    ass.write_text("".join(linhas))
    srt = base.with_suffix(".srt")
    srt.write_text("".join(
        f"{i}\n{ts_srt(a)} --> {ts_srt(b)}\n{texto.replace(chr(92) + 'N', chr(10))}\n\n"
        for i, (a, b, _, texto) in enumerate(eventos, 1)))
    return ass, srt


def queimar(video: Path, ass: Path, destino: Path) -> None:
    filtro = "ass=" + str(ass).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-vf", filtro,
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", "-movflags", "+faststart", str(destino)], check=True)


def previa(usadas, destino: Path, w: int, h: int, fps: int) -> None:
    """Junta as cenas já prontas como a montagem faria, sem tocar no run dir."""
    with tempfile.TemporaryDirectory() as tmp:
        partes = []
        for i, (clip, corte) in enumerate(usadas):
            p = Path(tmp) / f"{i:03d}.mp4"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{corte:.3f}", "-i", str(clip),
                            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:-1:-1,fps={fps}",
                            "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000",
                            "-ac", "2", str(p)], check=True)
            partes.append(p)
        lista = Path(tmp) / "lista.txt"
        lista.write_text("".join(f"file '{p}'\n" for p in partes))
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                        "-c", "copy", str(destino)], check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("script", type=Path)
    ap.add_argument("--previa", type=int, metavar="N",
                    help="só as N primeiras cenas, montadas num vídeo de prévia")
    ap.add_argument("--sem-video", action="store_true", help="só escreve .ass e .srt")
    ap.add_argument("--altura", type=float, default=0.30,
                    help="distância da legenda ao pé da tela, fração da altura (padrão 0.30)")
    args = ap.parse_args()
    global ALTURA
    ALTURA = args.altura

    script = load_script(args.script.resolve(), Workspace.resolve(ROOT))
    w, h = script.primary_size
    eventos, usadas = legendas(script, args.previa)
    run = script.layout
    base = run.movie.with_name(run.movie.stem + ("-previa" if args.previa else ""))
    ass, srt = escrever(eventos, base, w, h)
    print(f"{len(eventos)} legendas -> {ass.name}, {srt.name}")
    for a, b, quem, texto in eventos:
        print(f"  {a:6.2f}-{b:6.2f}  { {v: k for k, v in NOME.items()}[quem]:8}  {texto.replace(chr(92) + 'N', ' / ')}")
    if args.sem_video:
        return 0

    if args.previa:
        video = base.with_suffix(".mp4")
        previa(usadas, video, w, h, script.fps)
    else:
        video = run.movie
        if not video.is_file():
            raise SystemExit(f"erro: {video} não existe - rode ./mm assemble antes")
    destino = video.with_name(video.stem + "-legendado.mp4")
    queimar(video, ass, destino)
    print(f"-> {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
