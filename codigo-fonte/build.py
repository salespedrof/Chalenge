"""Gera o index.html do Elevate embutindo o dataset simulado (formato colunar, inteiros escalados)."""
import json, sys
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent
DS = next(d for d in [BASE.parent/'dados', BASE.parent/'dataset_sim'] if d.exists())
ORDEM = ['LUZ','REP','HIG','PTA','FRE','FRA','FAL','PIN','BUT','MBI','VSO','TVS']
VARS = [('vibracao_mm_s',100),('temperatura_c',10),('corrente_a',10),('tensao_v',10),('velocidade_m_s',10000),('nivel_oleo_pct',10)]
T0 = pd.Timestamp('2026-07-01 00:00')

esc = pd.read_csv(DS/'escadas.csv')
esc['o'] = esc.estacao_cod.map(ORDEM.index)
esc = esc.sort_values(['o','escada_id']).reset_index(drop=True)
perf = pd.read_csv(DS/'perfil_escadas.csv').set_index('equip')['n']
ix = {e:i for i,e in enumerate(esc.escada_id)}

lei = pd.read_csv(DS/'leituras_sensores.csv').drop_duplicates(subset=['escada_id','data_hora'])
lei = lei.sort_values(['escada_id','data_hora'])
v = []
for eid in esc.escada_id:
    d = lei[lei.escada_id==eid]
    assert len(d)==450, eid
    cols = []
    for c,sc in VARS:
        cols.append([None if pd.isna(x) else int(round(x*sc)) for x in d[c]])
    v.append(cols)

at = pd.read_csv(DS/'atendimentos.csv')
mot = sorted(at.motivo.unique())
mins = lambda s: int((pd.Timestamp(s)-T0).total_seconds()//60)
ats = [[int(r.atendimento_id), ix[r.escada_id], r.tecnico_id, 1 if r.tipo=='corretiva' else 0, mot.index(r.motivo), mins(r.entrada), mins(r.saida)] for r in at.itertuples()]

cen = [
  dict(id='CEN-01', nome='Atrito em FAL-ER02', escada='FAL-ER02', quando='2026-08-08T18:05', tela='detalhe', dica='temperatura subindo e velocidade caindo, em ALERTA desde 06/08. Avance até 11/08 para ver o atendimento.'),
  dict(id='CEN-02', nome='Rolamento em PIN-ER13', escada='PIN-ER13', quando='2026-09-05T18:05', tela='fila', dica='PIN-ER13 no topo da fila com despacho Imediato (vibração acima de 7,1 mm/s após semanas em ALERTA).'),
  dict(id='CEN-03', nome='Vazamento de óleo em FAL-ER01', escada='FAL-ER01', quando='2026-08-14T10:05', tela='fila', dica='FAL-ER01 (não crítica) em CRÍTICO por óleo: Prioridade no turno.'),
  dict(id='CEN-04', nome='Sensor sem resposta em PIN-ER09', escada='PIN-ER09', quando='2026-08-25T18:05', tela='detalhe', dica='leituras sem sinal desde 25/08 10h: CRÍTICO "Sem resposta".'),
  dict(id='CEN-05', nome='Pico de corrente em PIN-ER24', escada='PIN-ER24', quando='2026-07-24T06:05', tela='detalhe', dica='39,6 A numa leitura isolada: pela RN-02 vira ALERTA "Leitura suspeita".'),
  dict(id='CEN-06', nome='Leitura espúria em BUT-ER05', escada='BUT-ER05', quando='2026-09-21T06:05', tela='detalhe', dica='vibração isolada de 29,8 mm/s aparece como "Leitura suspeita", não como CRÍTICO.'),
  dict(id='CEN-07', nome='Manutenção longa em PIN-ER14', escada='PIN-ER14', quando='2026-09-28T14:00', tela='detalhe', dica='atendimento aberto desde 28/09 06:37, com cronômetro correndo.'),
  dict(id='CEN-08', nome='Parada de segurança em FAL-ER02', escada='FAL-ER02', quando='2026-09-13T14:02', tela='detalhe', dica='CRÍTICO "Parada". Dê entrada, registre "Resetado e testado" e saia.'),
  dict(id='CEN-09', nome='Tablet sem conexão', escada='', quando='2026-09-05T18:05', tela='sync', dica='ligue "Simular sem conexão", registre um atendimento e depois sincronize.'),
]

data = dict(
  est=[[c, esc[esc.estacao_cod==c].estacao_nome.iloc[0]] for c in ORDEM],
  esc=[[r.escada_id, r.estacao_cod, r.fabricante, 1 if r.grupo=='critica' else 0, float(r.fluxo_relativo), int(perf[r.escada_id])] for r in esc.itertuples()],
  v=v, mot=mot, at=ats, cen=cen,
)
js = json.dumps(data, ensure_ascii=False, separators=(',',':')).replace('</', '<\\/')
html = (BASE/'template.html').read_text(encoding='utf-8').replace('/*__DATA__*/', js)
TH = next(t for t in [BASE/'three.min.js', BASE.parent/'libs/node_modules/three/build/three.min.js'] if t.exists())
(BASE/'artifact.html').write_text(html.replace('<!--__THREE__-->','<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'), encoding='utf-8')
html = html.replace('<!--__THREE__-->', '<script>/* three.js r128 (MIT) embutido para funcionar sem internet */\n'+TH.read_text(encoding='utf-8')+'\n</script>')
full = '<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + html.replace('<div class="app">','</head>\n<body>\n<div class="app">',1) + '\n</body>\n</html>\n'
out = BASE/'index.html'
out.write_text(full, encoding='utf-8')
print(out, round(len(full.encode())/1e6,2), 'MB')
