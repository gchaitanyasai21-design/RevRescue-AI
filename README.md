# 💰 RevRescue.ai

### Turning failed payments into recovered revenue

**Razorpay Hackathon 2026 — Track 03: AI Revenue Recovery**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B.svg)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3-orange.svg)](https://groq.com)
[![Razorpay](https://img.shields.io/badge/Razorpay-Test%20Mode-072654.svg)](https://razorpay.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 The Problem

Every day, millions of payments fail across Indian commerce — insufficient funds, network timeouts, abandoned checkouts, expired cards, bank downtime.

Most systems either:
- **Blindly retry** (annoying customers, burning gateway fees), or
- **Do nothing** (leaving recoverable revenue on the table)

Reconciliation, settlement, and recovery are still largely manual.  
**Verification capacity — not generation speed — is the bottleneck.**

---

## 💡 The Solution

**RevRescue.ai** is an intelligent recovery agent that closes the full finance-ops loop:
Failed Transaction Batch
↓
Diagnose root cause
↓
Pick compliant strategy
↓
Execute recovery action
↓
Measure money recovered
↓
Honest exception list + full audit trail

It does **not** cherry-pick. It processes the **entire batch**, reports real metrics, and shows what it *couldn't* recover — and why.

---

## ✨ Key Features

### 1. Root-Cause-Aware Recovery (Not Blind Retries)
| Failure Reason        | Strategy                         | Why it works                          |
|-----------------------|----------------------------------|---------------------------------------|
| Insufficient Funds    | Hinglish nudge + EMI offer       | Wait for salary cycle, reduce friction |
| Network Timeout       | Silent auto-retry                | Transient — no customer spam           |
| Bank Downtime         | Retry via alternate route        | Bypass the down acquirer               |
| Abandoned Checkout    | Discount code `COMEBACK5`        | High intent, needs a nudge             |
| Card Expired          | Update card / switch to UPI      | Fix the instrument, not the intent     |
| User Cancelled        | **No action**                    | Respect explicit consent               |
| Fraud Suspected       | **Escalate to human**            | Never auto-recover risky txns          |
| Invalid Card          | **No action**                    | Not recoverable                        |

### 2. Hinglish Conversational Recovery
Context-aware WhatsApp-style messages in natural Indian Hinglish, powered by **Groq (Llama 3.3)** with production-safe fallback templates if the API is unavailable.

### 3. Compliance-First Design
- Max **3 retries** per transaction  
- **2-hour cooling-off** between contacts  
- Fraud → human escalation only  
- User cancellation always respected  
- Full **audit trail** of every decision  

### 4. Honest Exception List
Judges asked for it. We built it.  
Every unrecoverable transaction is listed with a clear reason — no hiding, no cherry-picking.

### 5. ROI Scale Projector
Interactive simulator that extrapolates your batch recovery rate to Razorpay-scale daily volume and shows projected annual recovery in crores.

### 6. Live Agent Processing View
Watch the agent diagnose and act on every transaction in the batch in real time — full transparency.

---

## 🏗️ Architecture
RevRescue/
├── app.py # Streamlit dashboard (metrics, charts, tabs, ROI)
├── data_generator.py # Synthetic Indian failed-payment dataset
├── recovery_agent.py # Decision engine + compliance rules
├── hinglish_bot.py # Groq/Llama Hinglish message generator
├── razorpay_service.py # Payment link creation (test mode + mock fallback)
├── audit_logger.py # Append-only action log
├── requirements.txt
├── .env.example
└── data/
├── failed_transactions.csv
└── audit_trail.log


**Flow:**
1. `data_generator` creates 50–100 realistic failed txns  
2. `recovery_agent` diagnoses each txn and selects a strategy  
3. `hinglish_bot` + `razorpay_service` execute customer-facing actions  
4. `audit_logger` records every step  
5. `app.py` renders metrics, charts, chats, audit trail, exceptions, ROI  

---

## 🛠️ Tech Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| UI           | Streamlit + custom dark/gold CSS + Plotly       |
| Agent Logic  | Python rule engine with weighted strategies     |
| LLM          | Groq API — `llama-3.3-70b-versatile`            |
| Payments     | Razorpay Python SDK (Test Mode)                 |
| Data         | Pandas + Faker (`en_IN`)                        |
| Config       | python-dotenv                                   |

**Design principle:** The demo must work **even without API keys**.  
Missing Groq → fallback Hinglish templates.  
Missing Razorpay → mock payment links.  
Zero broken demos on hackathon Wi-Fi.

---

## 🚀 Quick Start

### 1. Clone & setup
```bash
git clone https://github.com/YOUR_USERNAME/RevRescue-AI.git
cd RevRescue-AI

2. Create virtual environment (recommended)
# Windows
py -m venv env
env\Scripts\Activate.ps1

# Mac/Linux
python3 -m venv env
source env/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Configure environment
cp .env.example .env
Edit .env:
GROQ_API_KEY=gsk_your_key_here          # optional but recommended
RAZORPAY_KEY_ID=rzp_test_xxx            # optional
RAZORPAY_KEY_SECRET=your_secret_here    # optional
Get Groq key (free): https://console.groq.com/keys
Get Razorpay test keys: https://dashboard.razorpay.com → Test Mode → API Keys

5. Generate sample data & run
python data_generator.py
streamlit run app.py
Open http://localhost:8501

🎮 Demo Script (2 minutes)
1.Sidebar → Generate New Batch (50–100 txns)
2.Sidebar → Run Recovery Agent — watch full-batch processing
3.Top metrics — Total Failed / Recovered / Rate / Unrecoverable
4.Charts — Failure reasons + status distribution
5.ROI Projector — drag daily volume, show crore-scale impact
6.Tab: Hinglish Chats — bot message + customer reply
7.Tab: Audit Trail — every action, timestamped
8.Tab: Exception List — honest “could not recover” reasons

📏 Hitting The Bar (Track 03 Rubric)
Requirement 	                       How RevRescue delivers
Detect revenue at risk	                Batch ingest of failed txns with 8 failure classes
Determine right intervention	        Root-cause → strategy map
Execute bounded recovery workflow	    Auto-retry / Hinglish nudge / escalate / no-action
Measured money recovered	            Dashboard metrics + recovered_amount per txn
Compliant escalation & stopping        	Max retries, cooling-off, fraud escalate, cancel respect
Audit trail	                            data/audit_trail.log + in-app Audit tab
Honest exception list	                Exception List tab — no cherry-picking
Full batch, not one lucky match	        Entire CSV processed every run

📊 Sample                       Results (from a real local run)
Metric	                         Value
Batch size	                     75 transactions
Recovery rate	                ~42–54%
Avg transaction value	        ~₹3,800–4,500
Unrecoverable (honest)	        User cancel, fraud, invalid card
Projected annual (at scale)	    ₹1,000+ Cr illustration via ROI tool

Exact numbers vary per synthetic batch — that’s intentional. We optimize for honest measurement, not a fixed vanity metric.

🔒 Safety & Compliance Notes
Test mode only — no live money movement
Synthetic data — no real PII
Defense-only recovery — no offensive or spammy patterns
Stopping rules enforced in code, not just in the UI copy
API failures degrade gracefully to templates/mocks

📁 Project Structure (detail)

File	                        Responsibility
app.py	                        UI, metrics, charts, ROI, tabs, batch orchestration
data_generator.py	            Faker-based Indian txn generator with weighted error codes
recovery_agent.py	            Strategy dictionary, compliance checks, simulate_recovery
hinglish_bot.py	                Groq chat completions + fallback templates + reply simulator
razorpay_service.py	            Payment link create + mock URL fallback
audit_logger.py	                Timestamped append-only log read/write/clear
requirements.txt	            Pinned dependencies
.env.example	                Safe key placeholders

🧪 Development Notes
Built for demo reliability first — works offline on fallbacks
All money actions are explainable, bounded, and logged
One full batch run = one complete proof of the loop
UI theme: dark + Razorpay-adjacent gold accents

👥 Author
Built for Razorpay Hackathon 2026 — Track 03: AI Revenue Recovery

If you’re a judge or mentor reviewing this:
run the app, generate a batch, run the agent, and open the Exception List + Audit Trail tabs first — that’s the product philosophy.


📄 License
MIT — free to use, modify, and learn from

