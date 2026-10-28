"""Etapa 1: login com perfis (supervisor e técnico) e responsável por escada."""
p = 'template.html'; s = open(p, encoding='utf-8').read()
def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# ---------- CSS ----------
R("body.apres .techpill{display:flex}", """body.apres .techpill{display:flex}
/* ---------- login e perfis ---------- */
.techpill{display:flex}
.techpill .sair{min-height:36px;padding:4px 12px;font-size:.85rem;margin-left:4px}
body.papel-tec .sup-only{display:none!important}
.login{position:fixed;inset:0;z-index:80;background:var(--bg);overflow:auto;display:flex;justify-content:center;padding:48px var(--gut,24px)}
.login[hidden]{display:none!important}
.login-box{width:100%;max-width:980px;display:flex;flex-direction:column;gap:22px}
.login-brand{display:flex;align-items:center;gap:12px;color:var(--brand)}
.login-brand b{font-family:var(--f-display);font-size:1.6rem;letter-spacing:.08em;text-transform:uppercase;color:var(--fg)}
.login h1{font-size:2rem}
.login .lgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}
.ucard{display:flex;flex-direction:column;gap:4px;text-align:left;padding:14px 16px;border-radius:12px;border:1px solid var(--line-2);background:var(--surface);color:var(--fg);min-height:92px}
.ucard:hover{border-color:var(--brand)}
.ucard[aria-pressed="true"]{border-color:var(--brand);box-shadow:inset 0 0 0 2px var(--brand)}
.ucard b{font-size:1.02rem}
.ucard small{color:var(--muted);font-size:.82rem;line-height:1.3}
.ucard .papel{font-family:var(--f-display);font-weight:700;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--brand)}
.ucard.sup{border-color:var(--brand);background:linear-gradient(rgba(255,210,60,.08),rgba(255,210,60,.08)),var(--surface)}
.lpin{display:flex;gap:12px;align-items:flex-end;flex-wrap:wrap}
.lpin input{width:160px;font-size:1.3rem;letter-spacing:.4em;text-align:center}
.resp{font-size:.88rem;color:var(--muted)}
.resp b{color:var(--fg)}""")

# ---------- HTML: tela de login e topo ----------
R('<div class="toast" id="toast" role="status" hidden></div>', '''<div class="toast" id="toast" role="status" hidden></div>
<div class="login" id="login" hidden>
  <div class="login-box">
    <div class="login-brand"><svg width="44" height="44" viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M5 33h8v-8h8v-8h8V9h6" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M29 5h6v6" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg><b>Elevate</b></div>
    <div><h1>Entrar</h1><p class="muted" style="margin:6px 0 0">Escolha o seu usuário. O supervisor vê todas as escadas; cada técnico vê as escadas sob a responsabilidade dele.</p></div>
    <div><span class="lbl">Supervisão</span><div class="lgrid" id="lSup" style="margin-top:8px"></div></div>
    <div><span class="lbl">Técnicos de manutenção</span><div class="lgrid" id="lTec" style="margin-top:8px"></div></div>
    <div class="lpin">
      <label class="field"><span>PIN</span><input id="lPin" type="password" inputmode="numeric" maxlength="4" autocomplete="off" placeholder="····"></label>
      <button class="btn primary" id="lEntrar" disabled>Entrar</button>
      <span class="hint" id="lHint">Protótipo: o PIN de todos os usuários é 1234.</span>
    </div>
  </div>
</div>''')
R('<label class="field hide-apres"><span>Técnico no tablet</span><select id="selTec"></select></label>',
  '<label class="field" hidden><span>Técnico no tablet</span><select id="selTec"></select></label>')
R('<div class="techpill" id="techPill"><div><small>Técnico responsável</small><b id="techName">—</b></div><i id="techIni">—</i></div>',
  '<div class="techpill" id="techPill"><i id="techIni">—</i><div><small id="techPapel">Usuário</small><b id="techName">—</b></div><button class="btn sm sair" id="btnSair" title="Trocar de usuário">Sair</button></div>')
