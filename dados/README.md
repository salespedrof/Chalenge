# Dataset simulado de sensores: escadas rolantes da Linha 4

A Motiva não vai entregar leituras reais nas Sprints 1 e 2. Este pacote traz um dataset **simulado** com as 5 variáveis do enunciado (vibração, temperatura, corrente/tensão, nível de óleo e velocidade). Ele serve para Data Science, Dynamic Programming, o modelo de DDD/Database e o dashboard do tablet.

**Toda entrega que usar estes dados precisa dizer que eles são simulados.**

## O que é real e o que é simulado

| Item | Origem |
| --- | --- |
| 197 códigos de escada, 12 estações, fabricante (188 Thyssen e 9 ESCAL; o plano lista 10 ESCAL, uma não foi identificada nos dados) | Real: histórico SAP enviado pela Motiva |
| Risco relativo de cada escada | Derivado do número real de falhas de 2023 a 2026 (`perfil_escadas.csv`) |
| Todas as leituras de sensor | Simuladas |
| Limites de Alerta e Crítico | Hipótese do grupo (vibração inspirada nas zonas da ISO 10816) |
| Grupo crítica / não crítica | Hipótese: a lista real (REF-6ECR-0002) não foi enviada |
| Defeitos, manutenções e técnicos (T01 a T12) | Simulados |

## Arquivos

| Arquivo | Linhas | Conteúdo |
| --- | --- | --- |
| `leituras_sensores.csv` | 88.827 | Uma leitura por escada às 6h, 10h, 14h, 18h e 22h, de 01/07 a 28/09/2026 (90 dias) |
| `escadas.csv` | 197 | Cadastro das escadas |
| `atendimentos.csv` | 1.981 | Entrada e saída do técnico em cada manutenção (preventiva P1 e corretiva) |
| `limites_status.csv` | 6 | Limites usados para classificar o status |
| `gerar_dataset.py` | – | Script que gera tudo (semente fixa 2026: rodar de novo dá os mesmos arquivos) |
| `perfil_escadas.csv` | 197 | Falhas reais por escada (2023 a 2026), usado pelo script |

## Dicionário de dados

### leituras_sensores.csv

| Coluna | Tipo | Unidade | Descrição |
| --- | --- | --- | --- |
| `leitura_id` | inteiro | – | Identificador da linha |
| `escada_id` | texto | – | Código da escada (ex.: `PIN-ER24`), chave para `escadas.csv` |
| `data_hora` | data e hora | – | Momento da leitura (AAAA-MM-DD HH:MM) |
| `vibracao_mm_s` | decimal | mm/s | Vibração (RMS de velocidade) no motor e redutor |
| `temperatura_c` | decimal | °C | Temperatura dos componentes mecânicos |
| `corrente_a` | decimal | A | Corrente do motor |
| `tensao_v` | decimal | V | Tensão de alimentação (nominal 380 V) |
| `velocidade_m_s` | decimal | m/s | Velocidade dos degraus (nominal 0,50 m/s) |
| `nivel_oleo_pct` | decimal | % | Nível do reservatório de lubrificação |
| `status` | texto | – | `BOM`, `ALERTA`, `CRITICO` ou `EM_MANUTENCAO` |

### escadas.csv

| Coluna | Descrição |
| --- | --- |
| `escada_id` | Código da escada |
| `estacao_cod` / `estacao_nome` | Estação (LUZ, REP, HIG, PTA, FRE, FRA, FAL, PIN, BUT, MBI, VSO, TVS) |
| `fabricante` | `Thyssen` ou `ESCAL` |
| `grupo` | `critica` ou `nao_critica` (hipótese) |
| `fluxo_relativo` | Fluxo de passageiros relativo da estação, de 0 a 1 (hipótese) |

### atendimentos.csv

