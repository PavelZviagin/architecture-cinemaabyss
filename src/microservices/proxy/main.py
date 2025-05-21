import os
import random
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from starlette.status import HTTP_502_BAD_GATEWAY

app = FastAPI(title="CinemaAbyss Proxy Service")

PORT = int(os.getenv("PORT", 8000))
MONOLITH_URL = os.getenv("MONOLITH_URL", "http://monolith:8080")
MOVIES_SERVICE_URL = os.getenv("MOVIES_SERVICE_URL", "http://movies-service:8081")
EVENTS_SERVICE_URL = os.getenv("EVENTS_SERVICE_URL", "http://events-service:8082")
GRADUAL_MIGRATION = os.getenv("GRADUAL_MIGRATION", "true").lower() == "true"
MOVIES_MIGRATION_PERCENT = int(os.getenv("MOVIES_MIGRATION_PERCENT", 50))

client = httpx.AsyncClient()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    print(f"Request: {request.method} {request.url} - Status: {response.status_code}")
    return response

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    target_url = MONOLITH_URL

    if path.startswith("api/movies"):
        if GRADUAL_MIGRATION:
            if random.randint(1, 100) <= MOVIES_MIGRATION_PERCENT:
                target_url = MOVIES_SERVICE_URL
        else:
            target_url = MOVIES_SERVICE_URL
    elif path.startswith("api/events"):
        target_url = EVENTS_SERVICE_URL

    full_url = f"{target_url}/{path}"
    if request.query_params:
        full_url += f"?{request.query_params}"

    try:
        body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None

        response = await client.request(
            method=request.method,
            url=full_url,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            content=body,
            timeout=10.0
        )

        return JSONResponse(
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            status_code=response.status_code,
        )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=HTTP_502_BAD_GATEWAY,
            detail=f"Error connecting to backend service: {str(e)}"
        )

@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)