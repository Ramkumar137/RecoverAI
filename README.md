# RecoverAI — Autonomous AI Payment Revenue Recovery Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7+-3178C6.svg?style=flat&logo=typescript)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17+-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![Gemini](https://img.shields.io/badge/Google%20GenAI-Gemini%202.5%20Flash-4285F4.svg?style=flat&logo=google)](https://ai.google.dev)

Built for the **Razorpay AI Buildathon** under the **AI Revenue Recovery** track.

> **Important Safety Principle**:
> **AI recommends. Deterministic policy controls execution.**
> All payment recovery actions operate strictly in **Simulation Mode** and do not connect to real banking networks or process live financial transactions.

---

## 💡 The Core Problem

Businesses lose millions in revenue every month because payments fail, subscriptions lapse, customers abandon checkouts, and invoices linger unpaid. Blind retry algorithms fail: they repeatedly hit exhausted card limits, annoy customers with duplicate SMS/WhatsApp spam, and trigger banking gateway sanctions.

**RecoverAI answers the foundational product question:**
> *"How much revenue can we recover, and what should we do next?"*

---

## 🔄 End-to-End Recovery Lifecycle

```
DETECT          → Identify failed, expired, or abandoned payments across payment gateways
  ↓
DIAGNOSE        → Forensic classification of failure root cause (transient, systemic, liquidity)
  ↓
PREDICT         → ML recoverability scoring (0–100%) based on customer profile and tenure
  ↓
RECOMMEND       → Gemini 2.5 Flash AI Agent proposes recovery strategy, delay, and channel
  ↓
POLICY CHECK    → Deterministic Policy Engine validates recommendation against safety limits
  ↓
EXECUTE         → Bounded simulated recovery workflow execution with retry caps
  ↓
RECOVER         → Transaction settlement, idempotency guard, and zero double-counting
  ↓
AUDIT           → Immutable chronological audit trail recording every AI and policy decision
  ↓
MEASURE         → Real-time financial analytics, 14-day trends, and strategy conversion ROI
```

---

## 🏗 System Architecture

```
React Frontend
      |
FastAPI Backend
      |
+-----+-----+-----+
|     |     |     |
Risk  ML   AI   Policy
      |
Recovery State Machine
      |
Payment Simulator
      |
PostgreSQL Database
```

### Detailed Component Interaction

```
React 18 + Vite + Tailwind CSS + Recharts + React Router
   │  (Dashboard, Recovery Cases, Payments Ledger, Analytics, Audit Trail)
   ▼ (HTTP REST)
FastAPI Backend API
   │
   ├── Risk Detection Engine      (Revenue-at-Risk calculation & exposure tracking)
   ├── Diagnostic Engine          (Failure root-cause classification)
   ├── ML Recoverability Model    (Logistic Regression with Scikit-learn & Joblib)
   ├── AI Investigation Agent     (Google GenAI SDK + Gemini 2.5 Flash structured output)
   ├── Deterministic Policy Engine (Immutable business safety rules: max 3 retries, fatigue limits)
   ├── Recovery State Machine     (8 legal state transitions & terminal boundaries)
   ├── Payment Simulator Engine   (Deterministic MD5-hash reproducible probability roll)
   └── Analytics & Audit Engine   (14-day trends, failure breakdowns, chronological timeline)
   │
   ▼ (SQLAlchemy 2.0 + Alembic)
PostgreSQL 17 Database
   ├── Customers (115 profiles, lifetime transaction histories)
   ├── Merchants (23 registered businesses across categories)
   ├── Payments (551 transactions across statuses & failure reasons)
   ├── RecoveryCases (218 active & resolved recovery instances)
   ├── RecoveryActions (bounded scheduled & executed recovery actions)
   └── AuditLogs (2,530+ immutable chronological compliance events)
```

---

## 🧠 AI Layer Architecture

```
Payment Failure Telemetry
   │
   ▼
7 Read-Only DB Forensic Tools (Customer Profile, Payment Details, Method History, Failure Patterns, etc.)
   │
   ▼
Sanitized Investigation Context Builder (PII-free, ML score input, heuristic baseline)
   │
   ▼
Gemini 2.5 Flash Agent (Senior Revenue Recovery & Payment Intelligence Analyst persona)
   │   (Structured Output: Diagnosis, Confidence, Summary, Evidence, Action, Delay, Channel)
   ▼
Deterministic Policy Engine (Hard Guardrails)
   ├── Max 3 retries limit (retry_count >= 3 -> STOP_RECOVERY)
   ├── Card decline safety (prohibits naive retries on CARD_DECLINED / LIMIT_EXCEEDED)
   ├── Minimum salvageability threshold (score < 20% -> STOP_RECOVERY)
   ├── Critical value escalation (amount >= ₹50,000 with low score -> ESCALATE_TO_HUMAN)
   └── 48-hour recovery window TTL
   │
   ▼
Approved Recovery Workflow Execution (Simulated gateway retry, payment link, or reminder)
   │
   ▼
Immutable Chronological Audit Log
```

---

