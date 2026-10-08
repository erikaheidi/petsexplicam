# @petsexplicam

Workspace do [moviemakr](https://github.com/erikaheidi/moviemakr) para a conta
[@petsexplicam](https://instagram.com/petsexplicam) no Instagram: Reels curtos
em que pets explicam coisas, com fala em português do Brasil, gerados com
MiniMax-H3.

Este repositório guarda só o **conteúdo** — rascunhos, roteiros YAML e imagens
de referência. O código fica no checkout do moviemakr (`~/Projects/moviemakr`),
e os vídeos renderizados ficam em `renders/`, fora do git (são reproduzíveis a
partir dos roteiros).

## Requisitos

- Checkout do moviemakr em `~/Projects/moviemakr` com o venv criado
  (`uv sync --extra web` lá dentro). Outro caminho: exporte `MOVIEMAKR_HOME`.
- ffmpeg/ffprobe no PATH.
- Um ComfyUI rodando em `http://127.0.0.1:8188` com os modelos do MiniMax-H3
  (e do Qwen-Image-2.1, para `images`). Os caminhos estão nos templates.

## Uso

Use sempre o wrapper `./mm`: ele aponta o moviemakr para **este** diretório,
mesmo que o `MOVIEMAKR_WORKSPACE` do shell aponte para outro workspace.

```bash
./mm new    gato-gravidade                              # novo vídeo, escolhendo um template
./mm render movies/gato-gravidade/scripts/v1.yaml --dry-run   # confere sem gastar GPU
./mm render movies/gato-gravidade/scripts/v1.yaml --only 1    # renderiza só a cena 1
./mm render movies/gato-gravidade/scripts/v1.yaml             # tudo, e monta o vídeo
./mm status movies/gato-gravidade/scripts/v1.yaml             # estado de cada cena
./mm serve  --host 0.0.0.0                                    # navegar pelo workspace no browser
```

O vídeo final sai em
`movies/<nome>/renders/<nome>/<nome>.mp4`.

## Estrutura

```
assets/          referências compartilhadas (o elenco fixo do perfil)
templates/       roteiros iniciais para `./mm new`
movies/<nome>/
  drafts/        a ideia em prosa: falas, tom, legenda e hashtags do post
  scripts/       v1.yaml, v2.yaml ... cada versão do vídeo
  assets/        referências só deste vídeo
  renders/       saída (ignorada pelo git)
```

## Templates

| template | uso |
| --- | --- |
| `pet-explica` (padrão) | um pet falando com a câmera, cenas independentes |
| `pet-explica-encadeado` | várias cenas como um único take contínuo |
| `fl2va-first-frame` | o vídeo começa exatamente numa foto enviada |
| `ficha-pet` | imagens de referência do pet com Qwen-Image-2.1 |

## Idioma

Tudo que vai para o perfil é em português do Brasil. O texto técnico do
prompt H3 é escrito em inglês (formato exigido pelo modelo), mas as falas
entram literais em PT-BR: `<d>[Portuguese] ...</d>`. Detalhes em
[CLAUDE.md](CLAUDE.md).

## Licenças

O conteúdo deste repositório está sob a GPL-3.0 ([LICENSE](LICENSE)). Imagens
geradas com Qwen-Image-2.1 herdam a licença de pesquisa do modelo (**uso não
comercial**).
