"""P1 na rota: a revisão mensal atrasada ou perto de vencer entra sozinha na rota do técnico."""
p='template.html'; s=open(p,encoding='utf-8').read()
def R(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(s.count(a),a[:80]); s=s.replace(a,b)
R("  p1Dias: 30,", "  p1Dias: 30,\n  p1AvisoDias: 3,   /* a P1 entra na rota quando faltam 3 dias ou menos para vencer */")
R("  atendimento: {imediato:60, critico:60, alerta:45, tendencia:20},", "  atendimento: {imediato:60, critico:60, alerta:45, tendencia:20, p1:120},")
R("""function pendenciasDe(tec, incluirTend){
  const P=CFG.prioridade, out=[];
  for(const e of E){ if(respDe(e)!==tec) continue; const c=CUR[e.ix];
    if(c.code===1||c.code===2){ const h=Math.max(0,(NOW-c.since)/60); const d=c.code===2?(e.crit?0:1):(e.crit?2:3);
      out.push({e, c, d, score:(c.code===2?P.CRITICO:P.ALERTA)+(e.crit?P.grupoCritica:0)+P.fluxo*e.fluxo+Math.min(h,P.horasMax), tipo: d===0?'imediato':c.code===2?'critico':'alerta'}); }
    else if(incluirTend && TEND[e.ix]) out.push({e, c, d:4, score:0, tipo:'tendencia'}); }
  return out.sort((a,b)=>a.d-b.d || b.score-a.score);
}""", """/* situação da P1 (RN-06): dias desde a última, atrasada (> p1Dias) ou vencendo (faltam p1AvisoDias ou menos) */
function p1Status(e){
  const p=lastP1(e); if(p==null) return NOW>CFG.p1Dias*1440 ? {st:'atrasada', dias:null, txt:'P1 sem registro no período'} : null;
  const dias=(NOW-p)/1440, falta=CFG.p1Dias-dias;
  if(falta<0) return {st:'atrasada', dias, txt:'P1 atrasada · '+Math.floor(dias)+' dias'};
  if(falta<=CFG.p1AvisoDias) return {st:'vence', dias, txt:'P1 vence '+(falta<1?'hoje':'em '+Math.ceil(falta)+' dia'+(Math.ceil(falta)>1?'s':''))};
  return null;
}
function pendenciasDe(tec, incluirTend){
  const P=CFG.prioridade, out=[];
  for(const e of E){ if(respDe(e)!==tec) continue; const c=CUR[e.ix];
    if(c.code===3) continue;   /* já está em manutenção */
    const p1=p1Status(e); let it=null;
    if(c.code===1||c.code===2){ const h=Math.max(0,(NOW-c.since)/60); const d=c.code===2?(e.crit?0:1):(e.crit?2:3);
      it={e, c, d, score:(c.code===2?P.CRITICO:P.ALERTA)+(e.crit?P.grupoCritica:0)+P.fluxo*e.fluxo+Math.min(h,P.horasMax), tipo: d===0?'imediato':c.code===2?'critico':'alerta'}; }
    else if(incluirTend && TEND[e.ix]) it={e, c, d:4, score:0, tipo:'tendencia'};
    /* P1 é obrigatória por lei: entra sempre, sozinha ou junto com o atendimento da mesma escada */
    if(p1){ if(it) it.p1=p1; else it={e, c, d: p1.st==='atrasada'?1.5:3.5, score:p1.dias||99, tipo:'p1', p1}; }
    if(it) out.push(it); }
  return out.sort((a,b)=>a.d-b.d || b.score-a.score);
}
const attMin = x => REDE.atendimento[x.tipo] + (x.p1 && x.tipo!=='p1' ? REDE.atendimento.p1 : 0);""")
R("att=pz.itens.reduce((s,x)=>s+REDE.atendimento[x.tipo],0)", "att=pz.itens.reduce((s,x)=>s+attMin(x),0)")
R("    else fora.push({...pz, att});", "    else fora.push({...pz, att:pz.itens.reduce((s,x)=>s+attMin(x),0)});")
R("""  const itemHTML = x => '<button class="rt-e" data-ver="'+x.e.id+'"><span class="code">'+x.e.id+'</span>'+(x.tipo==='tendencia'?'<span class="chip-trend">↗ tendência</span>':pill(x.c.code))+(x.d<=3?despPill(x.d):'')+'</button>';""",
"""  const p1Chip = x => x.p1 ? '<span class="p1chip '+x.p1.st+'">'+esc(x.p1.txt)+'</span>' : '';
  const itemHTML = x => '<button class="rt-e" data-ver="'+x.e.id+'"><span class="code">'+x.e.id+'</span>'+(x.tipo==='p1'?'':x.tipo==='tendencia'?'<span class="chip-trend">↗ tendência</span>':pill(x.c.code))+(x.tipo!=='p1'&&x.d<=3?despPill(x.d):'')+p1Chip(x)+'</button>';
  const p1Fora=pl.fora.flatMap(p=>p.itens).filter(x=>x.p1&&x.p1.st==='atrasada');""")
R("""  $('#rtKpis').innerHTML = [[pl.dentro.length,'paradas no turno'],[nEsc,'escadas atendidas'],[fDur(pl.total),'tempo total, com a volta'],[pl.viagem+' min','em deslocamento']]""",
  """  const nP1=pl.dentro.reduce((s,p)=>s+p.itens.filter(x=>x.p1).length,0);
  $('#rtKpis').innerHTML = [[pl.dentro.length,'paradas no turno'],[nEsc,'escadas atendidas'],[nP1,'P1 incluídas (lei)'],[fDur(pl.total),'tempo total, com a volta']]""")
R("""  $('#rtLista').innerHTML = html;""", """  if(p1Fora.length) html = '<div class="banner" style="--c:var(--crit)">'+ICON[2]+'<div><strong>'+p1Fora.length+' P1 atrasada'+(p1Fora.length>1?'s':'')+' não coube'+(p1Fora.length>1?'ram':'')+' neste turno</strong><span class="muted">'+p1Fora.map(x=>x.e.id).join(' · ')+'. A P1 é obrigatória por lei: aumente o turno ou passe para outro técnico.</span></div></div>' + html;
  $('#rtLista').innerHTML = html;""")
R(".rt-note{font-size:.82rem;color:var(--muted)}", """.rt-note{font-size:.82rem;color:var(--muted)}
.p1chip{font-size:.78rem;font-weight:700;padding:2px 8px;border-radius:6px;border:1px solid var(--warn);color:var(--warn)}
.p1chip.atrasada{border-color:var(--crit);color:var(--crit)}""")
R("Ordem das escadas a atender, pelo caminho da Linha 4, a partir da base de manutenção.", "Ordem das escadas a atender, pelo caminho da Linha 4, a partir da base de manutenção. A P1 atrasada ou perto de vencer entra sozinha.")
R("""Despacho imediato primeiro; depois a linha num sentido só.';""", """Despacho imediato primeiro; depois a linha num sentido só. A P1 atrasada ou que vence em até '+CFG.p1AvisoDias+' dias entra sozinha na rota.';""")
R(""" e atendimento de '+REDE.atendimento.critico+' min (crítico), '+REDE.atendimento.alerta+' min (alerta) e '+REDE.atendimento.tendencia+' min (inspeção de tendência).';""",
  """ e atendimento de '+REDE.atendimento.critico+' min (crítico), '+REDE.atendimento.alerta+' min (alerta), '+REDE.atendimento.tendencia+' min (inspeção de tendência) e '+REDE.atendimento.p1+' min (P1).';""")
R("""  if(!pl.pend.length){ $('#rtLista').innerHTML='<div class="empty">Nenhuma escada '+(isTec()?'sua':'de '+esc(TECS[rtTec]))+' precisa de atendimento agora'+(tend?'':' na fila')+'. A P1 mensal segue o plano preventivo.</div>';""",
  """  if(!pl.pend.length){ $('#rtLista').innerHTML='<div class="empty">Nenhuma escada '+(isTec()?'sua':'de '+esc(TECS[rtTec]))+' precisa de atendimento agora'+(tend?'':' na fila')+', e nenhuma P1 está atrasada ou vencendo nos próximos '+CFG.p1AvisoDias+' dias.</div>';""")
open(p,'w',encoding='utf-8').write(s); print('patched v10 (P1 na rota)')
