"""Revisão pós-Sprint Review 1 (parte 1): perfis gestão/supervisor/técnico, equipe por estação,
P1 anual e rota reposicionada para apoio em emergência."""
p = 'template.html'; s = open(p, encoding='utf-8').read()
def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)
def RB(ini, fim, novo):
    """troca o trecho que começa em `ini` (incluso) e termina antes de `fim`"""
    global s
    assert s.count(ini) == 1 and s.count(fim) >= 1, (s.count(ini), s.count(fim), ini[:60], fim[:60])
    i = s.index(ini); j = s.index(fim, i); s = s[:i] + novo + s[j:]

# ---------------- pessoas ----------------
R("const TECS = {T01:'Marcos Lima'", "const TECS = {T13:'Bruno Carvalho',T14:'Juliana Prado',T15:'André Santos',T16:'Larissa Moura',T17:'Felipe Araújo',T18:'Renata Dias',T19:'Gustavo Teixeira',T20:'Aline Castro',T21:'Rodrigo Pinto',T22:'Vanessa Lopes',T23:'Eduardo Ramos',T24:'Priscila Duarte', T01:'Marcos Lima'")

# ---------------- P1 anual ----------------
R("  p1Dias: 30,\n  p1AvisoDias: 3,", "  p1Dias: 365,     /* P1: exigida anualmente pelo órgão fiscalizador */\n  p1AvisoDias: 30,")
R("const MOT_L = {'P1 mensal':'Preventiva P1 mensal',", "const MOT_L = {'P1 anual':'P1 anual (órgão fiscalizador)','P1 mensal':'Preventiva mensal (plano)',")
R("const MOTIVOS_FORM = ['status critico','parada de seguranca (reset)','sem resposta do sensor','alerta prolongado','P1 mensal'];",
  "const MOTIVOS_FORM = ['status critico','parada de seguranca (reset)','sem resposta do sensor','alerta prolongado','P1 mensal','P1 anual'];")
R("const lastP1 = e => { let m=null; for(const a of e.atv){ if(a.motivo==='P1 mensal' && a.ent<=NOW && (m==null||a.ent>m)) m=a.ent; } return m; };",
  """/* P1 anual: o dataset traz as preventivas mensais do plano; a data da última P1 anual de cada escada é
   simulada (espalhada nos últimos 12 meses) até a Motiva enviar o histórico real. Um registro 'P1 anual' feito no tablet vale por cima. */
const hashId = t => { let h=2166136261; for(const ch of t){ h^=ch.charCodeAt(0); h=Math.imul(h,16777619); } return h>>>0; };
const p1Simulada = e => (NS/5-1)*1440 - (hashId(e.id)%355 + 5)*1440 + 22*60;
const lastP1 = e => { let m=p1Simulada(e); for(const a of e.atv){ if(a.motivo==='P1 anual' && a.ent<=NOW && a.ent>m) m=a.ent; } return m<=NOW ? m : null; };""")
R("""  const p1=lastP1(e); const dias = p1==null ? null : (NOW-p1)/1440; const late = p1==null ? NOW>CFG.p1Dias*1440 : dias>CFG.p1Dias;
  $('#dP1').innerHTML = '<h3>Preventiva P1 mensal</h3><div class="p1big num'+(late?' late':'')+'">'+(p1==null?'—':Math.floor(dias)+' dias')+'</div><div class="muted">'+(p1==null?'Nenhuma P1 registrada desde '+fD(0)+'.':'desde a última P1, em '+fDH(p1)+'.')+'</div>'+
    (late?'<div>'+pill(2,'P1 ATRASADA')+'</div>':'<div>'+pill(0,'EM DIA')+'</div>')+'<p class="hint" style="margin:0">A P1 é exigência legal e continua obrigatória a cada '+CFG.p1Dias+' dias, mesmo com o monitoramento.</p>';""",
"""  const p1=lastP1(e); const dias = p1==null ? null : (NOW-p1)/1440; const falta = dias==null ? null : CFG.p1Dias-dias; const late = falta!=null && falta<0, perto = falta!=null && falta>=0 && falta<=CFG.p1AvisoDias;
  const dP=dt(p1==null?0:p1), dataP1 = p1==null ? '—' : pad(dP.getUTCDate())+'/'+pad(dP.getUTCMonth()+1)+'/'+dP.getUTCFullYear();
  $('#dP1').innerHTML = '<h3>P1 anual</h3><div class="p1big num'+(late?' late':'')+'">'+(falta==null?'—':late?Math.ceil(-falta)+' dias de atraso':Math.floor(falta)+' dias')+'</div><div class="muted">'+(p1==null?'Sem P1 registrada.':(late?'vencida':'para vencer')+' · última P1 em '+dataP1+'.')+'</div>'+
    (late?'<div>'+pill(2,'P1 ATRASADA')+'</div>':perto?'<div>'+pill(1,'P1 VENCE EM BREVE')+'</div>':'<div>'+pill(0,'EM DIA')+'</div>')+'<p class="hint" style="margin:0">A P1 é exigida anualmente pelo órgão fiscalizador e não pode ser eliminada pelo CBM. Data da última P1 simulada até recebermos o histórico real.</p>';""")
