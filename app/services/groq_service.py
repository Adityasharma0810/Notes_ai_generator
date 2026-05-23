import os
import re

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = "llama-3.3-70b-versatile"


def _strip_think_tags(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _convert_latex(text: str) -> str:
    text = re.sub(r"\\\(|\\\)", "", text)
    text = re.sub(r"\\\[|\\\]", "", text)
    replacements = [
        (r"\\rightarrow", "->"), (r"\\leftarrow", "<-"),
        (r"\\leq", "<="), (r"\\geq", ">="), (r"\\neq", "!="),
        (r"\\approx", "~"), (r"\\times", "x"), (r"\\cdot", "."),
        (r"\\ldots|\\dots", "..."), (r"\\infty", "infinity"),
        (r"\\sqrt\{(.+?)\}", r"sqrt(\1)"),
        (r"\\frac\{(.+?)\}\{(.+?)\}", r"(\1)/(\2)"),
        (r"\\text\{(.+?)\}", r"\1"),
        (r"\\mathbf\{(.+?)\}", r"\1"),
        (r"\\mathrm\{(.+?)\}", r"\1"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = re.sub(r" {2,}", " ", text)
    return text


def generate_notes(text: str, mode: str) -> str:
    if mode == "detailed":
        prompt = (
            "Generate detailed educational notes from the following content. "
            "Include explanations, examples, formulas, and definitions. "
            "Do NOT use LaTeX math notation. Write all math in plain text. "
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
    else:
        prompt = (
            "Generate mixed educational notes. "
            "Include bullet points, explanations for important concepts, and formulas where needed. "
            "Do NOT use LaTeX math notation. Write all math in plain text. "
            "Do NOT include any internal reasoning or thinking.\n\n"
            f"Content:\n{text}"
        )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0.3,
    )
    raw = response.choices[0].message.content
    raw = _strip_think_tags(raw)
    raw = _convert_latex(raw)
    return raw.strip()
