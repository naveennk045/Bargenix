#  Importing the required libraries

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from negotiation_bot import ElectronicsNegotiationBot
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Bargenix Negotiation API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the bot
negotiation_bot = ElectronicsNegotiationBot()


# Define the request and response models
class NegotiationRequest(BaseModel):
    message: str

class NegotiationResponse(BaseModel):
    response: str
    
#  Endpoint to negotiate
@app.post("/negotiate", response_model=NegotiationResponse)
async def negotiate(request: NegotiationRequest):
    try:
        response = negotiation_bot.negotiate(request.message)
        return NegotiationResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)