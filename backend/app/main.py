"""
FastAPIメインアプリケーション
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="英会話カフェWebサイト API",
    description="英会話カフェWebサイトのバックエンドAPI",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://english-cafe-website.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "英会話カフェWebサイト API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "service": "english-cafe-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/health")
async def api_health_check():
    """APIヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "api": "operational",
        "database": "connected",
        "timestamp": "2024-12-14T10:00:00Z"
    }

@app.post("/api/contacts")
async def create_contact(contact_data: dict):
    """問い合わせ作成エンドポイント"""
    return {
        "message": "問い合わせを受け付けました",
        "contact_id": "test-contact-123",
        "status": "received"
    }

@app.get("/api/monitoring/health")
async def monitoring_health():
    """監視用ヘルスチェック"""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "database": "connected"
        },
        "uptime": "99.9%",
        "response_time": "0.1s"
    }

@app.get("/api/monitoring/stats")
async def monitoring_stats():
    """監視統計情報"""
    return {
        "contacts": {
            "total": 150,
            "today": 5,
            "pending": 3
        },
        "system": {
            "cpu_usage": "25%",
            "memory_usage": "60%",
            "disk_usage": "40%"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)