
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

Every day, payments fail for many different reasons — insufficient funds, network timeouts, abandoned checkouts, expired cards, bank downtime, and more.

The problem is that most systems either:

- **Blindly retry** the payment, which can annoy customers and create unnecessary attempts.
- **Do nothing**, even when the payment could still be recovered.

The important question isn't just *"Can I retry this payment?"*

It's:

> **"What should I do next, and is this payment actually worth recovering?"**

RevRescue.ai was built around that idea.

---

## 💡 The Solution

**RevRescue.ai** is an AI-assisted payment recovery system that takes a batch of failed transactions, understands why they failed, chooses an appropriate recovery strategy, and measures the result.

```text
Failed Transaction Batch
        ↓
Understand the failure reason
        ↓
Choose the appropriate strategy
        ↓
Apply recovery action
        ↓
Measure recovered revenue
        ↓
Show exceptions + audit trail + ROI
```

Instead of looking only at successful transactions, the system processes the **complete batch** and also shows transactions that could not be recovered.

The system also supports multiple merchant scenarios, allowing the same recovery engine to be tested with different merchant profiles and policies.

---

# ✨ Key Features

## 1. 🎯 Root-Cause-Aware Recovery

The system doesn't use the same recovery action for every failed payment.

| Failure Reason | Strategy | Reason |
|---|---|---|
| Insufficient Funds | Hinglish nudge + EMI offer | Give the customer another way to complete the payment |
| Network Timeout | Automatic retry | Usually a temporary issue |
| Bank Downtime | Retry through an alternate route | The original banking route may be unavailable |
| Abandoned Checkout | Discount code `COMEBACK5` | Customer already showed purchase intent |
| Card Expired | Update card / switch to UPI | The payment instrument needs to be fixed |
| User Cancelled | **No action** | Respect the customer's decision |
| Fraud Suspected | **Escalate to human review** | Risky transactions should not be automatically recovered |
| Invalid Card | **No action** | The payment cannot be recovered without fixing the card |

---

## 2. 🧠 Explainable Decision Stream

Instead of showing only the final action, the application shows the important factors behind each recovery decision.

For example:

```text
Failure detected: Insufficient Funds

Risk level: Low
Recovery likelihood: High
Selected strategy: EMI + Hinglish reminder
Reason: Customer may be able to complete payment later
Next action: Send recovery message
```

This makes the system easier to understand and audit without relying on an opaque decision.

---

## 3. 🧬 Customer Intelligence

The system generates a customer profile for each transaction.

It includes:

- **Risk Score** — 0–100
- **Recovery Propensity**
- **Value Tier** — High / Medium / Growing
- **Estimated LTV**
- Preferred communication channel
- Customer sentiment
- Best contact time
- **Next-Best-Action**

This helps the recovery strategy consider more than just the payment failure reason.

---

## 4. 🧪 What-If Strategy Simulator

The **What-If Lab** allows different recovery policies to be tested before applying them.

The available controls include:

- Maximum retries
- Discount incentive
- Contact hour
- Cooling-off period
- EMI strategy strength
- Alternate payment route priority

The simulator compares the baseline strategy with the modified strategy and estimates the effect on recovery.

This makes it easier to understand the trade-off between aggressive recovery and customer-friendly policies.

---

## 5. 🏪 Multi-Merchant Dashboard

I designed the system so that the recovery engine can be tested across different merchant scenarios.

Current merchant profiles include:

- Myntra
- Swiggy
- Zomato
- Nykaa
- BookMyShow
- Ajio

Each merchant has its own profile containing information such as:

- Merchant category
- Average transaction value
- Peak hours
- Communication tone
- Common failure type
- Merchant-specific settings

The dashboard can be filtered by merchant, and the relevant metrics and charts update accordingly.

---

## 6. 🏆 Merchant Recovery Leaderboard

The leaderboard compares recovery performance across merchants.

It shows:

- Recovery rate
- Recovered amount
- Best-performing merchant
- Merchant needing attention
- Performance comparison
- Merchant-specific insights

This makes it easier to identify where the recovery strategy is working well and where it needs improvement.

---

## 7. 🗣️ Hinglish Recovery Messages

The system can generate customer-facing recovery messages in natural Indian Hinglish.

The messages are generated using **Groq / Llama 3.3-70B** when the API is available.

There are also fallback templates, so the application continues working even if the API is unavailable.

Current message types include:

### Empathetic Alternative

Used for insufficient-funds cases, where the customer may need another payment option or EMI.

### Discount Urgency

Used for abandoned checkouts with the `COMEBACK5` discount.

### Card Update

Used when a card has expired, with options to update the card or use UPI.

---

## 8. 🛡️ Compliance-First Recovery

