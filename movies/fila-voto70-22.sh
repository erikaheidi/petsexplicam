#!/bin/bash
# voto-depois-dos-70 v1 (salão): modo vídeo e 11 cenas em lotes, montando e legendando no fim.
cd /home/erika/Projects/petsexplicam
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
S=movies/voto-depois-dos-70/scripts/v1.yaml
echo "$(date +%H:%M) voto-depois-dos-70"
./renderqc $S --de 1 --ate 4 --sem-montar > movies/voto-depois-dos-70/render-v1-1a4.log 2>&1
./renderqc $S --de 5 --ate 8 --sem-montar > movies/voto-depois-dos-70/render-v1-5a8.log 2>&1
./renderqc $S --de 9 > movies/voto-depois-dos-70/render-v1-9afim.log 2>&1
echo "$(date +%H:%M) fim"
