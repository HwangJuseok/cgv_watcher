import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from telegram.ext import Application

import database
from crawler import crawler_task
from api import router as api_router
import telegram_bot
from config import TELEGRAM_TOKEN  # ✅ 하드코딩 대신 config.py(.env)에서 불러옴

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# 텔레그램 앱 객체 생성
tg_app = Application.builder().token(TELEGRAM_TOKEN).build()
crawler_task_ref = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. DB 초기화
    database.init_db()
    print("🚀 시스템 가동 시작!")
    
    # 2. 텔레그램 봇 핸들러 연결 및 백그라운드 폴링 시작
    telegram_bot.register_handlers(tg_app)
    await tg_app.initialize()
    await tg_app.start()
    await tg_app.updater.start_polling()
    print("🤖 텔레그램 봇 폴링 시작.")
    
    # 3. 크롤러 백그라운드 태스크 실행 (텔레그램 객체 전달)
    global crawler_task_ref
    crawler_task_ref = asyncio.create_task(crawler_task(tg_app))
    
    yield # 서버 구동 중...
    
    # 4. 서버 종료 시 깔끔하게 자원 정리
    print("🛑 서버 종료 시퀀스 진행 중...")
    if crawler_task_ref:
        crawler_task_ref.cancel()
    await tg_app.updater.stop()
    await tg_app.stop()
    await tg_app.shutdown()

# FastAPI 인스턴스 생성 및 아이폰 API 라우터 연결
app = FastAPI(lifespan=lifespan, title="CGV Watcher API")
app.include_router(api_router)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # 통합 서버 실행 (포트 8000)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
