"""Timed speech events for the embodied agent.

Each utterance carries the text to speak with source IDs removed; the IDs stay
in ``citations`` on the same utterance. ``motion_label`` is descriptive metadata
from simple keyword rules: in the browser demo, body motion comes from the BEAT
co-speech retrieval (``wild`` mode) and mouth motion from the shared speech
renderer, not from these labels.
"""
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any

_CITE = re.compile(r"\[([^\[\]\s]+(?:\s*[,;]\s*[^\[\]\s]+)*)\]")
_SECTION = re.compile(r"^\s*(?:#+\s*)?(objective facts|contextual analysis)\s*:?\s*", re.I)
_SENTENCE = re.compile(r"[^.!?。]*(?:[.!?。]+|$)")
_WORD = re.compile(r"[0-9A-Za-z가-힣一-鿿]+")


def _motion_label(sentence: str) -> str:
    low = sentence.lower()
    if any(x in low for x in ("first", "began", "established")): return "introduce"
    if any(x in low for x in ("however", "although", "conflict")): return "contrast"
    if any(x in low for x in ("therefore", "thus", "purpose")): return "emphasize"
    return "explain"


def spoken_segments(answer: str, known_ids: set[str] | None = None) -> list[dict[str, Any]]:
    """Split an answer into spoken sentences, binding each [id] to the sentence it
    follows ("Fact. [id]") or closes ("Fact [id]."). Section labels are not spoken."""
    segments: list[dict[str, Any]] = []
    section = "answer"
    for raw_line in answer.splitlines():
        line = raw_line.strip().lstrip("-*• ").strip()
        heading = _SECTION.match(line)
        if heading:
            section = "facts" if heading.group(1).lower().startswith("objective") else "analysis"
            line = line[heading.end():]
        if line.upper().startswith("INSUFFICIENT EVIDENCE:"):
            section = "abstention"; line = line.split(":", 1)[1]
        ids_by_slot: list[list[str]] = []

        def hold(m: re.Match[str]) -> str:
            # Every bracketed ID is removed from speech; only IDs of retrieved sources are kept as citations.
            ids = [i for i in re.split(r"\s*[,;]\s*", m.group(1)) if known_ids is None or i in known_ids]
            ids_by_slot.append(ids); return f"\x00{len(ids_by_slot) - 1}\x00"
        held = _CITE.sub(hold, line)
        # Citation placeholders right after sentence punctuation belong to that sentence.
        held = re.sub(r"([.!?。]+)((?:\s*\x00\d+\x00)+)", lambda m: m.group(2) + m.group(1), held)
        for chunk in _SENTENCE.findall(held):
            ids = [i for slot in re.findall(r"\x00(\d+)\x00", chunk) for i in ids_by_slot[int(slot)]]
            text = re.sub(r"\s*\x00\d+\x00", "", chunk)
            text = re.sub(r"\s+([.!?。,])", r"\1", re.sub(r"\s+", " ", text)).strip()
            if _WORD.search(text):
                segments.append({"text": text, "citations": list(dict.fromkeys(ids)), "section": section})
            elif ids and segments:
                segments[-1]["citations"] = list(dict.fromkeys(segments[-1]["citations"] + ids))
    return segments


def agent_events(result: dict[str, Any]) -> dict[str, Any]:
    known = {c["id"] for c in result.get("citations", [])} | {e["article"]["id"] for e in result.get("trace", {}).get("evidence", [])}
    events = []; t = 0.0
    for i, seg in enumerate(spoken_segments(result["answer"], known or None), 1):
        words = _WORD.findall(seg["text"]); duration = max(1.2, len(words) / 2.7)
        events.append({"id": f"utterance-{i}", "start": round(t, 3), "duration": round(duration, 3), "kind": "speech",
                       "text": seg["text"], "citations": seg["citations"], "section": seg["section"], "motion_label": _motion_label(seg["text"])})
        t += duration
    return {"schema": "paperreach.joseon.digital-human.v2", "duration": round(t, 3), "events": events,
            "citations": result.get("citations", []), "abstained": bool(result.get("abstained")),
            "note": ("Utterance text is citation-free for speech; source IDs stay in each event's citations. Start/duration are estimates. "
                     "motion_label is descriptive metadata; the browser demo drives body motion with BEAT co-speech retrieval and "
                     "mouth motion from the speech renderer.")}


def write_agent_package(result: dict[str, Any], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True); data = agent_events(result)
    (out / "agent-events.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    packed = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = f"""<!doctype html><meta charset='utf-8'><title>Joseon digital-human adapter</title><style>body{{font:16px system-ui;background:#121827;color:#eef2ff;display:grid;place-items:center;min-height:100vh}}main{{max-width:760px;padding:30px}}#head{{width:170px;height:210px;border-radius:48% 48% 45% 45%;background:#d5a77f;position:relative;margin:auto}}#mouth{{position:absolute;left:60px;top:145px;width:50px;height:8px;background:#572d2d;border-radius:50%}}#bubble{{background:white;color:#172033;padding:18px;border-radius:18px;margin-top:24px;min-height:70px}}small{{color:#a5b4fc}}</style><main><div id='head'><div id='mouth'></div></div><div id='bubble'>Press play to inspect the timed utterance events.</div><button id='play'>Play</button> <small id='meta'></small><script>const D={packed};let start;document.querySelector('#play').onclick=()=>{{start=performance.now();requestAnimationFrame(tick)}};function tick(now){{let t=(now-start)/1000,e=D.events.find(x=>x.start<=t&&t<x.start+x.duration);if(!e){{document.querySelector('#mouth').style.height='8px';return}}if(document.querySelector('#bubble').textContent!==e.text)document.querySelector('#bubble').textContent=e.text;document.querySelector('#meta').textContent='sources: '+(e.citations.join(', ')||'none')+' · label: '+e.motion_label;document.querySelector('#mouth').style.height=Math.floor(t*7)%2?'24px':'8px';requestAnimationFrame(tick)}};</script></main>"""
    (out / "agent-demo.html").write_text(page, encoding="utf-8")
