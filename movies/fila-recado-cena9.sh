#!/bin/bash
cd /home/erika/Projects/petsexplicam
S=movies/recado-final/scripts/v1.yaml
./renderqc $S --de 9 --ate 9 --sem-montar > movies/recado-final/render-v1-cena9.log 2>&1
./mm assemble $S > movies/recado-final/assemble-cena9.log 2>&1
./legendas $S --altura 0.15 > movies/recado-final/legendas-cena9.log 2>&1
echo "$(date +%H:%M) fim"
