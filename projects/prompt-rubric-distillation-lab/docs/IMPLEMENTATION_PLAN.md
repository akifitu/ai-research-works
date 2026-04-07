# Implementation Plan

## Goal

Build a research-engineering project that converts qualitative rubric text into
structured scoring artifacts suitable for AI evaluation programs.

## Phase 1: Framing

- Define a compact rubric benchmark schema
- Focus on dimension inference, ambiguity detection, and weight normalization
- Keep the baseline lightweight and transparent

## Phase 2: Core Data Model

- Create dataclasses for rubrics, criteria, distilled outputs, findings, and metrics
- Add config loading and result serialization helpers
- Preserve outputs in machine-readable forms for future judge pipelines

## Phase 3: Distillation Pipeline

- Infer evaluation dimensions from criterion wording
- Detect vague terms and explicit requirement language
- Normalize weights across criteria
- Generate checklist questions and scale anchors

## Phase 4: Metrics and Reporting

- Summarize ambiguity, specificity, and weight coverage per rubric
- Produce HTML reports suitable for portfolio screenshots
- Keep all artifacts stable enough for version control review

## Phase 5: Portfolio Growth

- Add representative rubrics and tests
- Update repo-level README, roadmap, and CI
- Leave a clean base for future judge-model integration

## Non-Goals For This Version

- No semantic parsing via local or hosted models
- No claim that heuristic distillation fully replaces evaluator design work
- No automatic scoring of model outputs yet
- No external experiment tracking dependency
