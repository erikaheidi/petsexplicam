"""Tom (F0) mediano de uma voz, por autocorrelação - só stdlib + ffmpeg.

Usado pelo renderqc para pegar a voz de um personagem que saiu no registro
errado (o Paçoca de ~296 Hz renderizado a ~157 Hz). Não mede timbre.
"""

from __future__ import annotations

import array
import statistics
import subprocess
from pathlib import Path

SR = 8000


def pcm(path, ss=None, to=None):
    """PCM mono 8 kHz de um trecho do arquivo."""
    cmd = ["ffmpeg", "-loglevel", "error"]
    if ss:
        cmd += ["-ss", ss]
    if to:
        cmd += ["-to", to]
    cmd += ["-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"]
    a = array.array("h")
    a.frombytes(subprocess.run(cmd, capture_output=True, check=True).stdout)
    return a


def f0s(x):
    n = 320  # 40 ms
    lo, hi = SR // 600, SR // 70
    out = []
    for start in range(0, len(x) - n - hi, n // 2):
        f = x[start:start + n + hi]
        energy = sum(v * v for v in f[:n]) / n
        if energy < 4e5:  # silêncio / ruído
            continue
        best, lag = 0.0, 0
        e0 = sum(v * v for v in f[:n])
        for k in range(lo, hi):
            c = sum(f[i] * f[i + k] for i in range(0, n, 2))
            if c > best:
                best, lag = c, k
        if lag and best / (e0 / 2) > 0.45:
            out.append(SR / lag)
    return out




def f0_mediano(arquivo: Path, inicio: float | None = None, fim: float | None = None) -> float | None:
    v = f0s(pcm(str(arquivo), f"{inicio}" if inicio else None, f"{fim}" if fim else None))
    return statistics.median(v) if len(v) >= 10 else None
