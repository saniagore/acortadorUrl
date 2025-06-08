import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from pydantic import BaseModel
import secrets
import string
from typing import Optional
from api.config.connection import get_db_connection
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

app = FastAPI()

class URLRequest(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None



def generate_short_url(length: int = 6):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("static/images/favicon.ico")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/shorten")
async def shorten_url(url_request: URLRequest):
    conn = await get_db_connection()
    
    try:
        short_code = url_request.custom_alias or generate_short_url()
        if url_request.custom_alias:
            exists = await conn.fetchval(
                "SELECT 1 FROM urls WHERE short_code = $1", 
                url_request.custom_alias
            )
            if exists:
                raise HTTPException(status_code=400, detail="Custom alias already exists.")
        
        await conn.execute(
            "INSERT INTO urls(original_url, short_code) VALUES ($1, $2)",
            url_request.original_url,
            short_code
        )

        # Cambia esta línea para usar tu dominio de Vercel
        return {"short_url": f"https://acortador-url-beta.vercel.app/{short_code}"}
    
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Short URL already exists.")
    finally:
        await conn.close()

@app.get("/{short_code}")
async def redirect_to_original(short_code: str):
    conn = await get_db_connection()
    try:
        original_url = await conn.fetchval(
            "SELECT original_url FROM urls WHERE short_code = $1", 
            short_code
        )
        
        if not original_url:
            raise HTTPException(status_code=404, detail="URL not found")
        
        await conn.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_code = $1",
            short_code
        )
        
        return RedirectResponse(url=original_url)
    finally:
        await conn.close()


@app.get("/stats/{short_code}")
async def get_stats(short_code:str):
    conn = await get_db_connection()

    try:
        stats = await conn.fetchval(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_code  = $1 RETURNING original_url",
            short_code
        )

        if not stats:
            raise HTTPException(status_code=404, detail="URL not found.")
     
        return dict(stats)
    finally:
        await conn.close()
