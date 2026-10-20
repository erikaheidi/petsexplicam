#!/usr/bin/env python3
"""Capa do post: um frame do vídeo com título e subtítulo no padrão do perfil.

    ./capa movies/<filme>/scripts/v2.yaml --frames
        folha com 4 frames de cada cena pronta, para escolher a base
    ./capa movies/<filme>/scripts/v2.yaml 2 "VÃO TAXAR|O PIX?" "o primo da TI explica"
        capa a partir da cena 2 -> movies/<filme>/assets/capa-vao-taxar-o-pix.png
    ./capa movies/<filme>/scripts/v2.yaml --folha
        todas as capas-*.png do filme lado a lado, para comparar

Opções da capa: --frame N (padrão 70), --y PX (topo do título, padrão 280),
--tamanho PX (corpo do título, padrão 150), --nome slug.

Padrão (terras-raras, secao-mudou, teste-cego): 1080x1920; título em caixa
alta, amarelo #FFD93B com contorno preto; subtítulo branco com contorno; "|"
quebra a linha. O texto fica dentro do recorte 3:4 do grid (y 240-1680) e
num degradê escuro para ler sobre qualquer fundo. Usa o Python do sistema
(Pillow + PyYAML; o venv do moviemakr não tem Pillow).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

FONTE = "/usr/share/fonts/truetype/lato/Lato-Black.ttf"
W, H = 1080, 1920
GRID = (240, 1680)  # recorte 3:4 que o grid do Instagram mostra
AMARELO = "#FFD93B"
MARGEM = 50


def run_dir(script: Path) -> Path:
    nome = yaml.safe_load(script.read_text())["name"]
    return script.parent.parent / "renders" / nome


def clipe(script: Path, cena: str) -> Path:
    cenas = run_dir(script) / "scenes"
    clipes = sorted(cenas.glob("*.mp4"))
    for c in clipes:
        num, _, ident = c.stem.partition("-")
        if cena in (num, num.lstrip("0"), ident):
            return c
    sys.exit(f"cena {cena} não renderizada em {cenas}")


def frame(video: Path, n: int, largura: int, altura: int, saida: Path) -> None:
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-vf",
                    f"select='eq(n\\,{n})',scale={largura}:{altura}:flags=lanczos",
                    "-frames:v", "1", str(saida)], check=True)


def slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto.replace("|", " ")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def bloco(d: ImageDraw.ImageDraw, linhas: list[str], tam: int, cor: str, y: int, contorno: int) -> int:
    for linha in linhas:
        t = tam
        f = ImageFont.truetype(FONTE, t)
        while d.textlength(linha, font=f) > W - 2 * MARGEM:
            t -= 4
            f = ImageFont.truetype(FONTE, t)
        d.text(((W - d.textlength(linha, font=f)) / 2, y), linha, font=f, fill=cor,
               stroke_width=contorno, stroke_fill="black")
        y += int(t * 1.08)
    return y


def capa(base: Path, saida: Path, titulo: str, sub: str, y0: int, tam: int) -> None:
    im = Image.open(base).convert("RGB")
    # degradê escuro centrado no texto, para ler sobre toldo, céu ou parede clara
    altura_txt = int(tam * 1.08) * len(titulo.split("|")) + (80 * len(sub.split("|")) if sub else 0)
    meio = y0 + altura_txt // 2
    mascara = Image.new("L", (1, H))
    for y in range(H):
        mascara.putpixel((0, y), int(150 * max(0.0, 1 - abs(y - meio) / 520)))
    im = Image.composite(Image.new("RGB", im.size), im, mascara.resize(im.size))
    d = ImageDraw.Draw(im)
    y = bloco(d, titulo.upper().split("|"), tam, AMARELO, y0, 10)
    if sub:
        y = bloco(d, sub.split("|"), 62, "white", y + 15, 6)
    if y0 < GRID[0] or y > GRID[1]:
        print(f"aviso: texto em y {y0}-{y}, fora do recorte 3:4 do grid ({GRID[0]}-{GRID[1]})")
    im.save(saida)
    print(f"{saida}  (texto em y {y0}-{y})")


def folha(imagens: list[Path], saida: Path, colunas: int, rotulos: list[str]) -> None:
    lado = (270, 480)
    linhas = -(-len(imagens) // colunas)
    out = Image.new("RGB", (lado[0] * colunas, lado[1] * linhas), "black")
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(FONTE, 22)
    for i, (img, rot) in enumerate(zip(imagens, rotulos)):
        x, y = lado[0] * (i % colunas), lado[1] * (i // colunas)
        out.paste(Image.open(img).convert("RGB").resize(lado), (x, y))
        d.text((x + 6, y + 6), rot, font=f, fill="white", stroke_width=3, stroke_fill="black")
    out.save(saida)
    print(saida)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", type=Path)
    ap.add_argument("cena", nargs="?", help="número ou id da cena")
    ap.add_argument("titulo", nargs="?", help='"LINHA 1|LINHA 2"')
    ap.add_argument("sub", nargs="?", default="", help='"linha 1|linha 2"')
    ap.add_argument("--frames", action="store_true", help="folha de frames de todas as cenas")
    ap.add_argument("--folha", action="store_true", help="compara as capas do filme")
    ap.add_argument("--frame", type=int, default=70)
    ap.add_argument("--y", type=int, default=280)
    ap.add_argument("--tamanho", type=int, default=150)
    ap.add_argument("--nome")
    a = ap.parse_args()
    rd = run_dir(a.script)
    assets = a.script.parent.parent / "assets"

    if a.frames:
        quadros = [0, 30, 60, 90]
        clipes = sorted((rd / "scenes").glob("*.mp4"))
        with tempfile.TemporaryDirectory() as tmp:
            imgs, rots = [], []
            for c in clipes:
                for n in quadros:
                    p = Path(tmp) / f"{c.stem}-{n}.png"
                    frame(c, n, 270, 480, p)
                    imgs.append(p)
                    rots.append(f"{c.stem.split('-')[0].lstrip('0')} f{n}")
            folha(imgs, rd / "frames-capa.png", len(quadros), rots)
        return
    if a.folha:
        capas = sorted(assets.glob("capa-*.png"))
        folha(capas, rd / "capas.png", len(capas), [c.stem[5:] for c in capas])
        return
    if not (a.cena and a.titulo):
        ap.error("informe cena e título, ou --frames / --folha")
    assets.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "base.png"
        frame(clipe(a.script, a.cena), a.frame, W, H, base)
        capa(base, assets / f"capa-{a.nome or slug(a.titulo)}.png", a.titulo, a.sub, a.y, a.tamanho)


if __name__ == "__main__":
    main()
