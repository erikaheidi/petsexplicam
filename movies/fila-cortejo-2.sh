#!/bin/bash
# Depois da cena 7, as cenas 8-10 com o script novo (a 8 abre num corte seco).
cd /home/erika/Projects/petsexplicam
D=movies/clipe-domingo/renders/clipe-domingo-cortejo/scenes
PID=$(cat /tmp/cortejo/pid)
until [ -f $D/007-07-pretinha.mp4 ]; do sleep 20; done
sleep 5
kill -TERM -- -$PID
sleep 15
until curl -s -m 5 localhost:8188/queue | grep -q '"queue_running": \[\]'; do sleep 5; done
echo "$(date +%H:%M) cenas 8-10"
./mm render movies/clipe-domingo/scripts/cortejo-v1.yaml --only 8-10 --halt-on-failure > movies/clipe-domingo/render-cortejo-8a10.log 2>&1
echo "$(date +%H:%M) fim"
