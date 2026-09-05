# RecoverAI: Autonomous AI Payment Revenue Recovery Platform

RecoverAI is an autonomous payment intelligence and revenue recovery platform engineered for the Razorpay AI Buildathon under Track 03: AI Revenue Recovery. It identifies at-risk revenue from failed transactions, diagnoses underlying failure root causes using forensic telemetry, predicts recoverability, and executes policy-governed interventions to capture revenue without customer harassment or gateway penalties.

> **Core Operating Principle**:
> **AI recommends. Deterministic policy controls execution.**
> All payment recovery actions operate strictly in Simulation Mode and do not connect to live banking networks or move real currency.

---

## Executive Summary

### The Revenue Failure Problem

Modern online merchants lose between 2% and 9% of gross merchandise value to payment failures. When a payment fails, traditional platforms typically respond with one of two flawed strategies:

1. **Passive Abandonment**: The merchant takes no action, writing off the customer and the transaction as lost churn.
2. **Blind Retry Storms**: The gateway blindly retries the payment immediately across the same rails. If the failure was caused by insufficient funds or account blocks, repeated retries exhaust card limits, trigger issuer fraud flags, damage merchant reputation, and rack up gateway failure penalties.

### The RecoverAI Solution

RecoverAI answers the central product question:

> *"How much revenue can we recover, and what should we do next?"*

Instead of treating all failures identically, RecoverAI decouples decision-making from execution:
- **Diagnostic Intelligence**: Evaluates error codes, network latency, customer history, and tenure.
- **Recoverability Prediction**: Scores the statistical likelihood of payment capture (0% to 100%).
- **Policy Enforcement**: A deterministic rule layer evaluates every AI suggestion against strict bounds (retry caps, cooldown windows, ticket size thresholds) before execution.
- **Auditable Execution**: Every recommendation, policy validation, and outcome is logged immutably in PostgreSQL.

---

## System Architecture

The following diagram illustrates the component hierarchy and data flow across the client, backend, intelligence services, and persistence layers.

```
+---------------------------------------------------------------------------------------------------+
|                                      CLIENT INTERACTION LAYER                                     |
|                                                                                                   |
|   React 18 Dashboard (TypeScript, Vite, Tailwind CSS, Recharts)                                    |
|   ├── Overview Dashboard (Live KPIs, Recovery Funnel, 14-Day Trend, Failure Breakdown)            |
|   ├── Recovery Cases Ledger (Filterable Cohorts, Salvageability Index, Case Forensics)            |
|   ├── Payment Explorer (Gateway Telemetry, Customer Tenure, Historical Patterns)                  |
|   ├── Analytics Suite (Strategy ROI, Action Efficiency, Conversion Heatmaps)                      |
|   └── Audit Log Viewer (Chronological Event Ledger, Actor Attribution, Metadata)                  |
+--------------------------------------------------+------------------------------------------------+
                                                   |
                                                   | HTTP REST / JSON
                                                   v
+---------------------------------------------------------------------------------------------------+
|                                      FASTAPI BACKEND SERVICE                                      |
|                                                                                                   |
|   Routing & Middleware Layer                                                                      |
|   ├── Request Validation & Schema Serialization (Pydantic v2)                                     |
|   ├── CORS & Security Middleware                                                                  |
|   └── Dependency Injection & Transaction Context (SQLAlchemy Session)                             |
+---------+----------------------------------------+--------------------------------------+---------+
          |                                        |                                      |
          v                                        v                                      v
+-----------------------+        +-----------------------------------+        +---------------------+
| RISK DETECTION ENGINE |        |     INTELLIGENCE TRIAD LAYER      |        | RECOVERY EXECUTION  |
|                       |        |                                   |        |                     |
| ├── Revenue-at-Risk   |        | 1. ML Scoring Model               |        | ├── State Machine   |
| │   Aggregation       |        |    ├── Logistic Regression        |        | │   (8 Transitions) |
| ├── Recoverable Pool  |        |    └── Feature Preprocessor       |        | ├── Gateway         |
| │   Calculation       |        |                                   |        | │   Simulator       |
| └── Cohort Exposure   |        | 2. Gemini 2.5 Flash Agent         |        | ├── Idempotency     |
|     Tracking          |        |    ├── Forensic Investigation     |        | │   Guard           |
|                       |        |    ├── Telemetry Evidence Parse   |        | └── Stopping Rule   |
|                       |        |    └── Strategy Recommendation    |        |     Enforcer        |
|                       |        |                                   |        |                     |
|                       |        | 3. Deterministic Policy Engine    |        |                     |
|                       |        |    ├── Max 3 Retries Cap          |        |                     |
|                       |        |    ├── Cooldown Window (15m)      |        |                     |
|                       |        |    ├── Card Decline Protection    |        |                     |
|                       |        |    └── Human Escalation (>50k)    |        |                     |
+-----------------------+        +-----------------------------------+        +---------------------+
          |                                        |                                      |
          +----------------------------------------+--------------------------------------+
                                                   |
                                                   | SQLAlchemy 2.0 ORM
                                                   v
+---------------------------------------------------------------------------------------------------+
|                                     PERSISTENCE & AUDIT LAYER                                     |
|                                                                                                   |
|   PostgreSQL 17 Database                                                                          |
|   ├── customers       (Demographics, payment success ratios, account age)                         |
|   ├── merchants       (Business profile, billing categories, historical GMV)                      |
|   ├── payments        (Transaction records, gateway error codes, retry counts)                    |
|   ├── recovery_cases  (Lifecycle state, ML score, AI diagnosis, final action)                     |
|   ├── recovery_actions(Scheduled & executed recovery attempts, execution status)                 |
|   └── audit_logs      (Immutable chronological ledger of all AI and policy events)                |
+---------------------------------------------------------------------------------------------------+
```