## 📡 Core API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Standard service health probe (`{"status": "ok"}`) |
| `GET` | `/api/health/system` | Detailed component health including PostgreSQL connection |
| `GET` | `/api/analytics/overview` | Financial KPIs: Revenue at Risk, Potentially Recoverable, Recovered Revenue, Recovery Rate |
| `GET` | `/api/analytics/recovery-trend` | 14-day daily recovery trend time series |
| `GET` | `/api/analytics/failure-breakdown` | Root cause failure counts, amount at risk, and recovery rate |
| `GET` | `/api/analytics/action-breakdown` | Recovery action performance: attempts, conversions, amount |
| `GET` | `/api/payments` | List payments with `search`, `status`, and `failure_reason` filters |
| `GET` | `/api/payments/{id}` | Detailed payment metadata with customer and merchant profile |
| `GET` | `/api/recovery/cases` | Paginated recovery cases with status filtering across 9 states |
| `GET` | `/api/recovery/cases/{id}` | Detailed case forensics with payment and action history |
| `GET` | `/api/recovery/cases/{id}/timeline` | Full chronological investigation and execution audit trail |
| `POST` | `/api/recovery/analyze/{payment_id}` | Trigger risk detection and ML recoverability prediction |
| `POST` | `/api/ai/investigate/{payment_id}` | Trigger Gemini 2.5 Flash AI investigation & policy governance |
| `GET` | `/api/ai/investigations/{payment_id}` | Retrieve cached forensic AI report and evidence factors |
| `POST` | `/api/recovery/execute/{case_id}` | Execute simulated recovery action with idempotency enforcement |
| `POST` | `/api/recovery/run-batch` | Run batch recovery processing over eligible cases |
| `GET` | `/api/recovery/audit-logs` | Query system audit ledger with pagination and event filtering |

---

## 🎯 5-Minute Buildathon Demo Flow (`PAY_10482`)

1. **Step 1 — Main Dashboard (`/dashboard`)**:
   - Highlight the 4 core financial KPIs: Revenue at Risk (`₹14.90L`), Potentially Recoverable (`₹9.43L`), Recovered Revenue (`₹751.44k`), Recovery Rate (`79.7%`).
   - Walk through the visual **Recovery Funnel** (`At Risk → Salvageable → Attempted → Recovered`).
   - Review the 14-day daily recovery trend and failure breakdown.
2. **Step 2 — Featured Demo Case Selection**:
   - Click the prominent **PAY_10482** shortcut card from the dashboard header (or open **Recovery Cases** and filter).
3. **Step 3 — Case Forensics (`/recovery/:caseId`)**:
   - Inspect payment details: `₹8,500.00`, `UPI`, failure reason: `BANK_TIMEOUT`, 0 prior retries.
   - Observe **ML Recoverability Score**: `98.5%` (HIGH salvageability tier).
4. **Step 4 — Gemini AI Autonomous Investigation**:
   - Review AI diagnosis: `TEMPORARY_BANK_FAILURE` with `95%` confidence.
   - Inspect forensic telemetry evidence cards (customer tenure, gateway transience, payment pattern).
   - See AI proposed action: `RETRY_LATER` via `GATEWAY_RETRY` with a 15-minute recommended delay.
5. **Step 5 — Deterministic Policy Check**:
   - Review visual 3-stage governance flow: `AI Proposed (RETRY_LATER) → Policy Check (ALLOWED) → Approved Final Action (RETRY_LATER)`.
   - Confirm safety constraints: `0/3` retries, `48h` TTL window, no human escalation needed.
6. **Step 6 — Simulated Recovery Execution**:
   - Click **Execute Recovery Action**.
   - Review the confirmation modal and simulation disclosure.
   - Confirm execution.
7. **Step 7 — Instant Resolution & Idempotency**:
   - Status transitions to `RECOVERED`.
   - Recovered amount updates to `₹8,500.00`.
   - Re-clicking execute returns `idempotent: True` with **zero double-counting** of recovered revenue.
8. **Step 8 — Chronological Audit Timeline**:
   - Inspect the 6-event chronological audit log from gateway failure through AI investigation, policy approval, execution start, and settlement.
9. **Step 9 — Batch Recovery Execution**:
   - Click **Run Batch Recovery** in the header.
   - Observe bulk execution across 500+ cases with instant aggregate revenue impact.

---

## 🚀 How to Run in Local Environment

### 1. Prerequisites
- Python 3.12+
- Node.js 18+ (verified with Node v24)
- PostgreSQL 17 (running on `localhost:5432`)

### 2. Backend Setup
```bash
cd backend

# Activate Python virtual environment
.\venv\Scripts\activate  # On Windows
# source venv/bin/activate # On macOS/Linux

# Run migrations
alembic upgrade head

# Start FastAPI server (restrict reload watcher to app/ to avoid watching venv)
uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
```
- API Health: `http://127.0.0.1:8000/api/health`
- Swagger Docs: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
```bash
cd frontend

# Run Vite dev server
npm run dev
```
- Dashboard UI: `http://localhost:5173`

### 4. Running Backend Tests
```bash
cd backend
.\venv\Scripts\pytest tests/ -v
```
**54 out of 54 tests passing (100% pass rate)** across risk calculation, ML prediction, Gemini investigation, policy safety rules, state machine, payment simulator, and recovery execution.

### 5. Running Frontend Production Build
```bash
cd frontend
npm run build
```
**0 TypeScript errors, 0 lint errors, clean Vite production bundle.**

---

## 🎤 5-Minute Buildathon Pitch Script

A full time-coded 5-minute presentation script matching the live demo flow is available at [`docs/pitch.md`](docs/pitch.md).
