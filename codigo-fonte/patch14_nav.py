"""Navegação enxuta: 12 itens viram 7 grupos com abas internas; barra lateral rola quando a tela é baixa."""
import re
p = 'template.html'; s = open(p, encoding='utf-8').read()
def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90]); s = s.replace(a, b)

# --- ícones atuais de cada tela ---
ini = s.index('<nav class="rail"'); fim = s.index('</nav>', ini)
rail = s[ini:fim]
ICO = {m.group(1): m.group(2) for m in re.finditer(r'data-view="(\w+)"[^>]*>(<svg.*?</svg>)', rail)}
assert len(ICO) == 12, ICO.keys()
logo = rail[rail.index('<div class="logo"'):rail.index('</div>', rail.index('<div class="logo"')) + 6]
def one_multi(multi, one):
    return ICO[multi].replace('<svg ', '<svg class="ic-multi" ', 1) + ICO[one].replace('<svg ', '<svg class="ic-one" ', 1)
novo = '''<nav class="rail" aria-label="Seções">
    ''' + logo + '''
    <button class="nav" data-g="painel" aria-current="page">''' + ICO['painel'] + '''<span class="nl">Painel</span></button>
    <button class="nav" data-g="fila">''' + ICO['fila'] + '''<span class="nl">Fila</span><span class="badge" id="badgeFila" hidden></span></button>
    <button class="nav" data-g="atend">''' + ICO['atend'] + '''<span class="nl">Atendi&shy;mentos</span><span class="badge" id="badgeAt" hidden style="background:var(--maint)"></span></button>
    <button class="nav sup-only" data-g="equipe">''' + ICO['equipe'] + '''<span class="nl">Equipe</span></button>
    <button class="nav sup-only" data-g="prev">''' + ICO['prev'] + '''<span class="nl">Preventivas</span></button>
    <button class="nav sup-only" data-g="rel">''' + one_multi('ind', 'boletim') + '''<span class="nl">Relatórios</span></button>
    <button class="nav" data-g="dados">''' + one_multi('dados', 'sync') + '''<span class="nl">Dados</span><span class="badge" id="badgeSync" hidden style="background:var(--warn);color:#1b1100"></span><span class="live-dot" id="badgeLive" hidden></span></button>
  '''
s = s[:ini] + novo + s[fim:]

# --- abas internas, logo abaixo do cabeçalho ---
R('    </header>\n', '    </header>\n    <div class="subtabs" id="subtabs" hidden><div class="seg" role="tablist" id="subSeg"></div></div>\n')

# --- CSS ---
R(".nav .badge[hidden]{display:none!important}", """.nav .badge[hidden]{display:none!important}
.rail{overflow-y:auto;overflow-x:hidden;scrollbar-width:thin}
.nav{flex:0 0 auto}
.nav.one .ic-multi,.nav:not(.one) .ic-one{display:none}
#badgeLive{right:auto;left:14px}
.subtabs{padding:14px max(24px,env(safe-area-inset-right,0px)) 0 max(24px,env(safe-area-inset-left,0px))}
.subtabs[hidden]{display:none}
.subtabs .seg{max-width:100%;overflow-x:auto}
.subtabs .seg button{white-space:nowrap}
.subtabs+.view{padding-top:14px}
@media (min-width:900px) and (max-height:720px){ .logo{padding-bottom:6px} .logo b{display:none} .nav{min-height:52px;padding:5px 4px;gap:2px} }""")
R("  .top,.view{padding-left:var(--gut);padding-right:var(--gutr)}", "  .top,.view,.subtabs{padding-left:var(--gut);padding-right:var(--gutr)}\n  .rail{overflow-y:hidden;overflow-x:auto} .nav{flex:1 0 auto}")

