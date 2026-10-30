"""4 grupos de manutenção: Crítica A/B e Não crítica A/B pelo desnível (simulado), com duração de preventiva por grupo."""
p = 'template.html'; s = open(p, encoding='utf-8').read()
def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# desnível simulado e grupos
R("  E = D.esc.map((r,ix) => ({ix, id:r[0], cod:r[1], fab:r[2], crit:r[3]===1, fluxo:r[4], v:D.v[ix], at:[]}));",
  "  E = D.esc.map((r,ix) => ({ix, id:r[0], cod:r[1], fab:r[2], crit:r[3]===1, fluxo:r[4], v:D.v[ix], at:[], desn:desnSim(r[0],r[1])}));")
R("const V = CFG.vars;", r"""const V = CFG.vars;
/* ---------- grupos de manutenção: crítica/não crítica × A/B pelo desnível ----------
   A Motiva ainda não informou o corte nem os tempos: valores propostos pelo grupo, a validar.
   Desnível simulado por estação (as mais profundas têm escadas mais altas) até recebermos o cadastro real. */
const GRUPO_CFG = {limiteB:10, min:{cA:130, cB:170, nA:110, nB:150}};
const PROF_EST = {LUZ:1.0, REP:1.1, HIG:1.25, PTA:1.3, FRE:1.15, FRA:1.0, FAL:1.2, PIN:1.0, BUT:1.1, MBI:1.2, VSO:0.95, TVS:0.8};
function desnSim(id,cod){ let h=2166136261; for(const ch of id+'#desn'){ h^=ch.charCodeAt(0); h=Math.imul(h,16777619); } const u=(h>>>0)/4294967296;
  return Math.round((4.5+u*8.5)*(PROF_EST[cod]||1)*10)/10; }
function subGrupo(e){ return e.desn>=GRUPO_CFG.limiteB ? 'B' : 'A'; }
function chaveGrupo(e){ return (e.crit?'c':'n')+subGrupo(e); }
function nomeGrupo(e){ return (e.crit?'Crítica ':'Não crítica ')+subGrupo(e); }
function durPrev(e){ return GRUPO_CFG.min[chaveGrupo(e)]; }""")

# painel: filtro com os 4 grupos e tag no card
R('<select id="fGrupo"><option value="">Todos</option><option value="c">Crítica</option><option value="n">Não crítica</option></select>',
  '<select id="fGrupo"><option value="">Todos</option><option value="c">Crítica (A e B)</option><option value="cA">Crítica A</option><option value="cB">Crítica B</option><option value="n">Não crítica (A e B)</option><option value="nA">Não crítica A</option><option value="nB">Não crítica B</option></select>')
R("    if(filt.grupo && (filt.grupo==='c')!==e.crit) return false;",
  "    if(filt.grupo && (filt.grupo[0]==='c')!==e.crit) return false;\n    if(filt.grupo && filt.grupo.length===2 && filt.grupo[1]!==subGrupo(e)) return false;")
R("(e.crit?'<span class=\"tag crit\">Crítica</span>':'<span class=\"tag\">'+e.fab+'</span>')",
  "(e.crit?'<span class=\"tag crit\">Crítica '+subGrupo(e)+'</span>':'<span class=\"tag\">'+e.fab+' · '+subGrupo(e)+'</span>')")
R("filt.grupo==='n' || filt.fab) return '';", "(filt.grupo && filt.grupo!=='c') || filt.fab) return '';")

# detalhe e OS
R("<span>'+(e.crit?'Grupo crítica':'Grupo não crítica')+'</span>",
  "<span>Grupo '+nomeGrupo(e)+'</span><span title=\"Simulado até recebermos o cadastro real\">Desnível '+nf(e.desn,1)+' m (simulado)</span>")
R("'+(e.crit?'grupo crítica':'grupo não crítica')+'</dd>'", "grupo '+nomeGrupo(e).toLowerCase()+'</dd>'")

# preventivas: duração por grupo
for a in ["min:PREV.duracaoMin*1.5}", ]:
    R(a, "min:durPrev(e)*1.5}")
R("min:PREV.duracaoMin}", "min:durPrev(e)}", 5)
R("  const n=k=>all.filter(x=>x.dec===k).length, disp=n('Dispensar');",
  "  const n=k=>all.filter(x=>x.dec===k).length, disp=n('Dispensar'), hhDisp=all.filter(x=>x.dec==='Dispensar').reduce((t,x)=>t+durPrev(x.e),0);")
R("[nf(disp*PREV.duracaoMin/60,0)+' h','homem-hora economizado no ciclo (estimado)']", "[nf(hhDisp/60,0)+' h','homem-hora economizado no ciclo (estimado)']")
R("<th>Escada</th><th>Estação</th><th>Decisão</th><th>Motivo</th>", "<th>Escada</th><th>Estação</th><th>Grupo</th><th>Decisão</th><th>Motivo</th>")
R("'</td><td>'+esc(ESTN[x.e.cod])+'</td><td><span class=\"dec '+x.dec+'\">'",
  "'</td><td>'+esc(ESTN[x.e.cod])+'</td><td style=\"white-space:nowrap\">'+nomeGrupo(x.e)+' <span class=\"muted\">· '+durPrev(x.e)+' min</span></td><td><span class=\"dec '+x.dec+'\">'")
R("  $('#pvNota').textContent='Regras propostas pelo grupo, a validar com a engenharia da Motiva: ",
  "  $('#pvNota').textContent='Regras propostas pelo grupo, a validar com a engenharia da Motiva: duração da preventiva por grupo (Crítica A '+GRUPO_CFG.min.cA+' min, Crítica B '+GRUPO_CFG.min.cB+' min, Não crítica A '+GRUPO_CFG.min.nA+' min, Não crítica B '+GRUPO_CFG.min.nB+' min; B = desnível de '+GRUPO_CFG.limiteB+' m ou mais, simulado); ")

# indicadores de sucesso
R("'Dispensáveis neste ciclo pela condição · ~'+nf(disp*PREV.duracaoMin/60,0)+' h de homem-hora'",
  "'Dispensáveis neste ciclo pela condição · ~'+nf(dec.filter(x=>x.dec==='Dispensar').reduce((t,x)=>t+durPrev(x.e),0)/60,0)+' h de homem-hora'")

# exportação
R("rows.push(['escada_id','estacao_cod','estacao_nome','fabricante','grupo','fluxo_relativo']); E.forEach(e=>rows.push([e.id,e.cod,ESTN[e.cod],e.fab,e.crit?'critica':'nao_critica',e.fluxo]));",
  "rows.push(['escada_id','estacao_cod','estacao_nome','fabricante','grupo','fluxo_relativo','desnivel_m_simulado','grupo_manutencao']); E.forEach(e=>rows.push([e.id,e.cod,ESTN[e.cod],e.fab,e.crit?'critica':'nao_critica',e.fluxo,e.desn,nomeGrupo(e)]));")
open(p, 'w', encoding='utf-8').write(s); print('patched v15 (4 grupos)')
