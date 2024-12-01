from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import shop, users, creatures
import json
import logging
import sys
from starlette.middleware.cors import CORSMiddleware

description = "A backend service for an interactive fictional creature café where users can play with creatures, buy treats to feed creatures, adopt them, and more."

app = FastAPI(
    title="Cute Creature Cafe",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={},
)

origins = [""]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(creatures.router)
app.include_router(shop.router)


@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response["message"].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)


@app.get("/")
async def root():
    return {"message": "Welcome to the Cute Creature Cafe."}