R("    ['Preventiva P1 em dia', pct(p1ok/E.length), p1ok+' de '+E.length+' escadas com P1 nos últimos '+CFG.p1Dias+' dias'],",
  "    ['P1 anual em dia', pct(p1ok/E.length), p1ok+' de '+E.length+' escadas com P1 nos últimos 12 meses'],")

# ---------------- perfis e equipes ----------------
RB("/* ================= perfis: supervisor e técnico ================= */", "\n/* RN-03 + RN-04 */", r"""/* ================= perfis: gestão da engenharia, supervisor da estação e técnico =================
   Cada estação da Linha 4 tem uma equipe dedicada (2 técnicos por enquanto) e um supervisor. */
const GES = {id:'G01', nome:'Juliana Alves', cargo:'Gestão da engenharia de manutenção'};
const SUPS = {S01:['LUZ','Ricardo Souza'],S02:['REP','Sandra Vieira'],S03:['HIG','Paulo Henrique'],S04:['PTA','Mônica Freitas'],S05:['FRE','Carlos Eduardo'],S06:['FRA','Tatiane Rocha'],
  S07:['FAL','Márcio Nogueira'],S08:['PIN','Cláudia Ramos'],S09:['BUT','Roberto Lima'],S10:['MBI','Elaine Cardoso'],S11:['VSO','Fábio Moreira'],S12:['TVS','Natália Pires']};
const SUP = {id:'S01', nome:'Ricardo Souza', cargo:'Supervisor'};   /* compatibilidade */
const PIN_DEMO = '1234';
const isTec = () => !!(S.login && S.login.papel==='tec');
const isGes = () => !!(S.login && S.login.papel==='ges');
const isSup = () => !!(S.login && (S.login.papel==='sup' || S.login.papel==='ges'));   /* gestão ou supervisor */
function equipesPadrao(){ const ids=['T01','T02','T03','T04','T05','T06','T07','T08','T09','T10','T11','T12','T13','T14','T15','T16','T17','T18','T19','T20','T21','T22','T23','T24'], o={}; EST.forEach((st,i)=>o[st.cod]=ids.slice(2*i,2*i+2)); return o; }
function garantirResp(){
  const pad=equipesPadrao(); S.equipes=S.equipes||{}; let ok=true;
  const todos=Object.values(S.equipes).flat(); if(todos.length!==24 || new Set(todos).size!==24 || EST.some(st=>!S.equipes[st.cod])) ok=false;
  if(!ok){ S.equipes=pad; save(); }
}
const equipeDe = cod => (S.equipes && S.equipes[cod]) || [];
const estDoTec = tec => EST.map(x=>x.cod).find(c=>equipeDe(c).includes(tec)) || null;
const escopoEst = () => !S.login ? null : S.login.papel==='ges' ? null : S.login.papel==='sup' ? (SUPS[S.login.id]||[])[0] : estDoTec(S.login.id);
const meu = e => !escopoEst() || e.cod===escopoEst();
const respDe = e => equipeDe(e.cod)[0];
const nomeEquipe = cod => equipeDe(cod).map(t=>TECS[t]).join(' e ') || '—';
const escadasDe = tec => E.filter(e=>e.cod===estDoTec(tec));
const trechoDe = tec => ESTN[estDoTec(tec)] || 'sem estação';
const supDe = cod => Object.entries(SUPS).find(([k,v])=>v[0]===cod);
/* técnico ocupado = tem atendimento aberto agora */
const ocupado = tec => { for(const e of E){ const a=openAt(e); if(a && a.tec===tec) return e; } return null; };
""")
RB("function fillEstFiltro(){", "function paintApres(){", r"""function fillEstFiltro(){
  const esc0=escopoEst(), cods = esc0 ? [esc0] : EST.map(x=>x.cod);
  const op='<option value="">Todas</option>'+EST.filter(x=>cods.includes(x.cod)).map(x=>'<option value="'+x.cod+'">'+x.cod+' · '+esc(x.nome)+'</option>').join('');
  [fEst,qEst].forEach(sel=>{ const v=sel.value; sel.innerHTML=op; sel.value=cods.includes(v)?v:''; });
  if(filt.est && !cods.includes(filt.est)) filt.est='';
}
function paintTech(){
  const L=S.login, n = !L ? '—' : L.papel==='ges' ? GES.nome : L.papel==='sup' ? (SUPS[L.id]||[])[1] : (TECS[L.id]||L.id);
  $('#techName').textContent=n; $('#techIni').textContent=String(n).split(' ').map(x=>x[0]).join('').slice(0,2);
  $('#techPapel').textContent = !L ? 'Usuário' : L.papel==='ges' ? GES.cargo : L.papel==='sup' ? 'Supervisor · '+ESTN[(SUPS[L.id]||[])[0]] : 'Técnico · '+(ESTN[estDoTec(L.id)]||'');
  document.body.classList.toggle('papel-tec', isTec()); document.body.classList.toggle('papel-ges', isGes());
  if(typeof fEst!=='undefined') fillEstFiltro();
}
""")

