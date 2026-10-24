#!/bin/bash
# neto-6x1 v1 (cozinha-lurdes) depois da fila da noite (fila-noite-20b, pid 3920733).
cd /home/erika/Projects/petsexplicam
while kill -0 3920733 2>/dev/null; do sleep 30; done
S=movies/neto-6x1/scripts/v1.yaml
echo "$(date +%H:%M) neto-6x1"
./renderqc $S --de 1 --ate 4 --sem-montar > movies/neto-6x1/render-v1-1a4.log 2>&1
./renderqc $S --de 5 --ate 8 --sem-montar > movies/neto-6x1/render-v1-5a8.log 2>&1
./renderqc $S --de 9 > movies/neto-6x1/render-v1-9afim.log 2>&1
echo "$(date +%H:%M) fim"
