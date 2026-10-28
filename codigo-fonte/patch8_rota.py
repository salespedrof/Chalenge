"""Etapa 3: rota do turno pela Linha 4 (grafo das estações + Dijkstra + planejar_turno)."""
p = 'template.html'; s = open(p, encoding='utf-8').read()
def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# ---------- CSS ----------
R(".eq-row.mudou{box-shadow:0 0 0 2px var(--brand)}", """.eq-row.mudou{box-shadow:0 0 0 2px var(--brand)}
/* ---------- rota ---------- */
.rt-tools{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end}
.rt-tools .field{min-width:0;max-width:100%}
.rt-map{border-radius:12px;border:1px solid var(--line);background:var(--surface);padding:12px 8px 4px;overflow-x:auto}
.rt-map svg{display:block;width:100%;min-width:720px;height:auto}
.rt-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.rt-kpi{padding:12px 14px;border-radius:12px;border:1px solid var(--line);background:var(--surface)}
.rt-kpi .n{font-family:var(--f-display);font-size:1.7rem;font-weight:700;line-height:1.05}
.rt-kpi .t{font-size:.82rem;color:var(--muted)}
.rt-stop{display:grid;grid-template-columns:44px minmax(0,1fr);gap:12px;padding:14px;border-radius:12px;border:1px solid var(--line);background:var(--surface)}
.rt-stop.fora{opacity:.6;border-style:dashed}
.rt-num{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:var(--f-display);font-weight:700;font-size:1.2rem;background:var(--brand);color:var(--brand-ink)}
.rt-stop.fora .rt-num{background:var(--surface-3);color:var(--muted)}
.rt-h{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline}
.rt-h b{font-size:1.08rem}
.rt-via{font-size:.85rem;color:var(--muted)}
.rt-esc{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.rt-e{display:flex;gap:8px;align-items:center;padding:6px 10px;border-radius:8px;border:1px solid var(--line-2);background:var(--surface-2);color:var(--fg);font-size:.88rem}
.rt-e .code{font-size:.92rem}
.rt-note{font-size:.82rem;color:var(--muted)}
@media (max-width:640px){ .rt-kpis{grid-template-columns:repeat(2,minmax(0,1fr))} }""")

# ---------- navegação e tela ----------
R('    <button class="nav" data-view="atend">', '''    <button class="nav" data-view="rota"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="18" r="2.2"/><circle cx="19" cy="6" r="2.2"/><path d="M7 18h7a3.5 3.5 0 0 0 0-7H10a3.5 3.5 0 0 1 0-7h7"/></svg>Rota</button>
    <button class="nav" data-view="atend">''')
R('    <!-- TELA 3 -->', '''    <!-- TELA: rota do turno -->
    <section class="view" id="v-rota" hidden aria-label="Rota do turno">
      <div class="vhead"><div><h2 id="rtTit">Rota do turno</h2><p id="rtSub">Ordem das escadas a atender, pelo caminho da Linha 4, a partir da base de manutenção.</p></div></div>
      <div class="rt-tools">
        <label class="field sup-only" id="rtTecF"><span>Técnico</span><select id="rtTec"></select></label>
        <label class="field"><span>Horas no turno</span><select id="rtHoras"><option value="4">4 horas</option><option value="6">6 horas</option><option value="8" selected>8 horas</option></select></label>
        <label class="field"><span>Incluir</span><select id="rtIncl"><option value="tend">Fila + escadas com tendência de piora</option><option value="fila">Só a fila (ALERTA e CRÍTICO)</option></select></label>
      </div>
      <div class="rt-kpis" id="rtKpis"></div>
      <div class="rt-map" id="rtMapa"></div>
      <div class="stack" style="gap:10px" id="rtLista"></div>
      <p class="rt-note" id="rtNota"></p>
    </section>

    <!-- TELA 3 -->''')
R("  else if(view==='fila') renderFila();", "  else if(view==='fila') renderFila();\n  else if(view==='rota') renderRota();")

