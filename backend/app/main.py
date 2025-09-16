import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .infrastructure.di.container import get_container
from .api.endpoints.contact import router as contact_router

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時の処理
    logger.info("英会話カフェ API starting up...")
    
    # DIコンテナの初期化
    container = get_container()
    logger.info("Dependency injection container initialized")
    logger.info("Domain layer initialized with event bus")
    
    yield
    
    # 終了時の処理
    logger.info("英会話カフェ API shutting down...")


# アプリケーション初期化
app = FastAPI(
    title="英会話カフェ API",
    description="英会話カフェWebサイトのバックエンドAPI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS設定
from .config import get_settings
settings = get_settings()
origins = settings.cors_origins.split(",") if "," in settings.cors_origins else [settings.cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "message": "英会話カフェ API is running",
        }
    )


# ルートエンドポイント
@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "英会話カフェ API",
            "version": "1.0.0",
            "docs": "/docs",
        }
    )


# APIルーターの登録
app.include_router(contact_router, prefix="/api/v1")





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
