#!/bin/bash
# Imagens do clipe de domingo, depois do recado-final (fila-recado, pid 600161).
cd /home/erika/Projects/petsexplicam
while kill -0 600161 2>/dev/null; do sleep 30; done
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
echo "$(date +%H:%M) imagens do clipe"
./mm images movies/cenarios/scripts/clipe.yaml > movies/cenarios/clipe.log 2>&1
python3 /tmp/claude-1000/-home-erika-Projects-petsexplicam/9ef5be4b-7d3f-529a-99f3-a2f86d107782/scratchpad/folha.py movies/cenarios/clipe-folha.png movies/cenarios/assets/clipe-*-acao.png
python3 /tmp/claude-1000/-home-erika-Projects-petsexplicam/9ef5be4b-7d3f-529a-99f3-a2f86d107782/scratchpad/folha.py movies/cenarios/clipe-folha-closes.png movies/cenarios/assets/clipe-*-close.png movies/cenarios/assets/clipe-todos-branco-*.png
echo "$(date +%H:%M) fim"