---

## End-to-End Recovery Lifecycle

```
[ Failed Payment Event ]
          |
          v
+-------------------+
|      DETECT       |  Identify failed, expired, or abandoned transactions from gateway feeds
+---------+---------+
          |
          v
+-------------------+
|     DIAGNOSE      |  Classify failure root cause: TEMPORARY_BANK_FAILURE, INSUFFICIENT_FUNDS,
+---------+---------+  AUTHENTICATION_FAILED, NETWORK_ERROR, EXPIRED_PAYMENT, or CARD_DECLINED
          |
          v
+-------------------+
|      PREDICT      |  Compute ML Recoverability Score (0.0% to 100.0%) based on customer tenure,
+---------+---------+  historical success rate, transaction amount, and failure reason
          |
          v
+-------------------+
|    RECOMMEND      |  Google Gemini 2.5 Flash evaluates forensic telemetry and proposes:
+---------+---------+  Action (RETRY_LATER, SEND_PAYMENT_LINK, CUSTOMER_REMINDER), delay, channel
          |
          v
+-------------------+
|   POLICY CHECK    |  Deterministic Policy Engine validates action against immutable guardrails.
+---------+---------+  Approve action, override to safe fallback, or halt execution
          |
          +-----------------------------+-----------------------------+
          |                             |                             |
      [ APPROVED ]                 [ OVERRIDDEN ]                  [ STOPPED ]
          |                             |                             |
          v                             v                             v
+-------------------+         +-------------------+         +-------------------+
|      EXECUTE      |         |   FALLBACK ACTION |         |   HALT WORKFLOW   |
| Run policy-safe   |         | Execute policy    |         | Terminate case to |
| recovery in       |         | substitution      |         | prevent fatigue & |
| simulation sandbox|         | (e.g., Smart Link)|         | gateway penalties |
+---------+---------+         +---------+---------+         +---------+---------+
          |                             |                             |
          +-----------------------------+                             |
          |                                                           |
          v                                                           |
+-------------------+                                                 |
|      RECOVER      |                                                 |
| Mark transaction  |                                                 |
| RECOVERED, credit |                                                 |
| settled ledger    |                                                 |
+---------+---------+                                                 |
          |                                                           |
          +-----------------------------+-----------------------------+
                                        |
                                        v
                              +-------------------+
                              |       AUDIT       |  Append chronological event to immutable
                              +---------+---------+  audit ledger with actor attribution
                                        |
                                        v
                              +-------------------+
                              |      MEASURE      |  Update real-time financial KPIs, recovery
                              +-------------------+  rate, conversion metrics, and ROI
```

---

## Technology Stack

### Frontend Application
- **Framework**: React 18.3 with Vite 6
- **Language**: TypeScript 5.7 (strict typing, zero any declarations in production paths)
- **Styling**: Tailwind CSS 3.4 (custom light fintech palette, slate borders, accessible contrast)
- **Data Visualization**: Recharts 2.15 (trend lines, funnel charts, failure distributions)
- **Icons**: Lucide React
- **Routing**: React Router DOM 7

### Backend Application
- **Framework**: FastAPI 0.115+ (ASGI high-performance web framework)
- **Language**: Python 3.12+
- **Data Validation & Settings**: Pydantic v2 & Pydantic Settings
- **Server**: Uvicorn with single-process reload targeting application code
- **Database ORM**: SQLAlchemy 2.0 (declarative models, relationship joins, transactional rollback)
- **Database Migrations**: Alembic

### Artificial Intelligence & Machine Learning
- **LLM Engine**: Google Gemini 2.5 Flash via official Google GenAI SDK (google-genai)
- **Reasoning Design**: Structured schema output enforcing strict JSON return types
- **Read-Only Telemetry Tools**: Forensic data gathering for customer history, gateway codes, and merchant profile
- **Classical ML**: Scikit-learn Logistic Regression pipeline serialized with Joblib for baseline recoverability scoring
- **Numerical Processing**: NumPy

### Persistence & Storage
- **Primary Database**: PostgreSQL 17
- **Connection Protocol**: psycopg2-binary driver with connection pooling
- **Audit Storage**: Append-only relational table with structured JSONB metadata

### Quality Assurance & Tooling
- **Backend Testing**: Pytest with HTTPX test client and test database isolation
- **Frontend Testing & Build**: TypeScript Compiler (tsc --noEmit) and Vite production bundler

---

