# Implementation Plan

## Goal

Build a research-engineering project that evaluates multi-hop evidence chains by
tracking support at each hop and verifying that the final conclusion remains
grounded across multiple documents.

## Phase 1: Framing

- Define a compact multi-hop benchmark schema
- Focus on hop support, bridge continuity, and conclusion grounding
- Keep the baseline stdlib-only and easy to inspect

## Phase 2: Core Data Model

- Create dataclasses for documents, reasoning hops, case results, findings, and metrics
- Add config loading and result serialization
- Keep outputs machine-readable and report-friendly

## Phase 3: Mapping Pipeline

- Score document support for each hop
- Track bridge term continuity across adjacent hops
- Measure final conclusion support against the combined mapped evidence
- Emit findings when chains break or evidence is too weak

## Phase 4: Metrics and Reporting

- Summarize hop support and bridge health at case and benchmark level
- Render HTML reports suitable for portfolio screenshots
- Preserve mapped evidence details for later inspection

## Phase 5: Portfolio Growth

- Add representative benchmark cases and tests
- Update repo-level README, roadmap, and CI
- Leave a clean extension point for entity linking or graph views

## Non-Goals For This Version

- No local model-based hop generation
- No learned retriever or graph database integration
- No claim that lexical support fully captures reasoning validity
- No external observability or evaluation SaaS dependency
