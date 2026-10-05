"""Build an index, answer a question and an erroneous question, and produce digital-human events."""
import json
from pathlib import Path

from joseon_rag.agent import write_agent_package
from joseon_rag.core import RuleRegenerator, answer, build_index, load_articles, retrieve

ROOT = Path(__file__).parents[1]
OUT = ROOT / "outputs" / "verify"
OUT.mkdir(parents=True, exist_ok=True)
index = build_index(load_articles(ROOT / "examples" / "articles.jsonl"))
events = json.loads((ROOT / "examples" / "events.json").read_text(encoding="utf-8"))
query = "What scholarly policy was discussed in 1420?"
result = answer(retrieve(index, query, RuleRegenerator(events).rewrite(query)))
erroneous = "Describe the new script for the people promulgated in 1420."
abstention = answer(retrieve(index, erroneous, RuleRegenerator(events).rewrite(erroneous)))
(OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "answer.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
write_agent_package(result, OUT / "agent")
write_agent_package(abstention, OUT / "agent-abstention")
spoken = json.loads((OUT / "agent" / "agent-events.json").read_text(encoding="utf-8"))
if not result["citations"] or not (OUT / "agent" / "agent-demo.html").exists():
    raise RuntimeError("verify run did not produce cited agent output")
if any("[" in e["text"] for e in spoken["events"]) or not any(e["citations"] for e in spoken["events"]):
    raise RuntimeError("spoken utterances must be citation-free with citations kept as event metadata")
if abstention["abstain_reason"] != "date-conflict":
    raise RuntimeError("date-contradicting question was answered instead of abstaining")
print(json.dumps({"articles": len(index["articles"]), "backend": index["backend"], "citations": [item["id"] for item in result["citations"]],
                  "utterances": [{"text": e["text"][:60], "citations": e["citations"]} for e in spoken["events"]],
                  "erroneous_question": abstention["abstain_reason"],
                  "outputs": ["index.json", "answer.json", "agent/agent-events.json", "agent/agent-demo.html", "agent-abstention/agent-events.json"]}, indent=2, ensure_ascii=False))
