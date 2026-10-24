#!/bin/bash
# Depois do checklist (pid 599995): veste a Pretinha na varanda (usa a versão a),
# volta para vídeo e renderiza o recado-final, montando e legendando no fim.
cd /home/erika/Projects/petsexplicam
while kill -0 599995 2>/dev/null; do sleep 30; done
reinicia() { (cd ~/Projects/rocm-comfyui && docker compose restart); until curl -s localhost:8188/queue >/dev/null; do sleep 5; done; }
echo "$(date +%H:%M) vestir"; reinicia
./mm images movies/cenarios/scripts/vestir-varanda.yaml > movies/cenarios/vestir-varanda.log 2>&1
cp movies/cenarios/assets/vestir-varanda-a.png assets/cenario-varanda-vlog-pretinha-vermelha.png
./dialogo gerar recado-final > movies/recado-final/gerar.log 2>&1
echo "$(date +%H:%M) recado-final"; reinicia
S=movies/recado-final/scripts/v1.yaml
./renderqc $S --de 1 --ate 5 --sem-montar > movies/recado-final/render-v1-1a5.log 2>&1
./renderqc $S --de 6 > movies/recado-final/render-v1-6afim.log 2>&1
echo "$(date +%H:%M) fim"
