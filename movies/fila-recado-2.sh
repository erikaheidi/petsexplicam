#!/bin/bash
# recado-final com o frame recortado e centralizado, depois as imagens do clipe.
cd /home/erika/Projects/petsexplicam
S=movies/recado-final/scripts/v1.yaml
P=/tmp/claude-1000/-home-erika-Projects-petsexplicam/9ef5be4b-7d3f-529a-99f3-a2f86d107782/scratchpad
echo "$(date +%H:%M) recado cena 1"
./renderqc $S --de 1 --ate 1 --sem-montar > movies/recado-final/render-v1-cena1.log 2>&1
ffmpeg -loglevel error -y -i movies/recado-final/renders/recado-final/scenes/001-so-pedir.mp4 -vf "select='eq(n\,5)+eq(n\,40)+eq(n\,80)+eq(n\,115)',scale=240:427,tile=4x1" -frames:v 1 $P/recado-teste2.png
echo "$(date +%H:%M) recado 2-9"
./renderqc $S --de 2 --ate 5 --sem-montar > movies/recado-final/render-v1-2a5.log 2>&1
./renderqc $S --de 6 > movies/recado-final/render-v1-6afim.log 2>&1
echo "$(date +%H:%M) imagens do clipe"
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
./mm images movies/cenarios/scripts/clipe.yaml > movies/cenarios/clipe.log 2>&1
python3 $P/folha.py movies/cenarios/clipe-folha.png movies/cenarios/assets/clipe-*-acao.png
python3 $P/folha.py movies/cenarios/clipe-folha-closes.png movies/cenarios/assets/clipe-*-close.png movies/cenarios/assets/clipe-todos-branco-*.png
echo "$(date +%H:%M) fim"
