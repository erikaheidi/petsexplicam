#!/bin/bash
# Fila da noite de 20/10, reordenada: a aposentadoria vem antes das imagens que
# faltam (closes da farmácia, ponto-onibus), para sair às ~1h50.
cd /home/erika/Projects/petsexplicam
reinicia() { (cd ~/Projects/rocm-comfyui && docker compose restart); until curl -s localhost:8188/queue >/dev/null; do sleep 5; done; }
lotes() {
  S=movies/$1/scripts/$2.yaml
  ./renderqc $S --de 1 --ate 4 --sem-montar > movies/$1/render-$2-1a4.log 2>&1
  ./renderqc $S --de 5 --ate 8 --sem-montar > movies/$1/render-$2-5a8.log 2>&1
  ./renderqc $S --de 9 > movies/$1/render-$2-9afim.log 2>&1
}
while kill -0  2>/dev/null; do sleep 15; done
echo "$(date +%H:%M) aposentadoria"; reinicia; lotes aposentadoria-subiu v2
echo "$(date +%H:%M) imagens"; reinicia
for c in farmacia-closes ponto-onibus; do ./mm images movies/cenarios/scripts/$c.yaml > movies/cenarios/$c.log 2>&1; done
echo "$(date +%H:%M) audio-falso"; reinicia; lotes audio-falso v2
echo "$(date +%H:%M) fim"
