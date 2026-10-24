#!/bin/bash
cd /home/erika/Projects/petsexplicam
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
./mm images movies/cenarios/scripts/rua-bairro.yaml > movies/cenarios/rua-bairro.log 2>&1
echo "$(date +%H:%M) fim"
