import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"
SARVAM_MODEL = "sarvam-m"


def _strip_think_tags(text: str) -> str:
    """Remove <think>...</think> reasoning blocks from model output."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _convert_latex(text: str) -> str:
    """Convert common LaTeX inline math to plain readable text."""
    # \( ... \) and \[ ... \] inline/block math — just remove delimiters
    text = re.sub(r"\\\(|\\\)", "", text)
    text = re.sub(r"\\\[|\\\]", "", text)

    # Common LaTeX commands to plain text
    replacements = {
        r"\\rightarrow": "->",
        r"\\leftarrow": "<-",
        r"\\leq": "<=",
        r"\\geq": ">=",
        r"\\neq": "!=",
        r"\\approx": "~",
        r"\\times": "x",
        r"\\cdot": ".",
        r"\\ldots": "...",
        r"\\dots": "...",
        r"\\infty": "infinity",
        r"\\alpha": "alpha",
        r"\\beta": "beta",
        r"\\gamma": "gamma",
        r"\\delta": "delta",
        r"\\theta": "theta",
        r"\\lambda": "lambda",
        r"\\mu": "mu",
        r"\\sigma": "sigma",
        r"\\pi": "pi",
        r"\\Omega": "Omega",
        r"\\omega": "omega",
        r"\\log": "log",
        r"\\ln": "ln",
        r"\\sum": "sum",
        r"\\prod": "product",
        r"\\sqrt\{(.+?)\}": r"sqrt(\1)",
        r"\\frac\{(.+?)\}\{(.+?)\}": r"(\1)/(\2)",
        r"\^(\{[^}]+\}|\S)": lambda m: "^" + m.group(1).strip("{}"),
        r"_(\{[^}]+\}|\S)": lambda m: "_" + m.group(1).strip("{}"),
        r"\\text\{(.+?)\}": r"\1",
        r"\\mathbf\{(.+?)\}": r"\1",
        r"\\mathrm\{(.+?)\}": r"\1",
    }

    for pattern, replacement in replacements.items():
        if callable(replacement):
            text = re.sub(pattern, replacement, text)
        else:
            text = re.sub(pattern, replacement, text)

    # Remove any remaining backslash commands
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    # Clean up extra spaces
    text = re.sub(r" {2,}", " ", text)
    return text


def _clean_response(text: str) -> str:
    text = _strip_think_tags(text)
    text = _convert_latex(text)
    return text.strip()


def generate_notes(text: str, mode: str) -> str:

    if mode == "detailed":
        prompt = (
            "Generate detailed educational notes from the following content. "
            "Include explanations, examples, formulas, and definitions. "
            "Do NOT use LaTeX math notation. Write all math in plain text (e.g., O(n!) not \\(O(n!)\\)). "
            "Do NOT include any internal reasoning or thinking.\n\n"
            f"Content:\n{text}"
        )
    elif mode == "important":
        prompt = (
            "Generate concise important-point notes for MCQ revision. "
            "Use bullet points and keywords only. "
            "Do NOT use LaTeX math notation. Write all math in plain text. "
            "Do NOT include any internal reasoning or thinking.\n\n"
            f"Content:\n{text}"
        )
    else:  # mixed
        prompt = (
            "Generate mixed educational notes. "
            "Include bullet points, explanations for important concepts, and formulas where needed. "
            "Do NOT use LaTeX math notation. Write all math in plain text. "
            "Do NOT include any internal reasoning or thinking.\n\n"
            f"Content:\n{text}"
        )

    payload = {
        "model": SARVAM_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2048,
        "temperature": 0.3
    }

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(SARVAM_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()

    data = response.json()
    raw = data["choices"][0]["message"]["content"]
    return _clean_response(raw)