# ---------------- visibilidade ----------------
R("body.papel-tec .sup-only{display:none!important}", "body.papel-tec .sup-only{display:none!important}\nbody:not(.papel-ges) .ges-only{display:none!important}")
for v in ['ind', 'live', 'dados']:
    R('<button class="nav sup-only" data-view="%s">' % v, '<button class="nav ges-only" data-view="%s">' % v)
R('<button class="nav" data-view="rota">', '<button class="nav sup-only" data-view="rota">')
R("  if(isTec() && ['ind','dados','live','equipe','foco'].includes(v)) v='painel';",
  "  if(isTec() && ['ind','dados','live','equipe','foco','rota'].includes(v)) v='painel';\n  if(!isGes() && ['ind','dados','live'].includes(v)) v='painel';")
R("  }).concat(!isTec() && typeof LV!=='undefined' && liveFilaItem() || []).sort(", "  }).concat(isGes() && typeof LV!=='undefined' && liveFilaItem() || []).sort(")
R("+ (!isTec() && typeof LV!=='undefined' && LV.", "+ (isGes() && typeof LV!=='undefined' && LV.")
R("  $('#frota').innerHTML = (isTec() ? '' : livePainelHTML()) + (html", "  $('#frota').innerHTML = (isGes() ? livePainelHTML() : '') + (html")
R("function openDetalhe(id){ if(id===LV.id) return isTec() ? null : show('live'); if(isTec() && BYID[id] && !meu(BYID[id])){ toast(id+' está com '+(TECS[respDe(BYID[id])]||'outro técnico')+'. Fale com o supervisor.'); return; }",
  "function openDetalhe(id){ if(id===LV.id) return isGes() ? show('live') : null; if(BYID[id] && !meu(BYID[id])){ toast(id+' é da estação '+ESTN[BYID[id].cod]+' (equipe: '+nomeEquipe(BYID[id].cod)+').'); return; }")

