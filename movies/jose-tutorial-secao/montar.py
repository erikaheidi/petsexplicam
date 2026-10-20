"""Monta o tutorial do José: abertura (cenas 1-4) + screencast com a voz dele
+ fecho (cenas 5-8), com legendas queimadas.

    python3 movies/jose-tutorial-secao/montar.py

Precisa de: ./mm assemble do jose-tutorial-secao (o vídeo das 8 cenas) e os
clipes do jose-tutorial-voz (a narração). O screencast é o da Erika, sem a
voz dela: a do José entra no lugar (tools/narrar.py).
Saída: renders/jose-tutorial-secao/jose-tutorial-secao-final[-legendado].mp4
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import legendas as L  # noqa: E402

SCREENCAST = Path.home() / "Videos/consulta-secao-tutorial.mp4"
# início de cada trecho da narração da Erika (silencedetect) + o fim do vídeo
CORTES = "0,3.97,7.29,9.86,12.58,14.99,17.16,19.08,23.08"
CENAS_ABERTURA = 4


def sh(*cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def main() -> int:
    ws = L.Workspace.resolve(ROOT)
    jose = L.load_script((ROOT / "movies/jose-tutorial-secao/scripts/v1.yaml").resolve(), ws)
    voz = L.load_script((ROOT / "movies/jose-tutorial-voz/scripts/v1.yaml").resolve(), ws)
    run = jose.layout
    dest = run.movie.with_name("jose-tutorial-secao-final.mp4")
    tmp = dest.parent / "montagem"
    tmp.mkdir(exist_ok=True)

    # 1. screencast com a voz do José
    narrado = tmp / "screencast.mp4"
    sh(sys.executable, ROOT / "tools/narrar.py", SCREENCAST, ROOT / "movies/jose-tutorial-voz/scripts/v1.yaml",
       narrado, "--cortes", CORTES)
    tempos = [ln.split("\t") for ln in Path(f"{narrado}.tempos.txt").read_text().splitlines()]

    # 2. o vídeo das 8 cenas, cortado depois da cena 4
    eventos, usadas = L.legendas(jose, None)
    corte = sum(L.duracao(c) - t for c, t in usadas[:CENAS_ABERTURA])
    partes = []
    for nome, extra in (("abertura", ["-to", f"{corte:.3f}"]), ("fecho", ["-ss", f"{corte:.3f}"])):
        p = tmp / f"{nome}.mp4"
        sh("ffmpeg", "-loglevel", "error", "-y", "-i", run.movie, *extra, "-c:v", "libx264", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-ar", "48000", "-ac", "2", p)
        partes.append(p)
    partes.insert(1, narrado)
    lista = tmp / "lista.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    sh("ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", dest)

    # 3. legendas: as do José (o fecho empurrado), e as da narração nos tempos dela
    meio = L.duracao(narrado)
    finais = [(a if a < corte else a + meio, b if a < corte else b + meio, q, t) for a, b, q, t in eventos]
    falas = {c.id: L.grafia(L.FALA.search(c.prompt).group(1).strip()) for c in voz.scenes}
    for a, b, cid in tempos:
        a, b = float(a) + corte, float(b) + corte
        blocos = L.quebrar(falas[cid])
        tams = [max(14, len(x.replace("\\N", " "))) for x in blocos]
        dur, ini = b - a, a
        for bloco, tam in zip(blocos, tams):
            fim = ini + dur * tam / sum(tams)
            finais.append((ini, fim, "3", bloco))
            ini = fim
    finais.sort()
    w, h = jose.primary_size
    ass, _ = L.escrever(finais, dest, w, h)
    legendado = dest.with_name(dest.stem + "-legendado.mp4")
    L.queimar(dest, ass, legendado)
    for a, b, _, t in finais:
        print(f"  {a:6.2f}-{b:6.2f}  {t.replace(chr(92) + 'N', ' / ')}")
    print(f"-> {legendado}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
