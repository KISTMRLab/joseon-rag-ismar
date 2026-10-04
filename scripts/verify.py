"""Build an index, answer a question, and produce digital-human events."""
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
(OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "answer.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
write_agent_package(result, OUT / "agent")
if not result["citations"] or not (OUT / "agent" / "agent-demo.html").exists():
    raise RuntimeError("verify run did not produce cited agent output")
print(json.dumps({"articles": len(index["articles"]), "backend": index["backend"], "citations": [item["id"] for item in result["citations"]], "outputs": ["index.json", "answer.json", "agent/agent-events.json", "agent/agent-demo.html"]}, indent=2))