Recovery actions are limited by rules built into the application.

Current safeguards include:

- Maximum **3 retries** per transaction
- **2-hour cooling-off period** between contacts
- Fraud cases → **human escalation**
- Customer cancellation → **no further recovery attempt**
- Every action → **audit log**

These rules are part of the application logic rather than being mentioned only in the UI.

---

## 9. 📋 Honest Exception List

Not every failed payment can or should be recovered.

The **Exception List** shows transactions that were not recovered and the reason behind them.

Examples include:

- User cancellation
- Suspected fraud
- Invalid payment instrument
- Other non-recoverable cases

This prevents the system from hiding unsuccessful cases and gives a more realistic view of recovery performance.

---

## 10. 📈 ROI Scale Projector

The ROI Projector takes the recovery results from the synthetic dataset and allows them to be projected to a larger transaction volume.

It can estimate:

- Potential recovered amount
- Annual recovery
- Effect of different recovery rates
- Additional upside from policy changes

The purpose is to connect the technical recovery system with the business impact it could have at scale.

---

# 🏗️ Architecture

```text
RevRescue/
│
├── app.py                    # Streamlit dashboard and main application
├── data_generator.py         # Synthetic failed-payment dataset
├── recovery_agent.py         # Recovery strategy and policy rules
├── ai_reasoning.py           # Decision explanation stream
├── customer_intel.py         # Customer scoring and profiles
├── whatif_simulator.py       # Policy simulation
├── merchant_intel.py         # Merchant profiles and leaderboard
├── hinglish_bot.py           # Groq/Llama message generation
├── razorpay_service.py       # Payment link creation + fallback
├── audit_logger.py           # Audit trail logging
│
├── requirements.txt
├── .env.example
├── README.md
│
└── data/
    ├── failed_transactions.csv
    └── audit_trail.log
```

### Runtime Flow

1. `data_generator.py` creates a synthetic batch of failed transactions.
2. `recovery_agent.py` analyses each transaction and selects a recovery strategy.
3. `ai_reasoning.py` provides an explanation of the selected decision.
4. `hinglish_bot.py` generates a customer-facing recovery message when required.
5. `razorpay_service.py` creates a payment link or uses a mock fallback.
6. `customer_intel.py` generates customer-level insights.
7. `merchant_intel.py` handles merchant filtering and leaderboard calculations.
8. `whatif_simulator.py` estimates the effect of different recovery policies.
9. `audit_logger.py` records the actions taken.
10. `app.py` brings everything together in the Streamlit dashboard.

---

# 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit + custom CSS + Plotly |
| Agent Logic | Python rule-based recovery engine |
| LLM | Groq API — `llama-3.3-70b-versatile` |
| Payments | Razorpay Python SDK — Test Mode |
| Data | Pandas + Faker (`en_IN`) |
| Configuration | python-dotenv |

### Reliability Principle

The application is designed so that its main workflow does not completely depend on external APIs.

- Groq unavailable → Hinglish fallback templates
- Razorpay unavailable → Mock payment links
- API keys not configured → Core application can still be explored

---

# 🚀 Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/RevRescue-AI.git
cd RevRescue-AI
```

## 2. Create a Virtual Environment

### Windows

```bash
py -m venv env
env\Scripts\Activate.ps1
```

### Mac / Linux

```bash
python3 -m venv env
source env/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Then add your keys if available:

```env
GROQ_API_KEY=gsk_your_key_here
RAZORPAY_KEY_ID=rzp_test_xxx
RAZORPAY_KEY_SECRET=your_secret_here
```

The Groq and Razorpay keys are optional because fallback mechanisms are included.

## 5. Generate Sample Data

```bash
python data_generator.py
```

## 6. Start the Application

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

---

# 🎮 Application Flow

The application can be explored in the following order:

1. Generate a new transaction batch.
2. Run the recovery agent.
3. Check total failed transactions and recovered revenue.
4. Filter results by merchant.
5. View failure reasons and transaction status.
6. Check the ROI Projector.
7. Compare merchants using the Leaderboard.
8. Open Customer Intelligence for individual transactions.
9. Test different policies in the What-If Lab.
10. Review the generated Hinglish recovery messages.
11. Check the Audit Trail.
12. Review the Exception List for transactions that were not recovered.

---

# 📏 Track 03 — Requirement Mapping

