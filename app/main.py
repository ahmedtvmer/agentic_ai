from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agent import get_agent_response

app = FastAPI(title="Agentic Customer Support")

class QueryRequest(BaseModel):
    query: str
    user_id: int = 1  

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    try:
        response = get_agent_response(request.query)
        return {"response": response}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}