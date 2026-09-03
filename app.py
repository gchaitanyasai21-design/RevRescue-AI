"""Streamlit dashboard for RevRescue.ai."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from ai_reasoning import generate_reasoning_stream
from audit_logger import clear_audit_trail, get_audit_trail, log_action
from customer_intel import build_customer_intelligence
from data_generator import OUTPUT_FILE, generate_failed_transactions
from hinglish_bot import generate_hinglish_message, simulate_customer_reply
from razorpay_service import create_payment_link
from recovery_agent import COOLING_OFF_HOURS, MAX_RETRIES, diagnose_and_strategize, simulate_recovery
from whatif_simulator import WhatIfInputs, simulate_whatif


DATA_DIR = Path(__file__).resolve().parent / "data"

st.set_page_config(
    page_title="RevRescue.ai",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: #0e1117;
            color: #f7f3ea;
        }
        section[data-testid="stSidebar"] {
            background: #151922;
            border-right: 1px solid rgba(255, 184, 77, 0.18);
        }
        h1, h2, h3 {
            color: #fff7e8;
            letter-spacing: 0;
        }
        .hero {
            padding: 1.2rem 0 0.8rem 0;
        }
        .hero h1 {
            font-size: 2.8rem;
            margin-bottom: 0.2rem;
        }
        .hero p {
            color: #f5b84b;
            font-size: 1.05rem;
            margin-top: 0;
        }
        div[data-testid="stMetric"] {
            background: #171b24;
            border: 1px solid rgba(255, 184, 77, 0.22);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.2);
        }
        div[data-testid="stMetricLabel"] p {
            color: #c6cad3;
        }
        div[data-testid="stMetricValue"] {
            color: #ffb84d;
        }
        .info-box {
            background: rgba(255, 184, 77, 0.10);
            border: 1px solid rgba(255, 184, 77, 0.26);
            border-radius: 8px;
            padding: 0.85rem;
            color: #f7f3ea;
            font-size: 0.92rem;
        }
        .chat-bubble-bot {
            background: #1d2430;
            border-left: 4px solid #ffb84d;
            border-radius: 8px;
            padding: 0.85rem;
            margin: 0.4rem 0;
            white-space: pre-wrap;
        }
        .chat-bubble-user {
            background: #2a2118;
            border-left: 4px solid #ff7a1a;
            border-radius: 8px;
            padding: 0.85rem;
            margin: 0.4rem 0 1rem 0;
            white-space: pre-wrap;
        }
        .exception-row {
            background: #21171a;
            border: 1px solid rgba(255, 99, 99, 0.25);
            border-radius: 8px;
            padding: 0.85rem;
            margin-bottom: 0.65rem;
        }
        .footer {
            color: #9da3ae;
            padding-top: 1.4rem;
            font-size: 0.9rem;
            text-align: center;
        }
        .stButton > button {
            background: linear-gradient(135deg, #ffb84d, #ff7a1a);
            color: #111318;
            border: 0;
            border-radius: 8px;
            font-weight: 700;
        }
        .stButton > button:hover {
            color: #111318;
            border: 0;
            filter: brightness(1.05);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_session_state() -> None:
    if "transactions" not in st.session_state:
        st.session_state.transactions = load_existing_data()
    if "chats" not in st.session_state:
        st.session_state.chats = []
    if "agent_has_run" not in st.session_state:
        st.session_state.agent_has_run = False


def load_existing_data() -> pd.DataFrame:
    if OUTPUT_FILE.exists():
        return pd.read_csv(OUTPUT_FILE)
    return pd.DataFrame()


def save_transactions(df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)


def money(value: float) -> str:
    return f"₹{value:,.0f}"


def status_for_failed_attempt(strategy: dict[str, Any]) -> str:
    action = strategy.get("action")
    if action in {"NO_ACTION", "ESCALATE_TO_HUMAN", "COMPLIANCE_BLOCK"}:
        return "UNRECOVERABLE"
    return "IN_PROGRESS"


def process_full_batch(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, str]]]:
    processed = df.copy()
    chats: list[dict[str, str]] = []
    progress = st.progress(0, text="Starting recovery agent...")
    terminal_container = st.empty()
    total = len(processed)

    for index, (row_label, row) in enumerate(processed.iterrows(), start=1):
        txn = row.to_dict()
        txn_id = str(txn["txn_id"])
        strategy = diagnose_and_strategize(txn)
        action = str(strategy["action"])

        log_action(
            txn_id,
            "DIAGNOSE",
            f"{txn.get('error_code')} -> {action}; {strategy.get('description')}",
        )

        # 🧠 FEATURE 1: Live AI reasoning stream
        reasoning_lines = generate_reasoning_stream(txn, strategy)
        reasoning_display = f"### 🧠 AI Agent Reasoning — `{txn_id}`\n\n"
        for line in reasoning_lines:
            reasoning_display += f"{line}\n\n"
            terminal_container.markdown(
                f"""
                <div style="
                    background:#0d1420;
                    border-left:3px solid #ffb84d;
                    padding:1rem 1.1rem;
                    border-radius:10px;
                    font-family:ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
                    color:#b7d0ea;
                    font-size:0.92rem;
                    line-height:1.55;
                    min-height:180px;
                ">
                {reasoning_display.replace(chr(10), '<br>')}
                </div>
                """,
                unsafe_allow_html=True,
            )
            time.sleep(0.08)

        recovered = False
        recovered_amount = 0.0
        payment_link = ""

        if action == "COMPLIANCE_BLOCK":
            log_action(txn_id, action, strategy.get("block_reason", "Blocked by compliance rules."), "WARNING")
        elif action == "ESCALATE_TO_HUMAN":
            log_action(txn_id, action, "Routed to manual risk review; no automated payment attempt.", "WARNING")
        elif action == "NO_ACTION":
            log_action(txn_id, action, strategy.get("description", "No recovery action selected."), "INFO")
        elif action in {"AUTO_RETRY", "AUTO_RETRY_ALT_ROUTE"}:
            recovered, recovered_amount = simulate_recovery(txn, strategy)
            log_action(
                txn_id,
                action,
                f"Attempted automated recovery; success={recovered}; recovered_amount={recovered_amount:.2f}",
                "SUCCESS" if recovered else "INFO",
            )
        elif action == "SEND_HINGLISH_NUDGE":
            payment_link = create_payment_link(txn)
            message_type = str(strategy.get("message_type") or "empathetic_alternative")
            bot_message = generate_hinglish_message(txn, message_type, payment_link)
            customer_reply = simulate_customer_reply(message_type)
            chats.append(
                {
                    "txn_id": txn_id,
                    "customer": str(txn.get("customer_name", "")),
                    "merchant": str(txn.get("merchant", "")),
                    "bot_message": bot_message,
                    "customer_reply": customer_reply,
                    "payment_link": payment_link,
                }
            )
            log_action(txn_id, "PAYMENT_LINK_CREATED", payment_link)
            log_action(txn_id, "HINGLISH_NUDGE_SENT", bot_message.replace("\n", " / "))
            recovered, recovered_amount = simulate_recovery(txn, strategy)
            log_action(
                txn_id,
                "CUSTOMER_OUTCOME",
                f"Simulated reply='{customer_reply}'; success={recovered}; recovered_amount={recovered_amount:.2f}",
                "SUCCESS" if recovered else "INFO",
            )

        processed.at[row_label, "retry_count"] = int(txn.get("retry_count") or 0) + (
            1 if strategy.get("is_recoverable") else 0
        )
        if action == "SEND_HINGLISH_NUDGE":
            processed.at[row_label, "last_contact_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        processed.at[row_label, "recovery_status"] = (
            "RECOVERED" if recovered else status_for_failed_attempt(strategy)
        )
        processed.at[row_label, "recovered_amount"] = recovered_amount
        processed.at[row_label, "recovery_action"] = action
        processed.at[row_label, "recovery_reason"] = strategy.get("block_reason") or strategy.get("description")
        processed.at[row_label, "payment_link"] = payment_link

        progress.progress(index / total, text=f"Processed {index}/{total} transactions")

    progress.empty()
    terminal_container.empty()
    save_transactions(processed)
    return processed, chats


def render_metrics(df: pd.DataFrame) -> None:
    total_failed = float(df["amount"].sum()) if not df.empty else 0.0
    total_recovered = float(df["recovered_amount"].sum()) if not df.empty and "recovered_amount" in df else 0.0
    recovery_rate = (total_recovered / total_failed * 100) if total_failed else 0.0
    unrecoverable_count = int((df.get("recovery_status", pd.Series(dtype=str)) == "UNRECOVERABLE").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Failed Amount", money(total_failed))
    c2.metric("Total Recovered Amount", money(total_recovered))
    c3.metric("Recovery Rate", f"{recovery_rate:.1f}%")
    c4.metric("Unrecoverable Txns", f"{unrecoverable_count}")


def render_charts(df: pd.DataFrame) -> None:
    left, right = st.columns(2)

    with left:
        reason_counts = df["error_code"].value_counts().reset_index()
        reason_counts.columns = ["Failure Reason", "Count"]
        fig = px.bar(
            reason_counts,
            x="Count",
            y="Failure Reason",
            orientation="h",
            color="Count",
            color_continuous_scale=["#ff7a1a", "#ffb84d"],
            title="Failure Reasons Breakdown",
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0e1117", plot_bgcolor="#151922", height=360)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        status_counts = df["recovery_status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.pie(
            status_counts,
            names="Status",
            values="Count",
            title="Recovery Status Distribution",
            color_discrete_sequence=["#ffb84d", "#ff7a1a", "#e85d75", "#64748b"],
            hole=0.42,
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="#0e1117", height=360)
        st.plotly_chart(fig, use_container_width=True)


def render_roi_projection(df: pd.DataFrame) -> None:
    st.markdown("<h3>📈 Projected Impact at Razorpay Scale</h3>", unsafe_allow_html=True)
    st.caption("What if this agent ran across Razorpay's full transaction volume?")

    total_failed = float(df["amount"].sum()) if not df.empty else 0.0
    total_recovered = float(df["recovered_amount"].sum()) if not df.empty and "recovered_amount" in df else 0.0
    recovery_rate = (total_recovered / total_failed) if total_failed > 0 else 0.0
    avg_txn_value = float(df["amount"].mean()) if not df.empty else 0.0

    c1, c2, c3 = st.columns(3)

    with c1:
        daily_failed_txns_at_scale = st.number_input(
            "Estimated Failed txns/day:",
            value=100000,
            step=10000,
            help="Simulate Razorpay's daily failed transaction volume",
        )

    projected_daily_recovery = daily_failed_txns_at_scale * recovery_rate * avg_txn_value
    projected_annual_recovery = projected_daily_recovery * 365

    with c2:
        st.metric("Avg Transaction Value", money(avg_txn_value))
        st.metric("Current Agent Recovery Rate", f"{recovery_rate * 100:.1f}%")

    with c3:
        st.metric("Projected Daily Recovery", money(projected_daily_recovery))
        st.metric(
            "💰 Projected Annual Recovery",
            money(projected_annual_recovery),
            delta="Generated by this AI agent",
        )

    if projected_annual_recovery > 10000000:
        st.success(
            f"🚀 At scale, this AI agent could recover **₹{projected_annual_recovery/10000000:.1f} Crores annually** for Razorpay's merchant ecosystem!"
        )


def render_transactions_tab(df: pd.DataFrame) -> None:
    columns = [
        "txn_id",
        "customer_name",
        "merchant",
        "amount",
        "payment_method",
        "error_code",
        "retry_count",
        "recovery_status",
        "recovered_amount",
        "recovery_action",
    ]
    visible = [col for col in columns if col in df.columns]
    st.dataframe(df[visible], use_container_width=True, hide_index=True)


def render_customer_intelligence(df: pd.DataFrame) -> None:
    st.markdown("### 🧬 Customer Intelligence Profile")
    st.caption("Select any transaction to view behavioral score, risk, propensity and next-best-action.")

    if df.empty:
        st.info("No transactions available.")
        return

    txn_ids = df["txn_id"].astype(str).tolist()
    selected_txn = st.selectbox("Select transaction", txn_ids, index=0)
    row = df[df["txn_id"].astype(str) == selected_txn].iloc[0].to_dict()
    intel = build_customer_intelligence(row)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Risk Score", f"{intel['risk_score']}/100")
    c2.metric("Recovery Propensity", f"{intel['recovery_propensity']}%")
    c3.metric("Value Tier", intel["value_tier"])
    c4.metric("Est. LTV", money(float(intel["estimated_ltv"])))

    left, right = st.columns(2)

    with left:
        st.markdown(
            f"""
            <div class='info-box'>
                <b>{intel['customer_name']}</b> · {intel['txn_id']}<br>
                Merchant: <b>{intel['merchant']}</b><br>
                Amount: <b>₹{intel['amount']:,.2f}</b><br>
                Failure: <b>{intel['error_code']}</b><br><br>
                <b>Best Channel:</b> {intel['best_channel']}<br>
                <b>Preferred Window:</b> {intel['preferred_window']}<br>
                <b>Sentiment:</b> {intel['sentiment']}<br>
                <b>Past Recoveries:</b> {intel['prior_success']} success / {intel['prior_fail']} fail
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div class='info-box'>
                <b>🎯 Next Best Action</b><br>
                {intel['best_action']}<br><br>
                <b>🧠 Agent Recommendation</b><br>
                {intel['recommendation']}<br><br>
                <b>Trust Signals</b><br>
                {"<br>".join(f"• {signal}" for signal in intel["trust_signals"])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    gauge_df = pd.DataFrame(
        {
            "Metric": ["Risk Score", "Recovery Propensity"],
            "Value": [intel["risk_score"], intel["recovery_propensity"]],
        }
    )
    fig = px.bar(
        gauge_df,
        x="Metric",
        y="Value",
        color="Metric",
        color_discrete_sequence=["#e85d75", "#ffb84d"],
        range_y=[0, 100],
        title="Risk vs Recovery Propensity",
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#151922",
        height=300,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_whatif_simulator(df: pd.DataFrame) -> None:
    """FEATURE 3: Interactive What-If Strategy Simulator."""
    st.markdown("### 🧪 What-If Strategy Simulator")
    st.caption("Tune recovery levers and instantly see projected upside on this batch.")

    if df.empty:
        st.info("Generate a batch to use the simulator.")
        return

    left, right = st.columns([1.1, 1.2])

    with left:
        st.markdown("#### Strategy Levers")
        max_retries = st.slider("Max retries", min_value=1, max_value=5, value=3, step=1)
        discount_pct = st.slider("Discount incentive (%)", min_value=0, max_value=15, value=5, step=1)
        contact_hour = st.slider("Contact hour (24h format)", min_value=0, max_value=23, value=19, step=1)
        cooling_off_hours = st.slider("Cooling-off (hours)", min_value=0.5, max_value=6.0, value=2.0, step=0.5)
        emi_push_strength = st.select_slider(
            "EMI push strength (Insufficient Funds)",
            options=[0, 1, 2],
            value=1,
            format_func=lambda x: {0: "Quiet", 1: "Balanced", 2: "Aggressive"}[x],
        )
        alt_route_priority = st.select_slider(
            "Alternate route priority (Bank/Network failures)",
            options=[0, 1],
            value=1,
            format_func=lambda x: {0: "Off", 1: "On"}[x],
        )

        inputs = WhatIfInputs(
            max_retries=max_retries,
            discount_pct=discount_pct,
            contact_hour=contact_hour,
            emi_push_strength=int(emi_push_strength),
            alt_route_priority=int(alt_route_priority),
            cooling_off_hours=float(cooling_off_hours),
        )

    result = simulate_whatif(df, inputs)

    with right:
        st.markdown("#### Projected Outcome")
        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Expected Recovery Rate",
            f"{result['expected_rate']*100:.1f}%",
            delta=f"{result['delta_rate_pp']:+.1f} pp vs baseline",
        )
        c2.metric(
            "Expected Recovered",
            money(result["expected_recovered"]),
            delta=f"{result['delta_recovered']:+,.0f} vs baseline",
        )
        c3.metric("Blocked (Compliance)", f"{result['blocked_txns']} txns")

        daily_vol = st.number_input(
            "Scale: failed txns/day",
            min_value=1000,
            max_value=500000,
            value=100000,
            step=5000,
            key="whatif_daily_vol",
        )
        avg_txn = float(df["amount"].mean()) if len(df) else 0.0
        annual = daily_vol * result["expected_rate"] * avg_txn * 365
        baseline_annual = daily_vol * result["baseline_rate"] * avg_txn * 365
        upside = annual - baseline_annual

        st.metric(
            "Projected Annual Recovery (scaled)",
            money(annual),
            delta=f"{upside:+,.0f} vs baseline policy",
        )

        if upside > 0:
            st.success(
                f"🚀 This policy tuning unlocks about **₹{upside/1e7:.2f} Cr/year** extra upside at selected scale."
            )
        elif upside < 0:
            st.warning("This tuning reduces expected recovery. Useful to show judges bad policies can hurt revenue.")
        else:
            st.info("No material change vs baseline policy.")

    by_error = result["by_error"]
    if not by_error.empty:
        chart_df = by_error.melt(
            id_vars=["error_code"],
            value_vars=["baseline_expected", "whatif_expected"],
            var_name="Scenario",
            value_name="Expected Amount",
        )
        chart_df["Scenario"] = chart_df["Scenario"].map(
            {
                "baseline_expected": "Baseline Policy",
                "whatif_expected": "What-If Policy",
            }
        )

        fig = px.bar(
            chart_df,
            x="error_code",
            y="Expected Amount",
            color="Scenario",
            barmode="group",
            title="Expected Recovery by Failure Reason (Baseline vs What-If)",
            color_discrete_sequence=["#64748b", "#ffb84d"],
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#151922",
            height=360,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Model notes: USER_CANCELLED / FRAUD_SUSPECTED / INVALID_CARD stay blocked (compliance-first). "
            "This is expected-value simulation on the current batch, not cherry-picked outcomes."
        )


def render_chats_tab() -> None:
    chats = st.session_state.get("chats", [])
    if not chats:
        st.info("No Hinglish nudges have been sent yet. Run the recovery agent to generate conversations.")
        return

    for chat in chats:
        with st.expander(f"{chat['txn_id']} - {chat['customer']} at {chat['merchant']}", expanded=False):
            st.markdown(
                f"<div class='chat-bubble-bot'><b>RevRescue Bot</b><br>{chat['bot_message']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='chat-bubble-user'><b>Customer</b><br>{chat['customer_reply']}</div>",
                unsafe_allow_html=True,
            )


def render_audit_tab() -> None:
    lines = get_audit_trail(limit=500)
    if not lines:
        st.info("Audit trail is empty.")
        return
    st.text_area("Most recent actions first", value="\n".join(lines), height=520)


def render_exception_tab(df: pd.DataFrame) -> None:
    if df.empty or "recovery_status" not in df:
        st.info("No exception data available yet.")
        return

    exceptions = df[df["recovery_status"] == "UNRECOVERABLE"].copy()
    if exceptions.empty:
        st.success("No unrecoverable transactions in this run.")
        return

    st.warning(
        f"{len(exceptions)} transactions could not be recovered. These are shown honestly for judging transparency."
    )
    for _, row in exceptions.iterrows():
        reason = row.get("recovery_reason", "No automated recovery path available.")
        st.markdown(
            f"""
            <div class='exception-row'>
                <b>{row['txn_id']}</b> | {row['customer_name']} | {row['merchant']} | ₹{float(row['amount']):,.2f}<br>
                <b>Error:</b> {row['error_code']} &nbsp; <b>Action:</b> {row.get('recovery_action', 'N/A')}<br>
                <b>Reason:</b> {reason}
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    inject_css()
    ensure_session_state()

    with st.sidebar:
        st.title("Controls")
        batch_size = st.slider("Batch size", min_value=10, max_value=100, value=75, step=5)

        if st.button("Generate New Batch", use_container_width=True):
            clear_audit_trail()
            st.session_state.transactions = generate_failed_transactions(batch_size=batch_size)
            st.session_state.chats = []
            st.session_state.agent_has_run = False
            log_action("BATCH", "GENERATE_NEW_BATCH", f"Generated {batch_size} synthetic failed transactions.")
            st.success(f"Generated {batch_size} transactions.")

        if st.button("Run Recovery Agent", use_container_width=True):
            if st.session_state.transactions.empty:
                st.warning("Generate a batch before running the recovery agent.")
            else:
                clear_audit_trail()
                log_action(
                    "BATCH",
                    "RUN_STARTED",
                    f"Processing full batch of {len(st.session_state.transactions)} transactions.",
                )
                updated_df, chats = process_full_batch(st.session_state.transactions)
                log_action(
                    "BATCH",
                    "RUN_COMPLETED",
                    f"Processed all {len(updated_df)} transactions with no cherry-picking.",
                    "SUCCESS",
                )
                st.session_state.transactions = updated_df
                st.session_state.chats = chats
                st.session_state.agent_has_run = True
                st.success("Recovery agent processed the full batch.")

        st.markdown(
            f"""
            <div class='info-box'>
                <b>Compliance Settings</b><br>
                Max retries per transaction: {MAX_RETRIES}<br>
                Contact cooling-off: {COOLING_OFF_HOURS} hours<br>
                Fraud suspected: human escalation only<br>
                User cancelled: no automated recovery
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class='hero'>
            <h1>💰 RevRescue.ai</h1>
            <p>Turning failed payments into recovered revenue</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = st.session_state.transactions
    if df.empty:
        st.info("Generate a synthetic failed-payment batch from the sidebar to start the demo.")
        st.stop()

    render_metrics(df)
    st.divider()
    render_charts(df)
    st.divider()
    render_roi_projection(df)
    st.divider()

    tab_transactions, tab_intel, tab_whatif, tab_chats, tab_audit, tab_exceptions = st.tabs(
        ["Transactions", "Customer Intel", "What-If Lab", "Hinglish Chats", "Audit Trail", "Exception List"]
    )

    with tab_transactions:
        render_transactions_tab(df)
    with tab_intel:
        render_customer_intelligence(df)
    with tab_whatif:
        render_whatif_simulator(df)
    with tab_chats:
        render_chats_tab()
    with tab_audit:
        render_audit_tab()
    with tab_exceptions:
        render_exception_tab(df)

    st.markdown(
        "<div class='footer'>Built for Razorpay Hackathon Track 03: AI Revenue Recovery</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()