| Requirement | How RevRescue.ai Addresses It |
|---|---|
| Detect revenue at risk | Processes failed transactions across multiple failure categories |
| Determine the right intervention | Maps failure reasons to specific recovery strategies |
| Execute bounded recovery workflow | Supports retry, customer messaging, escalation, and no-action paths |
| Measure recovered money | Tracks recovery status and recovered amount |
| Compliant stopping and escalation | Retry limits, cooling-off periods, fraud escalation, and cancellation handling |
| Audit trail | Timestamped audit logs for recovery actions |
| Honest exception handling | Separate Exception List for unrecovered transactions |
| Full-batch processing | Processes the complete synthetic transaction batch |
| Multi-merchant support | Merchant profiles, filtering, and leaderboard |
| Policy experimentation | What-If Lab for testing strategy changes |
| Explainability | Decision factors and strategy explanations |
| Customer intelligence | Risk, propensity, LTV, and next-best-action indicators |

---

# 📊 Sample Results

Results change depending on the generated synthetic batch.

An example local run may look like:

| Metric | Example |
|---|---:|
| Batch size | 75 transactions |
| Merchants | 6 |
| Recovery rate | ~42–54% |
| Average transaction value | ~₹3,800–₹4,500 |
| Unrecoverable cases | Cancellation, fraud, invalid card |
| Projected annual recovery | Depends on scale assumptions |
| What-If improvement | Depends on selected policy |

The numbers are intentionally not fixed. Every generated batch can contain different transaction combinations, so the results can change between runs.

The goal is to show the actual output of the recovery process rather than rely on a fixed success number.

---

# 🔒 Safety & Compliance

- **Test mode only** — no live money movement.
- **Synthetic data** — no real customer PII is used.
- Recovery actions are bounded by predefined rules.
- Fraud cases are not automatically recovered.
- Customer cancellation is respected.
- API failures fall back to local alternatives.
- Recovery actions are recorded in the audit trail.
- Payment functionality is intended for demonstration purposes.

---

# 🗺️ Future Improvements

If I continue developing RevRescue.ai after the hackathon, the next improvements would include:

- [ ] WhatsApp Business API / RCS integration
- [ ] Merchant-specific policy configuration
- [ ] Background jobs for scheduled recovery attempts
- [ ] ML model for recovery-success prediction
- [ ] Payment webhook integration
- [ ] Support for Tamil, Telugu, Bengali, Marathi, and other languages
- [ ] Voice-based recovery
- [ ] A/B testing for recovery strategies
- [ ] Persistent transaction and merchant databases
- [ ] Production payment-event monitoring

---

# 📁 Project Structure

| File | Responsibility |
|---|---|
| `app.py` | UI, metrics, charts, tabs, and application orchestration |
| `data_generator.py` | Generates synthetic Indian failed-payment data |
| `recovery_agent.py` | Recovery strategies and compliance rules |
| `ai_reasoning.py` | Decision explanation stream |
| `customer_intel.py` | Customer scoring, LTV, and next-best-action |
| `whatif_simulator.py` | Policy simulation and expected-value calculations |
| `merchant_intel.py` | Merchant profiles, filtering, and leaderboard |
| `hinglish_bot.py` | Groq message generation and fallback templates |
| `razorpay_service.py` | Razorpay test-mode payment links and mock fallback |
| `audit_logger.py` | Timestamped audit log |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |

---

# 🧪 Development Notes

A few decisions I made while building the project:

- I focused on keeping the application usable even when APIs are unavailable.
- Recovery rules are implemented in the application logic instead of being only UI descriptions.
- The complete transaction batch is processed instead of manually selecting successful examples.
- Failed and unrecoverable transactions are still shown in the dashboard.
- Merchant filtering affects the relevant dashboard views.
- The system uses synthetic data for testing.
- Razorpay functionality is kept in Test Mode.
- The dashboard uses a dark interface with gold accents.

---

# 🎯 Why I Built It This Way

A failed payment doesn't always mean that the customer is lost.

For example, an insufficient-funds failure is very different from a suspected fraud transaction. An abandoned checkout is different from a user who has explicitly cancelled the payment.

So instead of treating every failure the same way, RevRescue.ai tries to answer a few simple questions:

1. **Why did the payment fail?**
2. **Should I try to recover it?**
3. **What recovery method makes sense for this case?**
4. **When should I stop trying?**
5. **Did the recovery actually bring money back?**
6. **Can I explain what happened afterwards?**

The project combines these decisions into one workflow rather than treating payment recovery as just another automatic retry system.

---

# 👤 Author

**Built independently for Razorpay Hackathon 2026 — Track 03: AI Revenue Recovery**

RevRescue.ai was designed and developed as a solo project, including the recovery logic, dashboard, synthetic data generation, customer intelligence, merchant analytics, policy simulator, payment integration, fallback handling, and audit system.

---

# 📄 License

MIT License — free to use, modify, and learn from.

---

<p align="center">

<b>RevRescue.ai</b><br>
<i>Diagnose. Recover. Prove it.</i>

</p>