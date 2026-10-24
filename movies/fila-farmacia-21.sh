#!/bin/bash
# farmacia-popular v1: modo vídeo e 12 cenas em lotes, montando e legendando no fim.
cd /home/erika/Projects/petsexplicam
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
S=movies/farmacia-popular/scripts/v1.yaml
echo "$(date +%H:%M) farmacia-popular"
./renderqc $S --de 1 --ate 4 --sem-montar > movies/farmacia-popular/render-v1-1a4.log 2>&1
./renderqc $S --de 5 --ate 8 --sem-montar > movies/farmacia-popular/render-v1-5a8.log 2>&1
./renderqc $S --de 9 > movies/farmacia-popular/render-v1-9afim.log 2>&1
echo "$(date +%H:%M) fim"
