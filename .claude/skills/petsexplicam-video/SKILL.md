---
name: petsexplicam-video
description: Produzir um vídeo do @petsexplicam (Pretinha e Paçoca) do rascunho ao arquivo postável - roteiro, cenário e câmeras, render com QC de voz, montagem, legendas e legenda do post. Use sempre que a Erika pedir um vídeo novo, um roteiro, um cenário novo, para renderizar/refazer cenas, legendar, ou para preparar a postagem; e quando um render der problema (voz trocada, boca que não mexe, câmera tremendo, drift).
---

# Vídeo do @petsexplicam

Receita que funcionou no `direito-de-votar` e no `pesquise-antes` v2. Os
detalhes vivem nos arquivos - leia antes de começar:

- `CLAUDE.md` - regras do workspace, `./mm`, regras do moviemakr que mais pegam
- `ELENCO.md` - Pretinha (de esquerda, séria, incisiva com fonte) e Paçoca
  (bom coração, desinformado, aprende; nunca ridicularizado)
- `tools/dialogo.py` - a receita de prompt (elenco, `CENARIOS`, câmeras)
- `tools/roteiro-exemplo.yaml` - formato do roteiro

Missão: vídeos que movem eleitores antes do 2º turno (25/10/2026). Tom
incisivo à esquerda, **todo fato verificável** (TSE, camara.leg.br,
senado.leg.br). Nada inventado sobre candidatos.

## 1. Roteiro

```bash
./dialogo novo <filme>          # movies/<filme>/ + roteiro.yaml de exemplo
./dialogo cenas <filme>         # câmera, quem fala, palavras, duração; avisos
./dialogo gerar <filme>         # -> scripts/v1.yaml  (NUNCA edite o gerado)
```

- Falas em PT-BR **literais**, números por extenso, só `. , ? ! :`.
- Ações (`antes`/`depois`/`resumo`) em inglês, com os nomes "Pretinha" e
  "Paçoca" (viram os rótulos certos de cada plano).
- Uma fala por cena; cabe ~11 palavras (Pretinha) / ~13 (Paçoca) em 5,17 s.
  `./dialogo cenas` acusa fala longa - divida.
- Meta: 6-10 cenas, 25-45 s.
- Cenário padrão `sofa-frente` (os dois de frente, closes por cima do ombro).
  Sem `camera:`, a cena vai no close de quem fala; `camera: dupla` para
  abertura, reações e o gancho.
- **Olhar**: no `sofa-frente` eles já estão virados um para o outro - escreva
  "keeps looking at him", nunca "turns her head towards him" (o modelo vira
  para a câmera).
- **Fora de quadro**: num close, o outro cachorro não pode *fazer* nada
  ("Paçoca's ears droop" num close da Pretinha). O `cenas` avisa.
- Outra versão em outro cenário: `./dialogo gerar <filme> --versao v2 --cenario <nome>`.

Mostre a tabela de falas para a Erika aprovar antes de gastar GPU.

## 2. Render (GPU: ~20-25 min por cena)

```bash
./mm render movies/<filme>/scripts/v1.yaml --dry-run
./renderqc movies/<filme>/scripts/v1.yaml --de 1 --ate 2 --sem-montar   # teste
./renderqc movies/<filme>/scripts/v1.yaml --de 3                       # resto + montagem + legendas
```

- Sempre teste 1-2 cenas e mostre frames antes do render completo. Folha de
  frames: `ffmpeg -i clip.mp4 -vf "select='eq(n\,2)+eq(n\,40)+eq(n\,80)',scale=240:427,tile=3x1" -frames:v 1 out.png`
  e leia a imagem.
- O Claude **não ouve áudio**: peça para a Erika ouvir voz e boca. O
  `renderqc` mede o tom (F0): Pretinha ~258 Hz, Paçoca ~296 Hz; reprova
  20% abaixo / 35% acima, anota e **segue** (cenas são independentes).
- Cena ruim: `seed:` nova nela no roteiro, `./dialogo gerar`, `--only N`. Se a
  Erika gostar de uma cena que o QC reprovou, ela fica (a original ainda está
  em `~/Projects/rocm-comfyui/data/output/moviemakr/<nome>/`).
- Rode em background, um vídeo por vez, sem pipe (`exec ./renderqc ... > log`),
  para um SIGTERM chegar ao moviemakr e ele cancelar o job no ComfyUI. Se
  sobrar job órfão: `curl -X POST http://127.0.0.1:8188/interrupt`.
- **Imagem (Qwen) e vídeo não dividem o ComfyUI**: `docker compose restart`
  em `~/Projects/rocm-comfyui` entre um e outro.
- ComfyUI não sobe com "bind source path does not exist": o disco Storage
  (LUKS) está trancado - só a Erika destranca.

## 3. Postar

- Arquivo: `movies/<filme>/renders/<nome>/<nome>-legendado.mp4`
  (`./legendas <script>` refaz; `--previa N` legenda só as N primeiras cenas).
- Legenda do post + hashtags em `movies/<filme>/drafts/<filme>.md`.
- Checklist: rótulo de IA ligado; sem impulsionamento pago (só candidatos e
  partidos podem); nada novo no dia da votação (até a véspera, 24/10); fatos
  conferidos na fonte oficial.

## Cenário novo

1. Script `kind: images` em `movies/cenarios/scripts/` editando um frame
   aprovado (`ref_images: [cenario-sofa.png]`): plano da dupla + closes por
   cima do ombro, 2 seeds cada (~3 min por imagem). Modelo:
   `frente-sofa.yaml`.
2. A Erika escolhe; copie para `assets/cenario-<nome>[-pretinha|-pacoca].png`.
3. Entrada em `CENARIOS` (tools/dialogo.py) com `quadro`/`abertura` de cada
   câmera escritos **olhando a imagem escolhida**; quem está fora do plano é
   citado por descrição, não por rótulo.
4. Teste 1-2 cenas antes de usar num vídeo.

Já existem planos abertos (sem closes) de cozinha e varanda em
`movies/cenarios/assets/cenarios-{cozinha,varanda}-{a,b}.png`.

## Quando der errado

| sintoma | causa | conserto |
| --- | --- | --- |
| câmera tremendo | 4 passos / atenção esparsa desde o início | `steps: 8`, `sol_attn` start 0.2 / end 1.0 (já no `dialogo`) |
| câmera subindo, imagem degradando | chain longo | cenas independentes + frame de referência (já no `dialogo`) |
| voz uma oitava abaixo | texto da voz contradiz a referência | descrição em texto alinhada ao `<Audio 1>` (já no `dialogo`) |
| voz sai, boca não mexe | rosto escondido / cabeça baixa | "on screen ... mouth visibly opening", rosto para a câmera |
| personagem vira para a câmera | ação "turns towards him" quando já está virado | "keeps looking at him" |
| logo na tampa do notebook | prior do modelo | objeto preto fosco; prompt negativo não funciona no comfy |

Requer o moviemakr do branch `ref-audios` (suporte a `ref_audios`).
