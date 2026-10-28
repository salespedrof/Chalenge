"""Etapa 4: análise de foco do supervisor (ranking com motivos, estações, mapa de calor e recomendações)."""
p = 'template.html'; s = open(p, encoding='utf-8').read()
def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

R("@media (max-width:640px){ .rt-kpis{grid-template-columns:repeat(2,minmax(0,1fr))} }", """@media (max-width:640px){ .rt-kpis{grid-template-columns:repeat(2,minmax(0,1fr))} }
/* ---------- foco do supervisor ---------- */
.fc-recs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.fc-rec{display:flex;flex-direction:column;gap:8px;padding:16px;border-radius:12px;border:1px solid var(--line);border-top:4px solid var(--brand);background:var(--surface)}
.fc-rec .n{font-family:var(--f-display);font-weight:700;color:var(--brand);font-size:.85rem;letter-spacing:.08em;text-transform:uppercase}
.fc-rec b{font-size:1.05rem}
.fc-rec p{margin:0;line-height:1.45}
.fc-row{display:grid;grid-template-columns:36px minmax(140px,1fr) minmax(0,2.4fr) 92px auto;gap:12px;align-items:center;padding:12px 14px;border-radius:12px;border:1px solid var(--line);background:var(--surface)}
.fc-pos{font-family:var(--f-display);font-size:1.4rem;font-weight:700;color:var(--muted);text-align:center}
.fc-chips{display:flex;flex-wrap:wrap;gap:6px}
.fc-chip{font-size:.8rem;padding:3px 8px;border-radius:6px;border:1px solid var(--line-2);background:var(--surface-2);color:var(--fg)}
.fc-chip.c2{border-color:var(--crit);color:var(--crit)}.fc-chip.c1{border-color:var(--warn);color:var(--warn)}.fc-chip.cb{border-color:var(--brand);color:var(--brand)}
.fc-bar{height:8px;border-radius:4px;background:var(--surface-3);overflow:hidden}.fc-bar i{display:block;height:100%;background:var(--brand)}
.fc-score{font-family:var(--f-display);font-weight:700;font-size:1.2rem;text-align:right}
.fc-heat{border-collapse:separate;border-spacing:3px;width:100%;font-size:.85rem}
.fc-heat th{font-weight:600;color:var(--muted);text-align:center;padding:4px}
.fc-heat th:first-child{text-align:left}
.fc-heat td{text-align:center;border-radius:6px;padding:8px 4px;font-family:var(--f-mono);font-weight:600}
.fc-heat td:first-child{text-align:left;font-family:var(--f-body);font-weight:500;background:none!important}
.fc-two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px}
@media (max-width:1180px){ .fc-recs{grid-template-columns:minmax(0,1fr)} .fc-two{grid-template-columns:minmax(0,1fr)} .fc-row{grid-template-columns:32px minmax(0,1fr) 80px} .fc-row .fc-chips{grid-column:2 / -1} .fc-row .acts{grid-column:2 / -1} }""")

R('<button class="nav sup-only" data-view="equipe">', '''<button class="nav sup-only" data-view="foco"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1" fill="currentColor"/></svg>Foco</button>
    <button class="nav sup-only" data-view="equipe">''')
R('    <section class="view" id="v-equipe" hidden aria-label="Equipe">', '''    <section class="view" id="v-foco" hidden aria-label="Onde focar">
      <div class="vhead"><div><h2>Onde focar</h2><p id="fcSub">Escadas e estações que mais pedem atenção, com o motivo de cada uma.</p></div>
        <label class="field"><span>Período</span><select id="fcPer"><option value="7">Últimos 7 dias</option><option value="30" selected>Últimos 30 dias</option><option value="90">Últimos 90 dias</option></select></label></div>
      <div class="fc-recs" id="fcRecs"></div>
      <div class="vhead"><div><h3>Escadas que mais pedem atenção</h3><p>Pontuação de foco: status agora, tendência, falhas que se repetem, paradas, P1 atrasada e tempo de reparo, com peso maior para o grupo crítica.</p></div></div>
      <div class="stack" style="gap:8px" id="fcRank"></div>
      <div class="fc-two">
        <div class="panel"><h3>Estações</h3><div class="tbl-wrap" id="fcEst"></div></div>
        <div class="panel"><h3>Quando as falhas acontecem</h3><p class="hint" style="margin:0">Atendimentos corretivos por estação e horário da chamada no período.</p><div class="tbl-wrap" id="fcHeat"></div></div>
      </div>
      <p class="hint" id="fcNota"></p>
    </section>

    <section class="view" id="v-equipe" hidden aria-label="Equipe">''')
