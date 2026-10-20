#!/bin/bash
# Fila do pix-ameaca v2: espera as imagens da lotérica, volta o ComfyUI para
# vídeo e renderiza 3-12 em lotes de até 4 cenas, montando e legendando no fim.
cd /home/erika/Projects/petsexplicam
while pgrep -f 'moviemakr.py images' >/dev/null; do sleep 30; done
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
S=movies/pix-ameaca/scripts/v2.yaml
./renderqc $S --de 3 --ate 6 --sem-montar > movies/pix-ameaca/render-v2-3a6.log 2>&1
./renderqc $S --de 7 --ate 10 --sem-montar > movies/pix-ameaca/render-v2-7a10.log 2>&1
exec ./renderqc $S --de 11 > movies/pix-ameaca/render-v2-11a12.log 2>&1
