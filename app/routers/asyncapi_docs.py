from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse


router = APIRouter(tags=["AsyncAPI"])

DOCS_PATH = Path(__file__).resolve().parents[2] / "docs" / "asyncapi.yaml"


@router.get("/asyncapi.yaml", summary="AsyncAPI (YAML)", include_in_schema=False)
async def get_asyncapi_yaml() -> FileResponse:
    return FileResponse(str(DOCS_PATH), media_type="application/yaml")


@router.get("/asyncapi", summary="AsyncAPI UI", include_in_schema=False)
async def asyncapi_ui() -> HTMLResponse:
    html = f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>ITAM Chat AsyncAPI</title>
    <script src="https://unpkg.com/@asyncapi/web-component@1.16.0/lib/asyncapi-web-component.js"></script>
    <style>
      html, body, #root {{ height: 100%; margin: 0; }}
      asyncapi-component {{ height: 100%; }}
    </style>
  </head>
  <body>
    <asyncapi-component schema-url="/asyncapi.yaml"></asyncapi-component>
  </body>
</html>
"""
    return HTMLResponse(content=html)


