# Requirements and provenance — ISMAR adjunct variant

## Paper-supported facts

The complete ISMAR adjunct paper was read before this requirements file was written. It describes Annals/Sejong data, whole-article dynamic chunking, year/month/day metadata, GPT query regeneration, date filtering, maximum-token retrieval, evidence-based answers, and a Unity AI agent. Voice is converted with STT; the answer is synthesized with TTS while matching body and lip motion are presented. The abstract describes the broader Annals as 49,646,667 characters and the experiment uses 30 benchmark questions.

The full journal paper was also read as shared retrieval-architecture context. Details present only there—30,949 chunks, 163 Sejong volumes, explicit failure analysis, and extended limitations—must not be attributed to the shorter ISMAR paper.

## Functional requirements

The public implementation provides the paper-supported retrieval path plus a distinct integration artifact: timed utterances, coarse response-conditioned body-motion labels, lip/viseme timing markers, citations, and a portable browser demonstrator suitable for replacing with user-owned STT/TTS/avatar components.

## Assumptions and substitutions

This is independent educational code. TF-IDF, extractive answers, reranking, inferred-date widening, sentence timing, alternating open/closed mouth markers, rule-selected motion labels, and the bundled fictional CC0 Three.js character are explicit baselines/adapters. Browser speech and optional user-configured local STT/TTS can play the event contract. They do not reproduce the paper's GPT services, Unity scene, lip-sync system, animation generator, models, assets, benchmark scores, or institute implementation.

## Bundled fictional avatar substitution

Two newly generated fictional CC0 humanoids replace the original avatar assets in the browser demo. They provide a 53-bone rig and named ARKit/viseme targets. Motion retargeting adapts source joints to their bind pose; speaking envelopes approximate mouth motion rather than phoneme alignment. The optional recorded BEAT companion inspects public motion, face and audio files prepared locally, independently of the paper's learned algorithm. No dataset recordings or trained weights are bundled.

## Local recorded co-speech integration

The browser application retrieves prepared BEAT body-motion clips with `wild` mode: a current public-demo adapter; the ISMAR paper does not specify this body-motion method. The first `python scripts/start_demo.py` run fetches a small official BVH/TextGrid sample, constructs a nine-clip bank, and fits the local retrieval artifact under ignored `outputs/beat-library/`. Install `scripts/requirements-demo.txt` first. Preparation code and method dependencies are vendored in this repository; no sibling clone, original institute library, full dataset, or pretrained weights are bundled. The article-preserving retrieval, date filtering, citations, and timed answer events remain this application's core. The separate recorded-motion companion remains available for local motion/face/audio inspection.