for v in ['ind', 'live', 'dados']:
    R('<button class="nav" data-view="%s">' % v, '<button class="nav sup-only" data-view="%s">' % v)

# ---------- estado ----------
R("leve:false, apres:false, modo:'real', anchor:null, demoNow:null};",
  "leve:false, apres:false, modo:'real', anchor:null, demoNow:null, login:null, resp:null};")

# ---------- regras de perfil (antes do relógio) ----------
R("/* RN-03 + RN-04 */\nfunction fila(){", """/* ================= perfis: supervisor e técnico ================= */
const SUP = {id:'S01', nome:'Ricardo Souza', cargo:'Supervisor do CCO'};
const PIN_DEMO = '1234';
const isTec = () => !!(S.login && S.login.papel==='tec');
const isSup = () => !!(S.login && S.login.papel==='sup');
const respDe = e => S.resp && S.resp[e.id];
const meu = e => !isTec() || respDe(e)===S.login.id;
/* toda escada tem um técnico: distribuição inicial em trechos seguidos da linha, equilibrando a quantidade */
function distribuicaoPadrao(){
  const ids=Object.keys(TECS), n=E.length, out={};
  E.forEach((e,i)=>{ out[e.id]=ids[Math.min(ids.length-1, Math.floor(i*ids.length/n))]; });
  return out;
}
function garantirResp(){
  const pad=distribuicaoPadrao(); S.resp=S.resp||{}; let mudou=false;
  E.forEach(e=>{ if(!S.resp[e.id] || !TECS[S.resp[e.id]]){ S.resp[e.id]=pad[e.id]; mudou=true; } });
  if(mudou) save();
}
const escadasDe = tec => E.filter(e=>S.resp[e.id]===tec);
function trechoDe(tec){
  const cods=[...new Set(escadasDe(tec).map(e=>e.cod))];
  if(!cods.length) return 'nenhuma escada';
  const nomes=cods.map(c=>ESTN[c]);
  return nomes.length===1 ? nomes[0] : nomes[0]+' a '+nomes[nomes.length-1];
}

/* RN-03 + RN-04 */
function fila(){""")
R("  return E.filter(e=>CUR[e.ix].code===1||CUR[e.ix].code===2).map(e=>{",
  "  return E.filter(e=>meu(e)&&(CUR[e.ix].code===1||CUR[e.ix].code===2)).map(e=>{")
R("  }).concat(typeof LV!=='undefined' && liveFilaItem() || []).sort(",
  "  }).concat(!isTec() && typeof LV!=='undefined' && liveFilaItem() || []).sort(")

# ---------- topo ----------
R("  const imed = E.filter(e=>CUR[e.ix].code===2&&e.crit).length + (typeof LV!=='undefined' && LV.cur && LV.cur.code===2 ? 1 : 0);\n  const bf=$('#badgeFila');",
  "  const imed = E.filter(e=>meu(e)&&CUR[e.ix].code===2&&e.crit).length + (!isTec() && typeof LV!=='undefined' && LV.cur && LV.cur.code===2 ? 1 : 0);\n  const bf=$('#badgeFila');")
R("  const op = E.filter(e=>CUR[e.ix].code===3).length;", "  const op = E.filter(e=>meu(e)&&CUR[e.ix].code===3).length;")
R("function paintTech(){ const n=TECS[S.tec]||S.tec; $('#techName').textContent=n; $('#techIni').textContent=n.split(' ').map(x=>x[0]).join('').slice(0,2); }",
  """function paintTech(){
  const L=S.login, n = !L ? '—' : L.papel==='sup' ? SUP.nome : (TECS[L.id]||L.id);
  $('#techName').textContent=n; $('#techIni').textContent=n.split(' ').map(x=>x[0]).join('').slice(0,2);
  $('#techPapel').textContent = !L ? 'Usuário' : L.papel==='sup' ? SUP.cargo : 'Técnico · '+escadasDe(L.id).length+' escadas';
  document.body.classList.toggle('papel-tec', isTec());
}""")

