# Elenco do @petsexplicam

A dupla fixa do perfil. As descrições em inglês são o texto canônico para
colar em `subject_definitions` (vídeo) e nos prompts de imagem: reutilize-as
palavra por palavra, porque variar a descrição é o jeito mais rápido de o
personagem mudar de cara entre vídeos.

## Pretinha — a protagonista

Buldogue francês fêmea, preta. Baseada na Josy
(`assets/pretinha-referencia.jpg`).

- **Personalidade**: séria, metódica, paciente até certo ponto. **De
  esquerda**: quer o melhor para a população - SUS, escola pública, salário
  de quem trabalha - e não tem paciência para político de promessa vazia. É
  incisiva, mas nunca inventa: o que ela afirma tem fonte. É ela quem
  explica de verdade; fala com a autoridade de uma professora que já repetiu a
  mesma coisa muitas vezes. O humor dela é seco: olhar fixo para a câmera,
  pausa, suspiro.
- **Papel**: conduz a explicação, corrige o Paçoca.
- **Voz** (descrever fora do `<d>`): adult female voice, low and warm, precise
  diction, unhurried pace, firm but friendly. (Era "dry and slightly weary":
  saía brava até quando estava feliz. Emoção de uma fala: `tom:` no roteiro.)
- **Descrição canônica**:

  > Pretinha, a small female French bulldog: compact and muscular, a short
  > black coat with faint darker brindle striping, a white blaze covering the
  > centre of her chest, large upright bat ears set high and wide, round dark
  > brown eyes, and a short deeply wrinkled muzzle with a flat black nose. She
  > wears no collar and no harness.

## Paçoca — o coadjuvante

Pug macho, amarelo (fawn). Não existe foto real: a referência dele é a foto
de perfil aprovada (`assets/pacoca-referencia.png`, cópia de
`movies/foto-perfil/assets/foto-perfil-final.png`). A imagem tem os dois: o
Paçoca é **o pug à direita**. Diga isso no prompt
(`<Subject 2> is Paçoca, the pug on the right in <Picture N>`) para o modelo
não tirar a Pretinha dessa referência.

- **Personalidade**: atrapalhado, entusiasmado, cômico. **Desinformado, mas
  de boa índole**: está meio perdido, vota pelo vídeo mais engraçado ou pelo
  que viu no zap, e muda de ideia quando entende. Entende tudo pela metade,
  tira conclusões erradas com total confiança, se distrai com comida. É o
  melhor amigo da Pretinha e o motivo de ela suspirar. O arco de todo vídeo
  é ele aprendendo - nunca ridicularizado: é o eleitor que queremos alcançar.
- **Papel**: faz as perguntas que o público faria, erra para a Pretinha
  corrigir, entrega a piada no final.
- **Voz**: young male voice, bright and slightly nasal, fast and excitable,
  words tumbling over each other.
- **Descrição canônica**:

  > Paçoca, a male pug: stocky and round, a short fawn-yellow coat, a jet-black
  > mask over his muzzle and around his eyes, small black folded ears, large
  > round glossy dark eyes, deep wrinkles on his forehead, and a tightly curled
  > tail. He wears no collar and no harness.

## Primo José — o convidado

Vira-lata caramelo macho, primo do Paçoca. Formado em análise de sistemas,
trabalha com TI. Aparece quando o assunto é tecnologia. Joga bola com o
Paçoca e os dois vão lanchar no boteco depois da pelada. Referências
(Qwen, `movies/ficha-jose/`): `assets/jose-referencia.png` (de frente, corpo
inteiro) e `assets/jose-referencia-3q.png` (três quartos, boca entreaberta).

- **Personalidade**: tranquilo, didático, paciente com o primo. Explica
  tecnologia com exemplos do dia a dia (o celular, o computador), sem jargão.
  Tem consciência de classe de quem é trabalhador de TI: sabe que quem
  controla a tecnologia controla o emprego. Fala com fonte, como a Pretinha,
  mas com mais calor e menos suspiro.
- **Papel**: explica o assunto técnico para o Paçoca; o Paçoca pergunta.
- **Voz**: young adult male voice, a guy of about twenty-three, light and
  warm, relaxed and friendly, clear, steady explaining pace. ("adult male"
  saiu maduro demais.) (Ainda sem gravação de referência: a
  `jose-voz.wav` sai recortada da primeira cena boa dele, como as da dupla.)
