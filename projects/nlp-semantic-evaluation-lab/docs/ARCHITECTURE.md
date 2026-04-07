# Architecture

`nlp-semantic-evaluation-lab` treats NLP evaluation as a compact set of
orthogonal checks. A single sample can have a reference text, prediction text,
expected entities, predicted entities, and expected/predicted intents.

## Pipeline

1. Load benchmark samples from JSON.
2. Normalize text into stable lowercase tokens.
3. Compute token overlap and LCS-based sequence similarity.
4. Compare expected and predicted entity sets.
5. Aggregate sample scores into corpus-level metrics.

## Extension Points

- Add embedding similarity when a provider or local model is configured.
- Add hallucination checks with retrieved evidence.
- Add multilingual tokenization adapters.
- Add slice metrics for domain, language, or data source.
