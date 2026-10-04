from __future__ import annotations
import html, json, re
from pathlib import Path
from typing import Any

def agent_events(result: dict[str, Any]) -> dict[str, Any]:
    sentences = [x.strip() for x in re.split(r"(?<=[.!?])\s+", result["answer"]) if x.strip()]
    events = []; t = 0.0
    for i, sentence in enumerate(sentences, 1):
        words = re.findall(r"[0-9A-Za-z가-힣]+", sentence); duration = max(1.2, len(words) / 2.7)
        low = sentence.lower()
        motion = "explain"
        if any(x in low for x in ("first", "began", "established")): motion = "introduce"
        elif any(x in low for x in ("however", "although", "conflict")): motion = "contrast"
        elif any(x in low for x in ("therefore", "thus", "purpose")): motion = "emphasize"
        visemes = [{"time": round(t + duration * n / max(1, len(words)), 3), "shape": "open" if n % 2 else "closed"} for n in range(len(words))]
        events.append({"id": f"utterance-{i}", "start": round(t, 3), "duration": round(duration, 3), "kind": "speech", "text": sentence, "motion": motion, "visemes": visemes})
        t += duration
    return {"schema": "paperreach.joseon.digital-human.v1", "duration": round(t, 3), "events": events, "citations": result.get("citations", []), "note": "Timing, visemes, and motion labels are adapter signals, not generated animation assets."}

def write_agent_package(result: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True); data = agent_events(result)
    (out / "agent-events.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    packed = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = f"""<!doctype html><meta charset='utf-8'><title>Joseon digital-human adapter</title><style>body{{font:16px system-ui;background:#121827;color:#eef2ff;display:grid;place-items:center;min-height:100vh}}main{{max-width:760px;padding:30px}}#head{{width:170px;height:210px;border-radius:48% 48% 45% 45%;background:#d5a77f;position:relative;margin:auto}}#mouth{{position:absolute;left:60px;top:145px;width:50px;height:8px;background:#572d2d;border-radius:50%}}#bubble{{background:white;color:#172033;padding:18px;border-radius:18px;margin-top:24px;min-height:70px}}small{{color:#a5b4fc}}</style><main><div id='head'><div id='mouth'></div></div><div id='bubble'>Press play to inspect synchronized adapter events.</div><button id='play'>Play</button> <small id='motion'></small><script>const D={packed};let start;document.querySelector('#play').onclick=()=>{{start=performance.now();requestAnimationFrame(tick)}};function tick(now){{let t=(now-start)/1000,e=D.events.find(x=>x.start<=t&&t<x.start+x.duration);if(!e)return;if(document.querySelector('#bubble').textContent!==e.text)document.querySelector('#bubble').textContent=e.text;document.querySelector('#motion').textContent='motion: '+e.motion;let v=e.visemes.slice().reverse().find(x=>x.time<=t);document.querySelector('#mouth').style.height=v&&v.shape==='open'?'28px':'8px';requestAnimationFrame(tick)}};</script></main>"""
    (out / "agent-demo.html").write_text(page, encoding="utf-8")

