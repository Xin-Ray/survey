#!/usr/bin/env python3
"""Generate the phone labelling page (published as a private Artifact with the db capability)."""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
mine = {r["pmid"]: r for r in csv.DictReader(open(os.path.join(HERE, "my_labels.csv")))}
rows = []
for r in csv.DictReader(open(os.path.join(HERE, "handcheck_sheet.csv"))):
    m = mine.get(r["pmid"], {})
    rows.append({"i": int(r["index"]), "pmid": r["pmid"], "yr": r["year"], "jr": r["journal"],
                 "ti": r["title"], "ab": r["abstract"],
                 "sug": m.get("my_decision", ""), "sf": m.get("my_fails", ""), "why": m.get("my_reason", "")})
rows.sort(key=lambda x: x["i"])

HTML = """<title>IoT-J Screening Check</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>
:root{
  --paper:#f6f7f8; --card:#ffffff; --ink:#161b21; --mid:#57636f; --faint:#8b97a3;
  --line:#dce1e6; --line2:#eef1f4;
  --yes:#0d6b51; --yes-bg:#e7f2ee; --no:#9a3b2d; --no-bg:#f7eae7; --nav:#1d4e8f;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#12161a; --card:#191e24; --ink:#e7ebee; --mid:#9aa6b2; --faint:#6d7985;
  --line:#2a3138; --line2:#222830;
  --yes:#4cc39c; --yes-bg:#132a23; --no:#e08878; --no-bg:#2b1a17; --nav:#7fb0f0;
}}
:root[data-theme="dark"]{
  --paper:#12161a; --card:#191e24; --ink:#e7ebee; --mid:#9aa6b2; --faint:#6d7985;
  --line:#2a3138; --line2:#222830;
  --yes:#4cc39c; --yes-bg:#132a23; --no:#e08878; --no-bg:#2b1a17; --nav:#7fb0f0;
}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--paper);color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
  display:flex;flex-direction:column;overflow:hidden}

header{position:sticky;top:env(safe-area-inset-top,0px);background:var(--paper);
  border-bottom:1px solid var(--line);padding:10px 16px 8px;flex:0 0 auto;z-index:5}
.hrow{display:flex;align-items:baseline;gap:10px;justify-content:space-between}
.hname{font-size:12px;letter-spacing:.09em;text-transform:uppercase;color:var(--faint)}
.hcount{font-variant-numeric:tabular-nums;font-size:13px;color:var(--mid)}
.bar{height:3px;background:var(--line2);border-radius:2px;overflow:hidden;margin-top:8px}
.bar>i{display:block;height:100%;background:var(--nav);width:0;transition:width .25s}
@media (prefers-reduced-motion:reduce){.bar>i{transition:none}}
.critbtn{background:none;border:0;color:var(--nav);font:inherit;font-size:13px;padding:0;cursor:pointer;text-decoration:underline}
.crit{margin-top:10px;padding:12px 14px;background:var(--card);border:1px solid var(--line);
  border-radius:8px;font-size:13.5px;color:var(--mid);line-height:1.6}
.crit b{color:var(--ink)}
.crit p{margin:0 0 7px}.crit p:last-child{margin:0}

main{flex:1 1 auto;overflow-y:auto;padding:16px 16px 8px;-webkit-overflow-scrolling:touch}
.wrap{max-width:660px;margin:0 auto}
.meta{font-size:12px;color:var(--faint);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.meta a{color:var(--nav)}
.ti{font-family:Newsreader,Georgia,"Times New Roman",serif;font-size:21px;line-height:1.3;
  font-weight:500;margin:8px 0 12px;text-wrap:balance}
.ab{font-family:Newsreader,Georgia,"Times New Roman",serif;font-size:16.5px;line-height:1.62;
  color:var(--ink);border-left:2px solid var(--line);padding-left:14px}
.ab.none{font-family:inherit;font-size:14px;color:var(--faint);font-style:italic}
.note{margin-top:14px;width:100%;background:var(--card);color:var(--ink);border:1px solid var(--line);
  border-radius:8px;padding:9px 11px;font:inherit;font-size:14px}
.sug{margin-top:16px;padding:11px 13px;border-radius:8px;border:1px solid var(--line);
  background:var(--card);font-size:13.5px;line-height:1.5}
.sug .lab{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);
  display:block;margin-bottom:4px}
.sug .v{font-weight:600}
.sug .v.y{color:var(--yes)}.sug .v.n{color:var(--no)}
.sug .why{color:var(--mid);margin-top:3px}
.fails{margin-top:12px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.fails span{font-size:12.5px;color:var(--faint)}
.chip{border:1px solid var(--line);background:var(--card);color:var(--mid);border-radius:7px;
  padding:6px 12px;font:inherit;font-size:13.5px;cursor:pointer}
.chip[aria-pressed="true"]{border-color:var(--no);color:var(--no);background:var(--no-bg)}

footer{flex:0 0 auto;background:var(--paper);border-top:1px solid var(--line);
  padding:10px 16px calc(10px + env(safe-area-inset-bottom,0px))}
.pick{display:flex;gap:10px;max-width:660px;margin:0 auto}
.pick button{flex:1;padding:15px 8px;border-radius:10px;border:1.5px solid var(--line);
  background:var(--card);color:var(--ink);font:inherit;font-size:16px;font-weight:600;cursor:pointer}
#yes[aria-pressed="true"]{border-color:var(--yes);color:var(--yes);background:var(--yes-bg)}
#no[aria-pressed="true"]{border-color:var(--no);color:var(--no);background:var(--no-bg)}
.nav{display:flex;gap:14px;align-items:center;justify-content:space-between;
  max-width:660px;margin:9px auto 0;font-size:14px}
.nav button{background:none;border:0;color:var(--nav);font:inherit;padding:4px 0;cursor:pointer}
.nav button:disabled{color:var(--faint);cursor:default}
.nav .st{color:var(--mid);font-variant-numeric:tabular-nums;font-size:13px}
button:focus-visible,a:focus-visible,textarea:focus-visible{outline:2px solid var(--nav);outline-offset:2px}

.done{max-width:660px;margin:0 auto;padding:22px;background:var(--card);
  border:1px solid var(--line);border-radius:10px}
.done h2{font-family:Newsreader,Georgia,serif;font-weight:500;font-size:22px;margin:0 0 10px}
.done p{color:var(--mid);margin:0 0 8px;font-size:14.5px}
.tally{display:flex;gap:22px;margin:16px 0 4px;font-variant-numeric:tabular-nums}
.tally div{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
.tally b{display:block;font-size:26px;font-weight:600;letter-spacing:0;text-transform:none;color:var(--ink);margin-top:2px}
.warn{padding:12px 14px;border:1px solid var(--no);background:var(--no-bg);color:var(--no);
  border-radius:8px;font-size:13.5px;margin:0 auto 14px;max-width:660px}
</style>

<header>
  <div class="hrow">
    <span class="hname">Screening hand check</span>
    <span class="hcount" id="count">-</span>
  </div>
  <div class="bar"><i id="pb"></i></div>
  <div style="margin-top:7px"><button class="critbtn" id="ctog" aria-expanded="false">Show the three criteria</button></div>
  <div class="crit" id="crit" hidden>
    <p><b>Eligible</b> only if all three hold. Each record carries a suggestion and a reason; it is a starting point, not a vote &mdash; nothing is recorded until you tap.</p>
    <p><b>(i) structure</b> &mdash; indexed by both time and space, <i>or</i> longitudinal data with an explicit temporal model.</p>
    <p><b>(ii) task</b> &mdash; a human clinical or public-health task. Not animal or in-vitro, not a non-health domain (traffic, air quality, crops, machinery), not a non-clinical human task.</p>
    <p><b>(iii) evidence</b> &mdash; at least one quantitative result against a <i>named</i> alternative: a baseline, a prior method, another model.</p>
  </div>
</header>

<main id="main"><div class="wrap" id="wrap"></div></main>

<footer id="foot">
  <div class="pick">
    <button id="yes" aria-pressed="false">Eligible</button>
    <button id="no" aria-pressed="false">Excluded</button>
  </div>
  <div class="nav">
    <button id="prev">&larr; Back</button>
    <span class="st" id="pos"></span>
    <button id="next">Skip &rarr;</button>
  </div>
</footer>

<script>
const R = __DATA__;
let at = 0, S = {}, db = null, saving = false;

const $ = id => document.getElementById(id);
$("ctog").onclick = () => { const c = $("crit"), open = c.hidden;
  c.hidden = !open; $("ctog").setAttribute("aria-expanded", String(open));
  $("ctog").textContent = open ? "Hide the three criteria" : "Show the three criteria"; };

function decided(){ return R.filter(r => (S[r.pmid]||{}).decision).length; }

function paintHeader(){
  const n = decided();
  $("count").textContent = n + " / " + R.length;
  $("pb").style.width = (n / R.length * 100) + "%";
}

function render(){
  const r = R[at], st = S[r.pmid] || {};
  $("wrap").innerHTML = "";
  const meta = document.createElement("div");
  meta.className = "meta";
  const a = document.createElement("a");
  a.href = "https://pubmed.ncbi.nlm.nih.gov/" + r.pmid + "/";
  a.target = "_blank"; a.rel = "noreferrer"; a.textContent = "PMID " + r.pmid;
  meta.append(document.createTextNode("#" + String(r.i).padStart(2,"0")), a);
  if (r.jr) meta.append(document.createTextNode(r.jr + (r.yr ? " " + r.yr : "")));
  const ti = document.createElement("h1"); ti.className = "ti"; ti.textContent = r.ti;
  const ab = document.createElement("div");
  ab.className = "ab" + (r.ab ? "" : " none");
  ab.textContent = r.ab || "No abstract in PubMed — judge from the title, or open the record.";
  $("wrap").append(meta, ti, ab);

  if (r.sug){
    const sg = document.createElement("div"); sg.className = "sug";
    const lb = document.createElement("span"); lb.className = "lab";
    lb.textContent = "Claude would say \u2014 your tap is what counts";
    const v = document.createElement("span");
    v.className = "v " + (r.sug === "eligible" ? "y" : "n");
    v.textContent = r.sug === "eligible" ? "Eligible" : ("Excluded" + (r.sf ? " (fails " + r.sf + ")" : ""));
    const wy = document.createElement("div"); wy.className = "why"; wy.textContent = r.why;
    sg.append(lb, v, wy); $("wrap").append(sg);
  }
  const fw = document.createElement("div"); fw.className = "fails"; fw.hidden = st.decision !== "excluded";
  const lab = document.createElement("span"); lab.textContent = "which fails?"; fw.append(lab);
  ["i","ii","iii"].forEach(f => {
    const b = document.createElement("button");
    b.className = "chip"; b.textContent = f;
    b.setAttribute("aria-pressed", String((st.fails||[]).includes(f)));
    b.onclick = () => { const cur = S[r.pmid] || {}; const fl = (cur.fails||[]).slice();
      const k = fl.indexOf(f); k < 0 ? fl.push(f) : fl.splice(k,1);
      save(r, {...cur, fails: fl}); };
    fw.append(b);
  });
  const nt = document.createElement("input");
  nt.className = "note"; nt.id = "note-" + r.pmid; nt.placeholder = "reason, optional";
  nt.value = st.note || "";
  let t = null;
  nt.oninput = () => { clearTimeout(t); t = setTimeout(() => {
    const cur = S[r.pmid] || {}; if (cur.decision) save(r, {...cur, note: nt.value}); }, 700); };
  $("wrap").append(fw, nt);

  $("yes").setAttribute("aria-pressed", String(st.decision === "eligible"));
  $("no").setAttribute("aria-pressed", String(st.decision === "excluded"));
  $("pos").textContent = (at + 1) + " of " + R.length;
  $("prev").disabled = at === 0;
  $("next").textContent = at === R.length - 1 ? "Summary →" : (st.decision ? "Next →" : "Skip →");
  $("main").scrollTop = 0;
  paintHeader();
}

async function save(r, body){
  S[r.pmid] = {decision: body.decision || null, fails: body.fails || [], note: body.note || ""};
  render();
  if (!db || saving) return;
  saving = true;
  try {
    await db.doc("labels/" + r.pmid).set({
      index: r.i, pmid: r.pmid, decision: S[r.pmid].decision,
      fails: S[r.pmid].fails, note: S[r.pmid].note,
      suggested: r.sug || null,
      matched_suggestion: S[r.pmid].decision ? (S[r.pmid].decision === r.sug) : null,
      at: new Date().toISOString()});
  } catch (e) {
    if (e && e.code === "invalid_argument") $("count").textContent = "read-only";
  } finally { saving = false; }
}

function pick(v){
  const r = R[at], cur = S[r.pmid] || {};
  const d = cur.decision === v ? null : v;
  save(r, {...cur, decision: d, fails: d === "excluded" ? (cur.fails||[]) : []});
  if (d) setTimeout(() => { const nx = R.findIndex((x,k) => k > at && !(S[x.pmid]||{}).decision);
    if (nx > -1) { at = nx; render(); } else if (decided() === R.length) summary(); }, 160);
}
$("yes").onclick = () => pick("eligible");
$("no").onclick  = () => pick("excluded");
$("prev").onclick = () => { if (at > 0) { at--; render(); } };
$("next").onclick = () => { if (at < R.length - 1) { at++; render(); } else summary(); };

function summary(){
  const dec = R.map(r => S[r.pmid] || {}), n = dec.filter(d => d.decision).length;
  const el = dec.filter(d => d.decision === "eligible").length;
  $("foot").hidden = true;
  $("wrap").innerHTML = "";
  if (n < R.length){
    const w = document.createElement("div"); w.className = "warn";
    w.textContent = (R.length - n) + " record" + (R.length-n>1?"s":"") + " still unjudged — the precision figure needs all " + R.length + ".";
    $("wrap").append(w);
  }
  const d = document.createElement("div"); d.className = "done";
  const h = document.createElement("h2"); h.textContent = n === R.length ? "All 60 judged" : "Progress saved";
  const p1 = document.createElement("p");
  p1.textContent = db ? "Saved. Claude can read these now — nothing to download."
                      : "Saved on this device only: this view could not reach the store. Reopen the link from the chat.";
  d.append(h, p1);
  const t = document.createElement("div"); t.className = "tally";
  [["judged", n], ["eligible", el], ["excluded", n - el]].forEach(([k, v]) => {
    const c = document.createElement("div"); c.textContent = k;
    const b = document.createElement("b"); b.textContent = v; c.append(b); t.append(c); });
  d.append(t);
  const back = document.createElement("button");
  back.className = "critbtn"; back.style.marginTop = "14px";
  back.textContent = n < R.length ? "Go to the first unjudged record" : "Review from the start";
  back.onclick = () => { const k = R.findIndex(r => !(S[r.pmid]||{}).decision);
    at = k > -1 ? k : 0; $("foot").hidden = false; render(); };
  d.append(back);
  $("wrap").append(d);
  paintHeader();
}

render();

(async () => {
  db = await (window.claude?.use?.("db") ?? Promise.resolve(null));
  if (!db) return;
  try {
    const snap = await db.collection("labels").get();
    snap.docs.forEach(doc => { const v = doc.data() || {};
      if (v.pmid) S[v.pmid] = {decision: v.decision || null, fails: v.fails || [], note: v.note || ""}; });
    const k = R.findIndex(r => !(S[r.pmid]||{}).decision);
    at = k > -1 ? k : 0;
    if (decided() === R.length) summary(); else render();
  } catch (e) { /* keep the local view */ }
})();
</script>
"""
open(os.path.join(HERE, "artifact_sheet.html"), "w").write(HTML.replace("__DATA__", json.dumps(rows, ensure_ascii=False)))
print("wrote artifact_sheet.html", os.path.getsize(os.path.join(HERE, "artifact_sheet.html")), "bytes")