# ---------- painel ----------
R("""function renderPainel(){
  const n=[0,0,0,0]; CUR.forEach(c=>n[c.code]++);""", """function renderPainel(){
  const VE=E.filter(meu);
  const n=[0,0,0,0]; VE.forEach(e=>n[CUR[e.ix].code]++);""")
R("""  const nt=TEND.filter(Boolean).length, online=E.filter(e=>!V.every((_,k)=>val(e,k,IDX)==null)).length;
  $('#painelSub').textContent = E.length+' escadas rolantes da Linha 4-Amarela · '+online+' de '+E.length+' sensores respondendo. Toque em uma escada para ver o gêmeo digital, o diagnóstico e o histórico.';""",
"""  const nt=VE.filter(e=>TEND[e.ix]).length, online=VE.filter(e=>!V.every((_,k)=>val(e,k,IDX)==null)).length;
  $('#painelSub').textContent = isTec()
    ? 'Suas '+VE.length+' escadas, de '+trechoDe(S.login.id)+' · '+online+' de '+VE.length+' sensores respondendo. Toque em uma escada para ver o gêmeo digital, o diagnóstico e o procedimento.'
    : E.length+' escadas rolantes da Linha 4-Amarela · '+online+' de '+E.length+' sensores respondendo. Toque em uma escada para ver o gêmeo digital, o diagnóstico e o histórico.';
  $('#painelTit').textContent = isTec() ? 'Minhas escadas' : 'Painel da Frota';""")
R("  const imed = E.filter(e=>CUR[e.ix].code===2&&e.crit);", "  const imed = VE.filter(e=>CUR[e.ix].code===2&&e.crit);")
R("  const list = E.filter(e=>{\n    const c=CUR[e.ix];", "  const list = VE.filter(e=>{\n    const c=CUR[e.ix];")
R("""  $('#frota').innerHTML = livePainelHTML() + (html""", """  $('#frota').innerHTML = (isTec() ? '' : livePainelHTML()) + (html""")
R('<div><h2>Painel da Frota</h2><p id="painelSub">', '<div><h2 id="painelTit">Painel da Frota</h2><p id="painelSub">')

# ---------- fila: tendência só das escadas visíveis ----------
R("  const tl=E.filter(e=>TEND[e.ix]&&(!fe", "  const tl=E.filter(e=>meu(e)&&TEND[e.ix]&&(!fe")

# ---------- detalhe: responsável e bloqueio ----------
R("function openDetalhe(id){ if(id===LV.id) return show('live'); detalheId=id;",
  "function openDetalhe(id){ if(id===LV.id) return isTec() ? null : show('live'); if(isTec() && BYID[id] && !meu(BYID[id])){ toast(id+' está com '+(TECS[respDe(BYID[id])]||'outro técnico')+'. Fale com o supervisor.'); return; } detalheId=id;")
R("<span>Fluxo relativo '+nf(e.fluxo,1)+'</span></div>'+osl+'</div>'+",
  "<span>Fluxo relativo '+nf(e.fluxo,1)+'</span></div><div class=\"resp\">Responsável: <b>'+(TECS[respDe(e)]||'—')+'</b>'+(isTec()?'':' · '+(respDe(e)||''))+'</div>'+osl+'</div>'+")

# ---------- entrada do técnico: o técnico logado registra em nome próprio ----------
R("""'<label class="field"><span>Técnico</span><select id="mTec">'+Object.entries(TECS).map(([k,n])=>'<option value="'+k+'"'+(k===S.tec?' selected':'')+'>'+k+' · '+n+'</option>').join('')+'</select></label>'+""",
  """'<label class="field"><span>Técnico</span><select id="mTec"'+(isTec()?' disabled':'')+'>'+Object.entries(TECS).map(([k,n])=>'<option value="'+k+'"'+(k===(isTec()?S.login.id:(respDe(e)||S.tec))?' selected':'')+'>'+k+' · '+n+'</option>').join('')+'</select></label>'+""")