# --- lógica ---
R("""function show(v){
  if(isTec() && ['ind','dados','live','equipe','foco','rota','boletim','prev'].includes(v)) v='painel';
  if(!isGes() && ['ind','dados','live'].includes(v)) v='painel';""", r"""/* grupos da barra lateral: cada grupo abre a última aba usada; com uma aba só, o botão leva o nome dela */
function GRUPOS(){ return {
  painel:{t:'Painel', tabs:[['painel','Painel']]},
  fila:{t:'Fila', tabs:[['fila','Fila'],['foco','Foco']]},
  atend:{t:'Atendi&shy;mentos', tabs:[['atend','Atendimentos']]},
  equipe:{t:'Equipe', tabs:[['equipe','Equipe'],['rota','Emergência']]},
  prev:{t:'Preventivas', tabs:[['prev','Preventivas']]},
  rel:{t:'Relatórios', tabs:[['boletim','Boletim'],['ind','Indicadores']]},
  dados:{t:'Dados', tabs:[['sync','Sincronização'],['dados','Dataset'],['live','Maquete ao vivo']]},
}; }
function permitido(v){ return !(isTec() && ['ind','dados','live','equipe','foco','rota','boletim','prev'].includes(v)) && !(!isGes() && ['ind','dados','live'].includes(v)); }
function grupoDe(v){ return Object.keys(GRUPOS()).find(g=>GRUPOS()[g].tabs.some(t=>t[0]===v)); }
function abasDe(g){ return GRUPOS()[g].tabs.filter(t=>permitido(t[0])); }
const ULT = {};
function atualizarNav(){
  const G=GRUPOS();
  document.querySelectorAll('.nav[data-g]').forEach(b=>{ const ab=abasDe(b.dataset.g), um=ab.length===1;
    b.classList.toggle('one', um); b.querySelector('.nl').innerHTML = um ? ab[0][1] : G[b.dataset.g].t; });
}
function renderSubtabs(v){
  const g=grupoDe(v), ab=g?abasDe(g):[], box=$('#subtabs');
  if(v==='detalhe' || ab.length<2){ box.hidden=true; return; }
  box.hidden=false;
  $('#subSeg').innerHTML=ab.map(([id,t])=>'<button role="tab" data-sub="'+id+'" aria-pressed="'+(id===v)+'" aria-selected="'+(id===v)+'">'+t+'</button>').join('');
}
$('#subSeg').addEventListener('click',ev=>{ const b=ev.target.closest('[data-sub]'); if(b) show(b.dataset.sub); });
function show(v){
  if(!permitido(v)) v='painel';""")
R("""  document.querySelectorAll('.nav').forEach(b=>b.setAttribute('aria-current', (b.dataset.view===v || (v==='detalhe'&&b.dataset.view===prevView))?'page':'false'));""",
"""  const gAtual = grupoDe(v==='detalhe' ? prevView : v); if(v!=='detalhe' && gAtual) ULT[gAtual]=v;
  document.querySelectorAll('.nav[data-g]').forEach(b=>b.setAttribute('aria-current', b.dataset.g===gAtual?'page':'false'));
  atualizarNav(); renderSubtabs(v);""")
R("document.querySelectorAll('.nav').forEach(b=>b.onclick=()=>show(b.dataset.view));",
  "document.querySelectorAll('.nav[data-g]').forEach(b=>b.onclick=()=>{ const g=b.dataset.g, u=ULT[g]; show(u && permitido(u) ? u : abasDe(g)[0][0]); });")
R("  document.body.classList.toggle('papel-tec', isTec()); document.body.classList.toggle('papel-ges', isGes());",
  "  document.body.classList.toggle('papel-tec', isTec()); document.body.classList.toggle('papel-ges', isGes());\n  if(document.querySelector('.nav[data-g]')) atualizarNav();")
R("  document.querySelectorAll('.view').forEach(s=>s.hidden = s.id!=='v-detalhe'); window.scrollTo(0,0); renderAll(); }", "  document.querySelectorAll('.view').forEach(s=>s.hidden = s.id!=='v-detalhe'); $('#subtabs').hidden=true; window.scrollTo(0,0); renderAll(); }")
open(p, 'w', encoding='utf-8').write(s); print('patched v14 (navegação em grupos)')
