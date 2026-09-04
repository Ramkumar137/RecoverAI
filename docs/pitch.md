# RecoverAI — 5-Minute Buildathon Pitch Script

**Track**: 03 — AI Revenue Recovery  
**Product**: RecoverAI  
**Target Duration**: 5:00 minutes  

---

### ⏱ 0:00 – 0:30 | The Problem
> *"Failed payments don't always mean lost customers. Many failures are temporary, but businesses often don't know which payments are worth recovering or what action to take."*

Businesses lose significant revenue because payments fail, subscriptions lapse, and checkouts are abandoned. Most existing payment recovery mechanisms are naive: they retry blindly at arbitrary intervals, which degrades gateway success rates, triggers issuer penalties, and annoys customers.

---

### ⏱ 0:30 – 1:00 | The Solution
> *"RecoverAI is an AI revenue recovery agent that identifies revenue at risk, estimates recoverability, investigates the failure, recommends the safest intervention, and measures the money actually recovered."*

RecoverAI provides an end-to-end autonomous lifecycle:
**Detect** revenue at risk -> **Diagnose** root cause -> **Predict** recoverability via ML -> **Recommend** strategy via Gemini 2.5 Flash -> **Validate** with deterministic policy -> **Execute** bounded recovery workflows -> **Audit** every action -> **Measure** recovered revenue in real time.

---

### ⏱ 1:00 – 1:45 | The Dashboard
> *Open Main Dashboard (`http://localhost:5173/dashboard`)*

**Show the core metrics**:
- **Revenue at Risk**: `₹14.90L` (total failed & past-due transaction volume)
- **Potentially Recoverable**: `₹9.43L` (ML-predicted salvageable revenue)
- **Recovered Revenue**: `₹751.44k` (actual settled funds returned to merchant)
- **Recovery Rate**: `79.7%` of the recoverable pool

**Show the visual Recovery Funnel**:
- `Revenue at Risk → Potentially Recoverable → Recovery Attempts → Recovered Revenue`
- Explain that RecoverAI measures actual financial recovery rather than just generating advisory text or recommendations.
- Point out the product safety principle in the sidebar: *"AI recommends. Deterministic policy controls execution."*

---

### ⏱ 1:45 – 2:45 | PAY_10482 Forensic Demo
> *Click the featured VIP Demo card from the dashboard or navigate to `/recovery` and open `PAY_10482`.*

**Show the payment telemetry**:
- **Amount**: `₹8,500.00`
- **Method**: `UPI`
- **Failure Code**: `BANK_TIMEOUT`
- **Retry Count**: `0 / 3`
- **Customer**: Long-tenured customer with 92% historical payment success rate
- **ML Recoverability Score**: `98.5%` (HIGH tier)

**Review the Gemini AI Autonomous Investigation**:
- **Diagnosis**: `TEMPORARY_BANK_FAILURE` (95% confidence)
- **Evidence**: Transient gateway timeout detected, customer account has high lifetime value, zero prior retries.
- **AI Recommendation**: `RETRY_LATER` via `GATEWAY_RETRY` with a 15-minute recommended delay.

> *"The AI sees a temporary bank timeout, strong customer history, and a low retry count."*

---

### ⏱ 2:45 – 3:15 | Deterministic Policy Validation
> *Highlight the Policy Decision Card: `AI Proposed → Deterministic Policy Check → Approved Final Action`*

**Show policy status**:
- **Ruling**: `APPROVED` (`POLICY_MAX_RETRIES_COMPLIANT`)
- **Safety Limits Enforced**:
  - Retries: `0 / 3` (below max threshold of 3)
  - Recovery Window: `48 Hours TTL` (active window)
  - Escalation Required: `False`

> *"The AI does not control money movement. The policy engine decides whether the recommendation is allowed."*

---

### ⏱ 3:15 – 4:00 | Simulated Execution & Audit Timeline
> *Click 'Execute Recovery Action' → Confirm dialog*

**Show execution outcome**:
- Case status transitions to `RECOVERED`
- Recovered amount updates to `₹8,500.00`
- Click execute again to demonstrate **strict idempotency**: returns `idempotent: True` with zero double-counting.

**Review the Chronological Audit Timeline**:
- Trace the 6 immutable events:
  1. `[GATEWAY] PAYMENT_FAILED`
  2. `[RECOVERY_PIPELINE] CASE_CREATED`
  3. `[GEMINI_2_5_FLASH] AI_INVESTIGATION_COMPLETED`
  4. `[RECOVERY_EXECUTION_ENGINE] RECOVERY_ACTION_STARTED`
  5. `[PAYMENT_SIMULATOR] PAYMENT_RETRY_ATTEMPTED`
  6. `[RECOVERY_EXECUTION_ENGINE] PAYMENT_RECOVERED`

---

### ⏱ 4:00 – 4:40 | Batch Recovery & Macro Impact
> *Click 'Run Batch Recovery' in the top header → Confirm execution*

**Show batch results modal**:
- **Cases Processed**: 500+ payments analyzed
- **Revenue at Risk**: `₹14.90L`
- **Potentially Recoverable**: `₹9.43L`
- **Recovered Revenue**: `₹751.44k`
- **Aggregate Recovery Rate**: `79.7%`

> *"The important metric is not how smart the AI sounds. It is how much revenue the system actually recovers."*

---

### ⏱ 4:40 – 5:00 | Closing
> *"RecoverAI closes the loop from failed payment to measured recovery: detect, diagnose, recommend, validate, recover, audit, and measure."*

- Fully containerized & deployable monolith (React + FastAPI + PostgreSQL).
- Deterministic guardrails guarantee regulatory compliance and zero naive retry fatigue.
- Ready for production integration with Razorpay Webhooks and Payment Links.
