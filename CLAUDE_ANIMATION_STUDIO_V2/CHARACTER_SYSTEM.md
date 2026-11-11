# Sistema de personagem

## Rig
Trate o personagem como um boneco articulado:
- cabeça;
- pescoço;
- tronco;
- braço esquerdo/direito;
- antebraço;
- mãos;
- pernas;
- pés;
- olhos;
- sobrancelhas;
- boca;
- acessórios;
- roupa.

A estrutura pode ser implementada como componentes separados no código.

## Consistência
O personagem deve manter:
- proporções;
- formato do rosto;
- cabelo;
- paleta;
- roupa aprovada;
- acessórios;
- estilo de linha;
- escala relativa.

Não altere o design sem solicitação explícita.

## Expressões
Priorize mudanças pequenas e controladas:
- neutro;
- atenção;
- dúvida;
- surpresa;
- preocupação;
- alegria;
- irritação;
- alívio.

Use olhos, sobrancelhas, boca e inclinação da cabeça em conjunto.

## Movimento
Não troque uma pose por outra sem transição quando o plano pedir movimento. Use interpolação e, quando apropriado, pequenas sobreposições de movimento.

## QA do corpo
Em cada plano novo, procure:
- membro duplicado;
- mão ausente;
- objeto atravessando corpo;
- roupa atrás do tronco quando deveria estar na frente;
- pernas desconectadas;
- olhos desalinhados;
- acessórios mudando de posição sem motivo.
