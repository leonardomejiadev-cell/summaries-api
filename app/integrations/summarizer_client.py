"""
Cliente de generación de resúmenes con fallback chain.

Patrón: Chain of Responsibility — cada proveedor es un eslabón;
si falla, el error se loguea y se intenta el siguiente.

Orden:
  1. Claude Sonnet 4.6  (Anthropic) — principal
  2. Claude Haiku 4.5   (Anthropic) — fallback rápido y barato
  3. GPT-4o-mini        (OpenAI)    — fallback externo de emergencia
"""
import logging
from collections.abc import Awaitable, Callable

import httpx
import anthropic
import openai

logger = logging.getLogger(__name__)

# Límite de caracteres del contenido enviado al LLM para no exceder el contexto
_MAX_CONTENT_CHARS = 8_000
_MAX_TOKENS = 512

_PROMPT_TEMPLATE = (
    "Summarize the following web page content concisely in 2-4 sentences, "
    "capturing the main points.\n\nContent:\n{content}"
)


class SummarizerUnavailableError(Exception):
    """Se lanza cuando todos los proveedores del fallback chain han fallado."""


async def _fetch_url_content(url: str) -> str:
    """Descarga el contenido de la URL y retorna el texto truncado."""

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text[:_MAX_CONTENT_CHARS]


async def _summarize_anthropic(content: str, model: str) -> str:
    """Genera un resumen usando la API de Anthropic. Lee ANTHROPIC_API_KEY del entorno."""

    client = anthropic.AsyncAnthropic()
    response = await client.messages.create(
        model=model,
        max_tokens=_MAX_TOKENS,
        messages=[{"role": "user", "content": _PROMPT_TEMPLATE.format(content=content)}],
    )
    return response.content[0].text


async def _summarize_openai(content: str) -> str:
    """Genera un resumen usando la API de OpenAI. Lee OPENAI_API_KEY del entorno."""

    client = openai.AsyncOpenAI()
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=_MAX_TOKENS,
        messages=[{"role": "user", "content": _PROMPT_TEMPLATE.format(content=content)}],
    )
    return response.choices[0].message.content


async def generate_summary(url: str) -> str:
    """
    Genera un resumen del contenido de la URL usando un fallback chain.

    Intenta cada proveedor en orden; si uno falla, loguea el error y
    pasa al siguiente. Lanza SummarizerUnavailableError si todos fallan.
    """

    content = await _fetch_url_content(url)

    # Cada entrada: (nombre legible, coroutine factory)
    providers: list[tuple[str, Callable[[], Awaitable[str]]]] = [
        (
            "claude-sonnet-4-6 (Anthropic)",
            lambda: _summarize_anthropic(content, "claude-sonnet-4-6"),
        ),
        (
            "claude-haiku-4-5 (Anthropic)",
            lambda: _summarize_anthropic(content, "claude-haiku-4-5"),
        ),
        (
            "gpt-4o-mini (OpenAI)",
            lambda: _summarize_openai(content),
        ),
    ]

    last_error: Exception | None = None
    for name, fn in providers:
        try:
            logger.info("Intentando proveedor: %s", name)
            result = await fn()
            logger.info("Proveedor exitoso: %s", name)
            return result
        except Exception as exc:
            logger.warning("Proveedor %s falló: %s", name, exc)
            last_error = exc

    raise SummarizerUnavailableError(
        f"Todos los proveedores de resumen fallaron. Último error: {last_error}"
    ) from last_error
