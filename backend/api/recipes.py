from pathlib import Path

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.services.openai_service import RecipeServiceError, get_openai_service

router = APIRouter(tags=["recipes"])
FRONTEND_TEMPLATES = Path(__file__).resolve().parents[2] / "frontend" / "templates"
templates = Jinja2Templates(directory=str(FRONTEND_TEMPLATES))


@router.post("/recipes", response_class=HTMLResponse)
async def generate_recipes(
    request: Request,
    ingredients: str = Form(..., min_length=3),
    dietary_filter: str = Form("", alias="filter"),
) -> HTMLResponse:
    try:
        service = get_openai_service()
    except RecipeServiceError as exc:
        context = {"request": request, "recipes": [], "error": str(exc)}
        return templates.TemplateResponse(
            "results.html",
            context,
            status_code=status.HTTP_200_OK,
        )

    try:
        recipes = await service.generate_recipes(ingredients, dietary_filter)
    except RecipeServiceError as exc:
        context = {"request": request, "recipes": [], "error": str(exc)}
        return templates.TemplateResponse(
            "results.html",
            context,
            status_code=status.HTTP_200_OK,
        )

    context = {"request": request, "recipes": recipes, "error": None}
    return templates.TemplateResponse("results.html", context)
