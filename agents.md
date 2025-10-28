# 🤖 AGENTS.md – Smart Recipes

## 🧩 Opis projektu

**Smart Recipes** to prosta aplikacja webowa, która generuje przepisy kulinarne na podstawie składników wpisanych przez użytkownika. Aplikacja wykorzystuje **API OpenAI** do generowania propozycji przepisów oraz **HTMX** do dynamicznego ładowania wyników bez przeładowania strony.

Celem projektu jest stworzenie działającej wersji MVP w kilka godzin – prostej, czytelnej i łatwej do rozbudowy w przyszłości.

---

## ⚙️ Stack technologiczny

| Warstwa | Technologia | Opis |
|----------|--------------|------|
| Backend | FastAPI | Obsługa żądań HTTP, integracja z OpenAI API |
| Frontend | HTMX + Jinja2 | Renderowanie HTML, aktualizacja fragmentów strony bez przeładowania |
| Stylowanie | CSS (vanilla) | Lekki, prosty układ wizualny |
| AI | OpenAI GPT-4o-mini | Generowanie przepisów na podstawie składników |
| Konfiguracja | python-dotenv | Wczytywanie zmiennych środowiskowych z `.env` |
| Zarządzanie zależnościami | requirements.txt | Lista bibliotek Pythona |
| Wersja Pythona | Python 3.13 | Minimalna wymagana wersja środowiska |

---

## 🧱 Architektura aplikacji

### Struktura katalogów

```
smart-recipes/
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── recipes.py
│   ├── services/
│   │   └── openai_service.py
│   ├── templates/
│   │   ├── index.html
│   │   └── results.html
│   ├── static/
│   │   └── style.css
│   ├── .env
│   └── requirements.txt
├── frontend/
│   └── README.md
└── README.md
```

### Opis przepływu danych

1. Użytkownik otwiera `/` → otrzymuje stronę z formularzem.
2. Po wpisaniu składników i wybraniu filtra formularz wysyła żądanie `POST /api/recipes` do backendu.
3. Backend odbiera dane, tworzy prompt i wywołuje OpenAI API.
4. Odpowiedź (tekst z przepisami) renderowana jest w `results.html`.
5. HTMX aktualizuje sekcję `#results` na stronie bez przeładowania.

### Schemat przepływu

```
Użytkownik → / (formularz HTML)
            → POST /api/recipes
               → FastAPI → OpenAI API
                  → HTML fragment → HTMX → Przeglądarka
```

---

## 🔌 Endpointy API

| Metoda | Endpoint | Opis | Dane wejściowe | Dane wyjściowe |
|---------|-----------|------|----------------|----------------|
| GET | `/` | Strona główna aplikacji | – | HTML (formularz + wyniki) |
| POST | `/api/recipes` | Wysyła składniki do backendu, generuje przepisy | JSON lub `form-data`: `ingredients`, `filter` | HTML fragment z przepisami |

---

## 🧠 Integracja z OpenAI

- **Model:** definiowany w `.env` (np. `gpt-4o-mini`)  
- **Klucz API:** przechowywany w `.env`  
- **Prompt:** generowany dynamicznie na podstawie składników i filtra  
- **Biblioteka:** `openai` (oficjalny pakiet Python)

---

## ⚙️ Konfiguracja środowiska (.env)

```
OPENAI_API_KEY=sk-xxxxxx
OPENAI_MODEL=gpt-4o-mini
```

Opcjonalnie `.env.example`:

```
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

---

## 🧰 Uruchomienie aplikacji lokalnie

### 1️⃣ Instalacja zależności

```bash
python3.13 -m venv venv
source venv/bin/activate    # lub .\venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

### 2️⃣ Uruchom serwer

```bash
uvicorn main:app --reload
```

### 3️⃣ Otwórz w przeglądarce

```
http://127.0.0.1:8000
```

---

## 🔍 Przykładowe przepływy użytkownika

1. Użytkownik wpisuje: `makaron, pomidor, ser` i wybiera filtr „wegetariańskie”.
2. Frontend wysyła żądanie `POST /api/recipes`.
3. Backend pyta model OpenAI: „Podaj 3 proste przepisy, które można przygotować z makaronu, pomidora i sera. Tylko przepisy wegetariańskie.”
4. Backend renderuje `results.html` i odsyła fragment do frontendu.

---

## ⚡ Przyszłe rozszerzenia

- Dodanie kolejnych filtrów (np. „bez laktozy”, „szybkie przepisy”).
- Prosty system historii wyszukiwań.
- Możliwość zapisania ulubionych przepisów.
- Dodanie testów jednostkowych i integracyjnych.
- Tryb angielski (wersja międzynarodowa).

---

## 🧭 Zasady dla agentów AI

- Backend jest jedynym miejscem komunikacji z OpenAI API.
- Klucze i modele muszą być zawsze wczytywane z `.env`.
- Kod frontendu nie może zawierać żadnych sekretów.
- Generowany kod powinien być prosty i możliwy do rozwinięcia w ciągu kilku godzin.
- Używaj czystego HTML + HTMX, bez frameworków JS.
- Każda nowa funkcjonalność powinna być opisana w sekcji „Przyszłe rozszerzenia”.

---

© 2025 Smart Recipes — projekt edukacyjny.

