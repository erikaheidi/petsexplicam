# CLAUDE.md

Orientações para o Claude Code neste repositório.

## O que é isto

Um **workspace do [moviemakr](https://github.com/erikaheidi/moviemakr)** dedicado à conta
**[@petsexplicam](https://instagram.com/petsexplicam)** no Instagram: vídeos
curtos e verticais em que pets explicam coisas para a câmera.

Aqui só há **dados** (roteiros, rascunhos, imagens de referência). O código do
moviemakr fica em `~/Projects/moviemakr` — a documentação de referência é o
`README.md`, o `CLAUDE.md` e `docs/` de lá. Consulte-os antes de mexer em
qualquer chave de script que não esteja nos templates daqui.

## Elenco

A dupla fixa é **Pretinha** (buldogue francês preta, séria, protagonista) e
**Paçoca** (pug amarelo, atrapalhado, coadjuvante). Personalidade, vozes e as
descrições canônicas para os prompts estão em [ELENCO.md](ELENCO.md) — use-as
palavra por palavra em todo script. As referências ficam no `assets/`
compartilhado (`pretinha-referencia.jpg`; `pacoca-referencia.png` depois que a
foto de perfil for aprovada).

## Idioma: tudo em português do Brasil

Todo o conteúdo do perfil é em **PT-BR**: rascunhos, falas, texto que aparece
na tela, legendas, hashtags, nomes de filmes e de cenas, comentários nos YAML e
os próprios docs deste repo.

A única exceção é o **corpo do prompt H3**, que fica em **inglês** — é o que o
skill `h3-prompt-writing` exige e o que o modelo entende melhor. Dentro dele:

- **Fala** vai literal, em PT-BR, com a tag de idioma:
  `(S1) says: <d>[Portuguese] Gato não derruba copo, gato testa a gravidade.</d>`
  Nunca traduza nem reescreva a fala ao montar o prompt — o texto dentro de
  `<d>` é o que o pet vai dizer.
- **Texto visível na tela** (placas, legendas queimadas) também em PT-BR, entre
  aspas duplas, literal.
- A voz é descrita em inglês **fora** da tag (idade, timbre, ritmo, atitude).

## Sempre use `./mm`

O shell da Erika exporta `MOVIEMAKR_WORKSPACE=~/moviemakr-workspace` (o
workspace pessoal, da Josy). Rodar `moviemakr` direto daqui **escreve no
workspace errado**. O wrapper `./mm` fixa o workspace neste diretório e usa o
venv do checkout:

```bash
./mm new      gato-gravidade                                 # cria movies/gato-gravidade/
./mm new      gato-gravidade --template pet-explica-encadeado
./mm render   movies/gato-gravidade/scripts/v1.yaml --dry-run  # SEMPRE primeiro
./mm render   movies/gato-gravidade/scripts/v1.yaml --only 1   # uma cena para conferir
./mm render   movies/gato-gravidade/scripts/v1.yaml
./mm status   movies/gato-gravidade/scripts/v1.yaml
./mm assemble movies/gato-gravidade/scripts/v1.yaml
./mm images   movies/ficha-thor/scripts/v1.yaml --dest assets   # referências compartilhadas
./mm serve --host 0.0.0.0
```

`MOVIEMAKR_HOME` sobrescreve o caminho do checkout (padrão
`~/Projects/moviemakr`).

**Render real custa de minutos a horas de GPU.** Não dispare `render` nem
`images` sem `--dry-run` a menos que isso tenha sido pedido explicitamente. O
dry-run imprime o grafo exato que vai para o ComfyUI e não precisa de servidor.

## Estrutura

```
assets/                 referências compartilhadas: pets recorrentes do perfil
templates/              scripts iniciais oferecidos pelo `./mm new`
movies/<nome>/
  drafts/               rascunho em prosa (PT-BR): ideia, falas, legenda
  scripts/              v1.yaml, v2.yaml ... cada take do vídeo
  assets/               referências só deste vídeo
  renders/              saída; descartável, ignorada pelo git
```

- **Nomes de filme**: slug em PT-BR, curto e descritivo (`cachorro-explica-carteiro`).
- Um asset vai para `assets/` compartilhado quando dois ou mais vídeos usam
  (o elenco fixo do perfil); senão fica no `assets/` do filme.
- Só `renders/` e `.cache/` são descartáveis. Roteiros e referências são o
  trabalho — commite-os.
- **Não mude `name:`** de um script que já renderizou, nem mova o script para
  outro filme: o diretório de render deriva de `name:` e do filme, e os clipes
  ficam órfãos.

## Fluxo de um vídeo

1. **Rascunho** em `movies/<nome>/drafts/` (PT-BR): quem é o pet, o que ele
   explica, as falas exatas, o tom, e a **legenda + hashtags** do post.
2. **Roteiro**: expanda o rascunho em `scripts/v1.yaml` usando o skill
   `h3-prompt-writing` (formato Ref2VA de seis seções, `references/ref-en.txt`;
   para `first_frame:`/fl2va, o formato I2VA de `references/base-en.txt`).
3. `./mm render ... --dry-run`, depois `--only 1`, depois o resto.
4. Uma nova tentativa é um novo arquivo (`v2.yaml`), não uma edição destrutiva
   do que já renderizou bem.

## Templates

| template | quando usar |
| --- | --- |
| `pet-explica` (padrão) | um pet fala com a câmera; cenas independentes, ref2va |
| `pet-explica-encadeado` | explicação longa como um take contínuo: anchors + overlap |
| `fl2va-first-frame` | o vídeo abre exatamente numa foto sua (identidade mais fiel) |
| `ficha-pet` | gerar imagens de referência do pet com Qwen-Image-2.1 |

Os templates são scripts comuns; `__project__` vira o nome do filme e as
linhas `# template:` / `# default:` alimentam o seletor do `./mm new`.

## Regras do moviemakr que mais pegam

- **Formato Reels**: 544x960 (9:16), 24 fps. `video_frames` na grade **17n+5**
  (90 = 3,75 s; 107 = 4,46 s). Uma cena comporta uma frase curta; fala longa =
  mais cenas.
- **Bloco literal `|-`** no `prompt:`, nunca `>-` (achata os rótulos das seções).
- **`style_suffix: ""`** em scripts com prompt H3 estruturado — o sufixo seria
  colado depois de `non_diegetic_music:`. O visual vai em `detailed_description`.
- **`<Picture N>` segue a ordem real das refs.** No comfy: anchors primeiro,
  depois `ref_images` da cena; o encadeamento não ocupa índice. No sdcpp o
  último frame encadeado entra como `<Picture 1>` e tudo desloca uma posição.
- **fl2va**: `first_frame:` não pode coexistir com `ref_images` nem
  `continuity.anchors` — qualquer um troca o grafo para ref2va e a foto é
  **descartada em silêncio**.
- Nas trilhas, exclua explicitamente latido/miado por cima da fala no
  `overall_soundscape`.
- O aviso `carries no fl2va/ref2va marker` no dry-run dos templates comfy é
  esperado (o checkpoint VSA não tem marcador no nome); confira a cena 1 antes
  de rodar tudo.
- **Licença**: Qwen-Image-2.1 (`./mm images`) é de pesquisa, **uso não
  comercial**. Se o perfil for monetizado, não publique imagens geradas por ele
  nem vídeos que dependam delas sem rever isso.

## Skill de prompt

`.claude/skills/h3-prompt-writing` é um symlink para o skill instalado no
checkout do moviemakr (`../moviemakr/.claude/skills/h3-prompt-writing`), versão
fixada no `skills-lock.json` de lá.
