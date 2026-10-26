#!/bin/bash
cd /home/erika/Projects/petsexplicam
until grep -q "comfy pronto" movies/fila-cortejo-5.log; do sleep 10; done
echo "$(date +%H:%M) cenas 5-6"
./mm render movies/clipe-domingo/scripts/cortejo-v1.yaml --only 5-6 --halt-on-failure --no-assemble > movies/clipe-domingo/render-cortejo-5a6-v2.log 2>&1
echo "$(date +%H:%M) fim"
