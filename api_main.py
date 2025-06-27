import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api_gateway.routes import api_hooks, config_routes
from brain.core.state_manager import StateManager
from brain.core.text_generation import TextGenerator

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application's lifespan.
    Initializes services on startup and cleans them up on shutdown.
    """
    print("Initializing services...")
    state_manager = StateManager()
    text_generator = TextGenerator()
    
    # Load seed memories if the database is empty
    if not state_manager.state["long_term_memory"]:
        state_manager.load_seed_memories()
    
    app.state.state_manager = state_manager
    app.state.text_generator = text_generator
    print("Initialization complete. Server is ready.")
    
    yield
    
    print("Cleaning up services...")
    # Add any cleanup logic here if needed in the future

# Create the FastAPI app with the lifespan manager
app = FastAPI(
    title="Judy API",
    description="API for interacting with Judy's core functions.",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routers
app.include_router(api_hooks.router, prefix="/api", tags=["hooks"])
app.include_router(config_routes.router, prefix="/api", tags=["config"])

@app.get("/", tags=["Root"])
async def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"message": "Welcome to the Judy API. She's listening."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 