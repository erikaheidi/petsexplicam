#!/bin/bash
# Imagens para 23-24/10: salão (voto-depois-dos-70) e varanda do José (checklist-domingo).
cd /home/erika/Projects/petsexplicam
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
for c in salao varanda-jose; do ./mm images movies/cenarios/scripts/$c.yaml > movies/cenarios/$c.log 2>&1; done
echo "$(date +%H:%M) fim"
