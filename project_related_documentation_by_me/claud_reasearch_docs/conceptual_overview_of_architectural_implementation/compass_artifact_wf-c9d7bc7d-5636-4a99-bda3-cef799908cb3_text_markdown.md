# Where Databricks fits in your AI agent pipeline

**Databricks serves as the data platform and MLOps layer behind your application stack — it does not replace FastAPI, LangGraph, Claude, ARQ/Redis, or FastMCP.** For a `generate_description` tool in a multi-agent PIM system, Databricks adds value in six specific areas: product data pipeline engineering (Delta Lake + DLT), batch description generation at scale (Spark + LLM APIs), feature engineering for prompt enrichment (Feature Store), LLM experiment tracking and evaluation (MLflow), governance and lineage for AI-generated content (Unity Catalog), and centralized LLM call management (AI Gateway). The engineering team's task is not to rebuild the stack around Databricks, but to slot it in as the data and AI infrastructure layer underneath the existing real-time application.

---

## The six realistic roles Databricks plays in this pipeline

Each role below maps to a specific capability Databricks provides that your current stack either lacks or handles in a limited way.

**1. Product data pipeline (Delta Lake + Delta Live Tables).** Databricks becomes the centralized product data lakehouse. Raw product data from PostgreSQL syncs into a Bronze layer via CDC (Change Data Capture using Debezium/Kafka or JDBC). Delta Live Tables (DLT) then transforms this through Silver (cleaned, standardized attributes, HTML stripped, categories normalized) to Gold (ML-ready records with assembled prompt context). Delta Lake provides **ACID transactions, schema evolution, and time travel** — meaning you can version every product data change and audit exactly which attributes generated which descriptions. Your PostgreSQL remains the operational database; Delta Lake becomes the analytical and ML data layer.

**2. Batch description generation at scale.** When the PIM needs to generate or regenerate thousands of descriptions (new catalog onboarding, prompt template changes, seasonal refreshes), Databricks distributes LLM API calls across a Spark cluster. You wrap Claude API calls in Spark UDFs or use Databricks' built-in `ai_query()` SQL function, then apply them across millions of product rows with built-in **fault tolerance, retry logic, rate-limit management** via `repartition()`, and auto-scaling. Results write directly to Delta tables. This is fundamentally different from ARQ + Redis, which handles real-time single-product generation — Databricks handles bulk batch processing where parallelism across hundreds of workers matters.

**3. Feature engineering for prompt enrichment.** Databricks Feature Store (now "Feature Engineering in Unity Catalog") precomputes and serves features that enrich your `generate_description` prompts. Practical feature tables for this PIM include: **SEO keyword lists per category** (search volume, competition scores), **brand voice configurations** (tone templates, key phrases, banned words), **category-specific writing templates**, and **product enrichment signals** (review sentiment, price positioning, competitor differentiation). These features compute in batch on Databricks, then serve via online tables for real-time FastAPI lookups or via batch join for bulk generation. This is work your current stack would need custom code to handle.

**4. MLflow for LLM experiment tracking and evaluation.** MLflow — managed natively on Databricks — tracks prompt template versions, LLM parameters (temperature, max tokens, system prompt), and generated outputs across experiments. `mlflow.evaluate()` provides built-in LLM evaluation with metrics like toxicity, relevance, and readability, plus custom metrics you define (SEO score, brand voice adherence, keyword inclusion rate). **MLflow Tracing** captures the full execution trace of multi-step generation workflows. Mosaic AI Agent Evaluation adds LLM-as-judge scoring and a Review App for human feedback — critical for systematically measuring description quality before deploying prompt changes.

**5. Unity Catalog for governance and lineage.** Unity Catalog provides end-to-end lineage tracking: which product data fed which features, which prompt template generated which description, who approved it. For a PIM generating customer-facing product content at scale, this audit trail matters. Unity Catalog also enforces **fine-grained access control** — column-level security on sensitive product data (cost prices, supplier info), row-level filtering by region or brand, and model registry permissions for prompt configurations.

**6. AI Gateway for centralized LLM call management.** Databricks AI Gateway proxies Claude API calls through a unified interface, adding **rate limiting, credential isolation** (API keys never exposed to notebooks or end users), **request/response logging to Delta tables** (inference tables), cost tracking per token, and access control via Unity Catalog permissions. It also enables A/B testing different models (e.g., Claude vs. a fine-tuned Llama for simpler categories) behind a single endpoint name, without changing application code.

---

## What Databricks does versus what the existing stack already handles

The table below maps each architectural concern to whether Databricks, your existing stack, or both handle it.