# ---------------- painel ----------------
R("""  $('#painelSub').textContent = isTec()
    ? 'Suas '+VE.length+' escadas, de '+trechoDe(S.login.id)+' · '+online+' de '+VE.length+' sensores respondendo. Toque em uma escada para ver o gêmeo digital, o diagnóstico e o procedimento.'
    : E.length+' escadas rolantes da Linha 4-Amarela · '+online+' de '+E.length+' sensores respondendo. Toque em uma escada para ver o gêmeo digital, o diagnóstico e o histórico.';
  $('#painelTit').textContent = isTec() ? 'Minhas escadas' : 'Painel da Frota';""",
"""  const est0=escopoEst();
  $('#painelSub').textContent = est0
    ? VE.length+' escadas da estação '+ESTN[est0]+' · equipe: '+nomeEquipe(est0)+' · '+online+' de '+VE.length+' sensores respondendo.'
    : E.length+' escadas rolantes da Linha 4-Amarela, 12 estações · '+online+' de '+E.length+' sensores respondendo. Toque em uma escada para ver o diagnóstico e o histórico.';
  $('#painelTit').textContent = est0 ? 'Estação '+ESTN[est0] : 'Painel da Frota';""")

# ---------------- detalhe, fila, atendimentos ----------------
R("""<div class="resp">Responsável: <b>'+(TECS[respDe(e)]||'—')+'</b>'+(isTec()?'':' · '+(respDe(e)||''))+'</div>""",
  """<div class="resp">Equipe da estação: <b>'+esc(nomeEquipe(e.cod))+'</b>'+(supDe(e.cod)?' · supervisor '+esc(supDe(e.cod)[1][1]):'')+'</div>""")
R("""(isSup()&&!x.e.live&&respDe(x.e)?'<br>Resp.: '+esc(TECS[respDe(x.e)]):'')""", """(isGes()&&!x.e.live?'<br>Equipe: '+esc(nomeEquipe(x.e.cod)):'')""")
R("  const oss=[...(S.os||[])].filter(o=>!isTec()||o.tec===S.login.id).reverse();", "  const oss=[...(S.os||[])].filter(o=>!BYID[o.esc]||meu(BYID[o.esc])).reverse();")
R("  const open=[]; E.forEach(e=>{ const a=openAt(e); if(a && (!isTec()||a.tec===S.login.id)) open.push({e,a}); });",
  "  const open=[]; E.forEach(e=>{ const a=openAt(e); if(a && meu(e)) open.push({e,a}); });")
R(".filter(a=>!isTec()||a.tec===S.login.id).sort(", ".filter(a=>!BYID[a.esc]||meu(BYID[a.esc])).sort(")

# ---------------- foco: escopo e textos ----------------
R("  const all=E.map(e=>{ const f=focoEscada(e,dias), c=f.c; if(c.code===3) return null;", "  const all=E.filter(meu).map(e=>{ const f=focoEscada(e,dias), c=f.c; if(c.code===3) return null;")
R("""'. Confirme se o técnico responsável ('+(TECS[respDe(f.e)]||'—')+') já está a caminho.'""", """'. Confirme se a equipe da estação ('+nomeEquipe(f.e.cod)+') já está a caminho; se estiver ocupada, use Apoio em emergência.'""")
R("+' · '+esc(TECS[respDe(f.e)]||'—')+'</div></div>'+", "+' · equipe '+esc(nomeEquipe(f.e.cod))+'</div></div>'+")

