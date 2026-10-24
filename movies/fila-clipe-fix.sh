#!/bin/bash
cd /home/erika/Projects/petsexplicam
./mm images movies/cenarios/scripts/clipe-fix.yaml > movies/cenarios/clipe-fix.log 2>&1
python3 /tmp/claude-1000/-home-erika-Projects-petsexplicam/9ef5be4b-7d3f-529a-99f3-a2f86d107782/scratchpad/folha.py movies/cenarios/clipe-fix-folha.png movies/cenarios/assets/clipe-fix-*.png
echo "$(date +%H:%M) fim"