| Coluna | Descrição |
| --- | --- |
| `atendimento_id` | Identificador |
| `escada_id` | Escada atendida |
| `tecnico_id` | Técnico fictício (T01 a T12) |
| `tipo` | `preventiva` ou `corretiva` |
| `motivo` | `P1 mensal`, `parada de seguranca (reset)`, `status critico`, `sem resposta do sensor` ou `alerta prolongado` |
| `entrada` / `saida` | Horário em que o técnico deu entrada e saída no tablet |
| `duracao_min` | Saída menos entrada, em minutos |

## Regra de status (a mesma do dashboard)

1. **EM_MANUTENCAO:** um técnico deu entrada e ainda não deu saída. A escada fica desligada, com velocidade e corrente em 0.
2. **CRITICO:** o sensor não responde (todas as variáveis vazias), a escada parou (velocidade 0) ou alguma variável passou do limite crítico.
3. **ALERTA:** alguma variável passou do limite de alerta.
4. **BOM:** nenhum dos casos acima.

| Variável | Alerta | Crítico |
| --- | --- | --- |
| Vibração | ≥ 4,5 mm/s | ≥ 7,1 mm/s |
| Temperatura | ≥ 80 °C | ≥ 95 °C |
| Corrente | ≥ 30 A | ≥ 36 A |
| Tensão | desvio ≥ 7% de 380 V | desvio ≥ 10% |
| Nível de óleo | ≤ 35% | ≤ 20% |
| Velocidade | desvio ≥ 3% de 0,50 m/s | desvio ≥ 6% ou parada |

Distribuição resultante: 94,2% BOM, 3,5% ALERTA, 1,7% CRITICO e 0,5% EM_MANUTENCAO.

## Comportamentos simulados

- **Uso:** corrente e temperatura sobem nos picos de fluxo (6h e 18h) e caem no fim de semana. Estações de integração (Luz, Paulista, República, Pinheiros) têm mais fluxo.
- **Óleo:** consumo contínuo e reposição na P1 mensal; vazamentos fazem o nível cair rápido.
- **Defeitos que evoluem até a troca:** rolamento (vibração sobe aos poucos), atrito (temperatura e corrente sobem, velocidade cai), vazamento de óleo e falha elétrica (picos de corrente e quedas de tensão). Escadas com mais falhas reais e as ESCAL recebem mais defeitos.
- **Paradas de segurança:** a falha mais comum no histórico real, resolvida com reset em poucos minutos.
- **Sensor sem resposta:** períodos em que nenhuma variável é lida.
- **Reparo:** quando a escada fica crítica, ou fica em alerta por 4 a 10 dias, um técnico dá entrada. Depois da saída, os valores voltam ao normal. Nas ESCAL o reparo demora cerca de 3 vezes mais.

## Problemas de qualidade inseridos de propósito

Para a etapa de preparação dos dados da EDA. Se o grupo quiser descobrir sozinho, pule esta seção.

- Cerca de 0,15% de valores vazios isolados em vibração, temperatura, corrente e óleo (falha de transmissão), além dos períodos de sensor sem resposta.
- 177 linhas duplicadas (mesma escada, mesmo horário, mesmos valores, `leitura_id` diferente).
- 44 picos espúrios de vibração entre 18 e 30 mm/s em leituras isoladas (glitch do sensor). Não são falha real; o enunciado pede para discutir outliers, não para removê-los automaticamente.

## Como usar em cada matéria

- **Data Science:** `leituras_sensores.csv` + `escadas.csv` para a EDA completa.
- **Dynamic Programming:** cada escada tem 450 leituras, o que cabe na recursão pura do Python (limite padrão de cerca de 1.000 chamadas). A degradação acumulada pode somar, leitura a leitura, o quanto cada variável passou do normal.
- **DDD / Database Design:** as colunas viram atributos das classes `EscadaRolante`, `Estacao`, `LeituraSensor` e `Atendimento`.
- **Dashboard do tablet:** a última leitura de cada escada dá o status atual; `atendimentos.csv` dá o tempo de manutenção.

## Como gerar de novo

```
python gerar_dataset.py
```

Requer Python 3 com pandas e numpy. Para mudar o período, a frequência ou os limites, edite as constantes no topo do script.