## AI Architecture & Policy Governance

RecoverAI avoids black-box conversational chatbots. The AI layer operates as a **Forensic Intelligence Agent** paired with a **Deterministic Policy Engine**.

```
                           RAW PAYMENT FAILURE TELEMETRY
                                         │
                                         ▼
                 +───────────────────────────────────────────────+
                 │           Read-Only Telemetry Tools           │
                 │ ├── Customer Lifetime Transaction Ratio       │
                 │ ├── Payment Method Specific Reliability       │
                 │ ├── Gateway Error Classification              │
                 │ └── Merchant Category Average Ticket Size     │
                 +───────────────────────┬───────────────────────+
                                         │
                                         ▼
                 +───────────────────────────────────────────────+
                 │      Gemini 2.5 Flash Diagnostic Agent        │
                 │                                               │
                 │ Produces Structured JSON:                     │
                 │ ├── Diagnosis & Root Cause Classification     │
                 │ ├── Diagnostic Confidence Score (0.0 to 1.0)  │
                 │ ├── Weighted Evidence Factors (+/- impact)    │
                 │ ├── Proposed Recovery Action                  │
                 │ └── Recommended Cooldown Delay (Minutes)      │
                 +───────────────────────┬───────────────────────+
                                         │
                                         ▼
                 +───────────────────────────────────────────────+
                 │          Deterministic Policy Engine          │
                 │                                               │
                 │ Immutable Safety Checks:                      │
                 │ 1. Retry Count Check: retry_count < 3         │
                 │ 2. Window Validity: created_at within 48h TTL │
                 │ 3. Card Decline Check: Prohibits retries on   │
                 │    HARD_DECLINE / CARD_BLOCKED                │
                 │ 4. Ticket Size Threshold: >= 50,000 INR       │
                 │    automatically routed to ESCALATE_TO_HUMAN  │
                 │ 5. Minimum Score: score < 20% -> STOP         │
                 +───────────────────────┬───────────────────────+
                                         │
                       +─────────────────┴─────────────────+
                       │                                   │
              [ Policy: APPROVED ]                [ Policy: OVERRULED ]
                       │                                   │
                       ▼                                   ▼
          Execute Recommended Action             Execute Safe Fallback
          (e.g., Scheduled Retry)             (e.g., Alternative PayLink)
```

### Deterministic Safety Guardrails

| Guardrail Rule | Condition | Enforced Policy Action | Rationale |
|---|---|---|---|
| **Max Retry Cap** | retry_count >= 3 | STOP_RECOVERY | Prevents gateway spamming and customer harassment. |
| **Card Decline Guard** | Reason is CARD_DECLINED or LIMIT_EXCEEDED | SEND_PAYMENT_LINK | Retrying a declined card fails 98% of the time; a link allows selecting another card or UPI. |
| **High Value Escalation** | Amount >= INR 50,000 with score < 60% | ESCALATE_TO_HUMAN | High-value VIP transactions warrant personalized white-glove operations handling. |
| **Cooldown Period** | Network or bank timeout failure | Enforce 15-minute delay | Transient gateway switch failures require time to recover before re-querying. |
| **Minimum Salvageability** | Recoverability score < 20.0% | STOP_RECOVERY | Conserves merchant bandwidth on definitively dead or fraudulent transactions. |
| **Idempotency Guard** | Status is RECOVERED, STOPPED, or ESCALATED | Return current state | Prevents duplicate execution and artificial revenue inflation. |

---


## Repository File Structure

```
RecoverAI/
├── backend/
│   ├── alembic/                      # Database migration scripts
│   ├── app/
│   │   ├── api/                      # REST API routers (analytics, recovery, payments, ai)
│   │   ├── config.py                 # Pydantic environment settings
│   │   ├── database.py               # SQLAlchemy engine & session factory
│   │   ├── main.py                   # FastAPI initialization & middleware
│   │   ├── models/                   # Database models (Payment, Customer, RecoveryCase, etc.)
│   │   ├── recovery/                 # Core recovery logic, policy engine, simulator
│   │   ├── schemas/                  # Pydantic request & response models
│   │   ├── services/                 # Business logic services & seeders
│   │   └── utils/                    # ML pipeline, loggers, seed data
│   ├── tests/                        # 54 comprehensive Pytest test cases
│   ├── requirements.txt              # Python production dependencies
│   └── alembic.ini                   # Alembic configuration
├── frontend/
│   ├── src/
│   │   ├── api/                      # Axios API clients & typed endpoints
│   │   ├── components/               # UI components (dashboard, layout, common)
│   │   ├── pages/                    # Views (Dashboard, Cases, CaseDetails, Analytics, Audit)
│   │   ├── types/                    # TypeScript interfaces & enums
│   │   ├── utils/                    # Formatting helpers (Currency, Dates)
│   │   ├── App.tsx                   # Layout wrapper & client router
│   │   └── main.tsx                  # React entry point
│   ├── package.json                  # Node dependencies & scripts
│   ├── tailwind.config.js            # Tailwind theme tokens
│   └── vite.config.ts                # Vite build configuration
└── README.md                         # Project documentation
```

---