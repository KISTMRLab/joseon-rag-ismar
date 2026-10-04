# RAG based AI-Agent for Contextualized Analysis of High-Density Historical Records: Application to the Annals of the Joseon Dynasty

**Jeongha Lee, Ghazanfar Ali, Jae-In Hwang**

**IEEE ISMAR-Adjunct · 2025** · Published

[Paper / publisher](https://doi.org/10.1109/ismar-adjunct68609.2025.00243) · [Project page](https://ghazanfarali.com/research/joseon-rag-ismar/) · [BibTeX](citation.bib) · [Requirements](REQUIREMENTS.md) · [Code & setup](#implementation-and-usage)

> An embodied agent makes historical source retrieval conversational.

![Method diagram from Figure 2 of the joseon-rag-ismar paper](paper-assets/method.png)

*Original method figure from the paper: Figure 2, PDF page 2. Extracted for this research introduction; the diagram describes the original system, not verification of this reimplementation.*

## Why this research

Historical retrieval becomes more accessible when an embodied agent can explain its evidence conversationally. This adjunct paper connects the Annals retrieval pipeline with a speaking, animated agent.

This adjunct paper integrates a retrieval-augmented language model with a Unity-based 3D agent. Questions produce grounded historical answers delivered through synchronized voice and body motion. It is a separate publication from the related journal article.

## Method at a glance

**User question** → **Historical RAG** → **Embodied answer**

| | Research system |
|---|---|
| Input | Voice or text questions about the Annals |
| Method | Historical RAG pipeline integrated with a Unity agent |
| Output | Historical answers with voice and contextual body animation |

## Evidence and scope

Comparison on factual accuracy, reliability, and reasonableness against the paper’s GPT-4o and AI-Assistant v2 baselines

**Attribution:** These findings describe the paper or manuscript, not results obtained with this repository's code.

**Study context:** Annals corpus of 49,646,667 characters; 30 benchmark questions.

**Limitations:** A 30-question historical benchmark is limited in scope; the journal’s measurements should not be treated as measurements of this adjunct paper.

## Explore the implementation

The historical retrieval core plus timed digital-human presentation events and a schematic browser agent; native Unity rendering is outside this implementation.

This repository contains independently written research code. The institute's original source, datasets and trained models are not distributed. Public-data preparation, commands, assumptions and checks are documented below and in [REQUIREMENTS.md](REQUIREMENTS.md).

## Resources and citation

Read the paper through its [publisher record](https://doi.org/10.1109/ismar-adjunct68609.2025.00243). PDFs are hosted by publishers or preprint archives rather than stored in this repository.

Please cite the research paper when using its ideas; [download the BibTeX citation](citation.bib). The implementation has its own documented scope.

## Implementation and usage

<!-- implementation-guide -->

This repository combines article-preserving historical retrieval with a digital-human integration artifact. In addition to cited answers and an auditable retrieval trace, it emits timed speech segments, response-conditioned body-motion labels, lip markers, and a portable avatar adapter demo.

**Citation.** Jeong Ha Lee, Ghazanfar Ali, and Jae-In Hwang. “RAG based AI-Agent for Contextualized Analysis of High-Density Historical Records: Application to the Annals of the Joseon Dynasty.” *2025 IEEE International Symposium on Mixed and Augmented Reality Adjunct (ISMAR-Adjunct)* (2025). [https://doi.org/10.1109/ISMAR-Adjunct68609.2025.00243](https://doi.org/10.1109/ISMAR-Adjunct68609.2025.00243). Status: published.

This is an independent educational implementation. It is not the institute implementation and does not ship the Annals corpus, crawler output, API credentials, embedding cache, model weights, benchmark, or prompts.

### Run the offline example

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python scripts/smoke.py
start outputs/smoke/agent/agent-demo.html
```

The answer JSON includes claims, citations, filter and ranking trace. `agent-events.json` is an engine-neutral integration contract; `agent-demo.html` visualizes it. The motion and mouth timing are functional adapter baselines rather than reproduced Unity animation. The included corpus is an authored artificial schema fixture, not Annals text or evidence for historical claims.

### Bring your own public corpus

Download records through the official National Institute of Korean History service: [Annals of the Joseon Dynasty](https://sillok.history.go.kr/). Follow the site's current access terms and robots/API guidance. Export one article per JSONL row (or CSV row) with:

```json
{"id":"stable-id","date":"YYYY-MM-DD","title":"article title","text":"complete article text","source_url":"https://...","volume":"optional"}
```

`year`, `month`, and `day` columns may replace `date`. Keep downloads under ignored `data/`. This code does not crawl the site because endpoint structure and access policy can change.

After exporting real articles with that contract, run `joseon-agent build data/articles.jsonl --out outputs/my.index.json`, then `joseon-agent ask outputs/my.index.json "your question" --events examples/events.json --out outputs/my-answer.json --agent-out outputs/my-agent`. The smoke script uses the same loader, retrieval, answer, citation, and digital-human adapter paths.

The default index is an honestly labeled TF-IDF baseline. For a cache-only sentence-transformer, install `python -m pip install -e ".[semantic]"` and run `joseon-agent build data/articles.jsonl --out outputs/semantic.index.json --backend sentence-transformer --model path-or-cached-model-name`. The loader uses `local_files_only=True` and fails rather than downloading weights. The CLI also supports a user-run OpenAI-compatible endpoint or local JSON-in/query-out command adapter.

Extractive generation is the default. `--generator endpoint --base-url http://localhost:8000/v1 --model your-model` sends a source-labeled evidence prompt to a user-operated compatible endpoint. `--generator command --generator-command "your-program --json"` uses a local JSON adapter. Their text is explicitly marked unverified and should be checked against returned source IDs before digital-human playback.

This baseline cannot reproduce the reported evaluation scores. It does not know that an inferred date is historically correct, and the primary source may contain variant or conflicting accounts. Inspect citations and the trace. See [REQUIREMENTS.md](REQUIREMENTS.md) for the paper/assumption boundary.
