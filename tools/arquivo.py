#!/usr/bin/env python3
"""Arquivo de filmes encerrados: tira o peso do git e do disco sem perder nada.

    ./arquivar secao-mudou terras-raras      mostra o que faria (não mexe em nada)
    ./arquivar secao-mudou --executar        empacota, confere, apaga e tira do git
    ./arquivar --todos --exceto cenarios     todos os filmes de movies/
    ./arquivar --candidatos [--executar]     candidatos descartados de movies/cenarios
    ./arquivar --restaurar secao-mudou [--em DIR]

Um filme vira <dest>/<filme>.tar.zst com tudo que é dele, menos o miolo do
render: de cada run de renders/ vão só os arquivos da raiz (a montagem
<nome>.mp4, o <nome>-legendado.mp4, .srt/.ass); um run sem montagem leva os
clipes de scenes/. Conferido o pacote (zstd -t e a lista de membros), o
renders/ e os binários do filme (imagens, áudio, vídeo, logs) saem do disco e
do índice do git. Roteiros, drafts, scripts e ferramentas ficam: são o trabalho
e quase não pesam.

--candidatos empacota os PNGs de movies/cenarios/assets/ que nenhum
.yaml/.py/.md/.sh do workspace cita (as variantes -a/-b/-c descartadas), as
folhas de contato e os .log/.pid soltos de movies/ e movies/cenarios/.

Cada pacote ganha uma linha em ARQUIVO.md (data, tamanho, sha256, caminho).
Destino: --dest, senão $ARQUIVO_DIR, senão ~/Arquivo/<nome do workspace>.
Genérico para qualquer workspace do moviemakr: --workspace DIR.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import os
import subprocess
import sys
import tarfile
from pathlib import Path

BINARIOS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".wav", ".mp3", ".flac",
            ".mp4", ".webm", ".mov", ".mkv", ".log", ".pid"}
TEXTO = ("*.yaml", "*.py", "*.md", "*.sh")


def mb(n: int) -> str:
    return f"{n / 1e6:,.1f} MB".replace(",", ".")


def git(ws: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", str(ws), *args], capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def rastreados(ws: Path) -> set[str]:
    if not (ws / ".git").exists():
        return set()
    return set(git(ws, "ls-files", "-z").split("\0")) - {""}


def membros_filme(ws: Path, filme: Path) -> tuple[list[Path], list[Path]]:
    """(vai para o pacote, sai do disco). Tudo que sai do disco está no pacote."""
    pacote, remover = [], []
    for f in sorted(filme.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(filme)
        if rel.parts[0] == "renders":
            continue
        pacote.append(f)
        if f.suffix.lower() in BINARIOS:
            remover.append(f)
    renders = filme / "renders"
    for run in sorted(p for p in renders.glob("*") if p.is_dir()):
        raiz = sorted(p for p in run.iterdir() if p.is_file())
        pacote += raiz
        if not any(p.suffix == ".mp4" for p in raiz):
            pacote += sorted((run / "scenes").glob("*.mp4"))
    return pacote, remover


def citados(ws: Path) -> str:
    texto = []
    for padrao in TEXTO:
        for f in ws.rglob(padrao):
            if "renders" in f.parts or ".git" in f.parts or ".cache" in f.parts:
                continue
            texto.append(f.read_text(errors="ignore"))
    return "\n".join(texto)


def membros_candidatos(ws: Path) -> list[Path]:
    cen = ws / "movies" / "cenarios"
    todo_texto = citados(ws)
    fora = [p for p in sorted((cen / "assets").glob("*.png")) if p.name not in todo_texto]
    fora += sorted(p for p in cen.glob("*.png"))
    for d in (ws / "movies", cen):
        fora += sorted(d.glob("*.log")) + sorted(d.glob("*.pid"))
    fora += sorted(p for p in (ws / "movies").glob("*/*.pid") if p not in fora)
    return fora


def empacotar(ws: Path, membros: list[Path], destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".tar.tmp")
    with tarfile.open(tmp, "w") as tar:
        for f in membros:
            tar.add(f, arcname=str(f.relative_to(ws)), recursive=False)
    subprocess.run(["zstd", "-q", "-19", "-T0", "--rm", "-f", str(tmp), "-o", str(destino)],
                   check=True)
    subprocess.run(["zstd", "-q", "-t", str(destino)], check=True)
    lista = subprocess.run(["tar", "--zstd", "-tf", str(destino)], check=True,
                           capture_output=True, text=True).stdout.split("\n")
    esperado = {str(f.relative_to(ws)) for f in membros}
    if faltam := esperado - set(lista):
        destino.unlink()
        sys.exit(f"pacote incompleto ({len(faltam)} faltando, ex. {sorted(faltam)[0]}); nada apagado")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while bloco := f.read(1 << 20):
            h.update(bloco)
    return h.hexdigest()


def registrar(ws: Path, nome: str, pacote: Path, tam_original: int) -> None:
    indice = ws / "ARQUIVO.md"
    if not indice.exists():
        indice.write_text(
            "# Arquivo\n\n"
            "Filmes encerrados e candidatos descartados que saíram do git e do disco.\n"
            "Restaurar: `./arquivar --restaurar <nome>` (o pacote precisa estar no\n"
            "destino, padrão `~/Arquivo/<workspace>/`). Roteiros e drafts continuam no repo.\n\n"
            "| pacote | data | original | pacote | sha256 | caminho |\n"
            "| --- | --- | --- | --- | --- | --- |\n")
    caminho = str(pacote).replace(str(Path.home()), "~")
    with indice.open("a") as f:
        f.write(f"| {nome} | {datetime.date.today()} | {mb(tam_original)} | "
                f"{mb(pacote.stat().st_size)} | `{sha256(pacote)[:16]}` | `{caminho}` |\n")


def remover(ws: Path, arquivos: list[Path], rast: set[str]) -> None:
    sair_do_git = [str(f.relative_to(ws)) for f in arquivos if str(f.relative_to(ws)) in rast]
    for i in range(0, len(sair_do_git), 200):
        git(ws, "rm", "--cached", "--quiet", "--", *sair_do_git[i:i + 200])
    for f in arquivos:
        f.unlink(missing_ok=True)


def arquivar(ws: Path, nome: str, membros: list[Path], apagar: list[Path], extra_rm: Path | None,
             dest: Path, executar: bool, rast: set[str]) -> int:
    pacote = dest / f"{nome}.tar.zst"
    tam = sum(f.stat().st_size for f in membros)
    livre = sum(f.stat().st_size for f in apagar)
    if extra_rm and extra_rm.exists():
        livre += sum(f.stat().st_size for f in extra_rm.rglob("*") if f.is_file())
    no_git = sum(1 for f in apagar if str(f.relative_to(ws)) in rast)
    print(f"{nome:28} pacote {mb(tam):>10} ({len(membros)} arq.)  libera {mb(livre):>10}"
          f"  sai do git: {no_git}")
    if not executar:
        return livre
    if pacote.exists():
        sys.exit(f"{pacote} já existe; restaure ou apague antes de arquivar de novo")
    empacotar(ws, membros, pacote)
    registrar(ws, nome, pacote, tam)
    remover(ws, apagar, rast)
    if extra_rm and extra_rm.exists():
        subprocess.run(["rm", "-rf", "--", str(extra_rm)], check=True)
    return livre


def restaurar(ws: Path, nome: str, dest: Path, em: Path | None) -> None:
    pacote = dest / f"{nome}.tar.zst"
    if not pacote.exists():
        sys.exit(f"não achei {pacote}")
    alvo = em or ws
    alvo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["tar", "--zstd", "-xf", str(pacote), "-C", str(alvo), "--skip-old-files"],
                   check=True)
    print(f"{nome} restaurado em {alvo}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("filmes", nargs="*")
    ap.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--dest", type=Path)
    ap.add_argument("--executar", action="store_true", help="sem isto, só mostra")
    ap.add_argument("--todos", action="store_true", help="todos os filmes de movies/")
    ap.add_argument("--exceto", nargs="*", default=["cenarios"])
    ap.add_argument("--candidatos", action="store_true")
    ap.add_argument("--restaurar", metavar="NOME")
    ap.add_argument("--em", type=Path, help="com --restaurar: extrai em outro diretório")
    a = ap.parse_args()

    ws = a.workspace.resolve()
    dest = (a.dest or Path(os.environ.get("ARQUIVO_DIR", Path.home() / "Arquivo" / ws.name))).expanduser()
    if a.restaurar:
        return restaurar(ws, a.restaurar, dest, a.em)

    rast = rastreados(ws)
    nomes = list(a.filmes)
    if a.todos:
        nomes += [p.name for p in sorted((ws / "movies").iterdir())
                  if p.is_dir() and p.name not in a.exceto and p.name not in nomes]
    if not nomes and not a.candidatos:
        ap.error("diga os filmes, --todos ou --candidatos")

    total = 0
    if a.candidatos:
        membros = membros_candidatos(ws)
        nome = f"cenarios-candidatos-{datetime.date.today()}"
        total += arquivar(ws, nome, membros, membros, None, dest, a.executar, rast)
    for n in nomes:
        filme = ws / "movies" / n
        if not filme.is_dir():
            sys.exit(f"não existe {filme}")
        membros, apagar = membros_filme(ws, filme)
        total += arquivar(ws, n, membros, apagar, filme / "renders", dest, a.executar, rast)
    print(f"{'total':28} libera {mb(total)}  -> {dest}"
          + ("" if a.executar else "   (só mostrando; --executar para valer)"))


if __name__ == "__main__":
    main()
