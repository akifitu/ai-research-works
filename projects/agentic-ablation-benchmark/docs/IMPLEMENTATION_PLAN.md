# Implementation Plan

## Goal

Build a research-engineering project that compares agent variants through
prerecorded runs and produces ablation scorecards without any live agent
execution.

## Phase 1: Framing

- Define a compact benchmark schema for tasks and variants
- Focus on completion, recovery, efficiency, cost, and latency
- Keep the baseline transparent and stdlib-first

## Phase 2: Core Data Model

- Create dataclasses for tasks, variants, findings, and aggregate factor summaries
- Add config loading and result serialization
- Keep result objects stable for JSON and HTML reporting

## Phase 3: Scoring Pipeline

- Compute composite variant scores from completion, quality, recovery, and cost
- Compare each variant against the task baseline
- Track prompt, tool-policy, and retrieval deltas separately
- Identify winners, regressions, loop risk, and recovery gaps

## Phase 4: Metrics and Reporting

- Summarize task-level and benchmark-level performance
- Produce HTML reports suitable for portfolio screenshots
- Preserve factor-level deltas for later analysis

## Phase 5: Portfolio Growth

- Add benchmark examples and tests
- Update repo-level README, roadmap, and CI
- Leave a clean base for future repeated-run statistics

## Non-Goals For This Version

- No live agent execution or evaluation service integration
- No statistical significance claims from a tiny benchmark
- No learned judge model for answer quality
- No external experiment tracking dependency

