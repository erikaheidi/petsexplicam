#!/bin/bash
# checklist-domingo v1 (vlog do José na varanda): 8 cenas, montando e legendando no fim.
cd /home/erika/Projects/petsexplicam
S=movies/checklist-domingo/scripts/v1.yaml
echo "$(date +%H:%M) checklist-domingo"
./renderqc $S --de 1 --ate 4 --sem-montar > movies/checklist-domingo/render-v1-1a4.log 2>&1
./renderqc $S --de 5 > movies/checklist-domingo/render-v1-5afim.log 2>&1
echo "$(date +%H:%M) fim"