# ---------- atendimentos: técnico vê só os próprios ----------
R("  const oss=[...(S.os||[])].reverse();", "  const oss=[...(S.os||[])].filter(o=>!isTec()||o.tec===S.login.id).reverse();")
R("  const open=[]; E.forEach(e=>{ const a=openAt(e); if(a) open.push({e,a}); });",
  "  const open=[]; E.forEach(e=>{ const a=openAt(e); if(a && (!isTec()||a.tec===S.login.id)) open.push({e,a}); });")
R("  const mine=[...S.user.filter(a=>a.ent<=NOW), ...Object.keys(S.ov).map(id=>DSAT[id]).filter(Boolean)].sort(",
  "  const mine=[...S.user.filter(a=>a.ent<=NOW), ...Object.keys(S.ov).map(id=>DSAT[id]).filter(Boolean)].filter(a=>!isTec()||a.tec===S.login.id).sort(")

# ---------- telas proibidas para o técnico ----------
R("function show(v){\n", "function show(v){\n  if(isTec() && ['ind','dados','live'].includes(v)) v='painel';\n")

# ---------- login ----------
R("computeCurrent(); paintModo(); paintClock(); paintApres(); show('painel');", """/* ================= tela de login ================= */
let loginSel=null;
function renderLogin(){
  garantirResp();
  $('#lSup').innerHTML='<button class="ucard sup" data-u="sup|'+SUP.id+'" aria-pressed="'+(loginSel==='sup|'+SUP.id)+'"><span class="papel">Supervisor</span><b>'+SUP.nome+'</b><small>'+SUP.cargo+' · todas as '+E.length+' escadas</small></button>';
  $('#lTec').innerHTML=Object.entries(TECS).map(([k,n])=>'<button class="ucard" data-u="tec|'+k+'" aria-pressed="'+(loginSel==='tec|'+k)+'"><span class="papel">Técnico · '+k+'</span><b>'+n+'</b><small>'+escadasDe(k).length+' escadas · '+esc(trechoDe(k))+'</small></button>').join('');
  $('#lEntrar').disabled=!loginSel;
}
function abrirLogin(){ loginSel=null; $('#lPin').value=''; $('#lHint').textContent='Protótipo: o PIN de todos os usuários é 1234.'; $('#lHint').style.color=''; renderLogin(); $('#login').hidden=false; }
function entrar(){
  if(!loginSel) return;
  if($('#lPin').value!==PIN_DEMO){ $('#lHint').textContent='PIN incorreto. No protótipo, o PIN é 1234.'; $('#lHint').style.color='var(--crit)'; $('#lPin').focus(); return; }
  const [papel,id]=loginSel.split('|'); S.login={papel,id,em:Date.now()}; if(papel==='tec') S.tec=id; save();
  $('#login').hidden=true; Object.assign(filt,{status:null,busca:'',est:'',grupo:'',fab:''});
  paintTech(); show('painel'); toast(papel==='sup' ? 'Bem-vindo, '+SUP.nome+'. Você vê todas as escadas.' : 'Bem-vindo, '+TECS[id]+'. Você vê as suas '+escadasDe(id).length+' escadas.');
}
['#lSup','#lTec'].forEach(q=>$(q).addEventListener('click',ev=>{ const b=ev.target.closest('[data-u]'); if(!b) return; loginSel=b.dataset.u; renderLogin(); $('#lPin').focus(); }));
$('#lEntrar').onclick=entrar;
$('#lPin').addEventListener('keydown',ev=>{ if(ev.key==='Enter') entrar(); });
$('#lPin').addEventListener('input',()=>{ if($('#lPin').value.length===4 && loginSel) entrar(); });
$('#btnSair').onclick=()=>{ S.login=null; save(); document.body.classList.remove('papel-tec'); abrirLogin(); };
garantirResp();

computeCurrent(); paintModo(); paintClock(); paintApres(); show('painel');
if(!S.login) abrirLogin();""")

open(p, 'w', encoding='utf-8').write(s); print('patched v6 (login e perfis)')
