import asyncio
import json
from curl_cffi.requests import AsyncSession
import database

notified_set = set()

async def crawler_task(telegram_app=None):
    print("🔍 [크롤러] 모듈화된 백그라운드 감시 시작!")
    try:
        async with AsyncSession(impersonate="chrome110") as session:
            while True:
                targets = database.get_all_target_conditions()
                api_queries = set((t[0], t[1], t[2]) for t in targets)
                
                for movie_code, theater_code, target_date in api_queries:
                    url = f"https://cgv.co.kr/api/v1/booking/searchSchByMov?coCd=A420&siteNo={theater_code}&scnYmd={target_date}&movNo={movie_code}&rtctlScopCd=08"
                    headers = {"Accept": "application/json", "Referer": "https://m.cgv.co.kr/"}
                    
                    try:
                        response = await session.get(url, headers=headers, timeout=10)
                        if response.status_code == 200:
                            json_data = response.json()
                            if json_data.get("data"):
                                data_str = json.dumps(json_data, ensure_ascii=False).upper()
                                current_combo_targets = [t for t in targets if t[0] == movie_code and t[1] == theater_code and t[2] == target_date]
                                
                                for _, _, _, screen_type in current_combo_targets:
                                    target_key = (movie_code, theater_code, target_date, screen_type)
                                    if target_key in notified_set:
                                        continue
                                    
                                    is_open = False
                                    if screen_type == "IMAX" and ("IMAX" in data_str or "아이맥스" in data_str):
                                        is_open = True
                                    elif screen_type == "SCREENX" and ("SCREENX" in data_str or "스크린X" in data_str):
                                        is_open = True
                                    elif screen_type == "2D" and "2D" in data_str:
                                        is_open = True
                                    
                                    if is_open:
                                        print(f"🚨 오픈 감지! {target_key}")
                                        notified_set.add(target_key)
                                        subscribers = database.get_users_by_target(movie_code, theater_code, target_date, screen_type)
                                        
                                        # 1. 텔레그램 알림 전송
                                        if telegram_app:
                                            for uid in subscribers.get('telegram', []):
                                                msg = f"🚨 예매 오픈 감지!\n조건: {screen_type} 오픈\n바로 예매하기: http://m.cgv.co.kr/Schedule/?tc={theater_code}&t=T&d={target_date}"
                                                try:
                                                    await telegram_app.bot.send_message(chat_id=uid, text=msg)
                                                except:
                                                    pass
                                        
                                        # 2. 아이폰(iOS) 알림 전송 (추후 구현)
                                        for uid in subscribers.get('ios', []):
                                            print(f"📱 iOS 기기({uid}) 푸시 알림 전송 필요!")
                                            
                    except Exception as e:
                        pass
                    await asyncio.sleep(1.5) 
                await asyncio.sleep(10) 
    except asyncio.CancelledError:
        print("🛑 [크롤러] 봇 종료 요청을 받아 감시를 안전하게 종료합니다.")