# ---------------- rota → apoio em emergência ----------------
RB('    <section class="view" id="v-rota" hidden aria-label="Rota do turno">', '    <!-- TELA 3 -->', """    <section class="view" id="v-rota" hidden aria-label="Apoio em emergência">
      <div class="vhead"><div><h2>Apoio em emergência</h2><p>Quando a equipe da estação está ocupada, qual equipe chega primeiro pela Linha 4. Menor caminho calculado pelo algoritmo de Dijkstra.</p></div></div>
      <div class="rt-tools">
        <label class="field"><span>Escada com problema</span><select id="emEsc"></select></label>
      </div>
      <div class="fc-rec" id="emRec"></div>
      <div class="rt-map" id="rtMapa"></div>
      <div class="stack" style="gap:8px" id="rtLista"></div>
      <p class="rt-note" id="rtNota"></p>
    </section>

""")
RB("function renderRota(){", "/* ================= FOCO DO SUPERVISOR", r"""let emSel=null;
function mapaEmerg(origem, alvo, via){
  const n=EST.length, W=1000, x0=24, dx=(W-x0*2)/n, Y=60, xs=i=>x0+dx*i+dx/2, P=c=>xs(POS(c));
  let g='<line x1="'+xs(0)+'" y1="'+Y+'" x2="'+xs(n-1)+'" y2="'+Y+'" stroke="#FFD23C" stroke-width="8" stroke-linecap="round"/>';
  if(origem && origem!==alvo){ g+='<path d="M'+P(origem)+' '+(Y-8)+' L'+P(origem)+' '+(Y-26)+' L'+P(alvo)+' '+(Y-26)+' L'+P(alvo)+' '+(Y-8)+'" fill="none" stroke="var(--fg)" stroke-width="2.5" marker-end="url(#emA)"/>'; }
  EST.forEach((st,i)=>{ const isA=st.cod===alvo, isO=st.cod===origem;
    g+='<circle cx="'+xs(i)+'" cy="'+Y+'" r="'+(isA||isO?11:7)+'" fill="'+(isA?'var(--crit)':isO?'var(--brand)':'var(--surface)')+'" stroke="'+(isA?'var(--crit)':isO?'var(--brand)':'var(--fg)')+'" stroke-width="2.5"/>'+
      '<text x="'+xs(i)+'" y="'+(Y+30)+'" text-anchor="middle" font-size="12" font-weight="'+(isA||isO?700:500)+'" fill="'+(isA||isO?'var(--fg)':'var(--muted)')+'">'+st.cod+'</text>'+
      (isA?'<text x="'+xs(i)+'" y="'+(Y+46)+'" text-anchor="middle" font-size="10.5" fill="var(--crit)">ocorrência</text>':isO&&origem!==alvo?'<text x="'+xs(i)+'" y="'+(Y+46)+'" text-anchor="middle" font-size="10.5" fill="var(--brand)">apoio</text>':''); });
  return '<svg viewBox="0 0 '+W+' 112" role="img" aria-label="Linha 4 com a estação da ocorrência e a equipe de apoio"><defs><marker id="emA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="var(--fg)"/></marker></defs>'+g+'</svg>';
}
function renderRota(){
  if(isTec()) return show('painel');
  computeCurrent();
  const cand=fila().filter(x=>!x.e.live).map(x=>x.e);
  const sel=$('#emEsc');
  sel.innerHTML = cand.length ? cand.map(e=>'<option value="'+e.id+'">'+e.id+' · '+esc(ESTN[e.cod])+' · '+STL[CUR[e.ix].code]+' · '+esc(CUR[e.ix].txt)+'</option>').join('') : '<option value="">Nenhuma escada em ALERTA ou CRÍTICO</option>';
  if(!emSel || !cand.some(e=>e.id===emSel)) emSel = cand.length ? cand[0].id : null;
  if(emSel) sel.value=emSel;
  if(!emSel){ $('#emRec').innerHTML='<p>Nenhuma ocorrência em ALERTA ou CRÍTICO'+(escopoEst()?' na sua estação':'')+' agora.</p>'; $('#rtMapa').innerHTML=mapaEmerg(null,escopoEst()||'PIN'); $('#rtLista').innerHTML=''; $('#rtNota').textContent=''; return; }
  const e=BYID[emSel], alvo=e.cod;
  const ops=EST.map(st=>{ const r=rotaEntre(st.cod,alvo), tecs=equipeDe(st.cod).map(t=>({t, oc:ocupado(t)})), livres=tecs.filter(x=>!x.oc);
    return {cod:st.cod, min:r.min+tempoInterno(alvo), viagem:r.min, via:r.via, tecs, livres:livres.length}; })
    .sort((a,b)=>(b.livres>0)-(a.livres>0) || a.min-b.min);
  const melhor=ops[0], propria=ops.find(o=>o.cod===alvo);
  $('#emRec').innerHTML = '<span class="n">Recomendação</span><b>'+(melhor.cod===alvo?'Equipe da própria estação ('+esc(ESTN[alvo])+')':'Acionar a equipe de '+esc(ESTN[melhor.cod]))+'</b>'+
    '<p>'+(melhor.cod===alvo ? 'A equipe de '+esc(ESTN[alvo])+' tem '+melhor.livres+' técnico'+(melhor.livres>1?'s':'')+' livre'+(melhor.livres>1?'s':'')+': chega em cerca de '+Math.round(melhor.min)+' min.'
      : 'A equipe de '+esc(ESTN[alvo])+' está ocupada'+(propria.tecs.filter(x=>x.oc).length?' ('+propria.tecs.filter(x=>x.oc).map(x=>TECS[x.t]+' em '+x.oc.id).join(', ')+')':'')+'. A equipe de '+esc(ESTN[melhor.cod])+' chega em cerca de '+Math.round(melhor.min)+' min: '+melhor.via.map(NOME_NO).join(' → ')+'.')+'</p>';
  $('#rtMapa').innerHTML = mapaEmerg(melhor.cod, alvo, melhor.via);
  $('#rtLista').innerHTML = ops.slice(0,6).map((o,i)=>'<div class="rt-stop'+(o.livres?'':' fora')+'"><div class="rt-num">'+(i+1)+'</div><div><div class="rt-h"><b>Equipe '+esc(ESTN[o.cod])+'</b><span class="mono">~'+Math.round(o.min)+' min</span><span class="muted">'+(o.livres?o.livres+' de '+o.tecs.length+' livres':'todos ocupados')+'</span></div>'+
    '<div class="rt-via">'+o.tecs.map(x=>esc(TECS[x.t])+(x.oc?' (em atendimento em '+x.oc.id+')':' (livre)')).join(' · ')+'</div>'+
    (o.cod!==alvo?'<div class="rt-via">Caminho: '+o.via.map(NOME_NO).join(' → ')+' · '+o.viagem+' min de viagem + '+nf(tempoInterno(alvo),1)+' min dentro da estação</div>':'<div class="rt-via">Já está na estação · '+nf(tempoInterno(alvo),1)+' min até a escada</div>')+'</div></div>').join('');
  $('#rtNota').textContent = 'Tempos estimados pelo grupo, a confirmar com a Motiva: 2 a 3 min entre estações e 1 min + 15 s por escada dentro da estação. A equipe da estação vem primeiro sempre que tiver alguém livre.';
}
$('#emEsc').onchange=e=>{ emSel=e.target.value; renderRota(); };

""")

