import telebot
import os
from dotenv import load_dotenv
from utils.api_utils import get_dodo_units, get_lfl_data
from utils.data_utils import  get_user_data, update_user_subscriptions, get_user_subscriptions, \
    update_user_code_verifier, create_user_table # Removed set_user_started and create_new_user
import hashlib
import secrets
import base64
import logging
import schedule
import time
from threading import Thread
import json
from utils.menu_utils import _create_menu_buttons
import urllib.parse


load_dotenv()

logging.basicConfig(level=logging.DEBUG)

bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    print("Ошибка: токен бота не найден в файле .env")
    exit()
client_id = os.getenv("CLIENT_ID")
if not client_id:
    print("Ошибка: client_id не найден в файле .env")
    exit()
redirect_uri = os.getenv("REDIRECT_URI")
if not redirect_uri:
    print("Ошибка: redirect_uri не найден в файле .env")
    exit()


bot = telebot.TeleBot(bot_token)
create_user_table()


def generate_pkce_codes():
    code_verifier = secrets.token_urlsafe(100)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode('utf-8').replace('=', '')
    return code_verifier, code_challenge

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
       user_id = message.chat.id
       user_data = get_user_data(user_id)
       if user_data and "token" in user_data:
           show_main_menu_inline(message)
       else:
            code_verifier, code_challenge = generate_pkce_codes()
            update_user_code_verifier(user_id, code_verifier)
            auth_url = (f"https://auth.dodois.io/connect/authorize"
                   f"?client_id={os.getenv('CLIENT_ID')}"
                   f"&redirect_uri={urllib.parse.quote(os.getenv('REDIRECT_URI'))}"
                   f"&response_type=code"
                   f"&scope=openid profile offline_access"
                   f"&code_challenge={code_challenge}"
                   f"&code_challenge_method=S256"
                    f"&state={message.chat.id}"
                   )
            bot.send_message(message.chat.id, f"Пожалуйста, авторизуйтесь, перейдя по ссылке: {auth_url}")
    except Exception as e:
          bot.send_message(message.chat.id, f"Произошла ошибка: {e} ")

