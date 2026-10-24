#!/bin/bash
cd /home/erika/Projects/petsexplicam
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
./renderqc movies/recado-final/scripts/v1.yaml --de 1 --ate 1 --sem-montar > movies/recado-final/render-v1-teste.log 2>&1
S=/tmp/claude-1000/-home-erika-Projects-petsexplicam/9ef5be4b-7d3f-529a-99f3-a2f86d107782/scratchpad
ffmpeg -loglevel error -y -i movies/recado-final/renders/recado-final/scenes/001-so-pedir.mp4 -vf "select='eq(n\,5)+eq(n\,40)+eq(n\,80)+eq(n\,115)',scale=240:427,tile=4x1" -frames:v 1 $S/recado-teste.png
echo "$(date +%H:%M) fim"
