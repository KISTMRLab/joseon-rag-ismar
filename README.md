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

The retrieval path shares its research lineage with the separate [historical-analysis journal paper](https://github.com/ghazanPK/joseon-rag-journal); this repo adds the embodied presentation adapter while keeping its own citation and scope.

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

<!-- demo-preview:start -->
## Demo preview

![Joseon Rag Ismar runnable demo](demo-assets/preview.png)

*Local demo with small starter examples; the capture illustrates the interface, not a reproduced paper benchmark.*

From the repository root, using the Python environment described below:

```sh
python -m pip install -e .
python scripts/start_demo.py
```

Open **http://127.0.0.1:8080/**. Click **Search evidence** on the prefilled question, then **Speak answer** to play the cited answer through the avatar. The launcher selects the bundled inputs automatically; it also builds the small authored index for RAG demos. Avatar demos prepare their pinned Three.js modules on first launch, so that step needs internet access. Model weights and public datasets are optional for the starter workflow and are prepared separately for real-data use.

The 3D presentation uses shared Three.js avatar components and bundled fictional CC0 characters. The paper-specific algorithms and data adapters live in this repository.

<!-- demo-preview:end -->

## Implementation and usage

<!-- implementation-guide -->

This repository combines article-preserving historical retrieval with a digital-human integration artifact. In addition to cited answers and an auditable retrieval trace, it emits timed speech segments, response-conditioned body-motion labels, lip markers, and a portable avatar adapter demo.

**Citation.** Jeong Ha Lee, Ghazanfar Ali, and Jae-In Hwang. “RAG based AI-Agent for Contextualized Analysis of High-Density Historical Records: Application to the Annals of the Joseon Dynasty.” *2025 IEEE International Symposium on Mixed and Augmented Reality Adjunct (ISMAR-Adjunct)* (2025). [https://doi.org/10.1109/ISMAR-Adjunct68609.2025.00243](https://doi.org/10.1109/ISMAR-Adjunct68609.2025.00243). Status: published.

This is an independent educational implementation. It is not the institute implementation and does not ship the Annals corpus, crawler output, API credentials, embedding cache, model weights, benchmark, or prompts.

### Start the embodied evidence demo

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python scripts/prepare_viewer.py
joseon-agent build examples/articles.jsonl --out outputs/demo.index.json
joseon-agent serve outputs/demo.index.json --events examples/events.json
```

Open `http://127.0.0.1:8766` to inspect cited evidence and play the procedural 3D avatar. The included articles are authored interface examples, not Annals records. For an offline JSON/event check, run `python scripts/verify.py`; `outputs/verify/agent/agent-events.json` contains the engine-neutral integration contract. Motion and mouth timing remain adapter baselines rather than reproduced Unity animation.

### Bring your own public corpus

Download records through the official National Institute of Korean History service: [Annals of the Joseon Dynasty](https://sillok.history.go.kr/). Follow the site's current access terms and robots/API guidance. Export one article per JSONL row (or CSV row) with:

```json
{"id":"stable-id","date":"YYYY-MM-DD","title":"article title","text":"complete article text","source_url":"https://...","volume":"optional"}
```

`year`, `month`, and `day` columns may replace `date`. Keep downloads under ignored `data/`. This code does not crawl the site because endpoint structure and access policy can change.

After exporting real articles with that contract, run `joseon-agent build data/articles.jsonl --out outputs/my.index.json`, then `joseon-agent ask outputs/my.index.json "your question" --events examples/events.json --out outputs/my-answer.json --agent-out outputs/my-agent`. The verify script uses the same loader, retrieval, answer, citation, and digital-human adapter paths.

The default index is an honestly labeled TF-IDF baseline. For a cache-only sentence-transformer, install `python -m pip install -e ".[semantic]"` and run `joseon-agent build data/articles.jsonl --out outputs/semantic.index.json --backend sentence-transformer --model path-or-cached-model-name`. The loader uses `local_files_only=True` and fails rather than downloading weights. The CLI also supports a user-run OpenAI-compatible endpoint or local JSON-in/query-out command adapter.

Extractive generation is the default. `--generator endpoint --base-url http://localhost:8000/v1 --model your-model` sends a source-labeled evidence prompt to a user-operated compatible endpoint. `--generator command --generator-command "your-program --json"` uses a local JSON adapter. Their text is explicitly marked unverified and should be checked against returned source IDs before digital-human playback.

This baseline cannot reproduce the reported evaluation scores. It does not know that an inferred date is historically correct, and the primary source may contain variant or conflicting accounts. Inspect citations and the trace. See [REQUIREMENTS.md](REQUIREMENTS.md) for the paper/assumption boundary.


### Browser demo and selected-page import

The CLI and local browser share the same article-preserving index and retrieval code. The bundled articles are authored demonstration text, not historical records. After installing the package:

```powershell
joseon-agent build examples/articles.jsonl --out outputs/demo.index.json
joseon-agent serve outputs/demo.index.json --events examples/events.json
```

Open http://127.0.0.1:8766 to inspect rewritten questions, date filters, selected full articles, scores, token use and cited answers. Playback exposes timed speech and motion events alongside the evidence. Add `--base-url http://127.0.0.1:8000/v1 --model your-model` to enable model-powered rewrite and grounded generation controls; inspect model output against the source articles.

For a single public article you have selected and are permitted to use, import saved HTML or fetch that exact URL. The URL, manually supplied article ID/date, and extracted text are kept in each JSONL record. Review the extraction before building; complex pages may include navigation or omit JavaScript-rendered text.

```powershell
joseon-agent import-html "https://sillok.history.go.kr/your-selected-article" --file data/selected-article.html --id selected-id --date 1420-05-12 --title "Article title" --out data/articles.jsonl
joseon-agent build data/articles.jsonl --out outputs/my.index.json
joseon-agent serve outputs/my.index.json --events examples/events.json
```

### 3D playback and optional local speech

The quickstart prepares pinned Three.js 0.170.0 in ignored `static/vendor/`. The character is generated procedurally in code; no original Unity avatar or animation asset is included. Browser speech works without model downloads. For optional local Kokoro TTS and faster-whisper ASR, run `python -m pip install -e ".[speech]"`, install the English phonemizer requirements from [Kokoro's setup guide](https://github.com/hexgrad/kokoro) (including `espeak-ng` where required), then set `KOKORO_MODEL_DIR` to a local folder containing `config.json`, `kokoro-v1_0.pth`, and `voices/af_heart.pt`. Set `WHISPER_MODEL_DIR` to a local converted faster-whisper folder containing `model.bin`. Audio upload transcribes locally only when ASR is configured; typed input remains available. Timed motion is a research adapter, not recovered Unity animation.

<!-- avatar-recorded-motion:start -->
## Bundled characters and recorded public motion

The browser demos include Rowan and Mira, two new fictional GLB characters built with MPFB and MakeHuman community assets under CC0 1.0. See [avatar licensing and provenance](static/avatars/LICENSE.md). Use the character selector in the stage. The shared renderer supports body bones, ARKit facial channels, and approximate speaking motion.

Recorded motion is adapted to the characters' proportions. Palm landmarks set hand orientation; finger curl uses bounded hinge bends and preserves the character's finger spacing. Thumb-base opposition stays in the authored pose, with conservative recorded curl at the remaining joints. Distal bends are estimated from the preceding joint when fingertip landmarks are absent. Use the companion's hand close-up views to inspect the result.

The [avatar motion companion](static/recorded-motion.html) opens at `/static/recorded-motion.html` while the demo server is running. A small authored motion and face sample loads automatically; click **Play** without uploading files. It also plays locally selected BEAT motion, face, and WAV files on the bundled characters. These are presentation and data-inspection tools, separate from the paper implementation. No BEAT recording, dataset archive, or trained model is bundled. For recorded public motion, install the one preparation dependency and fetch a small official sample into ignored `outputs/beat-demo/`:

```sh
python -m pip install numpy
python scripts/beat_demo/fetch_modalities.py --speaker 1 --sequence 1_wayne_0_1_1 --include-bvh --max-bytes 25000000 --output-dir outputs/beat-demo/source
python scripts/beat_demo/prepare_bvh.py --bvh outputs/beat-demo/source/1_wayne_0_1_1.bvh --output outputs/beat-demo/sample/1_wayne_0_1_1-raw-motion.json --frames 120
python scripts/beat_demo/prepare_modalities.py --sequence 1_wayne_0_1_1 --source outputs/beat-demo/source --output outputs/beat-demo/sample --frames 120
```

Open the companion and select `outputs/beat-demo/sample/1_wayne_0_1_1-raw-motion.json`, `1_wayne_0_1_1-face.json`, and `1_wayne_0_1_1.wav`. The downloader caps each original file at 25 MB; the prepared clip contains up to 120 frames. The viewer uses local files and does not upload them. For other BEAT takes, substitute a matching official speaker and sequence ID.

If you already have OmniMo's processed 52-joint Unity humanoid data, use that normalized motion instead:

```sh
python scripts/beat_demo/prepare.py --dataset /path/to/processed/beat --speaker 1 --take 1_wayne_0_1_1 --output outputs/beat-demo/sample/1_wayne_0_1_1-motion.json --max-frames 120
```

Select the resulting `*-motion.json` in the companion. Its metadata carries the humanoid joint mapping and source-to-avatar coordinate conversion. The viewer fits source FK directions from the avatar's bind pose, following the spine explicitly at branching joints. This avoids applying incompatible source bone twist to the MPFB skin; it does not reproduce exact performer twist. The adapter supports Unity proximal/intermediate/distal finger names. Raw BVH remains a public-data alternative; do not mix the two skeleton conventions.
<!-- avatar-recorded-motion:end -->
