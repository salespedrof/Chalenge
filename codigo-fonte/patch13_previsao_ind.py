"""Revisão Motiva: previsão nos gráficos da escada e indicadores alinhados aos critérios de sucesso da Motiva."""
p = 'template.html'; s = open(p, encoding='utf-8').read()
def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# ---------- previsão no gráfico de cada variável ----------
R("  const m0=slotMin(i0), m1=Math.max(slotMin(i1), NOW);", """  const PJ = e.ss[i1]===3 ? null : projecao(e,k,i1);
  const m0=slotMin(i0), m1=Math.max(slotMin(i1), NOW) + (PJ ? PJ.dias*1440 : 0);""")
R("  const [y0,y1]=yRange(k, vals.filter((x,j)=>!(cf.k!=='vel' && isStop(i0+j)) ));",
  "  const [y0,y1]=yRange(k, vals.filter((x,j)=>!(cf.k!=='vel' && isStop(i0+j)) ).concat(PJ?[PJ.fim]:[]));")
R("  // ponto atual\n  const xl=val(e,k,i1);", """  // previsão: tendência das últimas 15 leituras projetada para frente (linha tracejada)
  if(PJ){ const t0=slotMin(i1), t1=NOW+PJ.dias*1440;
    g.save(); g.fillStyle='rgba(255,210,60,.07)'; g.fillRect(X(Math.max(t0,NOW)),T,X(t1)-X(Math.max(t0,NOW)),ph);
    g.setLineDash([6,4]); g.strokeStyle=COL.brand; g.lineWidth=2; g.beginPath(); g.moveTo(X(t0),Y(PJ.x0)); g.lineTo(X(t1),Y(PJ.fim)); g.stroke(); g.setLineDash([]);
    g.font='600 11px "IBM Plex Mono", ui-monospace, monospace';
    for(const c of PJ.cruz){ const tx=t0+c.d*1440; if(tx>t1) continue; const px=X(tx), py=Y(c.y); g.fillStyle=c.n===2?COL.crit:COL.warn; g.beginPath(); g.moveTo(px,py-6); g.lineTo(px+6,py); g.lineTo(px,py+6); g.lineTo(px-6,py); g.fill();
    }
    /* legenda da previsão no canto superior direito, fora da linha */
    const lbs=[['previsão',COL.muted]].concat(PJ.cruz.filter(c=>t0+c.d*1440<=t1).map(c=>[(c.n===2?'CRÍTICO ':'ALERTA ')+fD(t0+c.d*1440), c.n===2?COL.crit:COL.warn]));
    g.textAlign='right'; g.textBaseline='top'; const tw=Math.max(...lbs.map(l=>g.measureText(l[0]).width));
    g.fillStyle=COL.surface; g.globalAlpha=.85; g.fillRect(W-R-tw-10, T+1, tw+8, lbs.length*15+4); g.globalAlpha=1;
    lbs.forEach(([t,c],j)=>{ g.fillStyle=c; g.fillText(t, W-R-4, T+3+j*15); }); g.restore(); }
  // ponto atual
  const xl=val(e,k,i1);""")
R("  $('#cv'+k).textContent = xl==null?'sem sinal':'agora '+nf(xl,cf.dec)+' '+cf.un;",
  "  $('#cv'+k).textContent = (xl==null?'sem sinal':'agora '+nf(xl,cf.dec)+' '+cf.un) + (PJ&&PJ.cruz.length ? ' · '+(PJ.cruz[0].n===2?'CRÍTICO':'ALERTA')+' previsto em '+fD(slotMin(i1)+PJ.cruz[0].d*1440) : '');")

# função de projeção (junto do diagnóstico)
R("/* ================= DIAGNÓSTICO ELEVATE", r"""/* previsão de uma variável: só quando a tendência é consistente (R² ≥ 0,5) e piorando; horizonte de 3 a 14 dias */
function projecao(e,k,i){
  const cf=V[k]; if(cf.tipo==='desvio') return null;
  const t=tendencia(e,k,i), x0=val(e,k,i); if(!t || x0==null || t.r2<0.5) return null;
  const b=t.b; if((cf.tipo==='acima' && b<=0) || (cf.tipo==='abaixo' && b>=0)) return null;
  const dLim = lim => (lim-x0)/b, cruz=[];
  [[cf.a,1],[cf.c,2]].forEach(([lim,n])=>{ const d=dLim(lim); if(d>0 && lvl(cf,x0)<n) cruz.push({n, d, y:lim}); });
  const dias=Math.min(14, Math.max(3, cruz.length ? cruz[cruz.length-1].d+1 : 7));
  const lag=(NOW-slotMin(i))/1440, fim=x0+b*(dias+lag);
  return {b, x0, dias, fim, cruz, r2:t.r2};
}

/* ================= DIAGNÓSTICO ELEVATE""")

