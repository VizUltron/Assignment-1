from fastapi import FastAPI

app = FastAPI()
@app.get("/")
def home():
    return { 
        "name" : app.title,
        "version" : app.version,
        "endpoints" : ["/tasks"]
    }
    
@app.get("/health")
def health():
    return {"message": "OK"}

