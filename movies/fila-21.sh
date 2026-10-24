#!/bin/bash
# Fila única da madrugada de 21/10, que substitui as filas noite-20b, neto-21 e rua-21.
# Depois do lote 5-8 da aposentadoria (já rodando), o resto da aposentadoria
# refaz as cenas que ficaram obsoletas (1, 2, 4: as senhoras falavam juntas, o
# letreiro, gente no guichê). Depois vêm as imagens, o audio-falso, o neto e a
# rua-festa.
cd /home/erika/Projects/petsexplicam
reinicia() { (cd ~/Projects/rocm-comfyui && docker compose restart); until curl -s localhost:8188/queue >/dev/null; do sleep 5; done; }
lotes() {
  S=movies/$1/scripts/$2.yaml
  ./renderqc $S --de 1 --ate 4 --sem-montar > movies/$1/render-$2-1a4.log 2>&1
  ./renderqc $S --de 5 --ate 8 --sem-montar > movies/$1/render-$2-5a8.log 2>&1
  ./renderqc $S --de 9 > movies/$1/render-$2-9afim.log 2>&1
}
while pgrep -f '[r]enderqc.py movies/aposentadoria-subiu' >/dev/null; do sleep 20; done
echo "$(date +%H:%M) aposentadoria (resto + refazer 1, 2, 4)"
S=movies/aposentadoria-subiu/scripts/v2.yaml
./renderqc $S --de 1 --ate 4 --sem-montar > movies/aposentadoria-subiu/render-v2-refaz-1a4.log 2>&1
./renderqc $S --de 5 --ate 8 --sem-montar > movies/aposentadoria-subiu/render-v2-refaz-5a8.log 2>&1
./renderqc $S --de 9 > movies/aposentadoria-subiu/render-v2-9afim.log 2>&1
echo "$(date +%H:%M) audio-falso"; lotes audio-falso v2
echo "$(date +%H:%M) neto-6x1"; lotes neto-6x1 v1
echo "$(date +%H:%M) imagens"; reinicia
for c in farmacia-closes ponto-onibus rua-festa; do ./mm images movies/cenarios/scripts/$c.yaml > movies/cenarios/$c.log 2>&1; done
echo "$(date +%H:%M) fim"
