from fastapi import FastAPI
# from app.interfaces.api.orders import router as orders_router
# from app.interfaces.api.products import router as products_router
# from app.interfaces.api.users import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mini-Marketplace",
        version="0.1.0",
        description="Учебный проект"
    )
    
    # app.include_router(users_router, prefix="/users", tags=["users"])
    # app.include_router(products_router, prefix="/products", tags=["products"])
    # app.include_router(orders_router, prefix="/orders", tags=["orders"])
    
    return app

app = create_app()