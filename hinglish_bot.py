"""Hinglish WhatsApp-style recovery message generator."""

from __future__ import annotations

import os
import random
from typing import Any

from dotenv import load_dotenv
from groq import Groq  # CHANGED from openai

load_dotenv()

SYSTEM_PROMPTS = {
    "empathetic_alternative": (
        "You are a warm Indian payment recovery assistant. Write short Hinglish WhatsApp "
        "messages for insufficient funds. Be empathetic, suggest retrying later or EMI, "
        "and never sound pushy."
    ),
    "discount_urgency": (
        "You are a friendly Indian shopping assistant. Write short Hinglish WhatsApp "
        "messages for abandoned checkout. Mention 5% discount code COMEBACK5 with soft urgency."
    ),
    "card_update": (
        "You are a helpful Indian payment assistant. Write short Hinglish WhatsApp "
        "messages for expired card failures. Suggest updating card or using UPI as faster."
    ),
}

FALLBACK_TEMPLATES = {
    "empathetic_alternative": (
        "Hi {first_name}, {merchant} ka Rs {amount:,.2f} payment complete nahi ho paya.\n"
        "No stress 😊 Salary/EMI option ke saath jab ready ho, yahan se retry kar sakte ho: {payment_link}"
    ),
    "discount_urgency": (
        "Hi {first_name}, aapka {merchant} order abhi pending hai.\n"
        "Use code COMEBACK5 for 5% off, valid thodi der ke liye ✨ Pay here: {payment_link}"
    ),
    "card_update": (
        "Hi {first_name}, lagta hai card expire ho gaya for Rs {amount:,.2f} at {merchant}.\n"
        "Card update kar lo ya UPI se faster payment complete karo: {payment_link}"
    ),
}

CUSTOMER_REPLIES = {
    "empathetic_alternative": [
        "Thanks, salary credit hote hi retry kar dunga.",
        "EMI option dikha dena please, phir payment kar leti hoon.",
        "Okay, link save kar liya. Shaam tak try karta hoon.",
    ],
    "discount_urgency": [
        "Nice, COMEBACK5 use karke abhi complete karta hoon.",
        "Cart pending tha, thanks for reminder!",
        "Discount mil raha hai toh order place kar deti hoon.",
    ],
    "card_update": [
        "Haan old card tha, UPI se kar raha hoon.",
        "Thanks, card update karke payment complete karungi.",
        "UPI link helpful hai, abhi pay karta hoon.",
    ],
}


def _first_name(full_name: str) -> str:
    return (full_name or "there").strip().split()[0]


def _fallback_message(txn: dict[str, Any], message_type: str, payment_link: str) -> str:
    template = FALLBACK_TEMPLATES.get(message_type, FALLBACK_TEMPLATES["empathetic_alternative"])
    return template.format(
        first_name=_first_name(str(txn.get("customer_name", ""))),
        merchant=txn.get("merchant", "merchant"),
        amount=float(txn.get("amount", 0.0) or 0.0),
        payment_link=payment_link,
    )


def generate_hinglish_message(txn: dict[str, Any], message_type: str, payment_link: str) -> str:
    """Generate a short Hinglish message, falling back to templates on any API issue."""
    
    # CHANGED to look for GROQ_API_KEY
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _fallback_message(txn, message_type, payment_link)

    prompt = (
        f"Customer first name: {_first_name(str(txn.get('customer_name', '')))}\n"
        f"Merchant: {txn.get('merchant')}\n"
        f"Amount: Rs {float(txn.get('amount', 0.0) or 0.0):,.2f}\n"
        f"Payment link: {payment_link}\n\n"
        "Write one WhatsApp message in 2-4 short lines. Include the first name, amount, "
        "merchant, and payment link. Use light emoji. Do not mention internal error codes."
    )

    try:
        # CHANGED to use Groq client and Llama model
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS.get(message_type, SYSTEM_PROMPTS["empathetic_alternative"])},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=120,
        )
        content = response.choices[0].message.content
        return content.strip() if content else _fallback_message(txn, message_type, payment_link)
    except Exception:
        return _fallback_message(txn, message_type, payment_link)


def simulate_customer_reply(message_type: str) -> str:
    """Return a realistic Hinglish reply for the demo conversation view."""
    return random.choice(CUSTOMER_REPLIES.get(message_type, CUSTOMER_REPLIES["empathetic_alternative"]))