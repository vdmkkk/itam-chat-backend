from pathlib import Path
from urllib.parse import quote
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse


router = APIRouter(tags=["AsyncAPI"])

DOCS_PATH = Path(__file__).resolve().parents[2] / "docs" / "asyncapi.yaml"


@router.get("/asyncapi.yaml", summary="AsyncAPI (YAML)", include_in_schema=False)
async def get_asyncapi_yaml() -> FileResponse:
    return FileResponse(str(DOCS_PATH), media_type="application/yaml")


@router.get("/asyncapi", summary="AsyncAPI UI", include_in_schema=False)
async def asyncapi_ui(request: Request) -> HTMLResponse:
    yaml_url = str(request.url_for("get_asyncapi_yaml"))
    studio = f"https://studio.asyncapi.com/?load={quote(yaml_url, safe='')}"
    html = f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>ITAM Chat AsyncAPI</title>
    <style>
      html, body, #root {{ height: 100%; margin: 0; }}
      iframe {{ width: 100%; height: 100%; border: 0; }}
    </style>
  </head>
  <body>
    <iframe src="{studio}" title="AsyncAPI Studio"></iframe>
  </body>
</html>
"""
    return HTMLResponse(content=html)


