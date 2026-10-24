#!/bin/bash
# Ficha do Tio Renato depois das imagens do salão e da varanda do José (mesmo modo imagem).
cd /home/erika/Projects/petsexplicam
while pgrep -f '^/bin/bash movies/fila-imagens-21.sh' >/dev/null; do sleep 15; done
./mm images movies/ficha-renato/scripts/v1.yaml > movies/ficha-renato/images.log 2>&1
echo "$(date +%H:%M) fim"