# ---------- indicadores: critérios de sucesso ----------
R('      <div class="kpis" id="iKpis"></div>', '''      <div class="vhead"><div><h3>Critérios de sucesso combinados com a Motiva</h3><p>Tempo de escada parada, preventivas eliminadas, previsões que acertaram e homem-hora.</p></div></div>
      <div class="kpis" id="iSuc"></div>
      <div class="grid2">
        <div class="panel"><h3>Horas de escada parada por semana (corretivas)</h3><div id="iSem"></div></div>
        <div class="panel"><h3>Previsões para os próximos 7 dias</h3><div class="tbl-wrap" id="iPrev"></div></div>
      </div>
      <div class="vhead"><div><h3>Operação</h3></div></div>
      <div class="kpis" id="iKpis"></div>''')
R("  $('#iPer').textContent=", r"""  renderSucesso();
  $('#iPer').textContent=""")
R("/* ================= TELA 5: indicadores ================= */", r"""/* ================= TELA 5: indicadores ================= */
/* retroteste da previsão: em cada dia do histórico, as escadas BOM com "tendência de piora" (ALERTA previsto em até 48 h)
   realmente entraram em ALERTA ou CRÍTICO nos 3 dias seguintes? */
let BT=null;
function backtest(){
  if(BT && BT.raw===RAW && BT.idx===IDX) return BT;
  let pred=0, hit=0; const ant=[];
  for(const e of E){ for(let i=20;i<=IDX-15;i+=5){ if(e.ss[i]!==0 || e.rs[i]!==0) continue; const t=tendenciaPiora(e,i); if(!t) continue; pred++;
    for(let j=i+1;j<=i+15;j++){ if(e.ss[j]===3) break; if(e.rs[j]>=1){ hit++; ant.push((slotMin(j)-slotMin(i))/60); break; } } } }
  BT={raw:RAW, idx:IDX, pred, hit, ant:median(ant)}; return BT;
}
function renderSucesso(){
  const sum=a=>a.reduce((x,y)=>x+y,0), de30=NOW-30*1440;
  let parado30=0, hhPrev=0, hhCorr=0, hhReset=0;
  const SEM=8, sem=Array(SEM).fill(0);
  for(const e of E){ for(const a of e.atv){ if(a.ent>NOW) continue; const fim=a.sai==null||a.sai>NOW?NOW:a.sai, dur=fim-a.ent;
      if(a.tipo==='corretiva'){ parado30+=minOverlap(a.ent,fim,de30,NOW); for(let w=0;w<SEM;w++){ const w1=NOW-w*7*1440, w0=w1-7*1440; sem[SEM-1-w]+=minOverlap(a.ent,fim,w0,w1); } }
      if(a.ent>=de30){ if(a.tipo==='preventiva') hhPrev+=dur; else if(a.motivo==='parada de seguranca (reset)') hhReset+=dur; else hhCorr+=dur; } } }
  const dec=E.map(decisaoPrev).filter(Boolean), disp=dec.filter(x=>x.dec==='Dispensar').length, bt=backtest();
  let p1ok=0; E.forEach(e=>{ const p=lastP1(e); if(p!=null && (NOW-p)/1440<=CFG.p1Dias) p1ok++; });
  $('#iSuc').innerHTML=[
    ['Tempo de escada parada', nf(parado30/60,0)+' h', 'Corretivas nos últimos 30 dias · '+nf(parado30/60/E.length,1)+' h por escada'],
    ['Preventivas eliminadas', disp+' de '+dec.length, 'Dispensáveis neste ciclo pela condição · ~'+nf(disp*PREV.duracaoMin/60,0)+' h de homem-hora'],
    ['Previsões que acertaram', bt.pred?pct(bt.hit/bt.pred):'—', bt.pred?bt.hit+' de '+bt.pred+' avisos de tendência viraram ALERTA em até 3 dias (antecedência mediana de '+(bt.ant==null?'—':nf(bt.ant,0)+' h')+')':'Sem avisos de tendência no período'],
    ['Homem-hora em 30 dias', nf((hhPrev+hhCorr+hhReset)/60,0)+' h', 'Preventiva '+nf(hhPrev/60,0)+' h · corretiva '+nf(hhCorr/60,0)+' h · resets '+nf(hhReset/60,0)+' h'],
    ['P1 anual em dia', pct(p1ok/E.length), p1ok+' de '+E.length+' escadas · obrigatória, nunca eliminada'],
  ].map(([t,n,s2])=>'<div class="kpi"><span class="lbl">'+t+'</span><span class="n num">'+n+'</span><small>'+esc(s2)+'</small></div>').join('');
  /* barras semanais de horas paradas */
  const mx=Math.max(1,...sem), W=560, H=170, bw=(W-40)/SEM;
  $('#iSem').innerHTML='<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;height:auto" role="img" aria-label="Horas de escada parada por semana nas últimas 8 semanas">'+
    sem.map((v,i)=>{ const h=(H-46)*v/mx, x=20+i*bw+6, y=H-26-h; const d=dt(NOW-(SEM-1-i)*7*1440-7*1440); return '<rect x="'+x+'" y="'+y+'" width="'+(bw-12)+'" height="'+h+'" rx="4" fill="'+(i===SEM-1?'#FFD23C':'var(--line-2)')+'"/><text x="'+(x+(bw-12)/2)+'" y="'+(y-6)+'" text-anchor="middle" font-size="12" fill="var(--fg)" font-family="IBM Plex Mono, monospace">'+nf(v/60,0)+'</text><text x="'+(x+(bw-12)/2)+'" y="'+(H-8)+'" text-anchor="middle" font-size="11" fill="var(--muted)">'+pad(d.getUTCDate())+'/'+pad(d.getUTCMonth()+1)+'</text>'; }).join('')+'</svg>'+
    '<p class="hint" style="margin:0">Semana que começa no dia indicado. A barra amarela é a semana atual. Meta proposta: cair semana a semana com as preventivas por condição.</p>';
  /* previsões dos próximos 7 dias */
  const prev=[];
  for(const e of E){ const c=CUR[e.ix]; if(c.code>=2) continue;
    for(let k=0;k<V.length;k++){ const pj=projecao(e,k,IDX); if(!pj) continue; const alvo=pj.cruz.find(x=>x.n>c.code); if(!alvo) continue; const quando=slotMin(IDX)+alvo.d*1440; if(quando-NOW>7*1440) continue;
      prev.push({e, k, alvo, quando, r2:pj.r2}); } }
  prev.sort((a,b)=>a.quando-b.quando);
  $('#iPrev').innerHTML = prev.length ? '<table><thead><tr><th>Escada</th><th>Variável</th><th>Previsão</th><th>Quando</th><th>Confiança</th></tr></thead><tbody>'+
    prev.slice(0,15).map(x=>'<tr class="click" data-row="'+x.e.id+'"><td class="code">'+x.e.id+'</td><td>'+V[x.k].nome+'</td><td>'+(x.alvo.n===2?pill(2):pill(1))+'</td><td class="num">'+fD(x.quando)+' <span class="muted">(em '+fmtPrazo((x.quando-NOW)/1440).replace('cerca de ','~')+')</span></td><td>'+confi(x.r2)+'</td></tr>').join('')+'</tbody></table>'+(prev.length>15?'<p class="hint">Mostrando 15 de '+prev.length+'.</p>':'')
    : '<div class="empty">Nenhuma escada com piora prevista para os próximos 7 dias.</div>';
}
$('#iPrev') && document.addEventListener('click',ev=>{ const r=ev.target.closest('#iPrev [data-row]'); if(r) openDetalhe(r.dataset.row); });
""")
R(".kpis{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}", ".kpis{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}\n#iSuc .kpi{border-top:3px solid var(--brand)}")
R('<i class="box"></i>Em manutenção</span><span><span style="color:var(--faint)">▾</span> Sem sinal</span>',
  '<i class="box"></i>Em manutenção</span><span><i style="border-color:var(--brand);border-top-style:dashed"></i>Previsão</span><span><span style="color:var(--faint)">▾</span> Sem sinal</span>')
open(p, 'w', encoding='utf-8').write(s); print('patched v13 (previsão e indicadores)')
