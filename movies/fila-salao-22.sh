#!/bin/bash
# Closes do salão (voto-depois-dos-70) depois do Tio Renato (fila-renato-22, pid 131093).
cd /home/erika/Projects/petsexplicam
while kill -0 131093 2>/dev/null; do sleep 30; done
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
echo "$(date +%H:%M) closes do salão"
./mm images movies/cenarios/scripts/salao-closes.yaml > movies/cenarios/salao-closes.log 2>&1
echo "$(date +%H:%M) fim"
