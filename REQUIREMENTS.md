# Requirements and provenance — ISMAR adjunct variant

## Paper-supported facts

The complete ISMAR adjunct paper was read before this requirements file was written. It describes Annals/Sejong data, whole-article dynamic chunking, year/month/day metadata, GPT query regeneration, date filtering, maximum-token retrieval, evidence-based answers, and a Unity AI agent. Voice is converted with STT; the answer is synthesized with TTS while matching body and lip motion are presented. The abstract describes the broader Annals as 49,646,667 characters and the experiment uses 30 benchmark questions.

The full journal paper was also read as shared retrieval-architecture context. Details present only there—30,949 chunks, 163 Sejong volumes, explicit failure analysis, and extended limitations—must not be attributed to the shorter ISMAR paper.

## Functional requirements

The public implementation provides the paper-supported retrieval path plus a distinct integration artifact: timed utterances, coarse response-conditioned body-motion labels, lip/viseme timing markers, citations, and a portable browser demonstrator suitable for replacing with user-owned STT/TTS/avatar components.

## Assumptions and substitutions

This is independent educational code. TF-IDF, extractive answers, reranking, inferred-date widening, sentence timing, alternating open/closed mouth markers, rule-selected motion labels, and the SVG face are explicit baselines/adapters. They do not reproduce the paper's GPT services, STT/TTS, Unity scene, lip-sync system, animation generator, models, assets, benchmark scores, or institute implementation.
