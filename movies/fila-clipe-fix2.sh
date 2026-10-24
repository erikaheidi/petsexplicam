#!/bin/bash
cd /home/erika/Projects/petsexplicam
while pgrep -f '^/bin/bash movies/fila-clipe-fix.sh' >/dev/null; do sleep 10; done
./mm images movies/cenarios/scripts/clipe-fix2.yaml > movies/cenarios/clipe-fix2.log 2>&1
python3 /tmp/claude-1000/-home-erika-Projects-petsexplicam/9ef5be4b-7d3f-529a-99f3-a2f86d107782/scratchpad/folha.py movies/cenarios/clipe-fix2-folha.png movies/cenarios/assets/clipe-fix2-*.png
echo "$(date +%H:%M) fim"