def show_main_menu_inline(message):
    user_data = get_user_data(message.chat.id)
    markup = _create_menu_buttons(user_data)
    bot.send_message(message.chat.id, "Выберите раздел:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Меню')
def menu_command(message):
    show_main_menu_inline(message)


@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def main_menu_callback(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    user_data = get_user_data(user_id)
    markup = _create_menu_buttons(user_data)
    bot.send_message(user_id, "Выберите раздел:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def handle_menu_callback(call):
   bot.answer_callback_query(call.id)
   menu = call.data.split('_')[1]
   show_submenu(call.message, menu)



def show_submenu(message, menu):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    user_data = get_user_data(message.chat.id)
    token = user_data["token"] if user_data and "token" in user_data else None
    if menu == 'account':
       if token:
            markup.add(telebot.types.InlineKeyboardButton("🧾 Ревизии", callback_data='command_revisions'))
            markup.add(telebot.types.InlineKeyboardButton("🧮 Инвентаризация", callback_data='command_inventory'))
            markup.add(telebot.types.InlineKeyboardButton("🗑️ Списанное сырье", callback_data='command_write_off'))
            markup.add(telebot.types.InlineKeyboardButton("🚫 Забракованные продукты", callback_data='command_rejected_products'))
            markup.add(telebot.types.InlineKeyboardButton("🍽️ Питание персонала", callback_data='command_staff_food'))
            markup.add(telebot.types.InlineKeyboardButton("❌ Отмены заказов", callback_data='command_order_cancellations'))
            lfl_data, lfl_icon = get_lfl_data(token, get_dodo_units(token)["units"])
            markup.add(telebot.types.InlineKeyboardButton(f"📈 Продажи {lfl_icon} ({lfl_data})", callback_data='command_sales'))
            markup.add(telebot.types.InlineKeyboardButton("📉 Расход сырья за период", callback_data='command_raw_material_consumption'))
            markup.add(telebot.types.InlineKeyboardButton("🚚 Перемещения сырья", callback_data='command_raw_material_movements'))
            markup.add(telebot.types.InlineKeyboardButton("📦 Приходы сырья", callback_data='command_raw_material_receipts'))
            markup.add(telebot.types.InlineKeyboardButton("📦 Приходы сырья по поставке", callback_data='command_raw_material_receipts_by_delivery'))
            markup.add(telebot.types.InlineKeyboardButton("🚚 -> 🧾 Поставки -> Поступление", callback_data='command_delivery_to_receipt'))
            markup.add(telebot.types.InlineKeyboardButton("🗄️ Складские остатки", callback_data='command_stock_balances'))
       else:
           markup.add(telebot.types.InlineKeyboardButton("🧾 Ревизии", callback_data='command_revisions'))
           markup.add(telebot.types.InlineKeyboardButton("🧮 Инвентаризация", callback_data='command_inventory'))
           markup.add(telebot.types.InlineKeyboardButton("🗑️ Списанное сырье", callback_data='command_write_off'))
           markup.add(telebot.types.InlineKeyboardButton("🚫 Забракованные продукты", callback_data='command_rejected_products'))
           markup.add(telebot.types.InlineKeyboardButton("🍽️ Питание персонала", callback_data='command_staff_food'))
           markup.add(telebot.types.InlineKeyboardButton("❌ Отмены заказов", callback_data='command_order_cancellations'))
           markup.add(telebot.types.InlineKeyboardButton("📈 Продажи", callback_data='command_sales'))
           markup.add(telebot.types.InlineKeyboardButton("📉 Расход сырья за период", callback_data='command_raw_material_consumption'))
           markup.add(telebot.types.InlineKeyboardButton("🚚 Перемещения сырья", callback_data='command_raw_material_movements'))
           markup.add(telebot.types.InlineKeyboardButton("📦 Приходы сырья", callback_data='command_raw_material_receipts'))
           markup.add(telebot.types.InlineKeyboardButton("📦 Приходы сырья по поставке", callback_data='command_raw_material_receipts_by_delivery'))
           markup.add(telebot.types.InlineKeyboardButton("🚚 -> 🧾 Поставки -> Поступление", callback_data='command_delivery_to_receipt'))
           markup.add(telebot.types.InlineKeyboardButton("🗄️ Складские остатки", callback_data='command_stock_balances'))
    elif menu == 'controlling':
       markup.add(telebot.types.InlineKeyboardButton("🏆 Рейтинг клиентского опыта", callback_data='command_customer_experience_rating'))
       markup.add(telebot.types.InlineKeyboardButton("⭐ Рейтинг стандартов", callback_data='command_standard_rating'))
       markup.add(telebot.types.InlineKeyboardButton("⏳ История рейтинга клиентского опыта", callback_data='command_customer_experience_rating_history'))
       markup.add(telebot.types.InlineKeyboardButton("🕰️ История рейтинга стандартов", callback_data='command_standard_rating_history'))
    elif menu == 'reviews':
        markup.add(telebot.types.InlineKeyboardButton("📜 Недавние отзывы", callback_data='command_recent_reviews'))
        markup.add(telebot.types.InlineKeyboardButton("💯 Рейтинг клиентов", callback_data='command_customer_rating'))
    elif menu == 'delivery':
        markup.add(telebot.types.InlineKeyboardButton("📊 Статистика", callback_data='command_delivery_statistics'))
        markup.add(telebot.types.InlineKeyboardButton("🧾 Сертификаты за опоздание", callback_data='command_late_delivery_certificates'))
        markup.add(telebot.types.InlineKeyboardButton("🛵 Заказы курьеров", callback_data='command_courier_orders'))
        markup.add(telebot.types.InlineKeyboardButton("🗺️ Сектора доставки", callback_data='command_delivery_sectors'))
        markup.add(telebot.types.InlineKeyboardButton("🛑 Стоп-продажи по секторам", callback_data='command_stop_sales_by_sectors'))
    elif menu == 'orders':
        markup.add(telebot.types.InlineKeyboardButton("📊 Статистика по новым клиентам", callback_data='command_new_customer_statistics'))
    elif menu == 'units':
        logging.debug(f"Вызвана функция show_submenu для меню units. Токен {token}")  # Логирование
        if token:
            units_data = get_dodo_units(token)
            logging.debug(f"Результат get_dodo_units: {units_data}")  # Логирование
            if units_data:
                markup.add(telebot.types.InlineKeyboardButton("🔄 Смены заведений", callback_data='command_unit_shifts'))
                markup.add(telebot.types.InlineKeyboardButton("🎯 Цели на месяц", callback_data='command_monthly_goals'))
        else:
            markup.add(telebot.types.InlineKeyboardButton("🔄 Смены заведений", callback_data='command_unit_shifts'))
            markup.add(telebot.types.InlineKeyboardButton("🎯 Цели на месяц", callback_data='command_monthly_goals'))
    elif menu == 'team':
        markup.add(telebot.types.InlineKeyboardButton("👥 Список сотрудников", callback_data='command_employee_list'))
        markup.add(telebot.types.InlineKeyboardButton("🎁 Премия единоразовая", callback_data='command_bonus_one_time'))
        markup.add(telebot.types.InlineKeyboardButton("💰 Премия к вознаграждению в час", callback_data='command_bonus_hourly_rate'))
        markup.add(telebot.types.InlineKeyboardButton("🎖️ Премия по должности к вознаграждению в час", callback_data='command_bonus_position_hourly_rate'))
        markup.add(telebot.types.InlineKeyboardButton("💸 Премии", callback_data='command_bonuses'))
        markup.add(telebot.types.InlineKeyboardButton("💼 Вознаграждения (новое)", callback_data='command_new_rewards'))
        markup.add(telebot.types.InlineKeyboardButton("🔍 Поиск сотрудников", callback_data='command_search_employees'))
        markup.add(telebot.types.InlineKeyboardButton("🎂 Поиск дней рождения сотрудников", callback_data='command_search_employee_birthdays'))
        markup.add(telebot.types.InlineKeyboardButton("ℹ️ Информация о сотруднике", callback_data='command_employee_info'))
        markup.add(telebot.types.InlineKeyboardButton("📞 Контакты руководителей", callback_data='command_manager_contacts'))
        markup.add(telebot.types.InlineKeyboardButton("🔄 Смены сотрудников (по пиццериям)", callback_data='command_employee_shifts_by_unit'))
        markup.add(telebot.types.InlineKeyboardButton("🆔 Смены сотрудников (по идентификаторам)", callback_data='command_employee_shifts_by_id'))
        markup.add(telebot.types.InlineKeyboardButton("🚪 Закрытие смены", callback_data='command_close_shift'))
        markup.add(telebot.types.InlineKeyboardButton("🛵 Курьеры на смене", callback_data='command_couriers_on_shift'))
        markup.add(telebot.types.InlineKeyboardButton("📅 Расписания", callback_data='command_schedules'))
        markup.add(telebot.types.InlineKeyboardButton("📝 Расписания (создание)", callback_data='command_create_schedules'))
        markup.add(telebot.types.InlineKeyboardButton("📊 Расписания: прогнозные метрики", callback_data='command_schedule_forecast'))
        markup.add(telebot.types.InlineKeyboardButton("🗂️ Должности сотрудников", callback_data='command_employee_positions'))
        markup.add(telebot.types.InlineKeyboardButton("📜 История должностей сотрудников", callback_data='command_employee_position_history'))
        markup.add(telebot.types.InlineKeyboardButton("🗺️ Карта возможностей", callback_data='command_opportunity_map'))
        markup.add(telebot.types.InlineKeyboardButton("🔢 Количество открытых вакансий", callback_data='command_open_vacancies_count'))
        markup.add(telebot.types.InlineKeyboardButton("✅ Открытые вакансии", callback_data='command_open_vacancies'))
    elif menu == 'production':
       markup.add(telebot.types.InlineKeyboardButton("⏱️ Время выдачи заказа", callback_data='command_order_issue_time'))
       markup.add(telebot.types.InlineKeyboardButton("📊 Метрики с трекинга (Сводные)", callback_data='command_tracking_metrics_summary'))
       markup.add(telebot.types.InlineKeyboardButton("📈 Статистика выдачи заказов", callback_data='command_order_issue_statistics'))
       markup.add(telebot.types.InlineKeyboardButton("🚀 Производительность", callback_data='command_productivity'))
       markup.add(telebot.types.InlineKeyboardButton("🛑 Стоп-продажи по каналам продаж", callback_data='command_stop_sales_by_channels'))
       markup.add(telebot.types.InlineKeyboardButton("🛑 Стоп-продажи по ингредиентам", callback_data='command_stop_sales_by_ingredients'))
       markup.add(telebot.types.InlineKeyboardButton("🛑 Стоп-продажи по продуктам", callback_data='command_stop_sales_by_products'))
       markup.add(telebot.types.InlineKeyboardButton("⚖️ Нагрузка на заведение по заказам", callback_data='command_unit_load_by_orders'))
       markup.add(telebot.types.InlineKeyboardButton("⚖️ Нагрузка на заведение по продуктам", callback_data='command_unit_load_by_products'))
    elif menu == 'finance':
       if token:
           # lfl_data, lfl_icon = get_lfl_data(token, get_dodo_units(token)["units"])
           markup.add(telebot.types.InlineKeyboardButton(f"📈 Выручка", callback_data='command_sales'))
           markup.add(telebot.types.InlineKeyboardButton("☀️ Дневные продажи по заведениям",
                                                         callback_data='command_daily_sales_by_unit'))
           markup.add(telebot.types.InlineKeyboardButton("🌙 Месячные продажи по заведениям",
                                                         callback_data='command_monthly_sales_by_unit'))
           markup.add(telebot.types.InlineKeyboardButton("🗓️ Продажи по заведениям за период",
                                                         callback_data='command_sales_by_unit_for_period'))
       else:
           markup.add(telebot.types.InlineKeyboardButton("📈 Выручка", callback_data='command_sales'))
           markup.add(telebot.types.InlineKeyboardButton("☀️ Дневные продажи по заведениям",
                                                         callback_data='command_daily_sales_by_unit'))
           markup.add(telebot.types.InlineKeyboardButton("🌙 Месячные продажи по заведениям",
                                                         callback_data='command_monthly_sales_by_unit'))
           markup.add(telebot.types.InlineKeyboardButton("🗓️ Продажи по заведениям за период",
                                                         callback_data='command_sales_by_unit_for_period'))
    markup.add(telebot.types.InlineKeyboardButton("🔙 Главное меню", callback_data='main_menu'))
    bot.send_message(message.chat.id, f"Выберите команду из меню {menu}:", reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data == 'menu_subscriptions')
def handle_subscriptions_menu(call):
    bot.answer_callback_query(call.id)
    show_subscription_menu(bot, call.message, 'main') # added menu parameter


@bot.callback_query_handler(func=lambda call: call.data.startswith('sub_menu:'))
def sub_menu_callback(call):
    menu = call.data.split(":")[1]
    bot.answer_callback_query(call.id)
    show_subscription_menu(bot, call.message, menu)


@bot.callback_query_handler(func=lambda call: call.data.startswith('sub_report:'))
def sub_report_callback(call):
    report_type = call.data.split(":")[1]
    user_subs = get_user_subscriptions(call.from_user.id)
    if report_type in user_subs:
        user_subs.remove(report_type)
    else:
        user_subs.append(report_type)
    update_user_subscriptions(call.from_user.id, user_subs)
    bot.answer_callback_query(call.id, text=f"Подписка на {report_type} обновлена")
    menu = call.message.text.split(" ")[4][:-1]
    show_subscription_menu(bot, call.message, menu)


def send_scheduled_reports(bot):
    while True:
        current_time = time.strftime("%H:%M", time.localtime())
        try:
            with open("data/data.json", "r") as file:
                data = json.load(file)
            for user in data:
                if 'schedule_times' in user and "subs" in user:
                    if current_time in user["schedule_times"]:
                        report_types = user["subs"]
                        for report_type in report_types:
                            if report_type == "daily_sales":
                                bot.send_message(user['tg_user_id'], f"Отчет по выручке от {current_time}")
                            elif report_type == "ingredients_stops":
                                bot.send_message(user['tg_user_id'], f"Отчет по стоп-ингредиентам от {current_time}")
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        schedule.run_pending()
        time.sleep(60)


def run_scheduler(bot):
    scheduler_thread = Thread(target=send_scheduled_reports, args=(bot,))
    scheduler_thread.daemon = True  # позволяет завершить поток
    scheduler_thread.start()

def check_user_authorized(user_id):
    """Проверяет, авторизован ли пользователь."""
    user_data = get_user_data(user_id)
    if user_data and "token" in user_data:
       return True
    return False

def show_subscription_menu(bot, message, menu):
    if not check_user_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Вы не авторизованы!")
        return
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    user_subs = get_user_subscriptions(message.from_user.id)
    if menu == "main":
      markup.add(telebot.types.InlineKeyboardButton("Подписаться на выручку", callback_data='sub_report:daily_sales'))
      markup.add(telebot.types.InlineKeyboardButton("Подписаться на стопы ингредиентов", callback_data='sub_report:ingredients_stops'))
    elif menu == "account":
      markup.add(telebot.types.InlineKeyboardButton("Подписаться на выручку", callback_data='sub_report:daily_sales'))
      markup.add(telebot.types.InlineKeyboardButton("Подписаться на стопы ингредиентов", callback_data='sub_report:ingredients_stops'))
    user_data = get_user_data(message.chat.id)
    bot.send_message(message.chat.id, f"Выберите отчет из меню {menu}:", reply_markup=markup)


run_scheduler(bot)

bot.polling(none_stop=True)