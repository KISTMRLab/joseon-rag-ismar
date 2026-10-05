import unittest
from joseon_rag.core import Article, RuleRegenerator, answer, build_index, load_articles, query_date, retrieve
from joseon_rag.importer import import_page
from joseon_rag.agent import agent_events

class RagTest(unittest.TestCase):
    def test_bundled_records_identify_authored_provenance(self):
        from pathlib import Path
        path = Path(__file__).parents[1] / "examples" / "articles.jsonl"
        articles = load_articles(path)
        self.assertTrue(articles)
        self.assertTrue(all(a.title.startswith("Authored example:") for a in articles))
        self.assertTrue(all(a.source_url.endswith("/joseon-rag-ismar/blob/main/examples/articles.jsonl") for a in articles))

    def test_selected_html_keeps_provenance_and_full_article(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); source = folder / "page.html"; output = folder / "records.jsonl"
            source.write_text("<html><title>Public article</title><nav>Discard menu</nav><article><p>First paragraph describes a dated event and its participants.</p><p>Second paragraph supplies the source context and historical details.</p></article></html>", encoding="utf-8")
            import_page("https://example.org/article", output, source_file=source, article_id="record-1", date="1420-05-12")
            article = load_articles(output)[0]
            self.assertEqual((article.id, article.year, article.month, article.day, article.source_url), ("record-1", 1420, 5, 12, "https://example.org/article"))
            self.assertIn("First paragraph", article.text)
            self.assertIn("Second paragraph", article.text)
            self.assertNotIn("Discard menu", article.text)
    def test_filter_budget_and_citation(self):
        idx = build_index([Article("a", "Scholars discussed education and royal study.", "Policy", 1420, 5, 12, "https://example/a"), Article("b", "A new script was published for the people.", "Script", 1446, 9, 29, "https://example/b")])
        q = RuleRegenerator({"hall": {"year": 1420, "aliases": ["scholars"]}}).rewrite("Tell me about the hall")
        result = answer(retrieve(idx, "Tell me about the hall", q, 200))
        self.assertIn("a", result["answer"]); self.assertEqual(result["trace"]["date_filter"]["year"], 1420)
        self.assertTrue(agent_events(result)["events"])

    def test_full_iso_date(self):
        import json, tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.jsonl"; p.write_text(json.dumps({"id":"x","date":"1420-05-12","text":"record"}))
            a = load_articles(p)[0]; self.assertEqual((a.year, a.month, a.day), (1420, 5, 12))

    def test_later_joseon_years_and_explicit_date_precedence(self):
        self.assertEqual(query_date("1652년 기록"), (1652, None, None))
        self.assertEqual(query_date("1799-12-30 record"), (1799, 12, 30))
        idx = build_index([Article("old", "event", year=1652), Article("new", "event", year=1799)])
        bundle = retrieve(idx, "What happened in 1652?", "What happened in 1799?", 100)
        self.assertEqual(bundle["date_filter"]["year"], 1652)

    def test_strict_budget_skips_indivisible_article(self):
        idx = build_index([Article("large", "word " * 100, year=1652)])
        self.assertEqual(retrieve(idx, "1652 word", "1652 word", 5)["evidence"], [])


class AgentEventTest(unittest.TestCase):
    def test_citations_removed_from_speech_and_bound_to_their_sentence(self):
        # Audit failure: "Fact one. [a] Fact two. [b]" was split so that "[a]" opened the next utterance.
        result = {"answer": "Objective facts:\n- Fact one about scholars. [a]\n- Fact two about ships. [b]\n\nContextual analysis:\nBoth were court matters [a, b].",
                  "citations": [{"id": "a"}, {"id": "b"}], "trace": {"evidence": []}}
        events = agent_events(result)["events"]
        self.assertEqual([e["text"] for e in events], ["Fact one about scholars.", "Fact two about ships.", "Both were court matters."])
        self.assertEqual([e["citations"] for e in events], [["a"], ["b"], ["a", "b"]])
        self.assertEqual([e["section"] for e in events], ["facts", "facts", "analysis"])
        self.assertTrue(all("[" not in e["text"] and "visemes" not in e and e["motion_label"] for e in events))

    def test_inline_and_unknown_citations_are_not_spoken(self):
        result = {"answer": "The hall was founded [k_1]. It trained scholars [ghost].","citations": [{"id": "k_1"}], "trace": {"evidence": []}}
        events = agent_events(result)["events"]
        self.assertEqual(events[0]["text"], "The hall was founded."); self.assertEqual(events[0]["citations"], ["k_1"])
        self.assertEqual(events[1]["text"], "It trained scholars."); self.assertEqual(events[1]["citations"], [])

    def test_abstention_is_spoken_without_marker(self):
        idx = build_index([Article("a", "Scholars discussed education.", "Hall", 1420, 5, 12)])
        result = answer(retrieve(idx, "Tell me about the moon landing", "Tell me about the moon landing", 500))
        data = agent_events(result)
        self.assertTrue(data["abstained"]); self.assertNotIn("INSUFFICIENT", data["events"][0]["text"])
        self.assertEqual(data["events"][0]["section"], "abstention")

if __name__ == "__main__": unittest.main()
