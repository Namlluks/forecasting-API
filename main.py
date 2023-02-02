from fastapi import Depends, FastAPI, Request, HTTPException, APIRouter
import time
from fastapi.responses import RedirectResponse

from routers import forecasting

desc = """

A FastAPI forcasting app.

**Documentation** : [link](redoc)

"""

app = FastAPI(
    title="App",
    description=desc,
    version="0.0.1",
    contact={
        "name": "Siegfried Delannoy",
        "url": "https://www.linkedin.com/in/siegfried-delannoy/",
        "email": "siegfried.delannoy@gmail.com",
    },
    # dependencies= [Depends(get_query_token)]
)

api_router = APIRouter()

app.include_router(forecasting.router, prefix="/forecasting", tags=["forecasting"])

@app.get("/")
async def root(include_in_schema=False):
    """
    Redirect to Swagger
    """
    return RedirectResponse("/docs")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response