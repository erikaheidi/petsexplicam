#!/bin/bash
# Refrão (corte seco no frame do grupo), depois a cena 7 com seed nova, e a montagem.
cd /home/erika/Projects/petsexplicam
S=movies/clipe-domingo/scripts/cortejo-v1.yaml
echo "$(date +%H:%M) refrão 8-9"
./mm render $S --only 8-9 --halt-on-failure --no-assemble > movies/clipe-domingo/render-cortejo-refrao-v2.log 2>&1
echo "$(date +%H:%M) cena 7"
./mm render $S --only 7 --force --halt-on-failure > movies/clipe-domingo/render-cortejo-7-v3.log 2>&1
echo "$(date +%H:%M) fim"
