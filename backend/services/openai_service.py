import asyncio
import json
import os
import re
from functools import lru_cache
from typing import List, Dict

from openai import OpenAI


class RecipeServiceError(Exception):
    """Raised when the recipe service cannot produce a response."""


class OpenAIRecipeService:
    def __init__(self, client: OpenAI, model: str) -> None:
        if not model:
            raise RecipeServiceError("Brak skonfigurowanego modelu OpenAI.")
        self._client = client
        self._model = model

    async def generate_recipes(self, ingredients: str, dietary_filter: str) -> List[Dict[str, str]]:
        sanitized_ingredients = ingredients.strip()
        if not sanitized_ingredients:
            raise RecipeServiceError("Podaj przynajmniej jeden składnik.")

        prompt = self._build_prompt(sanitized_ingredients, dietary_filter.strip())

        try:
            raw_text = await asyncio.to_thread(self._query_openai, prompt)
        except Exception as exc:  # noqa: BLE001
            raise RecipeServiceError("Nie udało się wygenerować przepisów. Sprawdź konfigurację OpenAI.") from exc

        return self._parse_response(raw_text)

    def _query_openai(self, prompt: str) -> str:
        response = self._client.responses.create(
            model=self._model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "Jesteś pomocnikiem kulinarnym. Przygotowujesz krótkie przepisy na podstawie"
                        " listy składników i opcjonalnych filtrów dietetycznych."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return (response.output_text or "").strip()

    def _build_prompt(self, ingredients: str, dietary_filter: str) -> str:
        filter_fragment = f"Uwzględnij filtr: {dietary_filter}." if dietary_filter else ""
        return (
            "Przygotuj dokładnie 2 przepisy kulinarne. Każdy powinien zawierać nazwę, krótki opis,"
            " listę dodatkowych składników oraz instrukcje krok po kroku."
            f" Składniki startowe: {ingredients}. {filter_fragment}"
            " Zwróć odpowiedź wyłącznie jako JSON w formacie:"
            " [{\"title\": str, \"body\": str}, ...]."
            " Pole 'body' powinno być sformatowane w Markdownie z nagłówkami i listami, jeśli to pomocne."
            " Nie dodawaj żadnego innego tekstu poza JSON."
        )

    def _parse_response(self, raw_text: str) -> List[Dict[str, str]]:
        if not raw_text:
            raise RecipeServiceError("Model nie zwrócił treści przepisu.")

        text = raw_text.strip()

        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
            text = text.strip()

        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\[\s*{.*?}\s*\]", raw_text, re.DOTALL)
            if not match:
                raise RecipeServiceError("Nie udało się odczytać odpowiedzi modelu (niepoprawny JSON).")
            try:
                payload = json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise RecipeServiceError("Nie udało się odczytać odpowiedzi modelu (niepoprawny JSON).") from exc

        if not isinstance(payload, list):
            raise RecipeServiceError("Odpowiedź modelu ma nieoczekiwany format.")

        normalized: List[Dict[str, str]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            body = str(item.get("body", "")).strip()
            if not title:
                continue
            normalized.append({"title": title, "body": body})

        if len(normalized) < 2:
            raise RecipeServiceError("Model zwrócił zbyt mało przepisów.")

        return normalized[:2]


@lru_cache
def get_openai_service() -> OpenAIRecipeService:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise RecipeServiceError("Brakuje klucza API OpenAI. Uzupełnij plik .env.")

    client = OpenAI(api_key=api_key)
    return OpenAIRecipeService(client=client, model=model)
