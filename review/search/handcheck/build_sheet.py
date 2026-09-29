#!/usr/bin/env python3
"""Fetch the 60 sample records from PubMed and build a BLIND labelling sheet.
The rule's verdict is deliberately NOT included, so the labeller's judgement is
independent of the rule it is meant to validate. Outputs handcheck_sheet.html
(click-through UI, exports CSV) and handcheck_sheet.csv (fallback)."""
import csv, json, os, html, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
EMAIL = "xxiang@mail.yu.edu"
key = list(csv.DictReader(open(os.path.join(HERE, "sample60_key.csv"))))
pmids = [r["pmid"] for r in key]

recs = {}
for i in range(0, len(pmids), 20):
    batch = pmids[i:i+20]
    q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(batch), "retmode": "xml", "email": EMAIL})
    with urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + q, timeout=60) as r:
        root = ET.fromstring(r.read())
    for art in root.findall(".//PubmedArticle"):
        pmid = art.findtext(".//PMID")
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        parts = []
        for t in art.findall(".//Abstract/AbstractText"):
            lab = t.get("Label")
            txt = "".join(t.itertext())
            parts.append((lab + ": " + txt) if lab else txt)
        recs[pmid] = {"title": title, "abstract": " ".join(parts),
                      "journal": art.findtext(".//Journal/ISOAbbreviation") or art.findtext(".//Journal/Title") or "",
                      "year": art.findtext(".//PubDate/Year") or (art.findtext(".//PubDate/MedlineDate") or "")[:4]}
    time.sleep(0.4)
    print(f"  fetched {min(i+20, len(pmids))}/{len(pmids)}")

missing = [p for p in pmids if p not in recs]
data = []
for r in key:
    rec = recs.get(r["pmid"], {"title": "(record not returned by PubMed)", "abstract": "", "journal": "", "year": ""})
    data.append({"index": int(r["index"]), "pmid": r["pmid"], **rec})

