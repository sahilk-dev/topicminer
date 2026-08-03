from fastapi import FastAPI

app = FastAPI(title="TopicMiner API")

@app.get("/health")
def health_check():
    return {"status": "OK"}