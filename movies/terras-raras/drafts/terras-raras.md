# terras-raras

Estreia do **primo José** (vira-lata caramelo, analista de sistemas, trabalha
com TI - ver ELENCO.md). O Paçoca e o primo sempre jogam bola juntos; depois
da pelada, vão lanchar no boteco da esquina, os dois com a camiseta do time.
Entre uma coxinha e outra, o Paçoca pergunta de terras raras. O José explica o que são, para que servem (o celular, o computador, o
carro elétrico), que o Brasil tem a segunda maior reserva do mundo, e o que
está em jogo no 2º turno: processar aqui, com emprego brasileiro, ou entregar
a pedra bruta.

Tom: o José é calmo e didático, o Paçoca curioso e enganado pela metade
("é terra de plantar?", "vende tudo e fica rico"). Ninguém é ridicularizado.
Incisivo no fim, mas só com o que está publicado.

Cenário: `lanchonete` (novo, externo) - mesa de plástico vermelha na calçada
do boteco, coxinhas e refrigerante, bola no chão. Os dois com a mesma camiseta
do time da pelada: verde com listras brancas, lisa, sem escudo nem número.
Script: `movies/cenarios/scripts/lanchonete.yaml`.

## Falas (uma por cena)

| # | quem | fala |
| --- | --- | --- |
| 1 | Paçoca | Primo, todo mundo tá falando de terras raras. É terra de plantar? |
| 2 | José | Não, Paçoca. São dezessete elementos químicos escondidos nas rochas. |
| 3 | José | Estão no seu celular, no computador e no carro elétrico. |
| 4 | Paçoca | E o Brasil tem isso? |
| 5 | José | A segunda maior reserva do mundo. Só perde pra China. |
| 6 | Paçoca | Então a gente vende tudo e fica rico! |
| 7 | José | Vender pedra bruta dá pouco. O dinheiro tá em processar aqui. |
| 8 | José | Em setembro, o Lula sancionou a lei dos minerais críticos. |
| 9 | José | Ela dá incentivo pra quem processa aqui, com emprego brasileiro. |
| 10 | José | Já o Flávio foi aos Estados Unidos encontrar o Trump. |
| 11 | José | E prometeu aos americanos parceria nas nossas terras raras. |
| 12 | Paçoca | Entendi! É igual craque da várzea: o gringo leva barato! |
| 13 | José | Exato, primo. Dessa vez, o craque fica em casa. |

13 cenas, ~62 s - acima da meta (25-45 s), mas a Erika preferiu manter
todas. Fechamento: o craque da várzea vendido barato para fora é a mesma
lógica da pedra bruta exportada; "o craque fica em casa" é o gancho.

## Fatos citados (conferir na fonte oficial antes de postar)

- **17 elementos**: os 15 lantanídeos + escândio + ítrio (definição IUPAC).
- **Usos**: ímãs de neodímio (motores de carro elétrico, turbinas eólicas,
  discos rígidos, alto-falantes de celular), telas, fibra óptica.
- **2ª maior reserva**: USGS, Mineral Commodity Summaries - Brasil ~21 mi t,
  China ~44 mi t. Conferir a edição (2025 ou 2026) no usgs.gov e o número no
  Serviço Geológico do Brasil (sgb.gov.br). Produção brasileira ainda ínfima.
- **Lei dos minerais críticos**: Política Nacional de Minerais Críticos e
  Estratégicos, sancionada pelo Lula em ~16/09/2026, sem vetos; crédito fiscal
  ligado à agregação de valor no país; cria o conselho CIMCE, que homologa
  operações estratégicas (venda de controle de mineradora, acordos
  internacionais). Número citado pela imprensa: Lei 15.506/2026 - **conferir
  no planalto.gov.br** e os valores do incentivo (as fontes divergem: R$ 5 bi
  x R$ 7 bi; por isso a fala não cita valor).
- **Flávio e os EUA**: depois de se reunir com o Trump em Washington, disse
  que, se eleito, fará parceria estratégica de longo prazo com os EUA em terras
  raras (CNN Brasil, set/2026). **Não** citar o documento "Prosperity
  Partnership" atribuído à campanha: a autoria é contestada.

## Legenda do post

Capa (`assets/`, 1080x1920, texto dentro do recorte 3:4 do grid):
`capa-terra-de-plantar.png` (Paçoca, "É TERRA DE PLANTAR?"),
`capa-terras-raras-dupla.png` (os dois na lanchonete) ou
`capa-primo-jose.png` (José, "o primo da TI explica").

O Paçoca achou que terra rara era terra de plantar. 🌱🐶 O primo José, que
trabalha com TI, explicou: tá no seu celular, no seu computador, e o Brasil
tem a segunda maior reserva do mundo. A pergunta é quem vai processar e quem
vai ficar com o emprego. 🇧🇷

Fontes: USGS (reservas), Lei dos Minerais Críticos (planalto.gov.br).

#terrasraras #soberania #mineraiscriticos #eleicoes2026 #segundoturno
#vemprovoto #caramelo #pug #petsexplicam

## Pendências

- [ ] Aparência do José aprovada (`movies/ficha-jose/`) -> `assets/jose-referencia.png`
- [ ] Cenário `lanchonete`: rodada 1 (dupla), Erika escolhe, rodada 2 (closes) -> `assets/cenario-lanchonete*.png` + `CENARIOS`
- [ ] `tools/dialogo.py`: figurino por cenário (a camiseta) - hoje a aparência diz "no collar and no harness" e nada mais
- [ ] Voz do José: primeira cena dele sem referência de áudio, recortar -> `assets/jose-voz.wav`
- [ ] `tools/dialogo.py`: José no `ELENCO` (+ F0 de referência e cor de legenda)
- [ ] Fatos conferidos na fonte oficial (marcados acima)
- [ ] Rótulo de IA; sem impulsionamento; postar até 24/10
