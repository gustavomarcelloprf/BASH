from __future__ import annotations

import math
import re
from datetime import date, timedelta
from typing import Optional

from pydantic import BaseModel

from ..config import settings


class ParseResult(BaseModel):
    hours: Optional[float] = None
    project: Optional[str] = None
    date: str
    activity: Optional[str] = None
    confidence: float
    source: str
    clarification_needed: Optional[str] = None


_STOPWORDS = {
    "trabalhei", "fiz", "realizei", "no", "na", "em",
    "para", "do", "da", "hoje", "ontem", "de", "e", "a", "o",
}

# ── hour patterns (highest priority first) ──────────────────────────────────
_PAT_H_MIN_COMBO = re.compile(
    r"(\d+)\s*h\s*(\d+)\s*(?:min(?:utos?)?)?",
    re.IGNORECASE,
)
_PAT_DECIMAL_H = re.compile(r"(\d+)[,.](\d+)\s*h", re.IGNORECASE)
_PAT_PLAIN_H = re.compile(r"(\d+)\s*h\b", re.IGNORECASE)
_PAT_MIN = re.compile(r"(\d+)\s*min(?:utos?)?", re.IGNORECASE)
_PAT_MEIA = re.compile(r"\bmeia\s+hora\b", re.IGNORECASE)
_PAT_UMA = re.compile(r"\buma\s+hora\b", re.IGNORECASE)

# ── date patterns ────────────────────────────────────────────────────────────
_PAT_DATE_SLASH = re.compile(r"\b(\d{1,2})[/\-](\d{1,2})\b")
_PAT_HOJE = re.compile(r"\bhoje\b", re.IGNORECASE)
_PAT_ONTEM = re.compile(r"\bontem\b", re.IGNORECASE)


def _round_quarter(hours: float) -> float:
    return max(0.25, round(hours * 4) / 4)


def _extract_hours(text: str) -> tuple[Optional[float], str]:
    m = _PAT_H_MIN_COMBO.search(text)
    if m:
        h = int(m.group(1)) + int(m.group(2)) / 60
        return _round_quarter(h), _PAT_H_MIN_COMBO.sub("", text, count=1)

    m = _PAT_DECIMAL_H.search(text)
    if m:
        h = float(f"{m.group(1)}.{m.group(2)}")
        return _round_quarter(h), _PAT_DECIMAL_H.sub("", text, count=1)

    m = _PAT_PLAIN_H.search(text)
    if m:
        return _round_quarter(float(m.group(1))), _PAT_PLAIN_H.sub("", text, count=1)

    m = _PAT_MIN.search(text)
    if m:
        return _round_quarter(int(m.group(1)) / 60), _PAT_MIN.sub("", text, count=1)

    if _PAT_MEIA.search(text):
        return 0.5, _PAT_MEIA.sub("", text)

    if _PAT_UMA.search(text):
        return 1.0, _PAT_UMA.sub("", text)

    return None, text


def _extract_date(text: str) -> tuple[date, str]:
    if _PAT_ONTEM.search(text):
        return date.today() - timedelta(days=1), _PAT_ONTEM.sub("", text)
    if _PAT_HOJE.search(text):
        return date.today(), _PAT_HOJE.sub("", text)
    m = _PAT_DATE_SLASH.search(text)
    if m:
        d, mo = int(m.group(1)), int(m.group(2))
        try:
            return date(date.today().year, mo, d), _PAT_DATE_SLASH.sub("", text, count=1)
        except ValueError:
            pass
    return date.today(), text


def _extract_activity(text: str) -> Optional[str]:
    tokens = [t for t in text.split() if t.lower() not in _STOPWORDS and t.strip(".,!?;:")]
    result = " ".join(tokens).strip(".,!?;: ")
    return result if result else None


def parse_regex(text: str) -> ParseResult:
    hours, remaining = _extract_hours(text)
    entry_date, remaining = _extract_date(remaining)
    activity = _extract_activity(remaining)

    if hours is None:
        confidence = 0.0
    elif activity:
        confidence = 0.85
    else:
        confidence = 0.60

    clarification = None
    if confidence < 0.6:
        clarification = "Não consegui identificar as horas trabalhadas. Tente: '2h na petição do caso Silva'."

    return ParseResult(
        hours=hours,
        project=None,
        date=entry_date.isoformat(),
        activity=activity,
        confidence=confidence,
        source="regex",
        clarification_needed=clarification,
    )


async def parse_llm(text: str, projects: list[str]) -> ParseResult:
    import json

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    today = date.today().isoformat()

    system_prompt = (
        "Você extrai dados de registros de horas de um escritório jurídico.\n"
        f"Projetos existentes: {projects}\n"
        f"Data de hoje: {today}\n\n"
        "Retorne JSON com exatamente estas chaves:\n"
        "{\n"
        '  "hours": float,\n'
        '  "project": string ou null,\n'
        '  "date": "YYYY-MM-DD",\n'
        '  "activity": string ou null,\n'
        '  "confidence": float entre 0 e 1\n'
        "}\n\n"
        "Regras:\n"
        "- hours: mínimo 0.25, arredonde para 0.25 mais próximo\n"
        "- project: nome exato de um dos projetos listados, ou null se nenhum bater\n"
        "- date: padrão hoje se não mencionado\n"
        "- confidence: 0.9 se tudo claro, 0.7 se projeto inferido, 0.5 se ambíguo"
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=150,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
    )

    data = json.loads(response.choices[0].message.content)
    confidence = float(data.get("confidence", 0.7))
    return ParseResult(
        hours=data.get("hours"),
        project=data.get("project"),
        date=data.get("date", today),
        activity=data.get("activity"),
        confidence=confidence,
        source="llm",
        clarification_needed=None if confidence >= 0.6 else "Entrada ambígua — por favor confirme os dados.",
    )


async def parse(text: str, projects: list[str]) -> ParseResult:
    regex_result = parse_regex(text)
    no_key = not settings.OPENAI_API_KEY

    if regex_result.confidence >= 0.85 and no_key:
        return regex_result

    if regex_result.hours is None:
        return regex_result

    if no_key:
        return regex_result

    try:
        return await parse_llm(text, projects)
    except Exception:
        return regex_result
