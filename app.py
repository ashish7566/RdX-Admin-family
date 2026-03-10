from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import httpx
import time

app = FastAPI()

RATE_LIMIT_SECONDS = 1
ip_last_request = {}

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    last_time = ip_last_request.get(ip)
    if last_time and (now - last_time) < RATE_LIMIT_SECONDS:
        return JSONResponse(status_code=429, content={"error": "Slow down bro"})

    ip_last_request[ip] = now
    return await call_next(request)


# ===== CLEAN FUNCTION =====
def clean_response(data):
    if isinstance(data, dict):
        data.pop("owner", None)
        data.pop("cached", None)
        data.pop("proxyUsed", None)

        for k, v in data.items():
            data[k] = clean_response(v)

    elif isinstance(data, list):
        data = [clean_response(i) for i in data]

    return data


@app.get("/")
async def lookup(key: str = Query(None), number: str = Query(None)):

    if key != "Project2_0":
        return JSONResponse(status_code=403, content={"error": "Unauthorized: Invalid Key"})

    if not number:
        return JSONResponse(status_code=400, content={"error": "Number parameter is required"})

    target_url = f"https://family-api-mu.vercel.app/?key=IntelXPaid&number={number}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(target_url, timeout=15.0)
            data = response.json()

            # CLEAN RESPONSE
            cleaned = clean_response(data)

            return JSONResponse(content=cleaned)

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": "API error", "details": str(e)}
                )
