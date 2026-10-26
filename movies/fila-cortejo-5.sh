#!/bin/bash
cd /home/erika/Projects/petsexplicam
./mm images movies/cenarios/scripts/clipe-cortejo-grupo.yaml > movies/cenarios/clipe-cortejo-grupo.log 2>&1
A=movies/cenarios/assets
ffmpeg -loglevel error -y -i $A/clipe-cortejo-grupo-grupo-a.png -i $A/clipe-cortejo-grupo-grupo-b.png \
  -filter_complex "[0]scale=540:-2[a];[1]scale=540:-2[b];[a][b]hstack=2" movies/cenarios/clipe-cortejo-grupo-folha.png
echo "$(date +%H:%M) imagens prontas"
(cd ~/Projects/rocm-comfyui && docker compose restart) > /dev/null 2>&1
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
echo "$(date +%H:%M) comfy pronto"
