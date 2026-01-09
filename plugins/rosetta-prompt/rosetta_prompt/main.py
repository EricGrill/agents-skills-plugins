"""FastAPI entrypoint for the Rosetta Prompt API."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import OptimizeRequest, OptimizeResponse
from agents import OrchestratorAgent
from config import SUPPORTED_PROVIDERS

app = FastAPI(
    title="The Rosetta Prompt",
    description="Agentic prompt optimization for multiple AI providers",
    version="0.1.0",
)

# CORS middleware for future UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = OrchestratorAgent()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "rosetta-prompt"}


@app.get("/providers")
async def list_providers():
    """List available providers for optimization."""
    return {"providers": SUPPORTED_PROVIDERS}


@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_prompt(request: OptimizeRequest):
    """
    Optimize a prompt for multiple AI providers.
    
    The system analyzes your prompt and adapts it according to each
    provider's specific prompting guidelines and best practices.
    """
    # Validate providers
    invalid_providers = [p for p in request.providers if p not in SUPPORTED_PROVIDERS]
    if invalid_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported providers: {invalid_providers}. Supported: {SUPPORTED_PROVIDERS}"
        )
    
    # Run optimization
    result = await orchestrator.optimize(
        prompt=request.prompt,
        providers=request.providers,
        options=request.options,
    )
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


