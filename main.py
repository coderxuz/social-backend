from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api.auth import router as auth
from app.api.image import router as image
from app.api.posts import router as posts
from app.api.followings import router as following
from app.api.comments import router as comments
from app.api.search import router as search
from app.api.chat import router as chat
import uvicorn
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)
@app.get("/")
async def read_root(request: Request):
    template = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        body{{
            color: #fff;
            background-color: #000;
        }}
        a{{
            color: #fff;
        }}
    </style>
</head>
<body>
    <h1>Web server</h1>
    <a href="{a}://{b}/docs" target='_blank'>docs</a>

</body>
</html>
    """.format(a=request.url.scheme,b=request.url.netloc)
    return HTMLResponse(content=template)
app.include_router(auth)
app.include_router(image)
app.include_router(posts)
app.include_router(following)
app.include_router(comments)
app.include_router(search)
app.include_router(chat)
