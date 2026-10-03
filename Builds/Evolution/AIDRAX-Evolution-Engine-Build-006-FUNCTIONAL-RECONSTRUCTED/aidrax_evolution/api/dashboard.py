
def html():
    return r"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AIDRAX Evolution Control</title>
<style>
:root{--p:transparent;--line:#275f61;--lime:#e8ff72;--green:#7bffbe;--text:#ffffff;--muted:#d7fbff;--cyan:#8ffcff;--soft:#c8f7ff}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(rgba(1,8,14,.18),rgba(1,8,14,.28)),url(/assets/evolution-bg.png) center center / cover fixed no-repeat;color:var(--text);font:14px Inter,Segoe UI,Arial,sans-serif;min-height:100vh}
header{height:54px;display:flex;align-items:center;justify-content:space-between;padding:0 16px;background:rgba(255,255,255,0.00);border-bottom:1px solid rgba(180,255,255,0.18);backdrop-filter:blur(14px) saturate(150%);-webkit-backdrop-filter:blur(14px) saturate(150%)}.brand{display:flex;gap:10px;align-items:center}.logo{width:29px;height:29px;border-radius:9px;background:#6d1c8d;display:grid;place-items:center;font-weight:800}.sub{font-size:9px;letter-spacing:1.4px;color:var(--cyan);text-shadow:0 1px 3px rgba(0,0,0,.95)}.btn,.tab{background:rgba(255,255,255,0.00);border:1px solid rgba(180,255,255,0.20);color:#ecf8f6;border-radius:9px;padding:7px 10px;cursor:pointer;backdrop-filter:blur(14px) saturate(150%);-webkit-backdrop-filter:blur(14px) saturate(150%);box-shadow:inset 0 1px 0 rgba(255,255,255,0.08)}.pill{padding:5px 9px;border:1px solid rgba(143,252,255,.35);border-radius:999px;color:var(--green);font-size:10px;text-shadow:0 1px 3px rgba(0,0,0,.95)}
main{max-width:1180px;margin:18px auto;padding:0 14px}.metrics{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}.metric,.panel,.skill,.row{
  background:rgba(255,255,255,0.00);
  border:1px solid rgba(180,255,255,0.22);
  border-radius:14px;
  backdrop-filter:blur(18px) saturate(160%);
  -webkit-backdrop-filter:blur(18px) saturate(160%);
  box-shadow:0 8px 28px rgba(0,0,0,0.18),inset 0 1px 0 rgba(255,255,255,0.10)
}.metric{padding:11px}.metric small{display:block;color:var(--soft);text-shadow:0 1px 2px rgba(0,0,0,.85)}.metric strong{font-size:20px;color:#ffffff;text-shadow:0 1px 3px rgba(0,0,0,.95)}.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 18px}.tab.active{color:var(--lime);border-color:#768f38}.eyebrow{font-size:9px;letter-spacing:1.4px;color:var(--lime);font-weight:800;text-shadow:0 1px 3px rgba(0,0,0,.95)}h2{font-size:18px;margin:3px 0 13px}.skills{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.skill{padding:11px}.bar{height:7px;background:#35283a;border-radius:999px;margin-top:9px;overflow:hidden}.fill{height:100%;background:linear-gradient(90deg,#84ff9c,#dd74ff)}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}.panel{padding:12px}.row{padding:10px 12px;margin:7px 0}.row b{display:block}.row span{font-size:11px;color:var(--soft);text-shadow:0 1px 2px rgba(0,0,0,.9)}.actions{display:flex;gap:6px;flex-wrap:wrap}.hidden{display:none}.tabbody{margin-top:10px}
table{width:100%;border-collapse:collapse}th,td{text-align:left;border-bottom:1px solid rgba(143,252,255,.22);padding:7px;font-size:12px;color:#f7ffff;text-shadow:0 1px 2px rgba(0,0,0,.9)}input{background:rgba(255,255,255,0.00);color:white;border:1px solid rgba(180,255,255,0.20);border-radius:9px;padding:7px;backdrop-filter:blur(14px) saturate(150%);-webkit-backdrop-filter:blur(14px) saturate(150%);box-shadow:inset 0 1px 0 rgba(255,255,255,0.08)}
@media(max-width:900px){.metrics{grid-template-columns:repeat(3,1fr)}.skills,.grid{grid-template-columns:1fr}}
/* TRUE GLASS OVERRIDE */
.metric,.panel,.skill,.row,.btn,.tab,input,header{
  background:transparent !important;
  background-color:transparent !important;
  backdrop-filter:none !important;
  -webkit-backdrop-filter:none !important;
}
.metric,.panel,.skill,.row{
  border:1px solid rgba(180,255,255,.28) !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.10),0 4px 18px rgba(0,0,0,.10) !important;
}
.btn,.tab,input{
  border:1px solid rgba(180,255,255,.24) !important;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.08) !important;
}
table,thead,tbody,tr,th,td{
  background:transparent !important;
  background-color:transparent !important;
}
</style></head><body>
<header><div class="brand"><div class="logo">A</div><div><div class="sub">DRAGON CORE · BUILD 006</div><div><b>AIDRAX Evolution Control</b></div></div></div><div><span class="pill" id="local">LOCAL · ACTIVE</span> <button class="btn" onclick="refresh()">Aktualisieren</button></div></header>
<main>
<div class="metrics">
<div class="metric"><small>Bestätigte Memories</small><strong id="mem">0</strong></div>
<div class="metric"><small>Lern-Queue</small><strong id="q">0</strong></div>
<div class="metric"><small>Import-Vorschau</small><strong id="pv">0</strong></div>
<div class="metric"><small>Quarantäne</small><strong id="qu">0</strong></div>
<div class="metric"><small>Upgrades</small><strong id="up">0</strong></div>
<div class="metric"><small>Quellen</small><strong id="src">0</strong></div>
</div>
<div class="tabs" id="tabs"></div>
<div id="content"></div>
</main>
<script>
const tabs=['Evolution','Import-Vorschau','Quellen','Lern-Queue','Manuell lernen','Memory','Upgrades','Reflexion','Audit'];
let active='Evolution';
async function J(url,opt){let r=await fetch(url,opt);let t=await r.text();if(!r.ok)throw new Error(t);return JSON.parse(t)}
function buttons(){tabsEl.innerHTML=tabs.map(x=>`<button class="tab ${x==active?'active':''}" onclick="active='${x}';render()">${x}</button>`).join('')}
let tabsEl=document.getElementById('tabs'), content=document.getElementById('content');buttons();
async function refresh(){let s=await J('/health');document.getElementById('local').textContent=s.runtime_status==='running'?'LOCAL · ACTIVE':'LOCAL · DEGRADED';let st=await J('/api/status');mem.textContent=st.metrics.confirmed_memories;q.textContent=st.metrics.learning_queue;pv.textContent=st.metrics.import_preview;qu.textContent=st.metrics.quarantine;up.textContent=st.metrics.upgrades;src.textContent=st.metrics.sources;render()}
async function render(){buttons(); if(active==='Evolution') return evolution(); if(active==='Quellen') return sources(); if(active==='Import-Vorschau') return previews(); if(active==='Lern-Queue') return queue(); if(active==='Memory') return memories(); if(active==='Reflexion') return reflection(); if(active==='Audit') return audit(); content.innerHTML=`<div class="panel"><h2>${active}</h2><div class="row"><span>Build 006: Modul aktiv.</span></div></div>`}
async function evolution(){let s=await J('/api/status');content.innerHTML=`<div class="eyebrow">EXPERIENCE CORE</div><h2>Kompetenzentwicklung</h2><div class="skills">${s.skills.map(x=>`<div class="skill">${x.name} · LEVEL ${x.level}<div class="bar"><div class="fill" style="width:${Math.min(100,100*x.xp/x.next_xp)}%"></div></div><small>${x.xp} XP / ${x.next_xp} XP</small></div>`).join('')}</div><div class="grid"><div class="panel"><div class="eyebrow">IMMUTABLE</div><h2>Core Values <span class="pill">LOCKED</span></h2>${[['honesty','AIDRAX communicates truthfully and marks uncertainty.'],['identity','Core identity cannot be rewritten by learned content.'],['owner_gate','Persistent learning and capability upgrades require owner control.'],['respect','AIDRAX remains respectful.'],['safety','No hidden, destructive, or unauthorized actions.'],['source_integrity','Sources are previewed or quarantined before learning.']].map(v=>`<div class="row"><b>${v[0]}</b><span>${v[1]}</span></div>`).join('')}</div><div class="panel"><div class="eyebrow">RUNTIME</div><h2>Agentenstatus</h2>${Object.entries(s).filter(([k])=>k!='metrics'&&k!='skills').map(([k,v])=>`<div class="row"><b>${k}</b><span>${v}</span></div>`).join('')}</div></div>`}
async function sources(){let a=await J('/api/sources');content.innerHTML=`<div class="panel"><h2>Quellen</h2><div class="actions"><input id="sn" placeholder="Name"><input id="sp" placeholder="/pfad/zur/quelle"><button class="btn" onclick="addSource()">Quelle hinzufügen</button></div><table><tr><th>ID</th><th>Name</th><th>Pfad</th><th>Aktion</th></tr>${a.map(x=>`<tr><td>${x.id}</td><td>${x.name}</td><td>${x.path}</td><td><button class="btn" onclick="scan(${x.id})">Read-only Scan</button></td></tr>`).join('')}</table></div>`}
async function addSource(){await J('/api/sources',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:sn.value,path:sp.value})});sources();refresh()}
async function scan(id){let r=await J('/api/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source_id:id})});alert(`${r.created.length} Vorschauen erzeugt`);refresh()}
async function previews(){let a=await J('/api/previews');content.innerHTML=`<div class="panel"><h2>Import-Vorschau / Quarantäne</h2><table><tr><th>ID</th><th>Status</th><th>Titel</th><th>Flags</th><th></th></tr>${a.map(x=>`<tr><td>${x.id}</td><td>${x.status}</td><td>${x.title||''}</td><td>${x.flags||''}</td><td>${x.status=='preview'?`<button class="btn" onclick="approvePreview(${x.id})">Owner-Freigabe</button>`:''}</td></tr>`).join('')}</table></div>`}
async function token(){return 'SESSION'}
async function approvePreview(id){let t=await token();await J('/api/approve-preview',{method:'POST',headers:{'Content-Type':'application/json','X-Owner-Token':t},body:JSON.stringify({preview_id:id})});refresh()}
async function queue(){let a=await J('/api/queue');content.innerHTML=`<div class="panel"><h2>Lern-Queue</h2><table><tr><th>ID</th><th>Preview</th><th>Status</th><th>Titel</th><th></th></tr>${a.map(x=>`<tr><td>${x.id}</td><td>${x.preview_id}</td><td>${x.status}</td><td>${x.title||''}</td><td>${x.status!='approved'?`<button class="btn" onclick="approveLearn(${x.id})">2. Owner-Freigabe</button>`:''}</td></tr>`).join('')}</table></div>`}
async function approveLearn(id){let t=await token();await J('/api/approve-learning',{method:'POST',headers:{'Content-Type':'application/json','X-Owner-Token':t},body:JSON.stringify({queue_id:id,category:'general'})});refresh()}
async function memories(){let a=await J('/api/memories');content.innerHTML=`<div class="panel"><h2>Memory</h2><table><tr><th>ID</th><th>Kategorie</th><th>XP</th><th>Inhalt</th></tr>${a.map(x=>`<tr><td>${x.id}</td><td>${x.category}</td><td>${x.xp}</td><td>${(x.content||'').slice(0,180)}</td></tr>`).join('')}</table></div>`}
async function reflection(){content.innerHTML=`<div class="panel"><h2>Reflexion</h2><button class="btn" onclick="doReflect()">Owner-gesteuerte Reflexion starten</button></div>`}
async function doReflect(){let t=await token();let r=await J('/api/reflect',{method:'POST',headers:{'X-Owner-Token':t}});alert(JSON.stringify(r,null,2))}
async function audit(){let a=await J('/api/audit');content.innerHTML=`<div class="panel"><h2>Audit</h2><table><tr><th>Zeit</th><th>Event</th><th>Detail</th></tr>${a.map(x=>`<tr><td>${x.created_at}</td><td>${x.event}</td><td>${x.detail}</td></tr>`).join('')}</table></div>`}
refresh();
</script></body></html>"""
