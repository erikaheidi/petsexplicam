#!/bin/bash
# todos-perdem v1: modo vídeo, 6 cenas, montando e legendando no fim.
cd /home/erika/Projects/petsexplicam
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
S=movies/todos-perdem/scripts/v1.yaml
echo "$(date +%H:%M) todos-perdem"
./renderqc $S --de 1 --ate 3 --sem-montar > movies/todos-perdem/render-v1-1a3.log 2>&1
./renderqc $S --de 4 > movies/todos-perdem/render-v1-4afim.log 2>&1
echo "$(date +%H:%M) fim"
