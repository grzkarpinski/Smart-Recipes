import asyncio
import os
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
            "Podaj 3 krótkie przepisy zawierające listę kroków i wskazówki serwowania. "
            "Zwróć wyniki w formacie: 'Nazwa przepisu' w pierwszej linii, a następnie kolejne linie"
            " z opisem, składnikami dodatkowymi i instrukcjami. "
            f"Składniki startowe: {ingredients}. {filter_fragment}"
        )

    def _parse_response(self, raw_text: str) -> List[Dict[str, str]]:
        if not raw_text:
            raise RecipeServiceError("Model nie zwrócił treści przepisu.")

        blocks = [block.strip() for block in raw_text.split("\n\n") if block.strip()]
        results: List[Dict[str, str]] = []

        for block in blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue
            title = lines[0].lstrip("0123456789. ").strip()
            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
            results.append({"title": title, "body": body})

        if not results:
            raise RecipeServiceError("Nie udało się sparsować odpowiedzi modelu.")

        return results


@lru_cache
def get_openai_service() -> OpenAIRecipeService:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise RecipeServiceError("Brakuje klucza API OpenAI. Uzupełnij plik .env.")

    client = OpenAI(api_key=api_key)
    return OpenAIRecipeService(client=client, model=model)
