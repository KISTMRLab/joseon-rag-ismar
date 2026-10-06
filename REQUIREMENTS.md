# Requirements and provenance — ISMAR adjunct variant

## Paper-supported facts

The complete ISMAR adjunct paper was read before this requirements file was written. It describes Annals/Sejong data, whole-article dynamic chunking, year/month/day metadata, GPT query regeneration, date filtering, maximum-token retrieval, evidence-based answers, and a Unity AI agent. Voice is converted with STT; the answer is synthesized with TTS while matching body and lip motion are presented. The abstract describes the broader Annals as 49,646,667 characters and the experiment uses 30 benchmark questions.

The full journal paper was also read as shared retrieval-architecture context. Details present only there—30,949 chunks, 163 Sejong volumes, explicit failure analysis, and extended limitations—must not be attributed to the shorter ISMAR paper.

## Functional requirements

The public implementation provides the paper-supported retrieval path and a distinct integration artifact. The retrieval path covers:

- a polite, resumable Sejong Annals crawler with lunar-date metadata;
- whole-article chunks;
- exact, partial and range date filtering;
- maximum-token packing;
- a similarity floor with explicit abstention;
- cited facts plus contextual analysis.

The integration artifact consists of:

- timed utterances whose spoken text is citation-free, with source IDs kept as per-utterance metadata;
- descriptive motion labels;
- microphone or file speech input through a local STT endpoint;
- a portable browser demonstrator suitable for replacing with user-owned STT/TTS/avatar components.

## Assumptions and substitutions

This is independent educational code. The following are explicit baselines or adapters:

- Korean-aware TF-IDF (character bigrams), extractive answers and reranking;
- inferred-date widening and the similarity floors;
- fit-or-stop packing and a tiktoken-or-conservative token count;
- sentence timing and rule-selected motion labels;
- prompts written from the paper's description;
- the bundled fictional CC0 Three.js character;
- a one-month test sample in place of the full corpus. `joseon-agent crawl --sample` fetches Sejong year 2, month 5 (87 articles in 165 s on 6 October 2026), holds at most 100 records and runs at no less than 1.5 s per request. `scripts/start_demo.py --sample-crawl` serves it; the default demo stays on the authored offline examples. Crawled text stays under ignored `data/` and is not redistributed, and the full crawl is optional.

In the browser, body motion comes from BEAT co-speech retrieval and mouth motion from the shared speech renderer; the motion labels are metadata only. Browser speech and optional user-configured local STT/TTS can play the event contract. None of this reproduces the paper's GPT services, Unity scene, lip-sync system, animation generator, models, assets, benchmark scores, or institute implementation. The adjunct paper's Table 1 reports the same scores as the related journal article; this repository does not reproduce them.

## Bundled fictional avatar substitution

Two newly generated fictional CC0 humanoids replace the original avatar assets in the browser demo. They provide a 53-bone rig and named ARKit/viseme targets. Motion retargeting adapts source joints to their bind pose; mouth shapes follow a rule-based text-to-phoneme-to-viseme track timed to speech playback, an approximation rather than forced phoneme alignment. The optional recorded BEAT companion inspects public motion, face and audio files prepared locally, independently of the paper's learned algorithm. No dataset recordings or trained weights are bundled.

## Local recorded co-speech integration

The browser application retrieves prepared BEAT body-motion clips with `wild` mode: a current public-demo adapter; the ISMAR paper does not specify this body-motion method. The first `python scripts/start_demo.py` run fetches a small official BVH/TextGrid sample, constructs a nine-clip bank, and fits the local retrieval artifact under ignored `outputs/beat-library/`. Install `scripts/requirements-demo.txt` first. Preparation code and method dependencies are vendored in this repository; no sibling clone, original institute library, full dataset, or pretrained weights are bundled. The article-preserving retrieval, date filtering, citations, and timed answer events remain this application's core. The separate recorded-motion companion remains available for local motion/face/audio inspection.
