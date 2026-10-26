#!/bin/bash
cd /home/erika/Projects/petsexplicam
./mm images movies/cenarios/scripts/clipe-cortejo-grupo2.yaml > movies/cenarios/clipe-cortejo-grupo2.log 2>&1
A=movies/cenarios/assets/clipe-cortejo-grupo2
ffmpeg -loglevel error -y -i $A-amplia-a.png -i $A-amplia-b.png -i $A-centro-a.png -i $A-centro-b.png \
  -filter_complex "[0]scale=384:-2[a];[1]scale=384:-2[b];[2]scale=384:-2[c];[3]scale=384:-2[d];[a][b][c][d]hstack=4" movies/cenarios/clipe-cortejo-grupo2-folha.png
echo "$(date +%H:%M) imagens prontas"
(cd ~/Projects/rocm-comfyui && docker compose restart) > /dev/null 2>&1
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
echo "$(date +%H:%M) cenas 5-6"
./mm render movies/clipe-domingo/scripts/cortejo-v1.yaml --only 5-6 --halt-on-failure --no-assemble > movies/clipe-domingo/render-cortejo-5a6-v2.log 2>&1
echo "$(date +%H:%M) fim"
