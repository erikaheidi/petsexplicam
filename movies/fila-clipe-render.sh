#!/bin/bash
# Render do clipe-domingo. Usa provisoriamente a versão "a" do Renato e da
# Lurdes (fix3) e deixa as cenas deles (1 e 9) para o fim, para dar tempo de a
# Erika trocar a escolha antes de renderizar.
cd /home/erika/Projects/petsexplicam
while pgrep -f '^/bin/bash movies/fila-clipe-fix3.sh' >/dev/null; do sleep 10; done
A=movies/cenarios/assets
[ -f assets/cenario-clipe-renato-acao.png ] || cp $A/clipe-fix3-renato-acao-a.png assets/cenario-clipe-renato-acao.png
[ -f assets/cenario-clipe-lurdes-acao.png ] || cp $A/clipe-fix3-lurdes-acao-a.png assets/cenario-clipe-lurdes-acao.png
(cd ~/Projects/rocm-comfyui && docker compose restart)
until curl -s localhost:8188/queue >/dev/null; do sleep 5; done
./dialogo gerar clipe-domingo > movies/clipe-domingo/gerar.log 2>&1
S=movies/clipe-domingo/scripts/v1.yaml
echo "$(date +%H:%M) clipe 2-8"
./renderqc $S --de 2 --ate 8 --sem-montar > movies/clipe-domingo/render-2a8.log 2>&1
echo "$(date +%H:%M) clipe 10-17"
./renderqc $S --de 10 --ate 17 --sem-montar > movies/clipe-domingo/render-10a17.log 2>&1
# as cenas do Renato e da Lurdes: o script é gerado de novo para pegar a escolha final
./dialogo gerar clipe-domingo >> movies/clipe-domingo/gerar.log 2>&1
echo "$(date +%H:%M) clipe 1 e 9"
./renderqc $S --de 1 --ate 1 --sem-montar > movies/clipe-domingo/render-1.log 2>&1
./renderqc $S --de 9 --ate 9 > movies/clipe-domingo/render-9-montagem.log 2>&1
echo "$(date +%H:%M) fim"
