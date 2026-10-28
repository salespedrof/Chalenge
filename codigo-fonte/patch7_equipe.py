"""Etapa 2: o supervisor distribui as escadas entre os técnicos (tela Equipe)."""
p = 'template.html'; s = open(p, encoding='utf-8').read()
def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# ---------- CSS ----------
R(".resp{font-size:.88rem;color:var(--muted)}", """.resp{font-size:.88rem;color:var(--muted)}
.tec-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.tcard{display:flex;flex-direction:column;gap:6px;text-align:left;padding:12px 14px;border-radius:12px;border:1px solid var(--line);background:var(--surface);color:var(--fg)}
.tcard[aria-pressed="true"]{border-color:var(--brand);box-shadow:inset 0 0 0 2px var(--brand)}
.tcard .tn{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.tcard .tn b{font-size:1rem}
.tcard .big{font-family:var(--f-display);font-size:1.6rem;font-weight:700;line-height:1}
.tcard .mini{display:flex;gap:10px;flex-wrap:wrap;font-size:.8rem;color:var(--muted)}
.eq-tools{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end}
.eq-st{display:flex;flex-direction:column;gap:8px}
.eq-st-h{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:6px}
.eq-st-h h3 span{font-family:var(--f-mono);font-size:.85rem;color:var(--muted);margin-right:8px}
.eq-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px}
.eq-row{display:flex;flex-direction:column;gap:6px;padding:10px 12px;border-radius:10px;border:1px solid var(--line);border-left:3px solid var(--c);background:var(--surface)}
.eq-row.s0{border-left-color:var(--line-2)}
.eq-row .top{display:flex;justify-content:space-between;align-items:center;gap:6px}
.eq-row select{min-height:40px;font-size:.9rem}
.eq-row.mudou{box-shadow:0 0 0 2px var(--brand)}""")

# ---------- navegação e tela ----------
R('<button class="nav sup-only" data-view="ind">', '''<button class="nav sup-only" data-view="equipe"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17.5" cy="9" r="2.5"/><path d="M16 14.2c2.9.3 5 2.6 5 5.8"/></svg>Equipe</button>
    <button class="nav sup-only" data-view="ind">''')
R('    <section class="view" id="v-ind" hidden aria-label="Indicadores">', '''    <section class="view" id="v-equipe" hidden aria-label="Equipe">
      <div class="vhead"><div><h2>Equipe e responsáveis</h2><p>Cada escada tem sempre um técnico responsável. O técnico vê no painel e na fila só as escadas dele. Toque num técnico para ver as escadas dele.</p></div></div>
      <div class="tec-cards" id="eqTec"></div>
      <div class="eq-tools">
        <label class="field"><span>Estação</span><select id="eqEst"></select></label>
        <label class="field"><span>Mostrar</span><select id="eqFiltro"><option value="">Todas as escadas</option><option value="prob">Só ALERTA, CRÍTICO ou em manutenção</option><option value="crit">Só do grupo crítica</option></select></label>
        <button class="btn sm" id="eqLimpar">Limpar seleção</button>
        <button class="btn sm" id="eqPadrao">Restaurar distribuição padrão</button>
      </div>
      <div class="stack" style="gap:18px" id="eqLista"></div>
    </section>

    <section class="view" id="v-ind" hidden aria-label="Indicadores">''')
R("  else if(view==='ind') renderInd();", "  else if(view==='ind') renderInd();\n  else if(view==='equipe') renderEquipe();")
R("  if(isTec() && ['ind','dados','live'].includes(v)) v='painel';", "  if(isTec() && ['ind','dados','live','equipe'].includes(v)) v='painel';")

# ---------- fila do supervisor mostra o responsável ----------
R("""esc(ESTN[x.e.cod])+' · '+(x.e.crit?'<b style="color:var(--brand)">crítica</b>':'não crítica')+' · '+x.e.fab+'</div></div>'+""",
  """esc(ESTN[x.e.cod])+' · '+(x.e.crit?'<b style="color:var(--brand)">crítica</b>':'não crítica')+' · '+x.e.fab+(isSup()&&!x.e.live&&respDe(x.e)?'<br>Resp.: '+esc(TECS[respDe(x.e)]):'')+'</div></div>'+""")

# ---------- filtro de estação do técnico: só as estações dele ----------
R("function paintTech(){", """function fillEstFiltro(){
  const cods = isTec() ? [...new Set(escadasDe(S.login.id).map(e=>e.cod))] : EST.map(x=>x.cod);
  const op='<option value="">Todas</option>'+EST.filter(x=>cods.includes(x.cod)).map(x=>'<option value="'+x.cod+'">'+x.cod+' · '+esc(x.nome)+'</option>').join('');
  [fEst,qEst].forEach(sel=>{ const v=sel.value; sel.innerHTML=op; sel.value=cods.includes(v)?v:''; });
  if(filt.est && !cods.includes(filt.est)) filt.est='';
}
function paintTech(){""")
R("  document.body.classList.toggle('papel-tec', isTec());\n}", "  document.body.classList.toggle('papel-tec', isTec());\n  if(typeof fEst!=='undefined') fillEstFiltro();\n}")

