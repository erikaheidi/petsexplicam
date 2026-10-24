#!/bin/bash
# tio-renato-muda v2 (voz leve) com a voz de referência: 10 cenas em lotes,
# montando e legendando no fim.
cd /home/erika/Projects/petsexplicam
S=movies/tio-renato-muda/scripts/v2.yaml
echo "$(date +%H:%M) tio-renato-muda v2"
./renderqc $S --de 1 --ate 4 --sem-montar > movies/tio-renato-muda/render-v2-1a4.log 2>&1
./renderqc $S --de 5 --ate 8 --sem-montar > movies/tio-renato-muda/render-v2-5a8.log 2>&1
./renderqc $S --de 9 > movies/tio-renato-muda/render-v2-9afim.log 2>&1
echo "$(date +%H:%M) fim"