# ---------------- equipe por estação ----------------
RB('    <section class="view" id="v-equipe" hidden aria-label="Equipe">', '    <section class="view" id="v-ind"', """    <section class="view" id="v-equipe" hidden aria-label="Equipes">
      <div class="vhead"><div><h2>Equipes por estação</h2><p id="eqSub">Cada estação da Linha 4 tem um supervisor e uma equipe dedicada de manutenção (2 técnicos por enquanto).</p></div></div>
      <div class="tec-cards" id="eqTec"></div>
    </section>

""")
RB("/* ================= TELA: equipe e responsáveis (supervisor) ================= */", "/* ================= tela de login ================= */", r"""/* ================= TELA: equipes por estação ================= */
function renderEquipe(){
  if(!isSup()) return show('painel');
  computeCurrent();
  const est0=escopoEst(), lista = est0 ? [EST.find(x=>x.cod===est0), ...EST.filter(x=>x.cod!==est0)] : EST;
  $('#eqSub').textContent = 'Cada estação tem um supervisor e uma equipe dedicada (2 técnicos por enquanto).'+(isGes()?' A gestão pode mover um técnico para outra estação, por exemplo para cobrir férias.':' Para pedir apoio de outra estação, use Apoio em emergência.');
  $('#eqTec').innerHTML = lista.map(st=>{
    const es=E.filter(e=>e.cod===st.cod), m=[0,0,0,0]; es.forEach(e=>m[CUR[e.ix].code]++); const sp=supDe(st.cod);
    return '<div class="tcard"'+(st.cod===est0?' aria-pressed="true"':'')+'><div class="tn"><b>'+esc(st.nome)+'</b><span class="muted mono" style="font-size:.8rem">'+st.cod+'</span></div>'+
      '<div class="mini"><span>'+es.length+' escadas · '+es.filter(e=>e.crit).length+' do grupo crítica</span>'+(m[2]?'<b style="color:var(--crit)">'+m[2]+' crítico</b>':'')+(m[1]?'<b style="color:var(--warn)">'+m[1]+' alerta</b>':'')+(m[3]?'<b style="color:var(--maint)">'+m[3]+' em manutenção</b>':'')+'</div>'+
      '<div class="mini"><span>Supervisor: <b style="color:var(--fg)">'+(sp?esc(sp[1][1]):'—')+'</b></span></div>'+
      equipeDe(st.cod).map(t=>{ const oc=ocupado(t); return '<div class="mini" style="align-items:center;justify-content:space-between"><span style="color:var(--fg)">'+esc(TECS[t])+' <span class="muted mono">'+t+'</span></span>'+(oc?'<b style="color:var(--maint)">em atendimento · '+oc.id+'</b>':'<span style="color:var(--ok)">livre</span>')+
        (isGes()?'<select data-mover="'+t+'" aria-label="Mover '+esc(TECS[t])+' para outra estação" style="min-height:34px;font-size:.82rem">'+EST.map(x=>'<option value="'+x.cod+'"'+(x.cod===st.cod?' selected':'')+'>'+x.cod+'</option>').join('')+'</select>':'')+'</div>'; }).join('')+
      (equipeDe(st.cod).length<2?'<div class="mini"><b style="color:var(--crit)">Equipe abaixo do mínimo de 2 técnicos</b></div>':'')+'</div>';
  }).join('');
}
$('#eqTec').addEventListener('change',ev=>{ const s2=ev.target.closest('[data-mover]'); if(!s2||!isGes()) return; const t=s2.dataset.mover, de=estDoTec(t), para=s2.value; if(de===para) return;
  S.equipes[de]=S.equipes[de].filter(x=>x!==t); S.equipes[para]=[...S.equipes[para], t]; logEv('Técnico '+t+' → '+para,{id:'Q-'+t, esc:para}); save(); renderEquipe();
  toast(TECS[t]+' passou de '+ESTN[de]+' para '+ESTN[para]+'.'+(S.equipes[de].length<2?' Atenção: '+ESTN[de]+' ficou com menos de 2 técnicos.':''), 5000); });

""")

