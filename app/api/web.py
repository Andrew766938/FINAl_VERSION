from fastapi import APIRouter, Request

from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/pages", tags=["Фронтенд"])
templates = Jinja2Templates(directory="app/templates")


@router.get('/reg')
async def get_registration_html(request: Request):
    return templates.TemplateResponse(name='reg.html',
                                      context={'request': request})
@router.get('/login')
async def get_login_html(request: Request):
    return templates.TemplateResponse(name='login.html',
                                      context={'request': request})