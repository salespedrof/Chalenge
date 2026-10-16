# Elevate: MVP navegável

**Squad Elevate · Challenge Motiva + FIAP 2026**
Artur Henrique Siqueira (RM 566986) · Davi de Souza Malta (RM 560327) · Guilherme Cruz Alves (RM 566861) · Guilherme de Oliveira Scremin (RM 564788) · Pedro Sales Ferreira (RM 566910)

O Elevate é um tablet com Raspberry Pi que mostra o status de cada escada rolante da Linha 4 a partir dos sensores e registra a entrada e a saída do técnico em cada manutenção. Este pacote é o protótipo navegável descrito no PRD.

**Todos os dados de sensores são simulados.** A Motiva ainda não enviou leituras reais. O cadastro das 197 escadas, as estações, os fabricantes e o risco de cada escada vêm do histórico SAP real.

## Como abrir

1. Dê dois cliques em `index.html`. Ele abre no Chrome, Edge ou Firefox.
2. Não precisa de internet, instalação nem servidor. Os dados e os gráficos estão dentro do arquivo.
3. Para parecer um tablet, use a tela cheia (F11) ou abra no próprio tablet.

## Conteúdo do pacote

| Arquivo | Para quê |
| --- | --- |
| `index.html` | O protótipo completo (7 telas), com o dataset oficial e o gerador embutidos |
| `PRD_Elevate_MVP_Navegavel.md` | Documento de requisitos do MVP |
| `dados/` | Dataset oficial em CSV (semente 2026), o gerador em Python e o dicionário de dados |
| `codigo-fonte/` | `template.html` (código do app), `build.py`, que gera o `index.html` a partir dos CSVs, e `three.min.js` (biblioteca 3D, licença MIT) |

## As 7 telas

1. **Painel:** status das 197 escadas (BOM, ALERTA, CRÍTICO, EM MANUTENÇÃO) por estação, mini gráfico de cada escada e contador de **tendência de piora**.
2. **Detalhe da escada:** **gêmeo digital 3D** (ou modo leve 2D), **diagnóstico Elevate** com previsão, **ordem de serviço**, **procedimento sugerido**, gráficos das 6 variáveis, histórico e controle da P1.
3. **Fila:** ordem de atendimento, prazo de despacho e escadas com tendência de piora.
4. **Atendimentos:** ordens de serviço e entrada e saída do técnico, com cronômetro.
5. **Indicadores:** disponibilidade, tempo de reparo e de resposta, antecedência ALERTA → CRÍTICO, ranking.
6. **Sincronização:** funcionamento sem Wi-Fi e fila de envio.
7. **Dados:** botão para **gerar um novo dataset** e exportar os CSVs.

## O que o Elevate faz além de um painel de status

- **Gêmeo digital ligado aos dados:** o componente com problema acende na cor do status (redutor para vibração, reservatório para óleo, quadro para tensão, módulo de sensores quando não responde). Os degraus andam na velocidade medida e param na parada. O reservatório mostra o nível de óleo real. "Casa de máquinas" aproxima a câmera. "Modo leve" troca para um esquema 2D para o Raspberry Pi.
- **Diagnóstico com previsão:** o texto diz o modo de falha provável, a tendência das últimas 15 leituras e quando a escada chega a CRÍTICO se nada for feito. É gerado por regras e diz isso na tela, sem prometer IA.
- **Tendência de piora:** escadas ainda em BOM que vão entrar em ALERTA nas próximas 48 h aparecem antes do alarme.
- **Ordem de serviço ligada ao atendimento:** a OS abre com prioridade, prazo e diagnóstico, passa a "em execução" na entrada do técnico e fecha na saída.
- **Modo apresentação:** o botão "Apresentar" esconde os controles da simulação.

## Gerar um dataset no próprio dashboard

1. Abra a aba **Dados**.
2. Escolha a semente (ou toque em "Sortear"), o período (30, 60 ou 90 dias) e a intensidade de defeitos.
3. Toque em **Gerar dataset**. Leva menos de 1 segundo.
4. O painel passa a usar os dados novos e a lista de cenários de demonstração é montada a partir dos defeitos sorteados.
5. Para voltar aos dados do notebook e do PRD, toque em **Voltar ao dataset oficial**.

A mesma semente com as mesmas opções gera sempre os mesmos dados. O dataset escolhido continua depois de fechar e abrir o arquivo. Os CSVs podem ser baixados na mesma aba, no formato usado pelo notebook de Data Science.

O gerador do navegador segue o mesmo algoritmo do `dados/gerar_dataset.py`, mas usa outro gerador de números aleatórios. Por isso a semente 2026 do Python e uma semente 2026 gerada no navegador não dão os mesmos números. O "dataset oficial" é sempre o do Python.

## Roteiro de apresentação para a Motiva (cerca de 5 minutos)

Use o menu **Cenário de demonstração**, no topo. Ele pausa o relógio e leva direto ao ponto certo.

Antes de começar, toque em **Apresentar**.

1. **Problema (Painel):** "Hoje a falha é descoberta quando a escada já parou." Mostre os contadores, o aviso vermelho de despacho imediato e o contador de **tendência**.
2. **Gêmeo digital e diagnóstico (CEN-02, PIN-ER13):** abra a escada. O redutor está vermelho; toque em "Casa de máquinas". Leia o diagnóstico: desgaste de rolamento, +0,71 mm/s por dia, ação recomendada.
3. **Priorização e OS (Fila):** PIN-ER13 aparece no topo com despacho **Imediato**. Toque em "Abrir OS" e emita a ordem de serviço com prazo de 1 h.
4. **Atendimento (CEN-08, FAL-ER02):** toque em "Iniciar atendimento" (a barreira aparece no 3D e os degraus param), avance o relógio com ⏭ e finalize com componente e ação. A duração é calculada sozinha.
5. **Sem Wi-Fi (CEN-09):** ligue "Simular sem conexão", registre um atendimento e mostre o registro pendente. Desligue e veja a sincronização.
6. **Menos alarme falso (CEN-06, BUT-ER05):** um pico isolado de 29,8 mm/s vira "Leitura suspeita", e não CRÍTICO.
6b. **Antes do alarme (Fila → Tendência de piora):** escadas ainda BOM com ALERTA previsto em até 48 h.
7. **Indicadores:** disponibilidade, antecedência mediana entre ALERTA e CRÍTICO, e as escadas que mais exigem atenção.
8. **Dados:** gere um dataset novo na frente deles para mostrar que o protótipo não depende de um caso preparado.

Para começar de novo: aba **Sincronização** → **Reiniciar demonstração**.

## Regenerar o index.html a partir dos CSVs (opcional)

Com Python 3 e pandas instalados:

```
cd codigo-fonte
python build.py
```

O `build.py` lê os CSVs de `../dados` e grava `index.html` dentro de `codigo-fonte`.

## Limites do protótipo

- Os limites de ALERTA e CRÍTICO, o grupo crítica / não crítica e os prazos de despacho são hipóteses do grupo e precisam ser validados com a engenharia da Motiva.
- Não há integração com sensores reais, SAP ou servidor. A sincronização é simulada.
- O sistema é só consultivo: não liga, desliga nem reseta escadas.
