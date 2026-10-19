# Elevate

**Manutenção orientada por condição para as escadas rolantes da Linha 4-Amarela**
Challenge Motiva + FIAP · Engenharia de Software · Sprints 1 e 2

**Abrir o protótipo:** https://salespedrof.github.io/Chalenge/

O Elevate é um tablet com Raspberry Pi para a equipe de manutenção. Ele mostra o status de cada uma das 197 escadas da Linha 4 a partir dos sensores (BOM, ALERTA, CRÍTICO e EM MANUTENÇÃO), diz o que provavelmente está errado, prevê quando vai piorar, ordena o que atender primeiro e registra a entrada e a saída do técnico. Tudo funciona sem Wi-Fi.

> **Os dados de sensores são simulados.** A Motiva não conseguiu enviar leituras reais a tempo das Sprints 1 e 2. O cadastro das 197 escadas, as estações, os fabricantes e o risco de cada escada vêm do histórico SAP real.

## Squad Elevate

| Integrante | RM |
| --- | --- |
| Artur Henrique Siqueira | 566986 |
| Davi de Souza Malta | 560327 |
| Guilherme Cruz Alves | 566861 |
| Guilherme de Oliveira Scremin | 564788 |
| Pedro Sales Ferreira | 566910 |

## O que o protótipo faz

| Tela | Conteúdo |
| --- | --- |
| Painel | Status das 197 escadas por estação, mini gráfico de cada uma e contador de tendência de piora |
| Detalhe da escada | Gêmeo digital 3D ligado aos sensores (ou modo leve 2D), diagnóstico com previsão, ordem de serviço, procedimento, gráficos de 90 dias, P1 e histórico |
| Fila | Ordem de atendimento com prazo de despacho e escadas que vão entrar em ALERTA nas próximas 48 h |
| Atendimentos | Ordens de serviço e entrada e saída do técnico, com cronômetro |
| Indicadores | Disponibilidade, tempo de reparo e de resposta, antecedência ALERTA → CRÍTICO, comparativos e ranking |
| Sincronização | Simulação do tablet sem conexão e fila de envio |
| Ao vivo | Escada MAQ-01 da maquete com ESP32: 1 leitura por segundo por Wi-Fi (MQTT) ou cabo USB, gêmeo digital girando ou parado conforme a esteira, diagnóstico e gráficos ao vivo. Tem simulador embutido para testar sem a maquete |
| Dados | Gera um dataset novo no próprio navegador e exporta os CSVs |

O painel abre em **tempo real**: segue a hora do próprio aparelho, sem nenhum ajuste. Os 90 dias de dados simulados terminam hoje, e as leituras de 6h, 10h, 14h, 18h e 22h entram quando o horário chega.

Para apresentar, o botão **Modo demonstração** libera o relógio controlável (pausar, acelerar, ir para uma data) e o menu **Cenário de demonstração**, com casos preparados nas datas originais do dataset. **Voltar ao tempo real** retorna à hora do aparelho. O botão **Apresentar** esconde os controles.

## Como usar

- **Pelo site:** abra o link acima. Funciona no computador, no tablet e no celular.
- **Sem internet:** baixe o `index.html` (ou o repositório inteiro) e dê dois cliques. Ele não depende de servidor nem de internet.

## Estrutura

| Pasta | Conteúdo |
| --- | --- |
| `index.html` | O protótipo completo, com dados, gráficos e biblioteca 3D embutidos |
| `dados/` | Dataset oficial em CSV (semente 2026), o gerador `gerar_dataset.py` e o dicionário de dados |
| `codigo-fonte/` | `template.html` (código do app), `build.py` (gera o `index.html` a partir dos CSVs) e `three.min.js` |
| `docs/` | PRD do MVP e guia de apresentação |
| `maquete/` | Firmware do ESP32, projeto Wokwi, lista de materiais, ligações e roteiro da demonstração ao vivo |

Para gerar o `index.html` de novo a partir dos CSVs (Python 3 e pandas):

```
cd codigo-fonte
python build.py
```

O resultado é gravado em `codigo-fonte/index.html`. Para publicar, copie-o para a raiz do repositório.

## Tecnologia

HTML, CSS e JavaScript puro num arquivo só; gráficos em canvas próprio; gêmeo digital com [three.js](https://threejs.org/) r128 (licença MIT); dataset gerado em Python com pandas e NumPy.

## Limitações

Limites de ALERTA e CRÍTICO, grupo crítica / não crítica e prazos de despacho são hipóteses do grupo, a validar com a engenharia da Motiva. Fora a maquete MAQ-01, não há integração com sensores reais, SAP ou servidor: a sincronização é simulada. Os valores da maquete são convertidos para a escala de uma escada real (veja `maquete/README.md`). O sistema é só consultivo e não comanda as escadas.