| Concern | Your existing stack | Databricks role |
|---------|-------------------|-----------------|
| HTTP API / application server | **FastAPI** (keeps this role) | Not involved — not a web framework |
| Multi-agent orchestration | **LangGraph** (keeps this role) | Agent Framework can *deploy/evaluate* LangGraph agents, not replace orchestration logic |
| LLM reasoning | **Claude API** (keeps this role) | Can proxy Claude calls via AI Gateway for governance; can also host open-source alternatives |
| Real-time job queue | **ARQ + Redis** (keeps this role) | Not designed for sub-second task queuing |
| MCP tool protocol | **FastMCP** (keeps this role) | No equivalent; completely different layer |
| Operational product data | **PostgreSQL** (keeps this role) | Not a transactional database |
| Real-time vector search | **pgvector** (keeps this role) | Vector Search overlaps but pgvector is better co-located with PIM relational data |
| Product data ETL/pipeline | Limited (manual or custom scripts) | **Delta Lake + DLT** — major value-add |
| Batch generation at scale | ARQ can do this but limited scale | **Spark-distributed batch inference** — major value-add |
| Feature engineering | Custom code | **Feature Store** — structured precomputation and serving |
| Prompt/LLM experiment tracking | None in current stack | **MLflow** — major value-add |
| LLM output evaluation | None in current stack | **Agent Evaluation** — major value-add |
| Data governance & lineage | PostgreSQL RBAC only | **Unity Catalog** — major value-add |
| LLM call logging & cost tracking | Manual/custom | **AI Gateway + Inference Tables** — value-add |

The pattern is clear: **Databricks fills the data engineering, MLOps, governance, and batch processing gaps** that a real-time application stack (FastAPI + LangGraph + Redis) naturally leaves open.

---

## What Databricks does not replace and why

**FastAPI stays.** Databricks Model Serving exposes REST endpoints for models and agents, but it is not a general-purpose web application framework. FastAPI handles HTTP routing, request validation, authentication, business logic, API versioning, and webhooks. Databricks' own demos consistently show FastAPI or Streamlit as the application layer calling Databricks endpoints.

**LangGraph stays for orchestration.** The Mosaic AI Agent Framework provides simpler agent orchestration (tool-calling, chain-of-thought), but LangGraph provides **stateful multi-agent orchestration with explicit graph-based workflows, conditional branching, cycles, and human-in-the-loop patterns** that the Agent Framework does not match. For a multi-agent PIM system, LangGraph is the orchestration engine; Databricks Agent Framework is the deployment and evaluation wrapper around it. They are complementary, not competitive, in this architecture.

**Claude API stays.** Databricks can host open-source LLMs (Llama, DBRX, Mixtral) and proxy to Claude via External Model Endpoints, but it does not replace Claude's reasoning capability. The proxy adds governance; the LLM quality comes from Anthropic.

**ARQ + Redis stays for real-time.** Databricks Workflows handle batch and scheduled orchestration with startup latency measured in seconds to minutes. ARQ + Redis provides sub-second task queuing for real-time single-product description generation triggered by user actions. Keep ARQ for real-time, use Databricks Workflows for batch/ETL.

**pgvector likely stays.** Databricks Vector Search is a managed vector database, but pgvector lives inside PostgreSQL alongside relational PIM data — enabling transactional consistency and SQL joins between vector and relational queries in a single operation. For a PIM system where product data and embeddings are tightly coupled, **co-location in PostgreSQL is architecturally simpler**. Databricks Vector Search becomes relevant only if you need to search across massive datasets managed in the lakehouse.

**FastMCP stays.** Databricks has no MCP equivalent. Completely different layer.

---

## Official Databricks integrations with LangChain and LangGraph

Databricks maintains an official **`databricks-langchain`** partner package on PyPI that provides four key LangChain components:

- **`ChatDatabricks`** — chat model wrapper for Databricks Model Serving endpoints (Foundation Model APIs, external model endpoints including Claude, and custom models). Usable as any LangChain chat model inside LangGraph nodes.
- **`DatabricksEmbeddings`** — embeddings wrapper for Databricks-hosted embedding models.
- **`DatabricksVectorSearch`** — retriever for Databricks Vector Search indexes.
- **`UCFunctionToolkit`** — exposes Unity Catalog SQL/Python functions as LangChain tools for agents.

A separate **`databricks-agents`** package handles deployment and evaluation: `databricks.agents.deploy()` pushes MLflow-logged agents to Model Serving endpoints, and the Review App enables human evaluation. This package is framework-agnostic — it wraps LangGraph agents for deployment without replacing LangGraph's orchestration logic.

**LangGraph is officially supported** as an agent authoring framework within Mosaic AI Agent Framework. The documented pattern is: define a LangGraph `StateGraph` using `ChatDatabricks` as the LLM, log it with `mlflow.langchain.log_model()`, deploy with `databricks-agents`, and evaluate with Mosaic AI Agent Evaluation. Databricks provides example notebooks for this workflow in their GenAI Cookbook.

Key documentation and resources (based on standard Databricks doc patterns — verify for current availability):

