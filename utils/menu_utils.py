from telebot import types

def _create_menu_buttons(user_data):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🗂️ Отчеты", callback_data='menu_account'))
    markup.add(types.InlineKeyboardButton("📊 Контроль", callback_data='menu_controlling'))
    markup.add(types.InlineKeyboardButton("🗣️ Отзывы", callback_data='menu_reviews'))
    markup.add(types.InlineKeyboardButton("🚚 Доставка", callback_data='menu_delivery'))
    markup.add(types.InlineKeyboardButton("📦 Заказы", callback_data='menu_orders'))
    markup.add(types.InlineKeyboardButton("🏢 Заведения", callback_data='menu_units'))
    markup.add(types.InlineKeyboardButton("👥 Команда", callback_data='menu_team'))
    markup.add(types.InlineKeyboardButton("⚙️ Производство", callback_data='menu_production'))
    markup.add(types.InlineKeyboardButton("💰 Финансы", callback_data='menu_finance'))
    if user_data and 'token' in user_data:
      markup.add(types.InlineKeyboardButton("🔔 Подписки", callback_data='menu_subscriptions'))
    return markup