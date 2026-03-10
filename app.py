from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
import httpx
import time

app = FastAPI()

# ===== Simple In-Memory Rate Limit =====
RATE_LIMIT_SECONDS = 1
ip_last_request = {}

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    last_time = ip_last_request.get(ip)
    if last_time and (now - last_time) < RATE_LIMIT_SECONDS:
        return JSONResponse(
            status_code=429,
            content={"error": "Slow down bro"}
        )

    ip_last_request[ip] = now
    return await call_next(request)

# ===== API =====
@app.get("/")
async def lookup(
    key: str = Query(None), 
    number: str = Query(None)
):

    if key != "Project 2_0":
        return JSONResponse(status_code=403, content={"error": "Unauthorized: Invalid Key"})

    if not number:
        return JSONResponse(status_code=400, content={"error": "Number parameter is required"})

    target_url = f"https://family-api-mu.vercel.app/?key=IntelXPaid&number={number}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(target_url, timeout=15.0)

            try:
                data = response.json()

                # ===== FILTER REMOVE OWNER & API BY =====
                filtered_data = {
                    "success": data.get("success"),
                    "result": data.get("result")
                }

                return JSONResponse(content=filtered_data)

            except:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"raw_response": response.text}
                )

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": "API error", "details": str(e)}
    )
