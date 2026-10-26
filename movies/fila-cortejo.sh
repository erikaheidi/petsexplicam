#!/bin/bash
# Troca a fila do cortejo depois da cena 4: o render 3-10 em curso leu o script
# antigo (closes de todos em toda cena, lento demais); as cenas 5-10 seguem com
# o script novo (uma referência por cena).
cd /home/erika/Projects/petsexplicam
D=movies/clipe-domingo/renders/clipe-domingo-cortejo/scenes
PID=$(cat /tmp/cortejo/pid)
until [ -f $D/004-04-jose.mp4 ]; do sleep 20; done
sleep 5
kill -TERM -- -$PID
sleep 15
until curl -s -m 5 localhost:8188/queue | grep -q '"queue_running": \[\]'; do sleep 5; done
echo "$(date +%H:%M) cenas 5-10"
./mm render movies/clipe-domingo/scripts/cortejo-v1.yaml --only 5-10 --halt-on-failure > movies/clipe-domingo/render-cortejo-5a10.log 2>&1
echo "$(date +%H:%M) fim"
