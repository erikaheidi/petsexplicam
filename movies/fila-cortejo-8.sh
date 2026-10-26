#!/bin/bash
# Depois das cenas 5-6: a 7 (entrada da Pretinha, termina no frame do grupo),
# o refrão (8-9) e a montagem.
cd /home/erika/Projects/petsexplicam
until grep -q "fim" movies/fila-cortejo-7.log; do sleep 20; done
echo "$(date +%H:%M) cenas 7-9"
./mm render movies/clipe-domingo/scripts/cortejo-v1.yaml --only 7-9 --halt-on-failure > movies/clipe-domingo/render-cortejo-7a9-v2.log 2>&1
echo "$(date +%H:%M) fim"