with open(os.path.join(HERE, "handcheck_sheet.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["index", "pmid", "year", "journal", "title", "abstract", "decision(eligible|excluded)", "fails(i|ii|iii, comma-sep)", "note"])
    for d in data:
        w.writerow([d["index"], d["pmid"], d["year"], d["journal"], d["title"], d["abstract"], "", "", ""])

CRIT = """A record is <b>eligible</b> only if all three hold:<br>
<b>(i) structure</b> — data indexed by both time and space, <i>or</i> longitudinal data with an explicit temporal model.<br>
<b>(ii) task</b> — a human clinical or public-health task (not animals/in-vitro, not a non-health domain such as traffic, air quality, crops, machinery).<br>
<b>(iii) evidence</b> — reports at least one quantitative result against a <i>named</i> alternative (a baseline, a prior method, another model — not just its own ablation-free numbers)."""

tpl = """<!DOCTYPE html><meta charset="utf-8"><title>Hand check 60</title>
<style>
:root{--bg:#fff;--fg:#111;--mut:#666;--line:#e3e3e3;--acc:#1a5fb4;--ok:#1a7f37;--no:#a02c2c}
@media(prefers-color-scheme:dark){:root{--bg:#16181c;--fg:#e8e8e8;--mut:#9aa0a6;--line:#2c2f34;--acc:#7cb0ff;--ok:#5dd47f;--no:#ff8f8f}}
*{box-sizing:border-box}body{background:var(--bg);color:var(--fg);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;padding:0 16px 120px}
.wrap{max-width:820px;margin:0 auto}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:14px 0;z-index:9}
h1{font-size:18px;margin:0 0 6px}.crit{font-size:13px;color:var(--mut);background:color-mix(in srgb,var(--fg) 4%,transparent);padding:10px 12px;border-radius:8px;margin:8px 0}
.bar{height:6px;background:var(--line);border-radius:3px;overflow:hidden;margin-top:8px}.bar>div{height:100%;background:var(--acc);width:0}
.card{border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:16px 0}
.card.done{border-color:color-mix(in srgb,var(--acc) 45%,var(--line))}
.meta{font-size:12px;color:var(--mut);margin-bottom:6px}
.ttl{font-weight:600;margin-bottom:8px}
.abs{font-size:14px;color:var(--fg);max-height:9.6em;overflow:auto;padding-right:6px;border-left:2px solid var(--line);padding-left:10px}
.ctl{margin-top:12px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
button.ch{border:1px solid var(--line);background:transparent;color:var(--fg);padding:6px 14px;border-radius:999px;cursor:pointer;font:inherit;font-size:14px}
button.ch[aria-pressed=true][data-v=eligible]{border-color:var(--ok);color:var(--ok);font-weight:600}
button.ch[aria-pressed=true][data-v=excluded]{border-color:var(--no);color:var(--no);font-weight:600}
.fails{display:none;gap:6px;flex-wrap:wrap}.fails.on{display:flex}
button.f{border:1px dashed var(--line);background:transparent;color:var(--mut);padding:4px 10px;border-radius:6px;cursor:pointer;font:inherit;font-size:13px}
button.f[aria-pressed=true]{border-style:solid;border-color:var(--no);color:var(--no)}
input.note{flex:1;min-width:200px;background:transparent;color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px 8px;font:inherit;font-size:13px}
footer{position:fixed;left:0;right:0;bottom:0;background:var(--bg);border-top:1px solid var(--line);padding:10px 16px;display:flex;gap:10px;align-items:center;justify-content:center}
button.dl{background:var(--acc);color:#fff;border:0;padding:9px 18px;border-radius:8px;font:inherit;font-weight:600;cursor:pointer}
button.dl:disabled{opacity:.45;cursor:not-allowed}
a{color:var(--acc)}
</style><div class=wrap>
<header><h1>Hand check &mdash; 60 screening decisions</h1>
<div class=crit>__CRIT__</div>
<div style="font-size:13px;color:var(--mut)">Judged <b id=n>0</b>/60 &middot; saves in this browser as you go &middot; the rule's own verdict is hidden on purpose</div>
<div class=bar><div id=pb></div></div></header>
<div id=list></div></div>
<footer><button class=dl id=dl disabled>Download results CSV</button>
<span style="font-size:13px;color:var(--mut)" id=st></span></footer>
<script>
const DATA=__DATA__, K='hc60';
let S=JSON.parse(localStorage.getItem(K)||'{}');
const save=()=>{try{localStorage.setItem(K,JSON.stringify(S))}catch(e){}};
const list=document.getElementById('list');
DATA.forEach(d=>{
  const c=document.createElement('div'); c.className='card'; c.id='c'+d.index;
  c.innerHTML=`<div class=meta>#${d.index} &middot; PMID <a href="https://pubmed.ncbi.nlm.nih.gov/${d.pmid}/" target=_blank rel=noreferrer>${d.pmid}</a> &middot; ${d.journal||''} ${d.year||''}</div>
  <div class=ttl></div><div class=abs></div>
  <div class=ctl><button class=ch data-v=eligible aria-pressed=false>eligible</button>
  <button class=ch data-v=excluded aria-pressed=false>excluded</button>
  <span class=fails><button class=f data-f=i aria-pressed=false>fails i</button><button class=f data-f=ii aria-pressed=false>fails ii</button><button class=f data-f=iii aria-pressed=false>fails iii</button></span>
  <input class=note placeholder="reason (optional)"></div>`;
  c.querySelector('.ttl').textContent=d.title; c.querySelector('.abs').textContent=d.abstract||'(no abstract in PubMed)';
  list.appendChild(c);
  const st=S[d.pmid]||{};
  const fails=c.querySelector('.fails'), note=c.querySelector('.note');
  const paint=()=>{
    c.querySelectorAll('.ch').forEach(b=>b.setAttribute('aria-pressed', st.decision===b.dataset.v));
    fails.classList.toggle('on', st.decision==='excluded');
    c.querySelectorAll('.f').forEach(b=>b.setAttribute('aria-pressed', (st.fails||[]).includes(b.dataset.f)));
    c.classList.toggle('done', !!st.decision); note.value=st.note||'';
  };
  c.querySelectorAll('.ch').forEach(b=>b.onclick=()=>{st.decision=st.decision===b.dataset.v?null:b.dataset.v;
    if(st.decision!=='excluded') st.fails=[]; S[d.pmid]=st; save(); paint(); tally();});
  c.querySelectorAll('.f').forEach(b=>b.onclick=()=>{st.fails=st.fails||[];
    const i=st.fails.indexOf(b.dataset.f); i<0?st.fails.push(b.dataset.f):st.fails.splice(i,1); S[d.pmid]=st; save(); paint();});
  note.oninput=()=>{st.note=note.value; S[d.pmid]=st; save();};
  paint();
});
function tally(){const n=DATA.filter(d=>(S[d.pmid]||{}).decision).length;
  document.getElementById('n').textContent=n; document.getElementById('pb').style.width=(n/DATA.length*100)+'%';
  document.getElementById('dl').disabled=n<DATA.length;
  document.getElementById('st').textContent=n<DATA.length?(DATA.length-n)+' left':'complete \u2014 download and hand the file back';}
tally();
document.getElementById('dl').onclick=()=>{
  const q=s=>'"'+String(s==null?'':s).replace(/"/g,'""')+'"';
  const rows=[['index','pmid','decision','fails','note'].join(',')];
  DATA.forEach(d=>{const s=S[d.pmid]||{}; rows.push([d.index,d.pmid,s.decision||'',(s.fails||[]).join('|'),q(s.note||'')].join(','))});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([rows.join('\\n')+'\\n'],{type:'text/csv'}));
  a.download='handcheck60_labels.csv'; a.click();};
</script>"""

out = tpl.replace("__CRIT__", CRIT).replace("__DATA__", json.dumps(data, ensure_ascii=False))
open(os.path.join(HERE, "handcheck_sheet.html"), "w").write(out)
print(f"records fetched: {len(recs)}/60; missing: {missing or 'none'}")
print("wrote handcheck_sheet.html + handcheck_sheet.csv")