# ---------- lógica da tela Equipe ----------
R("/* ================= tela de login ================= */", r"""/* ================= TELA: equipe e responsáveis (supervisor) ================= */
const eqF = {tec:'', est:'', filtro:''}; let eqMudou = null;
$('#eqEst').innerHTML = '<option value="">Todas</option>'+EST.map(x=>'<option value="'+x.cod+'">'+x.cod+' · '+esc(x.nome)+'</option>').join('');
const tecOpts = sel => Object.entries(TECS).map(([k,n])=>'<option value="'+k+'"'+(k===sel?' selected':'')+'>'+k+' · '+esc(n)+'</option>').join('');
function renderEquipe(){
  if(!isSup()) return show('painel');
  computeCurrent();
  $('#eqTec').innerHTML = Object.entries(TECS).map(([k,n])=>{
    const es=escadasDe(k), m=[0,0,0,0]; es.forEach(e=>m[CUR[e.ix].code]++); const cr=es.filter(e=>e.crit).length;
    return '<button class="tcard" data-tec="'+k+'" aria-pressed="'+(eqF.tec===k)+'"><div class="tn"><b>'+esc(n)+'</b><span class="muted mono" style="font-size:.8rem">'+k+'</span></div>'+
      '<div><span class="big num">'+es.length+'</span> <span class="muted">escadas</span></div><div class="mini"><span>'+esc(trechoDe(k))+'</span></div>'+
      '<div class="mini"><span>'+cr+' do grupo crítica</span>'+(m[2]?'<b style="color:var(--crit)">'+m[2]+' crítico</b>':'')+(m[1]?'<b style="color:var(--warn)">'+m[1]+' alerta</b>':'')+(m[3]?'<b style="color:var(--maint)">'+m[3]+' em manutenção</b>':'')+'</div></button>';
  }).join('');
  const list = E.filter(e=>{
    if(eqF.tec && respDe(e)!==eqF.tec) return false;
    if(eqF.est && e.cod!==eqF.est) return false;
    const c=CUR[e.ix].code;
    if(eqF.filtro==='prob' && c===0) return false;
    if(eqF.filtro==='crit' && !e.crit) return false;
    return true;
  });
  let html='';
  for(const st of EST){
    const es=list.filter(e=>e.cod===st.cod); if(!es.length) continue;
    const donos=[...new Set(es.map(respDe))];
    html += '<section class="eq-st"><div class="eq-st-h"><h3><span>'+st.cod+'</span>'+esc(st.nome)+' <span class="muted" style="font-family:var(--f-body);font-size:.9rem;font-weight:400">'+es.length+' escadas</span></h3>'+
      '<div class="eq-tools"><label class="field"><span>Toda a estação para</span><select data-estsel="'+st.cod+'">'+tecOpts(donos.length===1?donos[0]:'')+'</select></label><button class="btn sm" data-estok="'+st.cod+'">Aplicar</button></div></div>'+
      '<div class="eq-grid">'+es.map(e=>{ const c=CUR[e.ix];
        return '<div class="eq-row s'+c.code+(eqMudou&&eqMudou.has(e.id)?' mudou':'')+'"><div class="top"><span class="code">'+e.id+'</span>'+(e.crit?'<span class="tag crit">Crítica</span>':'<span class="tag">'+e.fab+'</span>')+'</div>'+
          '<div>'+pill(c.code)+'</div><select data-esc="'+e.id+'" aria-label="Responsável por '+e.id+'">'+tecOpts(respDe(e))+'</select></div>'; }).join('')+'</div></section>';
  }
  $('#eqLista').innerHTML = html || '<div class="empty">Nenhuma escada com esses filtros.</div>';
}
function atribuir(ids, tec){
  const mud=ids.filter(id=>S.resp[id]!==tec); if(!mud.length){ toast('Nada mudou: '+(ids.length>1?'essas escadas já estão':'a escada já está')+' com '+TECS[tec]+'.'); return; }
  const de=[...new Set(mud.map(id=>S.resp[id]))];
  mud.forEach(id=>{ S.resp[id]=tec; logEv('Responsável → '+tec,{id:'R-'+id, esc:id}); });
  eqMudou=new Set(mud); save(); paintTop(); renderEquipe();
  toast(mud.length===1 ? mud[0]+' agora está com '+TECS[tec]+' (antes: '+TECS[de[0]]+').' : mud.length+' escadas passaram para '+TECS[tec]+'.', 4500);
}
$('#eqTec').addEventListener('click',ev=>{ const b=ev.target.closest('[data-tec]'); if(!b) return; eqF.tec = eqF.tec===b.dataset.tec ? '' : b.dataset.tec; eqMudou=null; renderEquipe(); });
$('#eqLista').addEventListener('change',ev=>{ const s=ev.target.closest('[data-esc]'); if(s) atribuir([s.dataset.esc], s.value); });
$('#eqLista').addEventListener('click',ev=>{ const b=ev.target.closest('[data-estok]'); if(!b) return; const cod=b.dataset.estok, tec=$('[data-estsel="'+cod+'"]').value;
  const ids=E.filter(e=>e.cod===cod && (!eqF.tec||respDe(e)===eqF.tec)).map(e=>e.id); atribuir(ids, tec); });
$('#eqEst').onchange=e=>{ eqF.est=e.target.value; renderEquipe(); };
$('#eqFiltro').onchange=e=>{ eqF.filtro=e.target.value; renderEquipe(); };
$('#eqLimpar').onclick=()=>{ Object.assign(eqF,{tec:'',est:'',filtro:''}); $('#eqEst').value=''; $('#eqFiltro').value=''; eqMudou=null; renderEquipe(); };
$('#eqPadrao').onclick=()=>{ const pad=distribuicaoPadrao(), mud=E.filter(e=>S.resp[e.id]!==pad[e.id]).map(e=>e.id);
  if(!mud.length){ toast('A distribuição já é a padrão.'); return; }
  mud.forEach(id=>{ S.resp[id]=pad[id]; logEv('Responsável → '+pad[id],{id:'R-'+id, esc:id}); }); eqMudou=new Set(mud); save(); renderEquipe(); toast(mud.length+' escadas voltaram ao responsável padrão.'); };

/* ================= tela de login ================= */""")

open(p, 'w', encoding='utf-8').write(s); print('patched v7 (equipe)')
