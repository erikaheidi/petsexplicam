#!/bin/bash
# Imagens da abertura da cena 5, depois as cenas 8-10 (independentes da 7)
# enquanto a Erika escolhe o frame.
cd /home/erika/Projects/petsexplicam
./mm images movies/cenarios/scripts/clipe-cortejo-5.yaml > movies/cenarios/clipe-cortejo-5.log 2>&1
A=movies/cenarios/assets
ffmpeg -loglevel error -y -i $A/clipe-cortejo-5-renato-abertura-a.png -i $A/clipe-cortejo-5-renato-abertura-b.png \
  -filter_complex "[0]scale=540:-2[a];[1]scale=540:-2[b];[a][b]hstack=2" movies/cenarios/clipe-cortejo-5-folha.png
echo "$(date +%H:%M) imagens prontas"
(cd ~/Projects/rocm-comfyui && docker compose restart) > /dev/null 2>&1
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
echo "$(date +%H:%M) cenas 8-10"
./mm render movies/clipe-domingo/scripts/cortejo-v1.yaml --only 8-10 --halt-on-failure --no-assemble > movies/clipe-domingo/render-cortejo-8a10.log 2>&1
echo "$(date +%H:%M) fim"
