#!/bin/bash
# Teste de voz do Tio Renato: cena 2 (take "lado") sem voz de referência,
# depois das imagens do take de frente.
cd /home/erika/Projects/petsexplicam
# (as imagens já terminaram)
echo "$(date +%H:%M) teste de voz"
./renderqc movies/tio-renato-muda/scripts/v1.yaml --de 2 --ate 2 --sem-montar > movies/tio-renato-muda/render-voz.log 2>&1
echo "$(date +%H:%M) fim"
