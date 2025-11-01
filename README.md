# Smart-Recipes

## Uruchamianie aplikacji

1. **Zainstaluj zależności:**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r backend\requirements.txt
   ```

2. **Ustaw zmienne środowiskowe:**

   - Utwórz plik `.env` w folderze `backend` na podstawie `.env.example`.
   - Wypełnij `OPENAI_API_KEY` swoim kluczem API OpenAI.

3. **Uruchom serwer (z katalogu głównego repozytorium):**

   ```powershell
   uvicorn backend.main:app --reload
   ```

4. **Otwórz przeglądarkę:**
   - Przejdź do [http://127.0.0.1:8000](http://127.0.0.1:8000).