- **Descrição canônica**:

  > José, a male Brazilian caramelo mixed-breed dog (vira-lata caramelo):
  > medium-sized and lean, a short smooth caramel-golden coat, slightly paler
  > cream fur on his muzzle, throat and chest, medium triangular ears that
  > stand up at the base and fold forward at the tips, warm amber-brown eyes,
  > a longish muzzle with a black nose, and a long tail that curves up in a
  > loose sickle. He wears no collar and no harness.

  A descrição canônica é sem roupa. O figurino é do cenário: na `lanchonete`
  os dois usam a camiseta do time da pelada (verde com listras brancas, lisa,
  sem escudo nem número).

  No `home-office` (vlog, sentado à mesa) ele usa camiseta cinza lisa e fone
  no pescoço, e a descrição vai **sem a frase do rabo** (`sem_rabo` no
  cenário): o rabo aparecia estranho atrás da cadeira.

## Seu Tião — o motorista de aplicativo

Vira-lata malhado macho, uns cinquenta anos. Motorista de aplicativo:
aparece no cenário `uber`, com a Pretinha no banco de trás. Referências
(Qwen, `movies/ficha-tiao/`): `assets/tiao-referencia.png` (de frente) e
`assets/tiao-referencia-3q.png` (três quartos, boca entreaberta) - par A
da ficha, escolhido pela Erika.

- **Personalidade**: gente boa, trabalhador, cansado. Faz as horas dele,
  acha que política não muda a vida dele ("eu faço meu horário"). Pai de
  uma filha, que é o que o faz prestar atenção. É o eleitor indiferente que
  queremos alcançar: nunca ridicularizado, a conversa é de igual para igual.
- **Papel**: conversa com a Pretinha durante a corrida; começa indiferente e
  termina pensando na filha.
- **Voz**: middle-aged male voice, a man of about fifty, deep and slightly
  hoarse, relaxed and unhurried, plain-spoken, a little tired but friendly.
  (A `tiao-voz.wav` sai recortada da primeira cena boa dele, como a do José.)
- **Descrição canônica**:

  > Tião, a male Brazilian mixed-breed dog (vira-lata malhado): medium-sized
  > and sturdy, a short white coat with large irregular black patches - one
  > black patch covering his left ear and the area around his left eye, and
  > a large black patch across his back - tan-brown markings on his cheeks
  > and above his eyes, a greying muzzle with white hairs around the mouth,
  > semi-floppy ears that stand up at the base and fold over halfway, kind,
  > slightly tired brown eyes, a medium-length muzzle with a black nose, and
  > a long tail. He wears no collar and no harness.

  A descrição canônica é sem roupa. No `uber` ele usa uma camisa polo
  azul-clara, lisa, sem logo.

## Dona Cida e Dona Lurdes — as vizinhas

Duas senhoras do bairro, amigas de longa data, que a Pretinha encontra no
supermercado (cenário `supermercado`, estreia no `secao-mudou`). Referências
(Qwen, `movies/ficha-senhoras/`): `assets/cida-referencia.png`,
`assets/lurdes-referencia.png` e as `-3q.png`. Vozes ainda sem gravação: a
`cida-voz.wav` / `lurdes-voz.wav` saem recortadas da primeira cena boa de
cada uma.

- **Personalidade**: queridas, conversadeiras, desconfiadas de aplicativo.
  Votam desde sempre e não abrem mão. Representam o eleitor idoso, que mais
  perde com mudança de última hora - nunca ridicularizadas.
- **Papel**: perguntam, se espantam, aceitam a ajuda da Pretinha.
- **Voz da Cida**: elderly female voice, a woman of about seventy-five, thin
  and slightly quavering, sweet and chatty, a little breathless.
- **Voz da Lurdes**: elderly female voice, a woman of about seventy, low and
  a little husky, warm and motherly, at an unhurried pace.
- **Descrição canônica da Cida**:

  > Dona Cida, an elderly female poodle: small and slender, a soft curly
  > coat of off-white fur gone slightly creamy with age, a greying muzzle,
  > long curly ears hanging down beside her face, gentle dark brown eyes a
  > little cloudy with age, a narrow muzzle with a black nose. She wears a
  > plain lilac hand-knitted cardigan with no pattern, buttoned at the
  > chest, her front legs through the sleeves, and no collar.

- **Descrição canônica da Lurdes**:

  > Dona Lurdes, an elderly female cocker spaniel: medium-sized and plump,
  > a wavy golden-red coat, a muzzle and eyebrows gone white with age, long
  > silky wavy ears hanging below her jaw, warm, slightly droopy brown
  > eyes, a broad muzzle with a brown nose. She wears a plain sea-green
  > hand-knitted cardigan with no pattern, buttoned at the chest, her front
  > legs through the sleeves, and no collar.

  O cardigã faz parte da descrição canônica: liso, sem estampa (estampa vira
  borrão no vídeo).

## A dinâmica

Melhores amigos. Ela explica, ele atrapalha; ela perde a paciência, mas nunca
o carinho. Nos vídeos a dupla funciona como "professora e aluno que não
estudou": a Pretinha olha para a câmera quando o Paçoca fala besteira.
