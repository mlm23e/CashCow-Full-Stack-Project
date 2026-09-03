"""
CashCow Command Center
FastAPI application entrypoint

This file will control the entry point for our API. We build the FastAPI object here and 
register our various different routers to it for routing of our requests

run using
    fastapi dev
in the terminal from the backend directory

Day 7 update -- Added CORS configuration to connect with the front-end

Day 9 - phase B answer key
"""
import os

from fastapi import Request # day 10
from fastapi.responses import JSONResponse # day 10
from sqlalchemy.exc import IntegrityError # day 10

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # day 7 - update

from app.routers import atms, branches, diagnostic_reports, service_calls, users, auth

from app.config import settings # day 11 update
#FRONTEND_ORIGIN = settings.frontend_origin

app = FastAPI(
    title="RoboPulse Fleet Command Center",
    description="Fleet Management API for Apex Robotics autonomous inspection rovers and aerial drones",
    version="0.1.0"
)


# #CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     #The endpoint for our frontent, currently provided by the vite dev server
#     allow_origins=[FRONTEND_ORIGIN],
#     #This allows us to pass an Authorization header (JWT)
#     allow_credentials=True,
#     #This allows all methods and headers through
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# Include our routers in our API
app.include_router(atms.router)
app.include_router(branches.router)
app.include_router(diagnostic_reports.router)
app.include_router(service_calls.router)
app.include_router(users.router)
app.include_router(auth.router)


# Simple health endpoint to validate the application is running correctly
@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

##Endpoint to check the version number (day 10)
@app.get("/version", tags=["health"])
async def version() -> dict[str, str]:
    return {"version": app.version}

# ---------------------------------
# BEGIN EXCEPTION HANDLING (day 10)
# ---------------------------------

# this exception handles when our database constraint (our battery_level NOT being between 0 and 100) 
# is violated. This is a common error that we want to handle gracefully
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exception: IntegrityError):
    return JSONResponse(
        status_code=409, #CONFLICT
        content={"detail": "A database constraint was violated (e.g. a duplicate value)."}
    )

# this is a catch-all exception handler so that any unexpected failure 
# (bugs or unknown conditions) returns a constant JSON response
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exception: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."}
    )