R("  else if(view==='equipe') renderEquipe();", "  else if(view==='equipe') renderEquipe();\n  else if(view==='foco') renderFoco();")
R("  if(isTec() && ['ind','dados','live','equipe'].includes(v)) v='painel';", "  if(isTec() && ['ind','dados','live','equipe','foco'].includes(v)) v='painel';")

R("/* ================= TELA: equipe e responsáveis (supervisor) ================= */", r"""/* ================= FOCO DO SUPERVISOR: onde agir primeiro, com o motivo =================
   Pontuação por escada (pesos em FOCO.peso, ajustáveis): status agora, tendência, corretivas e paradas
   no período, P1 atrasada e reparo demorado; multiplicada para o grupo crítica e pelo fluxo. */
const FOCO = {peso:{critico:30, alerta:15, tendencia:12, corretiva:4, parada:3, p1:10, reparoLongo:6}, multCritica:1.3, reparoLongoMin:180};
function focoEscada(e, dias){
  const c=CUR[e.ix], de=NOW-dias*1440, at=e.atv.filter(a=>a.ent<=NOW && a.ent>=de);
  const corr=at.filter(a=>a.tipo==='corretiva'), par=corr.filter(a=>a.motivo==='parada de seguranca (reset)');
  const fech=corr.filter(a=>a.sai!=null && a.sai<=NOW), mttr=fech.length ? fech.reduce((s,a)=>s+(a.sai-a.ent),0)/fech.length : 0;
  const p1=lastP1(e), p1Atr = p1==null ? NOW>CFG.p1Dias*1440 : (NOW-p1)/1440>CFG.p1Dias;
  const tr=TEND[e.ix], W=FOCO.peso, m=[];
  let pt=0;
  if(c.code===2){ pt+=W.critico; m.push({t:'CRÍTICO agora · '+c.txt, k:'c2', modo:'agora'}); }
  else if(c.code===1){ pt+=W.alerta; m.push({t:'ALERTA agora · '+c.txt, k:'c1', modo:'agora'}); }
  if(tr){ pt+=W.tendencia; m.push({t:V[tr.k].nome+' piorando: ALERTA em '+fmtPrazo(tr.tA).replace('cerca de ','~'), k:'cb', modo:'tend'}); }
  const outras=corr.length-par.length;
  if(par.length>=2){ pt+=W.parada*par.length; m.push({t:par.length+' paradas com reset', k:'', modo:'parada'}); }
  if(outras>=1){ pt+=W.corretiva*outras; m.push({t:outras+' corretiva'+(outras>1?'s':'')+' por sensor ou status', k:'', modo:'recorre'}); }
  if(p1Atr){ pt+=W.p1; m.push({t:'P1 atrasada', k:'c1', modo:'p1'}); }
  if(mttr>=FOCO.reparoLongoMin){ pt+=W.reparoLongo; m.push({t:'reparo médio de '+fDur(mttr), k:'', modo:'mttr'}); }
  pt *= (e.crit?FOCO.multCritica:1) * (0.8+0.2*e.fluxo);
  return {e, c, pt, m, corr:corr.length, par:par.length, mttr, p1Atr};
}
function recomendacao(f){
  const modos=f.m.map(x=>x.modo);
  if(modos.includes('agora') && f.c.code===2) return 'Atender agora: '+f.e.id+' está crítica'+(f.e.crit?' e é do grupo crítica':'')+'. Confirme se o técnico responsável ('+(TECS[respDe(f.e)]||'—')+') já está a caminho.';
  if(modos.includes('parada')) return f.e.id+' parou '+f.par+' vezes com reset. Em vez de só resetar, programe uma inspeção do dispositivo de segurança para achar a causa.';
  if(modos.includes('tend')) return 'Programar inspeção em '+f.e.id+' antes do ALERTA: a tendência indica '+MODOS[modoDaVar(f.e,TEND[f.e.ix].k,IDX)].t.toLowerCase()+'.';
  if(modos.includes('agora')) return 'Programar o atendimento de '+f.e.id+' dentro do prazo de despacho.';
  if(modos.includes('p1')) return 'Encaixar a P1 de '+f.e.id+' na próxima rota do técnico: a revisão mensal está atrasada.';
  if(modos.includes('mttr')) return 'Os reparos em '+f.e.id+' estão demorando. Vale levar peças de reposição já na primeira visita.';
  return 'Acompanhar '+f.e.id+'.';
}
function renderFoco(){
  if(!isSup()) return show('painel');
  computeCurrent();
  const dias=+$('#fcPer').value, all=E.map(e=>focoEscada(e,dias)).filter(f=>f.pt>0).sort((a,b)=>b.pt-a.pt);
  const top=all.slice(0,12), max=top.length?top[0].pt:1;
  $('#fcSub').textContent='Escadas e estações que mais pedem atenção nos últimos '+dias+' dias, com o motivo de cada uma. '+all.length+' das '+E.length+' escadas têm algum ponto de atenção.';
  /* recomendações: as três primeiras com motivos diferentes */
  const recs=[], usados=new Set();
  for(const f of all){ const tipo=f.m[0].modo; if(usados.has(tipo)) continue; usados.add(tipo); recs.push({f,r:recomendacao(f)}); if(recs.length===3) break; }
  for(const f of all){ if(recs.length>=3) break; if(!recs.some(x=>x.f===f)) recs.push({f,r:recomendacao(f)}); }
  $('#fcRecs').innerHTML = recs.map((x,i)=>'<div class="fc-rec"><span class="n">Recomendação '+(i+1)+'</span><b>'+x.f.e.id+' · '+esc(ESTN[x.f.e.cod])+'</b><p>'+esc(x.r)+'</p><div><button class="btn sm" data-ver="'+x.f.e.id+'">Ver escada</button></div></div>').join('') || '<div class="empty">Nenhum ponto de atenção no período.</div>';
  $('#fcRank').innerHTML = top.map((f,i)=>'<div class="fc-row"><div class="fc-pos">'+(i+1)+'</div><div><div class="code">'+f.e.id+'</div><div class="muted" style="font-size:.85rem">'+esc(ESTN[f.e.cod])+' · '+(f.e.crit?'<b style="color:var(--brand)">crítica</b>':'não crítica')+' · '+esc(TECS[respDe(f.e)]||'—')+'</div></div>'+
    '<div class="fc-chips">'+f.m.map(x=>'<span class="fc-chip '+x.k+'">'+esc(x.t)+'</span>').join('')+'</div>'+
    '<div><div class="fc-score num">'+nf(f.pt,0)+'</div><div class="fc-bar"><i style="width:'+Math.round(f.pt/max*100)+'%"></i></div></div>'+
    '<div class="acts"><button class="btn sm" data-ver="'+f.e.id+'">Ver escada</button></div></div>').join('');
  /* estações */
  const est=EST.map(st=>{ const fs=E.filter(e=>e.cod===st.cod).map(e=>all.find(f=>f.e===e)).filter(Boolean); const es=E.filter(e=>e.cod===st.cod);
    const prob=es.filter(e=>CUR[e.ix].code===1||CUR[e.ix].code===2).length, corr=fs.reduce((s,f)=>s+f.corr,0), par=fs.reduce((s,f)=>s+f.par,0);
    return {st, n:es.length, pt:fs.reduce((s,f)=>s+f.pt,0)/es.length, prob, corr, par, tend:es.filter(e=>TEND[e.ix]).length}; }).sort((a,b)=>b.pt-a.pt);
  $('#fcEst').innerHTML = '<table><thead><tr><th>Estação</th><th class="n">Escadas</th><th class="n">Alerta ou crítico</th><th class="n">Tendência</th><th class="n">Corretivas</th><th class="n">Paradas</th><th class="n">Foco médio</th></tr></thead><tbody>'+
    est.map(x=>'<tr><td>'+esc(x.st.nome)+'</td><td class="n">'+x.n+'</td><td class="n">'+(x.prob?'<b style="color:var(--warn)">'+x.prob+'</b>':'0')+'</td><td class="n">'+x.tend+'</td><td class="n">'+x.corr+'</td><td class="n">'+x.par+'</td><td class="n"><b>'+nf(x.pt,1)+'</b></td></tr>').join('')+'</tbody></table>';
  /* mapa de calor: corretivas por estação × horário da chamada */
  const de=NOW-dias*1440, F=[[0,8,'0–8h'],[8,12,'8–12h'],[12,16,'12–16h'],[16,20,'16–20h'],[20,24,'20–24h']];
  const hora=m=>dt(m).getUTCHours(), M={}; let mx=0, tot=Array(F.length).fill(0);
  E.forEach(e=>e.atv.forEach(a=>{ if(a.tipo!=='corretiva'||a.ent>NOW||a.ent<de) return; const h=hora(a.ent), j=F.findIndex(f=>h>=f[0]&&h<f[1]); const k=e.cod+'|'+j; M[k]=(M[k]||0)+1; tot[j]++; if(M[k]>mx) mx=M[k]; }));
  const cor=v=>!v?'var(--surface-2)':'rgba(255,210,60,'+(0.15+0.75*v/mx).toFixed(2)+')', ink=v=>v/mx>0.55?'#1b1600':'var(--fg)';
  const jMax=tot.indexOf(Math.max(...tot));
  $('#fcHeat').innerHTML='<table class="fc-heat"><thead><tr><th>Estação</th>'+F.map(f=>'<th>'+f[2]+'</th>').join('')+'</tr></thead><tbody>'+
    EST.map(st=>'<tr><td>'+esc(st.nome)+'</td>'+F.map((f,j)=>{ const v=M[st.cod+'|'+j]||0; return '<td style="background:'+cor(v)+';color:'+ink(v)+'">'+v+'</td>'; }).join('')+'</tr>').join('')+
    '<tr><td><b>Total</b></td>'+tot.map((v,j)=>'<td style="background:none;'+(j===jMax?'color:var(--brand)':'')+'">'+v+'</td>').join('')+'</tr></tbody></table>'+
    (Math.max(...tot)?'<p class="hint" style="margin:8px 0 0">Faixa com mais chamados: <b>'+F[jMax][2]+'</b>. Concentrar a equipe e as inspeções antes desse horário reduz as paradas no pico.</p>':'');
  $('#fcNota').textContent='Pesos da pontuação (ajustáveis em FOCO no código): crítico '+FOCO.peso.critico+', alerta '+FOCO.peso.alerta+', tendência '+FOCO.peso.tendencia+', cada corretiva '+FOCO.peso.corretiva+', cada parada com reset '+FOCO.peso.parada+', P1 atrasada '+FOCO.peso.p1+', reparo médio acima de '+FOCO.reparoLongoMin/60+' h '+FOCO.peso.reparoLongo+'; ×'+FOCO.multCritica+' para o grupo crítica e ajuste pelo fluxo. Dados de sensores e atendimentos simulados.';
}
$('#fcPer').onchange=renderFoco;
['#fcRecs','#fcRank'].forEach(q=>$(q).addEventListener('click',ev=>{ const b=ev.target.closest('[data-ver]'); if(b) openDetalhe(b.dataset.ver); }));

/* ================= TELA: equipe e responsáveis (supervisor) ================= */""")
open(p, 'w', encoding='utf-8').write(s); print('patched v9 (foco)')
