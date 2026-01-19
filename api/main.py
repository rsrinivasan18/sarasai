from fastapi import FastAPI

app = FastAPI(
    title="Sarasai",
    description="Where Wisdom Flows - AI-powered investment analysis",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "🦢 Sarasai - Where Wisdom Flows",
        "status": "flowing",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "sarasai-api"}
