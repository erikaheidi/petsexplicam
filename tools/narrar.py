"""Troca a narração de um screencast pela voz renderizada de um personagem.

    python3 tools/narrar.py <screencast.mp4> <script-da-voz.yaml> <saida.mp4> --cortes 0,3.97,...

`--cortes` são os inícios de cada trecho da narração original (um por cena do
script da voz, na ordem) mais o fim do vídeo. De cada cena renderizada sai só
o trecho com fala; ele entra no começo do seu corte, sobre o screencast sem o
áudio original. Se a fala não cabe no corte, o último quadro do corte fica
congelado até ela terminar (mais um respiro), para não atropelar a tela
seguinte. Saída no formato do vídeo: 544x960, 24 fps, áudio 48 kHz.

Escreve também <saida>.tempos.txt: início, fim e cena de cada fala na saída,
para o `legendas`.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(os.environ.get("MOVIEMAKR_HOME", Path.home() / "Projects/moviemakr"))))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from moviemakr.config import load_script  # noqa: E402
from moviemakr.layout import Workspace  # noqa: E402
from legendas import duracao, trecho_falado  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESPIRO = 0.25  # s entre o fim de uma fala e a tela seguinte


def sh(*cmd: str) -> None:
    subprocess.run(cmd, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("screencast", type=Path)
    ap.add_argument("script", type=Path)
    ap.add_argument("saida", type=Path)
    ap.add_argument("--cortes", required=True)
    args = ap.parse_args()

    cortes = [float(c) for c in args.cortes.split(",")]
    script = load_script(args.script.resolve(), Workspace.resolve(ROOT))
    cenas = script.scenes
    if len(cortes) != len(cenas) + 1:
        print(f"--cortes precisa de {len(cenas) + 1} valores (um por cena + o fim)", file=sys.stderr)
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="narrar-"))
    partes, tempos, t_saida = [], [], 0.0
    for i, cena in enumerate(cenas):
        clip = script.layout.clip(cena.slug)
        if not clip.is_file():
            print(f"falta o clipe da cena {cena.index} ({cena.id})", file=sys.stderr)
            return 1
        ini, fim = trecho_falado(clip, 0.0, duracao(clip)) or (0.1, duracao(clip) - 0.1)
        ini, fim = max(0.0, ini - 0.05), fim + 0.05
        fala = fim - ini
        a, b = cortes[i], cortes[i + 1]
        tam = max(b - a, fala + RESPIRO)
        congela = tam - (b - a)
        voz = tmp / f"voz{i}.wav"
        sh("ffmpeg", "-loglevel", "error", "-y", "-ss", f"{ini:.3f}", "-to", f"{fim:.3f}", "-i", str(clip),
           "-vn", "-ac", "2", "-ar", "48000", "-af", f"apad=whole_dur={tam:.3f}", str(voz))
        parte = tmp / f"parte{i}.mp4"
        vf = f"scale=544:960:flags=lanczos,fps=24,tpad=stop_mode=clone:stop_duration={congela:.3f}"
        sh("ffmpeg", "-loglevel", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(args.screencast),
           "-i", str(voz), "-map", "0:v", "-map", "1:a", "-vf", vf, "-t", f"{tam:.3f}",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k", str(parte))
        partes.append(parte)
        tempos.append((t_saida, t_saida + fala, cena.id))
        print(f"  {cena.id}: corte {b - a:.2f} s, fala {fala:.2f} s"
              f"{f', congela {congela:.2f} s' if congela > 0 else ''}")
        t_saida += tam

    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    sh("ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy",
       str(args.saida))
    Path(f"{args.saida}.tempos.txt").write_text("".join(f"{a:.3f}\t{b:.3f}\t{c}\n" for a, b, c in tempos))
    print(f"-> {args.saida} ({t_saida:.1f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
