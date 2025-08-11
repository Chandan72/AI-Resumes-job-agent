from __future__ import annotations

import os
import json
from typing import Dict, Any, Tuple, List

INDUSTRIES: List[str] = [
    "Building Materials Sector",
    "Media & Entertainment",
    "Paper and Pulp Manufacturing",
    "Consumer Electronics",
    "Construction/Infrastructure",
    "Battery Manufacturing",
    "Mining and Minerals",
    "Ship Building",
    "Cement",
    "Pharmaceutical",
    "MSW Management",
    "NBFC",
    "Healthcare",
    "Aluminium",
    "Paint",
    "Telecommunications",
    "Oil and Gas",
    "Renewable Energy",
    "Explosives",
    "Financial Services",
    "Automobiles",
    "Textiles",
    "Travel and Tourism",
    "Auto Ancillaries",
    "Recruitment and Human Resources Services",
    "Power/Transmission & Equipment",
    "Real Estate & Construction Software",
    "Electronic Manufacturing Services",
    "Fast Moving Consumer Goods",
    "Contract Development and Manufacturing Organisation",
    "Fashion & Apparels",
    "Aviation",
]


def _build_system_prompt() -> str:
    return (
        "You are an expert industry analyst. Classify Indian business news articles into exactly one industry from the provided list. "
        "Return strict JSON with keys 'industry' and 'confidence' (0.0-1.0). If uncertain, pick the closest and lower confidence."
    )


def _build_user_prompt(title: str, summary: str | None) -> str:
    industries_list = "\n".join(f"- {i}" for i in INDUSTRIES)
    return (
        f"Classify the following article into ONE of these industries:\n{industries_list}\n\n"
        f"Article Title: {title}\n"
        f"Summary: {summary or 'N/A'}\n\n"
        f"Respond with JSON: {{\"industry\": <string>, \"confidence\": <0..1 float>}}"
    )


def _parse_json_response(text: str) -> Tuple[str | None, float | None]:
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            payload = json.loads(text[start : end + 1])
            industry = payload.get("industry")
            confidence = payload.get("confidence")
            return industry, float(confidence) if confidence is not None else None
    except Exception:
        pass
    return None, None


def _classify_with_openai(title: str, summary: str | None) -> Dict[str, Any]:
    from openai import OpenAI  # lazy import

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": _build_system_prompt()},
        {"role": "user", "content": _build_user_prompt(title, summary)},
    ]
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=120,
    )
    content = resp.choices[0].message.content or ""
    industry, confidence = _parse_json_response(content)
    return {"industry": industry, "confidence": confidence}


def _classify_with_gemini(title: str, summary: str | None) -> Dict[str, Any]:
    import google.generativeai as genai  # lazy import

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GEMINI_API_KEY")
    model_name = os.getenv("GOOGLE_GEMINI_MODEL", "gemini-2.5-pro")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    generation_config = {"temperature": 0.2, "response_mime_type": "application/json"}
    prompt = _build_system_prompt() + "\n\n" + _build_user_prompt(title, summary)
    resp = model.generate_content(prompt, generation_config=generation_config)

    text = ""
    if hasattr(resp, "text") and resp.text:
        text = resp.text
    elif getattr(resp, "candidates", None):
        parts = []
        for c in resp.candidates:
            for p in getattr(c, "content", {}).get("parts", []) or []:
                parts.append(getattr(p, "text", ""))
        text = "\n".join([t for t in parts if t])

    industry, confidence = _parse_json_response(text)
    return {"industry": industry, "confidence": confidence}


def classify_article(title: str, summary: str | None) -> Dict[str, Any]:
    provider = (os.getenv("LLM_PROVIDER") or "openai").lower()

    try:
        if provider == "gemini":
            result = _classify_with_gemini(title, summary)
        else:
            result = _classify_with_openai(title, summary)
        industry = result.get("industry")
        confidence = result.get("confidence")
        if industry not in INDUSTRIES:
            if industry:
                norm = industry.strip().lower()
                for i in INDUSTRIES:
                    if i.lower() == norm:
                        industry = i
                        break
        if industry not in INDUSTRIES:
            industry = "Uncategorized"
        if confidence is None:
            confidence = 0.5
        return {"industry": industry, "confidence": confidence}
    except Exception:
        # Fallback: simple keyword heuristic
        lower = (title + " " + (summary or "")).lower()
        chosen = None
        if any(k in lower for k in ["cement", "concrete"]):
            chosen = "Cement"
        elif any(k in lower for k in ["pharma", "drug", "vaccine"]):
            chosen = "Pharmaceutical"
        elif any(k in lower for k in ["steel", "aluminium", "metal"]):
            chosen = "Aluminium"
        elif any(k in lower for k in ["telecom", "5g", "4g"]):
            chosen = "Telecommunications"
        elif any(k in lower for k in ["auto", "car", "vehicle", "ev "]):
            chosen = "Automobiles"
        elif any(k in lower for k in ["bank", "nbfc", "lending"]):
            chosen = "NBFC"
        else:
            chosen = "Uncategorized"
        return {"industry": chosen, "confidence": 0.3}