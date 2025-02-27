from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальные переменные для хранения состояния
queue = []  # Очередь курьеров
ADMINS = []  # Сюда добавьте Telegram ID администраторов через запятую

def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    keyboard = []
    
    # Добавляем кнопки в зависимости от роли пользователя
    if user.id in ADMINS:
        keyboard.append([
            InlineKeyboardButton("Вызвать следующего", callback_data='call_next')
        ])
    
    keyboard.append([
        InlineKeyboardButton("Встать в очередь", callback_data='join_queue'),
        InlineKeyboardButton("Обновить список", callback_data='refresh')
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Формируем текст с текущей очередью
    queue_list = "\n".join(
        [f"{i+1}. @{user['username']}" for i, user in enumerate(queue)]
    ) if queue else "Очередь пуста"
    
    message = f"🚚 Очередь курьеров:\n{queue_list}"
    
    if update.message:
        update.message.reply_text(message, reply_markup=reply_markup)
    else:
        update.callback_query.edit_message_text(message, reply_markup=reply_markup)

def button_click(update: Update, context: CallbackContext) -> None:
    """Обработчик нажатий на инлайн-кнопки"""
    query = update.callback_query
    user = query.from_user
    
    if query.data == 'join_queue':
        # Добавление в очередь
        if not any(u['user_id'] == user.id for u in queue):
            queue.append({
                'user_id': user.id,
                'username': user.username
            })
            query.answer("✅ Вы добавлены в очередь!")
        else:
            query.answer("⚠️ Вы уже в очереди!")
            
    elif query.data == 'call_next':
        # Вызов следующего курьера
        if user.id in ADMINS:
            if queue:
                next_user = queue.pop(0)
                context.bot.send_message(
                    chat_id=next_user['user_id'],
                    text="🚀 Вас вызвали! Пожалуйста, подойдите."
                )
                query.answer(f"Вызван @{next_user['username']}")
            else:
                query.answer("❌ Очередь пуста!")
        else:
            query.answer("⛔ У вас нет прав для этого действия!")
    
    # Обновляем сообщение
    start(update, context)

def main() -> None:
    """Запуск бота"""
    updater = Updater("YOUR_BOT_TOKEN")  # Замените на ваш токен
    
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_click))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
