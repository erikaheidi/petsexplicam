#!/bin/bash
# Fila da noite de 20/10: imagens dos cenários (modo imagem), depois a
# aposentadoria v2 e o audio-falso v2 (modo vídeo), em lotes de até 4 cenas.
cd /home/erika/Projects/petsexplicam
reinicia() { (cd ~/Projects/rocm-comfyui && docker compose restart); until curl -s localhost:8188/queue >/dev/null; do sleep 5; done; }
echo "$(date +%H:%M) imagens"; reinicia
for c in vestir cozinha-lurdes-closes farmacia-closes ponto-onibus; do
  ./mm images movies/cenarios/scripts/$c.yaml > movies/cenarios/$c.log 2>&1
done
echo "$(date +%H:%M) video"; reinicia
lotes() {  # filme versão: 1-4, 5-8 sem montar; 9-fim monta e legenda
  S=movies/$1/scripts/$2.yaml
  ./renderqc $S --de 1 --ate 4 --sem-montar > movies/$1/render-$2-1a4.log 2>&1
  ./renderqc $S --de 5 --ate 8 --sem-montar > movies/$1/render-$2-5a8.log 2>&1
  ./renderqc $S --de 9 > movies/$1/render-$2-9afim.log 2>&1
}
echo "$(date +%H:%M) aposentadoria"; lotes aposentadoria-subiu v2
echo "$(date +%H:%M) audio-falso"; lotes audio-falso v2
echo "$(date +%H:%M) fim"
