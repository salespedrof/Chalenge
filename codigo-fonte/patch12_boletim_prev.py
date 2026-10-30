"""Revisão Motiva (parte 2): boletim de escadas paradas e plano noturno de preventivas (CBM, P1 mantida)."""
p = 'template.html'; s = open(p, encoding='utf-8').read()
def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# ---------- CSS ----------
R(".p1chip.atrasada{border-color:var(--crit);color:var(--crit)}", """.p1chip.atrasada{border-color:var(--crit);color:var(--crit)}
/* ---------- boletim e preventivas ---------- */
.bl-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.dec{display:inline-block;font-family:var(--f-display);font-weight:700;font-size:.82rem;letter-spacing:.04em;padding:3px 9px;border-radius:6px;border:1px solid var(--c);color:var(--c);white-space:nowrap}
.dec.P1{--c:var(--crit)}.dec.Antecipar{--c:var(--warn)}.dec.Manter{--c:var(--muted)}.dec.Dispensar{--c:var(--ok)}
.pv-est{display:flex;flex-direction:column;gap:8px}
.pv-cap{height:10px;border-radius:5px;background:var(--surface-3);overflow:hidden}.pv-cap i{display:block;height:100%;background:var(--brand)}
.pv-cap.over i{background:var(--crit)}
.tbl-wrap td .dec{margin:0}
@media (max-width:899px){ .rail{overflow-x:auto;justify-content:flex-start} .rail .nav{flex:0 0 auto;min-width:72px} }
@media (max-width:640px){ .bl-kpis{grid-template-columns:repeat(2,minmax(0,1fr))} }""")

# ---------- navegação ----------
R('<button class="nav sup-only" data-view="equipe">', '''<button class="nav sup-only" data-view="boletim"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V3h6v1M9 10h6M9 14h6M9 18h3"/></svg>Boletim</button>
    <button class="nav sup-only" data-view="prev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/><path d="M15 3v4M13 5h4"/></svg>Preventivas</button>
    <button class="nav sup-only" data-view="equipe">''')
R("  if(isTec() && ['ind','dados','live','equipe','foco','rota'].includes(v)) v='painel';", "  if(isTec() && ['ind','dados','live','equipe','foco','rota','boletim','prev'].includes(v)) v='painel';")
R("  else if(view==='foco') renderFoco();", "  else if(view==='foco') renderFoco();\n  else if(view==='boletim') renderBoletim();\n  else if(view==='prev') renderPrev();")

# ---------- telas ----------
R('    <section class="view" id="v-equipe" hidden aria-label="Equipes">', '''    <section class="view" id="v-boletim" hidden aria-label="Boletim de escadas paradas">
      <div class="vhead"><div><h2>Boletim de escadas paradas</h2><p id="blSub">Quais escadas estão paradas agora, há quanto tempo e por quê.</p></div>
        <div class="rt-tools"><button class="btn sm" id="blCopiar">Copiar boletim</button><button class="btn sm" id="blCsv">Baixar CSV</button></div></div>
      <div class="bl-kpis" id="blKpis"></div>
      <div class="panel"><h3>Paradas agora</h3><div class="tbl-wrap" id="blAgora"></div></div>
      <div class="fc-two">
        <div class="panel"><h3>Liberadas nas últimas 24 horas</h3><div class="tbl-wrap" id="blLib"></div></div>
        <div class="panel"><h3>Reincidentes: 3 ou mais corretivas em 7 dias</h3><div class="tbl-wrap" id="blRein"></div></div>
      </div>
      <textarea id="blTxt" hidden rows="10" style="width:100%"></textarea>
    </section>

    <section class="view" id="v-prev" hidden aria-label="Plano noturno de preventivas">
      <div class="vhead"><div><h2>Preventivas por condição</h2><p id="pvSub">Para cada escada, o que fazer com a próxima preventiva do plano: dispensar, manter ou antecipar. A P1 anual nunca é dispensada.</p></div>
        <label class="field"><span>Mostrar</span><select id="pvFiltro"><option value="">Todas as decisões</option><option value="P1">P1 obrigatória</option><option value="Antecipar">Antecipar</option><option value="Manter">Manter no calendário</option><option value="Dispensar">Dispensar (condição boa)</option></select></label></div>
      <div class="bl-kpis" id="pvKpis"></div>
      <div class="vhead"><div><h3>Plano desta noite</h3><p id="pvNoiteSub"></p></div></div>
      <div class="tec-cards" id="pvNoite"></div>
      <div class="panel"><h3>Decisão por escada</h3><div class="tbl-wrap" id="pvLista"></div></div>
      <p class="hint" id="pvNota"></p>
    </section>

    <section class="view" id="v-equipe" hidden aria-label="Equipes">''')

