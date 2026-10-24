#!/bin/bash
# Imagens da rua-festa (vídeo de domingo) depois do neto-6x1 (fila-neto-21, pid 3929214).
cd /home/erika/Projects/petsexplicam
while kill -0 3929214 2>/dev/null; do sleep 30; done
echo "$(date +%H:%M) rua-festa"
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
./mm images movies/cenarios/scripts/rua-festa.yaml > movies/cenarios/rua-festa.log 2>&1
echo "$(date +%H:%M) fim"