# ---------- lógica ----------
R("/* ================= TELA: equipe e responsáveis (supervisor) ================= */", r"""/* ================= ROTA DO TURNO: grafo da Linha 4 + Dijkstra + planejarTurno =================
   Vértices: as 12 estações e a base de manutenção (pátio Vila Sônia). Arestas: trechos, com peso em minutos.
   Os tempos são ESTIMATIVAS do grupo, a confirmar com a Motiva. */
const REDE = {
  base: {cod:'BASE', nome:'Base de manutenção · Pátio Vila Sônia'},
  trechos: [['LUZ','REP',2],['REP','HIG',2],['HIG','PTA',2],['PTA','FRE',2],['FRE','FRA',2],['FRA','FAL',2],['FAL','PIN',2],['PIN','BUT',3],['BUT','MBI',3],['MBI','VSO',3],['VSO','TVS',2],['BASE','VSO',5]],
  minPorEscadaNaEstacao: 0.25,   /* deslocamento dentro da estação cresce com o número de escadas */
  minBaseEstacao: 1,
  atendimento: {imediato:60, critico:60, alerta:45, tendencia:20},
};
const GRAFO = (()=>{ const g={}; const add=(a,b,w)=>{ (g[a]=g[a]||[]).push([b,w]); (g[b]=g[b]||[]).push([a,w]); }; REDE.trechos.forEach(([a,b,w])=>add(a,b,w)); return g; })();
const NOME_NO = c => c==='BASE' ? 'Base' : ESTN[c];
/* Dijkstra: menor tempo de 'origem' até cada vértice, com o caminho reconstruído */
function dijkstra(origem){
  const dist={}, prev={}, feito=new Set(); Object.keys(GRAFO).forEach(v=>dist[v]=Infinity); dist[origem]=0;
  while(feito.size<Object.keys(GRAFO).length){
    let u=null; for(const v in dist) if(!feito.has(v) && (u===null || dist[v]<dist[u])) u=v;
    if(u===null || dist[u]===Infinity) break; feito.add(u);
    for(const [v,w] of GRAFO[u]) if(dist[u]+w<dist[v]){ dist[v]=dist[u]+w; prev[v]=u; }
  }
  const caminho = d => { const c=[d]; while(c[0]!==origem && prev[c[0]]) c.unshift(prev[c[0]]); return c; };
  return {dist, caminho};
}
const DIJ = {}; const rotaEntre = (a,b) => { const r = DIJ[a] || (DIJ[a]=dijkstra(a)); return {min:r.dist[b], via:r.caminho(b)}; };
const tempoInterno = cod => REDE.minBaseEstacao + REDE.minPorEscadaNaEstacao * E.filter(e=>e.cod===cod).length;
const POS = cod => cod==='BASE' ? EST.length : EST.findIndex(x=>x.cod===cod);

/* o que o técnico tem a atender: a fila dele (RN-03/RN-04) e, se pedido, as escadas BOM com tendência de piora */
function pendenciasDe(tec, incluirTend){
  const P=CFG.prioridade, out=[];
  for(const e of E){ if(respDe(e)!==tec) continue; const c=CUR[e.ix];
    if(c.code===1||c.code===2){ const h=Math.max(0,(NOW-c.since)/60); const d=c.code===2?(e.crit?0:1):(e.crit?2:3);
      out.push({e, c, d, score:(c.code===2?P.CRITICO:P.ALERTA)+(e.crit?P.grupoCritica:0)+P.fluxo*e.fluxo+Math.min(h,P.horasMax), tipo: d===0?'imediato':c.code===2?'critico':'alerta'}); }
    else if(incluirTend && TEND[e.ix]) out.push({e, c, d:4, score:0, tipo:'tendencia'}); }
  return out.sort((a,b)=>a.d-b.d || b.score-a.score);
}
/* planejarTurno(base, horas): quais escadas atender, em que ordem e por qual caminho.
   1) despacho imediato primeiro, pelo menor caminho;  2) o resto agrupado por estação e percorrido num sentido só
   (primeiro até a ponta mais próxima do que falta, depois varrendo a linha);  3) só entra o que cabe com a volta à base. */
function planejarTurno(base, horas, tec, incluirTend){
  const pend=pendenciasDe(tec, incluirTend), limite=horas*60;
  const porEst = itens => { const m=new Map(); itens.forEach(x=>{ if(!m.has(x.e.cod)) m.set(x.e.cod,[]); m.get(x.e.cod).push(x); }); return m; };
  const paradas=[]; let aqui=base;
  const imed=porEst(pend.filter(x=>x.d===0)), resto=porEst(pend.filter(x=>x.d!==0));
  /* imediatos: a estação mais próxima primeiro, repetindo até acabar */
  const restImed=new Map(imed);
  while(restImed.size){ let best=null; for(const cod of restImed.keys()){ const r=rotaEntre(aqui,cod); if(!best||r.min<best.r.min) best={cod,r}; }
    paradas.push({cod:best.cod, itens:restImed.get(best.cod), r:best.r}); restImed.delete(best.cod); aqui=best.cod; }
  /* demais: estações que ainda faltam (as já visitadas recebem os itens extras na mesma parada) */
  for(const pz of paradas){ if(resto.has(pz.cod)){ pz.itens=pz.itens.concat(resto.get(pz.cod)); resto.delete(pz.cod); } }
  if(resto.size){
    const pos=[...resto.keys()].map(POS), a=Math.min(...pos), b=Math.max(...pos), p=POS(aqui);
    const ida = Math.abs(p-a) <= Math.abs(p-b) ? [...resto.keys()].sort((x,y)=>POS(x)-POS(y)) : [...resto.keys()].sort((x,y)=>POS(y)-POS(x));
    for(const cod of ida){ paradas.push({cod, itens:resto.get(cod), r:rotaEntre(aqui,cod)}); aqui=cod; }
  }
  /* tempos e corte pelo turno */
  let t=0, ultimo=base; const dentro=[], fora=[];
  for(const pz of paradas){
    const r=rotaEntre(ultimo,pz.cod), att=pz.itens.reduce((s,x)=>s+REDE.atendimento[x.tipo],0), interno=tempoInterno(pz.cod);
    const volta=rotaEntre(pz.cod,base).min, fim=t+r.min+interno+att;
    if(fim+volta<=limite || (!dentro.length && pz.itens.some(x=>x.d===0))){ dentro.push({...pz, r, chegada:t+r.min, att, interno, saida:fim}); t=fim; ultimo=pz.cod; }
    else fora.push({...pz, att});
  }
  const volta = rotaEntre(ultimo, base);
  return {base, horas, dentro, fora, volta, total:t+volta.min, viagem: dentro.reduce((s,x)=>s+x.r.min,0)+volta.min, pend};
}

const TIPO_L = {imediato:'Imediato', critico:'Crítico', alerta:'Alerta', tendencia:'Tendência'};
let rtTec=null;
function mapaSVG(plano){
  const n=EST.length, W=1000, x0=40, dx=(W-x0*2)/(n), Y=70, xs=i=>x0+dx*i+dx/2, xb=xs(n-1)+dx*0.9;
  const X=cod=>cod==='BASE'?xb:xs(POS(cod));
  const parada=new Map(plano.dentro.map((p,i)=>[p.cod,i+1])), foraS=new Set(plano.fora.map(p=>p.cod));
  const pts=['BASE'].concat(...plano.dentro.map(p=>p.r.via.slice(1))).concat(plano.volta.via.slice(1));
  let path='', y=Y; const seg=[];
  for(let i=1;i<pts.length;i++){ seg.push([X(pts[i-1]),X(pts[i])]); }
  /* o percurso aparece em faixas acima da linha, uma por perna, para não sobrepor ida e volta */
  const legs=[]; let cur=[]; for(let i=1;i<pts.length;i++){ cur.push(pts[i-1]); const isStop=parada.has(pts[i])||(i===pts.length-1); if(isStop){ cur.push(pts[i]); legs.push(cur); cur=[]; } }
  legs.forEach((lg,i)=>{ const yy=Y-18-((i%3)*7); path+='<path d="M'+X(lg[0])+' '+(Y-6)+' L'+X(lg[0])+' '+yy+' L'+X(lg[lg.length-1])+' '+yy+' L'+X(lg[lg.length-1])+' '+(Y-6)+'" fill="none" stroke="var(--brand)" stroke-width="2" stroke-opacity="'+(i===legs.length-1?0.45:0.9)+'"'+(i===legs.length-1?' stroke-dasharray="5 4"':'')+'/>'; });
  let g='<line x1="'+xs(0)+'" y1="'+Y+'" x2="'+xs(n-1)+'" y2="'+Y+'" stroke="#FFD23C" stroke-width="8" stroke-linecap="round"/>'+
    '<line x1="'+xs(EST.findIndex(e=>e.cod==='VSO'))+'" y1="'+Y+'" x2="'+xb+'" y2="'+Y+'" stroke="var(--line-2)" stroke-width="3" stroke-dasharray="4 4"/>';
  EST.forEach((st,i)=>{ const k=parada.get(st.cod), f=foraS.has(st.cod), qtd=E.filter(e=>e.cod===st.cod&&respDe(e)===rtTec).length;
    g+='<circle cx="'+xs(i)+'" cy="'+Y+'" r="'+(k?11:7)+'" fill="'+(k?'var(--brand)':'var(--surface)')+'" stroke="'+(k?'var(--brand)':f?'var(--warn)':'var(--fg)')+'" stroke-width="'+(f?3:2.5)+'"'+(f?' stroke-dasharray="3 2"':'')+'/>'+
      (k?'<text x="'+xs(i)+'" y="'+(Y+5)+'" text-anchor="middle" font-size="13" font-weight="700" fill="#1b1600">'+k+'</text>':'')+
      '<text x="'+xs(i)+'" y="'+(Y+30)+'" text-anchor="middle" font-size="12" font-weight="'+(k?700:500)+'" fill="'+(k?'var(--fg)':'var(--muted)')+'">'+st.cod+'</text>'+
      (qtd?'<text x="'+xs(i)+'" y="'+(Y+46)+'" text-anchor="middle" font-size="10.5" fill="var(--muted)">'+qtd+' suas</text>':''); });
  g+='<rect x="'+(xb-14)+'" y="'+(Y-14)+'" width="28" height="28" rx="6" fill="var(--surface-3)" stroke="var(--fg)" stroke-width="2"/><text x="'+xb+'" y="'+(Y+5)+'" text-anchor="middle" font-size="12" font-weight="700" fill="var(--fg)">B</text>'+
    '<text x="'+xb+'" y="'+(Y+30)+'" text-anchor="middle" font-size="12" fill="var(--muted)">Base</text>';
  return '<svg viewBox="0 0 '+W+' 130" role="img" aria-label="Mapa da Linha 4 com as paradas numeradas da rota">'+path+g+'</svg>';
}
const hhmm = m => { const d=dt(NOW+m); return pad(d.getUTCHours())+':'+pad(d.getUTCMinutes()); };
function renderRota(){
  computeCurrent();
  if(isTec()) rtTec=S.login.id;
  else if(!rtTec || !TECS[rtTec]){ let best=null; for(const k of Object.keys(TECS)){ const n=pendenciasDe(k,false).length; if(!best||n>best.n) best={k,n}; } rtTec=best.k; }
  const sel=$('#rtTec'); if(!sel.options.length) sel.innerHTML=Object.entries(TECS).map(([k,n])=>'<option value="'+k+'">'+k+' · '+esc(n)+'</option>').join(''); sel.value=rtTec;
  const horas=+$('#rtHoras').value, tend=$('#rtIncl').value==='tend';
  const pl=planejarTurno('BASE', horas, rtTec, tend);
  const nEsc=pl.dentro.reduce((s,p)=>s+p.itens.length,0), nFora=pl.fora.reduce((s,p)=>s+p.itens.length,0);
  $('#rtTit').textContent = isTec() ? 'Minha rota do turno' : 'Rota do turno · '+TECS[rtTec];
  $('#rtSub').textContent = 'Sai da base de manutenção às '+hhmm(0)+', '+(isTec()?'pelas suas escadas':'pelas escadas de '+TECS[rtTec])+' ('+trechoDe(rtTec)+'), e volta à base. Despacho imediato primeiro; depois a linha num sentido só.';
  $('#rtKpis').innerHTML = [[pl.dentro.length,'paradas no turno'],[nEsc,'escadas atendidas'],[fDur(pl.total),'tempo total, com a volta'],[pl.viagem+' min','em deslocamento']].map(([n,t])=>'<div class="rt-kpi"><div class="n num">'+n+'</div><div class="t">'+t+'</div></div>').join('');
  $('#rtMapa').innerHTML = mapaSVG(pl);
  if(!pl.pend.length){ $('#rtLista').innerHTML='<div class="empty">Nenhuma escada '+(isTec()?'sua':'de '+esc(TECS[rtTec]))+' precisa de atendimento agora'+(tend?'':' na fila')+'. A P1 mensal segue o plano preventivo.</div>'; $('#rtNota').textContent=''; return; }
  const itemHTML = x => '<button class="rt-e" data-ver="'+x.e.id+'"><span class="code">'+x.e.id+'</span>'+(x.tipo==='tendencia'?'<span class="chip-trend">↗ tendência</span>':pill(x.c.code))+(x.d<=3?despPill(x.d):'')+'</button>';
  let html = pl.dentro.map((p,i)=>'<div class="rt-stop"><div class="rt-num">'+(i+1)+'</div><div><div class="rt-h"><b>'+esc(ESTN[p.cod])+'</b><span class="mono">chegada '+hhmm(p.chegada)+' · saída '+hhmm(p.saida)+'</span><span class="muted">'+p.itens.length+' escada'+(p.itens.length>1?'s':'')+' · '+p.att+' min de atendimento</span></div>'+
    '<div class="rt-via">Caminho: '+p.r.via.map(NOME_NO).join(' → ')+' · '+p.r.min+' min de viagem + '+nf(p.interno,1)+' min dentro da estação</div><div class="rt-esc">'+p.itens.map(itemHTML).join('')+'</div></div></div>').join('');
  html += '<div class="rt-stop"><div class="rt-num" style="background:var(--surface-3);color:var(--fg)">B</div><div><div class="rt-h"><b>Volta à base</b><span class="mono">chegada '+hhmm(pl.total)+'</span></div><div class="rt-via">Caminho: '+pl.volta.via.map(NOME_NO).join(' → ')+' · '+pl.volta.min+' min</div></div></div>';
  if(pl.fora.length) html += '<div class="vhead" style="margin-top:6px"><h3>Fica para o próximo turno</h3></div>'+pl.fora.map(p=>'<div class="rt-stop fora"><div class="rt-num">–</div><div><div class="rt-h"><b>'+esc(ESTN[p.cod])+'</b><span class="muted">'+p.itens.length+' escada'+(p.itens.length>1?'s':'')+' · '+p.att+' min de atendimento</span></div><div class="rt-esc">'+p.itens.map(itemHTML).join('')+'</div></div></div>').join('');
  $('#rtLista').innerHTML = html;
  $('#rtNota').textContent = 'Menor caminho pelo algoritmo de Dijkstra no grafo das 12 estações + base. Tempos estimados pelo grupo, a confirmar com a Motiva: '+REDE.trechos.filter(t=>t[0]!=='BASE').map(t=>t[2]).join('/')+' min entre estações, '+REDE.trechos.find(t=>t[0]==='BASE')[2]+' min da base a Vila Sônia, '+REDE.minBaseEstacao+' min + '+REDE.minPorEscadaNaEstacao*60+' s por escada dentro da estação, e atendimento de '+REDE.atendimento.critico+' min (crítico), '+REDE.atendimento.alerta+' min (alerta) e '+REDE.atendimento.tendencia+' min (inspeção de tendência).';
}
$('#rtTec').onchange=e=>{ rtTec=e.target.value; renderRota(); };
['#rtHoras','#rtIncl'].forEach(q=>$(q).onchange=renderRota);
$('#rtLista').addEventListener('click',ev=>{ const b=ev.target.closest('[data-ver]'); if(b) openDetalhe(b.dataset.ver); });

/* ================= TELA: equipe e responsáveis (supervisor) ================= */""")

open(p, 'w', encoding='utf-8').write(s); print('patched v8 (rota)')
