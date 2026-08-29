# MercadoVoz — Cuenca External Corpus v1

## Purpose

Independent, web-derived benchmark for MercadoVoz, grounded in public evidence from Cuenca first and Ecuador second.

- Records: 240
- Locale: es-EC
- Provenance: WEB_DERIVED_MULTISOURCE
- Real participants: **none**
- Eligible for real held-out: **no**
- Intended use: technical generalization, safety, context-layer tests, schema-gap discovery, adversarial evaluation.
- Forbidden use: claiming field accuracy, user validation, product-market fit, or real-participant held-out performance.

## Gate policy

This corpus may unlock **TECHNICAL_GO_SPRINT_1** if:
1. the corpus is frozen before any tuning;
2. v0 and v1 are evaluated first without edits;
3. safety expectations are met on unseen patterns;
4. no per-utterance regex patching is used;
5. all changes are evaluated against synthetic v0 + P00-WEB + P01-WEB-DERIVED + this corpus;
6. results are reproducible.

It does **not** unlock **FIELD_VALIDATION_GO**.

## Dataset composition

- 60 explicit sales
- 40 ambiguous/context-dependent sales
- 35 receivable/payment cases
- 30 expense/owner-money cases
- 25 inventory cases
- 25 compound/adversarial cases
- 15 approximate daily-close cases
- 10 promotion/yapa/regateo cases

## Source traceability

See `mercadovoz_cuenca_sources.csv`. Each row in the corpus carries a `source_id`.

## Important

Most utterances are not quotations. They are controlled derivations of documented local patterns.
Do not attribute them to named merchants or publications as verbatim speech.

SHA256 JSONL: 02558a7450035b712c95eb240016efc716a47c3fc66feb57ee62a68ea8bd2788