# ---------------- login ----------------
R('    <div><span class="lbl">Supervisão</span><div class="lgrid" id="lSup" style="margin-top:8px"></div></div>',
  '    <div><span class="lbl">Gestão da engenharia</span><div class="lgrid" id="lGes" style="margin-top:8px"></div></div>\n    <div><span class="lbl">Supervisores de estação</span><div class="lgrid" id="lSup" style="margin-top:8px"></div></div>')
R('<p class="muted" style="margin:6px 0 0">Escolha o seu usuário. O supervisor vê todas as escadas; cada técnico vê as escadas sob a responsabilidade dele.</p>',
  '<p class="muted" style="margin:6px 0 0">Escolha o seu usuário. A gestão vê a linha toda; o supervisor e os técnicos veem a estação deles.</p>')
R("""  $('#lSup').innerHTML='<button class="ucard sup" data-u="sup|'+SUP.id+'" aria-pressed="'+(loginSel==='sup|'+SUP.id)+'"><span class="papel">Supervisor</span><b>'+SUP.nome+'</b><small>'+SUP.cargo+' · todas as '+E.length+' escadas</small></button>';
  $('#lTec').innerHTML=Object.entries(TECS).map(([k,n])=>'<button class="ucard" data-u="tec|'+k+'" aria-pressed="'+(loginSel==='tec|'+k)+'"><span class="papel">Técnico · '+k+'</span><b>'+n+'</b><small>'+escadasDe(k).length+' escadas · '+esc(trechoDe(k))+'</small></button>').join('');""",
"""  $('#lGes').innerHTML='<button class="ucard sup" data-u="ges|'+GES.id+'" aria-pressed="'+(loginSel==='ges|'+GES.id)+'"><span class="papel">Gestão</span><b>'+GES.nome+'</b><small>'+GES.cargo+' · as 12 estações, '+E.length+' escadas</small></button>';
  $('#lSup').innerHTML=Object.entries(SUPS).map(([k,[cod,n]])=>'<button class="ucard" data-u="sup|'+k+'" aria-pressed="'+(loginSel==='sup|'+k)+'"><span class="papel">Supervisor · '+cod+'</span><b>'+esc(n)+'</b><small>'+esc(ESTN[cod])+' · '+E.filter(e=>e.cod===cod).length+' escadas</small></button>').join('');
  $('#lTec').innerHTML=EST.map(st=>equipeDe(st.cod).map(k=>'<button class="ucard" data-u="tec|'+k+'" aria-pressed="'+(loginSel==='tec|'+k)+'"><span class="papel">Técnico · '+st.cod+'</span><b>'+esc(TECS[k])+'</b><small>'+esc(st.nome)+' · '+E.filter(e=>e.cod===st.cod).length+' escadas</small></button>').join('')).join('');""")
