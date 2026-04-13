from fastapi import FastAPI
import sys
import os

app = FastAPI()

@app.get("/test")
def test():
    results = {}
    try:
        import google.genai as genai
        results["google-genai"] = "ok"
    except Exception as e:
        results["google-genai"] = str(e)

    try:
        import psycopg2
        results["psycopg2"] = "ok"
    except Exception as e:
        results["psycopg2"] = str(e)

    try:
        from app import models
        results["app-models"] = "ok"
    except Exception as e:
        results["app-models"] = str(e)
        
    return {"status": "testing", "results": results}
