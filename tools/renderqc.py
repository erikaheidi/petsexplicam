"""Renderiza cena a cena, checando o tom da voz de cada uma contra a referência.

    ./renderqc movies/<filme>/scripts/v1.yaml [--de 4] [--ate 12]

Para cenas independentes (o formato do ./dialogo), uma cena que sai com a voz
errada NÃO para o run: ela é anotada e o render segue - uma noite inteira não
pode morrer na cena 3. No fim monta o filme, gera o legendado e imprime o
relatório: o que refazer (com outra `seed:` no roteiro e --only N).

A voz de cada cena é reconhecida pelo arquivo em ref_audios
(pretinha-voz.wav / pacoca-voz.wav). Cena sem referência de voz não é checada.
O teste só pega erro grosseiro (o Paçoca uma oitava abaixo); timbre e boca
continuam precisando de alguém assistindo.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(os.environ.get("MOVIEMAKR_HOME", Path.home() / "Projects/moviemakr"))))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from moviemakr.config import load_script  # noqa: E402
from moviemakr.layout import Workspace  # noqa: E402
from voz import f0_mediano  # noqa: E402

F0_REF = {"pretinha-voz.wav": ("Pretinha", 258.0), "pacoca-voz.wav": ("Paçoca", 296.0)}
# Assimétrica: a falha real é a voz cair de registro (o Paçoca a 157 Hz, voz de
# adulto); empolgado ele sobe bastante e continua certo (381 Hz aprovado de
# ouvido na cena 13 do direito-de-votar, referência 296).
ABAIXO, ACIMA = 0.20, 0.35


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("script", type=Path)
    ap.add_argument("--de", type=int, default=1)
    ap.add_argument("--ate", type=int)
    ap.add_argument("--sem-montar", action="store_true")
    args = ap.parse_args()

    script = load_script(args.script.resolve(), Workspace.resolve(ROOT))
    cenas = [c for c in script.scenes if c.index >= args.de and (args.ate is None or c.index <= args.ate)]
    problemas: list[str] = []
    for cena in cenas:
        print(f"\n##### cena {cena.index} ({cena.id})", flush=True)
        r = subprocess.run([str(ROOT / "mm"), "render", str(args.script), "--only", str(cena.index),
                            "--no-assemble"], cwd=ROOT)
        clip = script.layout.clip(cena.slug)
        if r.returncode != 0 or not clip.is_file():
            problemas.append(f"cena {cena.index} ({cena.id}): render falhou")
            print(f"QC: {problemas[-1]}", flush=True)
            continue
        refs = [F0_REF[p.name] for p in cena.ref_audios if p.name in F0_REF]
        if not refs:
            continue
        quem, ref = refs[0]
        f0 = f0_mediano(clip, inicio=0.2)
        ok = f0 is not None and ref * (1 - ABAIXO) <= f0 <= ref * (1 + ACIMA)
        medido = f"{f0:.0f} Hz" if f0 else "sem voz detectável"
        print(f"QC: cena {cena.index} {quem}: {medido}, referência {ref:.0f} Hz -> {'ok' if ok else 'FORA'}",
              flush=True)
        if not ok:
            problemas.append(f"cena {cena.index} ({cena.id}): voz de {quem} {medido}, referência {ref:.0f} Hz")

    if not args.sem_montar and all(script.layout.clip(c.slug).is_file() for c in script.scenes):
        subprocess.run([str(ROOT / "mm"), "assemble", str(args.script)], cwd=ROOT, check=False)
        subprocess.run([str(ROOT / "legendas"), str(args.script)], cwd=ROOT, check=False)

    print("\n===== relatório")
    if problemas:
        print("refazer (mude a seed da cena no roteiro, gere e use --only N):")
        for p in problemas:
            print(f"  - {p}")
    else:
        print("todas as cenas passaram no QC de voz")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
