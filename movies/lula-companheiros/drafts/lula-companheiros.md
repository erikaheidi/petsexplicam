# lula-companheiros

Animação curta do Lula esculpido pela Erika no NomadSculpt: ele diz
"Companheiros e companheiras" e abre um sorriso. Um clipe só, ~3,75 s.

## Como

1. **Primeiro frame (Qwen)** - `scripts/frame.yaml`: um cenário caseiro atrás
   dele, no mesmo acabamento de escultura 3D, em verde, amarelo e tons de
   vermelho. Sem bandeira, faixa ou texto.
   - variante A: edição do render com fundo gradiente (`lula-gradiente.png`);
   - variante B: o Qwen gera só o cenário (`fundo-*`) e o render transparente
     (`lula-transparente.png`) é colado por cima - a escultura sai intacta.
2. **Vídeo (fl2va)** - `scripts/v1.yaml`, `first_frame:` = o frame escolhido,
   em 544x960.

## Fala

> Companheiros e companheiras.

Depois, um sorriso largo e caloroso. Voz descrita no prompt (madura, rouca,
cadência nordestina) - **nunca** voz real do Lula como referência.

## Post

Rotular como feito com IA (legenda e/ou na tela), como pede a resolução do TSE
sobre IA em conteúdo eleitoral.

- Legenda: (a definir)
- Hashtags: (a definir)
