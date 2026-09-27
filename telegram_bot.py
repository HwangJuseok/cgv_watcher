import itertools
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import database 

user_sessions = {}

# 날짜를 9월 한 달 전체 및 넉넉하게 확장
OPTIONS = {
    "movie": {"30001323": "🪐 오디세이", "30001192": "🕷️ 스파이더맨"},
    "theater": {"0013": "용산아이파크몰", "0059": "영등포"},
    "date": {
    "20260921": "9월 21일",
    "20260922": "9월 22일",
    "20260923": "9월 23일",
    "20260924": "9월 24일",
    "20260925": "9월 25일",
    "20260926": "9월 26일",
    "20260927": "9월 27일",
    "20260928": "9월 28일",
    "20260929": "9월 29일",
    "20260930": "9월 30일",
    "20261001": "10월 1일",
    "20261002": "10월 2일",
    "20261003": "10월 3일",
    "20261004": "10월 4일",
    "20261005": "10월 5일"
},
    "screen": {"IMAX": "IMAX", "SCREENX": "ScreenX", "2D": "일반 2D"}
}

def get_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {'movie': set(), 'theater': set(), 'date': set(), 'screen': set()}
    return user_sessions[user_id]

def build_keyboard(step, selected_set, next_step_name):
    keyboard = []
    for key, name in OPTIONS[step].items():
        display_name = f"✅ {name}" if key in selected_set else name
        keyboard.append([InlineKeyboardButton(display_name, callback_data=f"toggle_{step}_{key}")])
        
    if selected_set:
        btn_text = "✅ 완료 및 저장" if next_step_name == "done" else "➡️ 다음 단계로"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"next_{next_step_name}")])
        
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["🎬 새로운 예매 알림 설정"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text("환영합니다! 화면 하단의 버튼을 눌러 설정을 시작하세요.", reply_markup=markup)
    await reset_and_start(update.message.from_user.id, update.message.reply_text)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reset_and_start(update.message.from_user.id, update.message.reply_text)

async def reset_and_start(user_id, send_message_func):
    user_sessions[user_id] = {'movie': set(), 'theater': set(), 'date': set(), 'screen': set()}
    reply_markup = build_keyboard('movie', set(), 'theater')
    await send_message_func("🎬 1. 원하는 영화를 모두 선택해 주세요.", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = get_session(user_id)
    data_parts = query.data.split('_')
    action = data_parts[0]

    if action == "toggle":
        step = data_parts[1]
        item_key = data_parts[2]
        
        if item_key in session[step]:
            session[step].remove(item_key)
        else:
            session[step].add(item_key)
            
        next_step_map = {'movie': 'theater', 'theater': 'date', 'date': 'screen', 'screen': 'done'}
        next_step = next_step_map[step]
        
        messages = {
            'movie': "🎬 1. 원하는 영화를 모두 선택해 주세요.",
            'theater': "🏢 2. 원하는 영화관을 모두 선택해 주세요.",
            'date': "📅 3. 관람 가능한 날짜를 모두 선택해 주세요.",
            'screen': "🎥 4. 원하는 상영관 타입을 모두 선택해 주세요."
        }
        await query.edit_message_text(messages[step], reply_markup=build_keyboard(step, session[step], next_step))

    elif action == "next":
        next_step = data_parts[1]
        
        if next_step == "theater":
            await query.edit_message_text("🏢 2. 원하는 영화관을 모두 선택해 주세요.", reply_markup=build_keyboard('theater', session['theater'], 'date'))
        elif next_step == "date":
            await query.edit_message_text("📅 3. 관람 가능한 날짜를 모두 선택해 주세요.", reply_markup=build_keyboard('date', session['date'], 'screen'))
        elif next_step == "screen":
            await query.edit_message_text("🎥 4. 원하는 상영관 타입을 모두 선택해 주세요.", reply_markup=build_keyboard('screen', session['screen'], 'done'))
        elif next_step == "done":
            combinations = list(itertools.product(
                list(session['movie']), 
                list(session['theater']), 
                list(session['date']), 
                list(session['screen'])
            ))
            
            for m, t, d, s in combinations:
                database.add_subscription(user_id, "telegram", m, t, d, s)
                
            await query.edit_message_text(
                text=f"✅ 총 {len(combinations)}개의 감시 조건이 저장되었습니다!\n예매가 오픈되면 즉시 알려드릴게요."
            )

def register_handlers(app):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(CallbackQueryHandler(button_handler))