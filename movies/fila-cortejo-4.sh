#!/bin/bash
# Depois das cenas 8-10: as cenas 5-7 (a 5 abre no frame renato-abertura-a,
# escolha da Erika) e a montagem.
cd /home/erika/Projects/petsexplicam
PID=$(cat /tmp/cortejo/pid)
while kill -0 $PID 2>/dev/null; do sleep 20; done
echo "$(date +%H:%M) cenas 5-7"
./mm render movies/clipe-domingo/scripts/cortejo-v1.yaml --only 5-7 --halt-on-failure > movies/clipe-domingo/render-cortejo-5a7.log 2>&1
echo "$(date +%H:%M) fim"
