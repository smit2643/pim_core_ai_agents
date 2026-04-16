# Architecture Validation: PIM-AI vs. Custonomy Core Principles

## Principle 1 — "Process once, decide many times" / Shared Feature Layer
Status: VIOLATED

- C-03 creates "read-only DB views and stored procedures for agent bulk queries — category stats, data completeness scores, missing attribute reports." This is the Catalog Management Agent going directly to the operational database, not consuming a precomputed feature layer.
- P-02 and P-03 expose raw real-time pricing and inventory APIs to the Procurement Agent — these are operational data endpoints, not feature tables.
- Only Agent 3 (Content & Enrichment) is correctly designed: Databricks computes missing_description_flag, low_quality_content_flag, and seo_gap_flag as precomputed signals before the agent runs.

Fix needed: Agents 1 and 2 need a feature layer between them and the raw operational data. C-03 should be a feature store read, not a DB view.

## Principle 2 — No Agent Scans Raw Enterprise Tables Directly
Status: VIOLATED

- C-10 ("Autonomous data quality patrol workflow") explicitly says it "scans the catalog for data gaps." This is a full catalog scan — the exact anti-pattern the architecture forbids.
- C-03 is direct DB access via read-only views, still bypassing the feature layer.

Fix needed: C-10 should be driven by a data_quality_flag precomputed in the feature store, not a scheduled full scan. Only products that cross a threshold trigger the agent.

## Principle 3 — Trigger & Eligibility Engine (Only Move Records That Cross a Threshold)
Status: PARTIAL

| Workflow                         | Trigger-based?                                         |
|----------------------------------|--------------------------------------------------------|
| C-11 (new product onboarding)    | Yes — triggered on new product ingestion               |
| E-10 (new supplier onboarding)   | Yes — triggered on ingestion event                    |
| P-11 (autonomous reorder)        | Yes — triggered when stock falls below threshold      |
| P-12 (procurement request intake)| Yes — triggered by user request                       |
| C-10 (data quality patrol)       | No — scheduled full scan                              |

Three out of four major workflows respect the trigger principle. C-10 is the clear violator.

## Principle 4 — Supervisor Routing Before Expensive Child Agents
Status: MISSING

- PIM-AI has 3 flat, independent agents with no supervisor routing layer between them. In Custonomy, a supervisor first does lightweight routing before invoking any expensive child agent.

- In PIM-AI:
    - There is nothing to prevent Agent 1 and Agent 3 from processing the same product simultaneously
    - No lightweight check happens before calling an LLM tool
    - No routing logic decides which agent should handle a given product

Fix needed: A lightweight routing or orchestration layer that decides which agent (or combination) is appropriate for a given product or event, before any expensive LLM call is made.

## Principle 5 — Three-Tier Compute Cost Strategy
Status: MISSING

Custonomy is explicit: Tier 1 (cheap rules) → Tier 2 (medium scoring) → Tier 3 (expensive LLM reasoning), applied sequentially to progressively smaller populations.

PIM-AI agents invoke tools directly with no tiered filtering:
- classify_product, tag_product, generate_description are all Tier 3 operations (LLM calls)
- There is no cheap pre-filter to avoid calling these on products that don't need them
- check_data_quality (C-07) could serve as a Tier 1 filter, but it's not positioned that way in the architecture

Fix needed: Before any LLM tool call, a cheap rule layer should eliminate products that don't need processing.

## Principle 6 — NBA Layer (One Arbiter of Final Action)
Status: MISSING

There is no Next Best Action equivalent in PIM-AI. The 3 agents operate independently. If all three produce outputs for the same product, nothing coordinates which output takes precedence or resolves conflicts.

C-12 ("Conflict detection & resolution logic") partially addresses this for the Catalog Agent internally, but there is no cross-agent coordination mechanism.

## Principle 7 — Human-in-the-Loop
Status: ALIGNED

This is the strongest area of alignment:
- F-07 — HITL escalation framework: agents pause and await approval before irreversible actions
- F-06 — Centralized audit logging of every agent decision and tool call
- F-05 — Agent identity management and permission scopes

## Summary
Custonomy Principle	PIM-AI Status
| Principle / Layer                | Status    | Notes                                              |
|:--------------------------------|:----------|:---------------------------------------------------|
| Feature layer (process once)    | VIOLATED  | Agents 1 & 2 hit raw DB                           |
| No raw table scans              | VIOLATED  | C-10 is a full catalog scan                       |
| Trigger / eligibility engine    | PARTIAL   | C-10 misses it; others respect it                 |
| Supervisor routing              | MISSING   | 3 flat agents, no routing layer                   |
| Three-tier compute cost         | MISSING   | No filtering before LLM calls                     |
| NBA / coordination              | MISSING   | Agents are fully independent                      |
| Human-in-the-loop               | ALIGNED   |                                                   |

The biggest structural gap: PIM-AI was designed with a flat "3 agents + tools" model. Custonomy's architecture requires a signal layer, a trigger engine, and a coordinator sitting above the agents before any expensive work is done. The Content Agent (Agent 3) is the closest to compliant because the Databricks integration was designed with Custonomy principles in mind — that same thinking needs to be applied to Agents 1 and 2.