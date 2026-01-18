from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import users, pets, categories, subcategories, inventory, cart, orders, pet_profiles, wishlist, admin

app = FastAPI(
    title="PawStore Backend API",
    description="Backend API for PawStore application with FastAPI and MongoDB",
    version="1.0.0"
)

# CORS configuration - Add this BEFORE other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://127.0.0.1:8080", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)


@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()


@app.get("/")
async def root():
    return {
        "message": "Welcome to PawStore Backend API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Register routers
app.include_router(users.router)
app.include_router(pets.router)
app.include_router(categories.router)
app.include_router(subcategories.router)
app.include_router(inventory.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(pet_profiles.router)
app.include_router(wishlist.router)
app.include_router(admin.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