# ---------- lógica ----------
R("/* ================= TELA: equipes por estação ================= */", r"""/* ================= BOLETIM DE ESCADAS PARADAS ================= */
const minOverlap = (a0,a1,b0,b1) => Math.max(0, Math.min(a1,b1)-Math.max(a0,b0));
function dadosBoletim(){
  const VE=E.filter(meu), agora=[];
  for(const e of VE){ const c=CUR[e.ix];
    if(c.code===3) agora.push({e, tipo:'Em manutenção', desde:c.since, motivo:MOT_L[c.at.motivo]||c.at.motivo, quem:TECS[c.at.tec]||c.at.tec});
    else if(c.kind==='parada') agora.push({e, tipo:'Parada por falha', desde:c.since, motivo:'Dispositivo de segurança atuou', quem:'equipe '+nomeEquipe(e.cod)});
    else if(c.kind==='sem') agora.push({e, tipo:'Sem monitoramento', desde:c.since, motivo:'Sensor sem resposta: a escada pode estar operando', quem:'equipe '+nomeEquipe(e.cod)}); }
  agora.sort((a,b)=>(a.tipo==='Sem monitoramento')-(b.tipo==='Sem monitoramento') || (b.e.crit-a.e.crit) || a.desde-b.desde);
  const lib=[], rein=[]; let parado24=0;
  for(const e of VE){
    for(const a of e.atv){ if(a.ent>NOW) continue; const fim=a.sai==null||a.sai>NOW?NOW:a.sai;
      if(a.tipo==='corretiva') parado24+=minOverlap(a.ent,fim,NOW-1440,NOW);
      if(a.tipo==='corretiva' && a.sai!=null && a.sai<=NOW && a.sai>NOW-1440) lib.push({e,a}); }
    const c=CUR[e.ix]; if(c.kind==='parada') parado24+=minOverlap(c.since,NOW,NOW-1440,NOW);
    const n7=e.atv.filter(a=>a.tipo==='corretiva'&&a.ent<=NOW&&a.ent>NOW-7*1440).length; if(n7>=3) rein.push({e,n:n7});
  }
  lib.sort((x,y)=>y.a.sai-x.a.sai); rein.sort((x,y)=>y.n-x.n);
  const paradas=agora.filter(x=>x.tipo!=='Sem monitoramento');
  return {VE, agora, paradas, lib, rein, parado24, disp:1-paradas.length/VE.length};
}
function renderBoletim(){
  if(!isSup()) return show('painel');
  computeCurrent(); const B=dadosBoletim(), est0=escopoEst();
  $('#blSub').textContent='Boletim de '+(est0?'Estação '+ESTN[est0]:'Linha 4-Amarela, 12 estações')+' às '+fDH(NOW)+'. Quais escadas estão paradas agora, há quanto tempo e por quê.';
  $('#blKpis').innerHTML=[[B.paradas.length,'paradas agora'],[B.paradas.filter(x=>x.e.crit).length,'do grupo crítica'],[nf(B.disp*100,1)+'%','disponibilidade agora'],[fDur(B.parado24),'escada-horas paradas em 24 h (corretivas)']]
    .map(([n,t])=>'<div class="rt-kpi"><div class="n num">'+n+'</div><div class="t">'+t+'</div></div>').join('');
  $('#blAgora').innerHTML = B.agora.length ? '<table><thead><tr><th>Escada</th><th>Estação</th><th>Grupo</th><th>Situação</th><th>Motivo</th><th>Desde</th><th class="n">Tempo</th><th>Quem</th></tr></thead><tbody>'+
    B.agora.map(x=>'<tr class="click" data-row="'+x.e.id+'"><td class="code">'+x.e.id+'</td><td>'+esc(ESTN[x.e.cod])+'</td><td>'+(x.e.crit?'<b style="color:var(--brand)">crítica</b>':'não crítica')+'</td><td>'+(x.tipo==='Em manutenção'?pill(3):x.tipo==='Parada por falha'?pill(2,'PARADA'):'<span class="muted">'+x.tipo+'</span>')+'</td><td>'+esc(x.motivo)+'</td><td class="num">'+fDH(x.desde)+'</td><td class="n"><span data-since="'+x.desde+'">'+fDur(NOW-x.desde)+'</span></td><td>'+esc(x.quem)+'</td></tr>').join('')+'</tbody></table>'
    : '<div class="empty">Nenhuma escada parada agora.</div>';
  $('#blLib').innerHTML = B.lib.length ? '<table><thead><tr><th>Escada</th><th>Liberada</th><th class="n">Ficou parada</th><th>Motivo</th></tr></thead><tbody>'+
    B.lib.slice(0,15).map(({e,a})=>'<tr class="click" data-row="'+e.id+'"><td class="code">'+e.id+'</td><td class="num">'+fDH(a.sai)+'</td><td class="n">'+fDur(a.sai-a.ent)+'</td><td>'+esc(MOT_L[a.motivo]||a.motivo)+'</td></tr>').join('')+'</tbody></table>'+(B.lib.length>15?'<p class="hint">Mostrando 15 de '+B.lib.length+'.</p>':'')
    : '<div class="empty">Nenhuma escada liberada nas últimas 24 horas.</div>';
  $('#blRein').innerHTML = B.rein.length ? '<table><thead><tr><th>Escada</th><th>Estação</th><th class="n">Corretivas em 7 dias</th></tr></thead><tbody>'+
    B.rein.map(x=>'<tr class="click" data-row="'+x.e.id+'"><td class="code">'+x.e.id+'</td><td>'+esc(ESTN[x.e.cod])+'</td><td class="n"><b>'+x.n+'</b></td></tr>').join('')+'</tbody></table>'
    : '<div class="empty">Nenhuma escada reincidente nos últimos 7 dias.</div>';
}
function textoBoletim(){
  computeCurrent(); const B=dadosBoletim(), est0=escopoEst();
  const L=['BOLETIM DE ESCADAS PARADAS · '+(est0?'Estação '+ESTN[est0]:'Linha 4-Amarela')+' · '+fDH(NOW),
    'Paradas agora: '+B.paradas.length+' ('+B.paradas.filter(x=>x.e.crit).length+' do grupo crítica) · disponibilidade '+nf(B.disp*100,1)+'%', ''];
  B.paradas.forEach(x=>L.push('• '+x.e.id+' ('+ESTN[x.e.cod]+(x.e.crit?', crítica':'')+'): '+x.tipo.toLowerCase()+' há '+fDur(NOW-x.desde)+' · '+x.motivo+' · '+x.quem));
  const sem=B.agora.filter(x=>x.tipo==='Sem monitoramento'); if(sem.length) L.push('', 'Sem monitoramento: '+sem.map(x=>x.e.id).join(', '));
  L.push('', 'Liberadas nas últimas 24 h: '+B.lib.length+(B.lib.length?' ('+B.lib.slice(0,8).map(x=>x.e.id).join(', ')+(B.lib.length>8?'…':'')+')':''));
  if(B.rein.length) L.push('Reincidentes (3+ corretivas em 7 dias): '+B.rein.map(x=>x.e.id+' ('+x.n+')').join(', '));
  L.push('', 'Gerado pelo Elevate · dados simulados');
  return L.join('\n');
}
$('#blCopiar').onclick=()=>{ const t=textoBoletim(), ta=$('#blTxt'); const fb=()=>{ ta.hidden=false; ta.value=t; ta.focus(); ta.select(); toast('O boletim está selecionado na caixa abaixo: use Copiar.'); };
  try{ navigator.clipboard.writeText(t).then(()=>toast('Boletim copiado. Cole no e-mail ou na mensagem para a gestão.'), fb); }catch(err){ fb(); } };
$('#blCsv').onclick=()=>{ computeCurrent(); const B=dadosBoletim(), q=v=>'"'+String(v).replace(/"/g,'""')+'"';
  const rows=[['escada','estacao','grupo','situacao','motivo','desde','minutos_parada','quem']].concat(B.agora.map(x=>[x.e.id,ESTN[x.e.cod],x.e.crit?'critica':'nao_critica',x.tipo,x.motivo,fDH(x.desde),Math.round(NOW-x.desde),x.quem]));
  try{ const url=URL.createObjectURL(new Blob(['﻿'+rows.map(r=>r.map(q).join(',')).join('\n')],{type:'text/csv;charset=utf-8'})); const a=document.createElement('a'); a.href=url; a.download='boletim_paradas.csv'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),2000); }catch(err){ toast('Não foi possível baixar o CSV neste navegador.'); } };
['#blAgora','#blLib','#blRein'].forEach(q=>$(q).addEventListener('click',ev=>{ const r=ev.target.closest('[data-row]'); if(r) openDetalhe(r.dataset.row); }));

/* ================= PREVENTIVAS POR CONDIÇÃO (plano noturno) =================
   Regras (hipótese do grupo, a validar com a engenharia da Motiva):
   P1 anual vencendo em 30 dias ou atrasada → obrigatória (nunca dispensada);
   ALERTA/CRÍTICO, tendência de piora ou 2+ corretivas em 30 dias → antecipar;
   BOM, todas as variáveis abaixo de 60% do limite de ALERTA e sem corretivas em 30 dias → dispensar esta preventiva;
   o resto → manter no calendário. As preventivas são feitas à noite, com a equipe da estação. */
const PREV = {cicloDias:30, duracaoMin:130, limiteBom:0.6, noiteMin:270, janela:'0h às 4h30'};
const ultimaPrev = e => { let m=null; for(const a of e.atv){ if(a.motivo==='P1 mensal' && a.ent<=NOW && (m==null||a.ent>m)) m=a.ent; } return m; };
function decisaoPrev(e){
  const c=CUR[e.ix]; if(c.code===3) return null;
  const p1=p1Status(e), last=ultimaPrev(e), prox = last==null ? NOW : last+PREV.cicloDias*1440;
  const corr=e.atv.filter(a=>a.tipo==='corretiva'&&a.ent<=NOW&&a.ent>NOW-30*1440).length;
  let rmax=0, kmax=0; V.forEach((cf,k)=>{ const x=val(e,k,IDX); if(x==null) return; const r=ratio(cf,x); if(r>rmax){ rmax=r; kmax=k; } });
  const base={e, last, prox, corr, rmax};
  if(p1) return {...base, dec:'P1', ordem:0, motivo:p1.txt+' · exigida pelo órgão fiscalizador', min:PREV.duracaoMin*1.5};
  if(c.code>=1) return {...base, dec:'Antecipar', ordem:1, motivo:STL[c.code]+' agora · '+c.txt, min:PREV.duracaoMin};
  if(TEND[e.ix]) return {...base, dec:'Antecipar', ordem:1, motivo:V[TEND[e.ix].k].nome+' piorando: ALERTA em '+fmtPrazo(TEND[e.ix].tA).replace('cerca de ','~'), min:PREV.duracaoMin};
  if(corr>=2) return {...base, dec:'Antecipar', ordem:1, motivo:corr+' corretivas em 30 dias', min:PREV.duracaoMin};
  if(c.code===0 && rmax<PREV.limiteBom && corr===0) return {...base, dec:'Dispensar', ordem:3, motivo:'BOM · todas as variáveis abaixo de '+Math.round(PREV.limiteBom*100)+'% do limite (maior: '+V[kmax].nome.toLowerCase()+' a '+Math.round(rmax*100)+'%) · sem corretivas em 30 dias', min:0};
  return {...base, dec:'Manter', ordem:2, motivo:corr?corr+' corretiva em 30 dias':V[kmax].nome+' a '+Math.round(rmax*100)+'% do limite', min:PREV.duracaoMin};
}
const DEC_L = {P1:'P1 obrigatória', Antecipar:'Antecipar', Manter:'Manter', Dispensar:'Dispensar'};
function renderPrev(){
  if(!isSup()) return show('painel');
  computeCurrent();
  const all=E.filter(meu).map(decisaoPrev).filter(Boolean).sort((a,b)=>a.ordem-b.ordem || a.prox-b.prox);
  const n=k=>all.filter(x=>x.dec===k).length, disp=n('Dispensar');
  $('#pvKpis').innerHTML=[[disp,'preventivas dispensáveis neste ciclo'],[fDur(disp*PREV.duracaoMin),'homem-hora economizado (estimado)'],[n('Antecipar'),'antecipar (condição piorando)'],[n('P1'),'P1 anual nos próximos '+CFG.p1AvisoDias+' dias']]
    .map(([v,t])=>'<div class="rt-kpi"><div class="n num">'+v+'</div><div class="t">'+t+'</div></div>').join('');
  /* plano desta noite, por estação: P1, antecipadas e as do calendário que vencem até amanhã */
  const noite=all.filter(x=>x.dec==='P1' || x.dec==='Antecipar' || (x.dec==='Manter' && x.prox<=NOW+1440));
  const cods=[...new Set(noite.map(x=>x.e.cod))], cap=PREV.noiteMin*2;
  $('#pvNoiteSub').textContent='Janela de '+PREV.janela+', com a equipe de cada estação (2 técnicos, '+fDur(cap)+' de trabalho por noite). Entra primeiro a P1, depois o que precisa ser antecipado.';
  $('#pvNoite').innerHTML = cods.length ? EST.filter(st=>cods.includes(st.cod)).map(st=>{ const it=noite.filter(x=>x.e.cod===st.cod); let soma=0; const cabe=[], sobra=[];
      it.forEach(x=>{ if(soma+x.min<=cap){ cabe.push(x); soma+=x.min; } else sobra.push(x); });
      return '<div class="tcard pv-est"><div class="tn"><b>'+esc(st.nome)+'</b><span class="muted" style="font-size:.82rem">'+esc(nomeEquipe(st.cod))+'</span></div>'+
        '<div class="pv-cap'+(sobra.length?' over':'')+'"><i style="width:'+Math.min(100,Math.round(soma/cap*100))+'%"></i></div><div class="mini"><span>'+fDur(soma)+' de '+fDur(cap)+'</span>'+(sobra.length?'<b style="color:var(--crit)">'+sobra.length+' para a próxima noite</b>':'')+'</div>'+
        cabe.map(x=>'<div class="mini" style="justify-content:space-between;align-items:center"><span class="code" style="color:var(--fg)">'+x.e.id+'</span><span class="dec '+x.dec+'">'+DEC_L[x.dec]+'</span></div>').join('')+
        sobra.map(x=>'<div class="mini" style="justify-content:space-between;align-items:center;opacity:.6"><span class="code">'+x.e.id+'</span><span class="dec '+x.dec+'">'+DEC_L[x.dec]+'</span></div>').join('')+'</div>'; }).join('')
    : '<div class="empty">Nenhuma preventiva para esta noite.</div>';
  const f=$('#pvFiltro').value, lista=all.filter(x=>!f||x.dec===f);
  $('#pvLista').innerHTML = '<table><thead><tr><th>Escada</th><th>Estação</th><th>Decisão</th><th>Motivo</th><th>Última preventiva</th><th>Próxima pelo calendário</th></tr></thead><tbody>'+
    lista.slice(0,120).map(x=>'<tr class="click" data-row="'+x.e.id+'"><td class="code">'+x.e.id+'</td><td>'+esc(ESTN[x.e.cod])+'</td><td><span class="dec '+x.dec+'">'+DEC_L[x.dec]+'</span></td><td>'+esc(x.motivo)+'</td><td class="num">'+(x.last==null?'—':fD(x.last))+'</td><td class="num">'+(x.prox<=NOW?'<b style="color:var(--warn)">vencida</b>':fD(x.prox))+'</td></tr>').join('')+'</tbody></table>'+
    (lista.length>120?'<p class="hint">Mostrando 120 de '+lista.length+'. Use o filtro para ver o resto.</p>':'');
  $('#pvSub').textContent='Para cada escada '+(escopoEst()?'da estação '+ESTN[escopoEst()]:'da Linha 4')+', o que fazer com a próxima preventiva mensal do plano. A P1 anual nunca é dispensada. A decisão final é da engenharia.';
  $('#pvNota').textContent='Regras propostas pelo grupo, a validar com a engenharia da Motiva: P1 anual vencendo em até '+CFG.p1AvisoDias+' dias é obrigatória; ALERTA, CRÍTICO, tendência de piora ou 2 ou mais corretivas em 30 dias antecipam a preventiva; BOM com todas as variáveis abaixo de '+Math.round(PREV.limiteBom*100)+'% do limite e sem corretivas em 30 dias permite dispensar. Duração média de '+PREV.duracaoMin+' min por preventiva (histórico simulado). Escadas em manutenção ficam de fora.';
}
$('#pvFiltro').onchange=renderPrev;
['#pvLista','#pvNoite'].forEach(q=>$(q).addEventListener('click',ev=>{ const r=ev.target.closest('[data-row]'); if(r) openDetalhe(r.dataset.row); }));

/* ================= TELA: equipes por estação ================= */""")
open(p, 'w', encoding='utf-8').write(s); print('patched v12 (boletim e preventivas)')