R("""  paintTech(); show('painel'); toast(papel==='sup' ? 'Bem-vindo, '+SUP.nome+'. Você vê todas as escadas.' : 'Bem-vindo, '+TECS[id]+'. Você vê as suas '+escadasDe(id).length+' escadas.');""",
  """  paintTech(); show('painel'); toast(papel==='ges' ? 'Bem-vinda, '+GES.nome+'. Você vê as 12 estações.' : 'Bem-vindo(a), '+(papel==='sup'?SUPS[id][1]:TECS[id])+'. Você vê a estação '+ESTN[escopoEst()]+'.');""")
R("['#lSup','#lTec'].forEach(q=>", "['#lGes','#lSup','#lTec'].forEach(q=>")
R(".lgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}", ".lgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:8px}")
R("""$('#btnSair').onclick=()=>{ S.login=null; save(); document.body.classList.remove('papel-tec'); abrirLogin(); };""",
  """$('#btnSair').onclick=()=>{ S.login=null; save(); document.body.classList.remove('papel-tec','papel-ges'); abrirLogin(); };
if(S.login && S.login.papel==='sup' && !SUPS[S.login.id]) S.login=null;   /* login salvo da versão anterior */""")

open(p, 'w', encoding='utf-8').write(s); print('patched v11 (Motiva: perfis, equipes, P1 anual, emergência)')