- **`databricks-langchain` on PyPI**: `https://pypi.org/project/databricks-langchain/`
- **`databricks-agents` on PyPI**: `https://pypi.org/project/databricks-agents/`
- **LangChain Databricks provider docs**: `https://python.langchain.com/docs/integrations/providers/databricks/`
- **Databricks Agent Framework docs**: `https://docs.databricks.com/en/generative-ai/agent-framework/index.html`
- **GenAI Cookbook (GitHub)**: `https://github.com/databricks/genai-cookbook`

---

## Mosaic AI and Model Serving explained in context

**Mosaic AI** is Databricks' unified AI platform brand (post-MosaicML acquisition in 2023) encompassing all AI/ML tooling. For LLM agent pipelines, the relevant components are:

**Model Serving** provides scalable REST API endpoints in three modes: Foundation Model APIs for Databricks-hosted open models (DBRX, Llama, Mixtral) with pay-per-token or provisioned throughput billing; Custom Model Endpoints for fine-tuned models logged via MLflow; and **External Model Endpoints** for proxying to providers like Anthropic Claude. All expose an OpenAI-compatible API format (`/chat/completions`), meaning agent frameworks can swap between providers without code changes.

**AI Gateway** sits in front of Model Serving to add governance: unified API interface, rate limiting, credential isolation, request/response logging to inference tables, access control, cost tracking, and guardrails (content filtering, PII detection). For your stack, this means routing Claude API calls through AI Gateway gives you automatic logging of every `generate_description` LLM call to Delta tables — invaluable for debugging, compliance, and cost analysis.

**Agent Framework** handles the lifecycle of deploying and evaluating agents built with LangGraph or other frameworks. It is not a replacement for LangGraph's orchestration capabilities but rather the **deployment, evaluation, and monitoring wrapper** around your agent logic.

**Agent Evaluation** provides systematic quality assessment using LLM-as-judge scoring (correctness, groundedness, relevance, safety), human review via the Review App, and custom metrics. For product descriptions, you would define custom evaluators for SEO score, brand voice adherence, and keyword density.

Reference architecture documentation:
- **Mosaic AI overview**: `https://docs.databricks.com/en/machine-learning/mosaic-ai.html`
- **Model Serving**: `https://docs.databricks.com/en/machine-learning/model-serving/index.html`
- **External Models**: `https://docs.databricks.com/en/generative-ai/external-models/index.html`
- **AI Gateway**: `https://docs.databricks.com/en/generative-ai/ai-gateway/index.html`

---

## Recommended architecture for your PIM system

Based on this analysis, here is how Databricks integrates with your existing stack without replacing any component:

```
┌──────────────────────────────────────────────────────────┐
│              DATABRICKS PLATFORM (New Layer)              │
│                                                          │
│  Delta Live Tables → Delta Lake (Bronze/Silver/Gold)     │
│  Feature Store (SEO keywords, brand voice configs)       │
│  Databricks Workflows (batch orchestration)              │
│  MLflow (prompt tracking, evaluation, tracing)           │
│  Unity Catalog (governance, lineage, access control)     │
│  AI Gateway (Claude proxy + logging + rate limiting)     │
│  Batch Inference (Spark + Claude for bulk generation)    │
└──────────┬────────────────────────────┬──────────────────┘
           │ Sync product data (CDC)    │ Serve features / 
           │ Write back descriptions    │ batch results
           ▼                            ▼
┌──────────────────────┐    ┌──────────────────────────────┐
│ PostgreSQL + pgvector │    │ FastAPI + LangGraph +        │
│ (operational DB,     │◄──►│ Claude API + ARQ/Redis +     │
│  real-time vectors)  │    │ FastMCP (real-time app)       │
└──────────────────────┘    └──────────────────────────────┘
```

The integration points are: **PostgreSQL → Databricks** via CDC or scheduled JDBC sync for product data ingestion; **Databricks → PostgreSQL** to write back batch-generated descriptions; **Feature Store → FastAPI** via online tables for real-time prompt enrichment; **AI Gateway → Claude** as an optional governed proxy for LLM calls; and **MLflow** tracking experiments across both batch (Databricks) and real-time (FastAPI + Claude) generation paths.

---

## Conclusion

The engineering team should think of Databricks as the **data and AI infrastructure layer**, not as a replacement for any application component. Its strongest value for this `generate_description` pipeline comes from three areas the current stack lacks entirely: **batch processing at scale** (generating thousands of descriptions when catalogs change), **systematic evaluation** (MLflow + Agent Evaluation for measuring description quality before deploying prompt changes), and **data governance** (Unity Catalog lineage tracking which data produced which AI-generated content). The weakest case for Databricks in this stack is replacing pgvector (co-location with PostgreSQL is more practical for PIM) or replacing ARQ/Redis (Databricks is not built for sub-second job queuing). Start with Delta Lake as the product data pipeline and MLflow for prompt experiment tracking — these deliver immediate value with minimal architectural disruption. Add batch inference and AI Gateway as scale demands grow.