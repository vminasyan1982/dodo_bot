import telebot

from auth import bot
from utils.api_utils import get_dodo_units, get_daily_sales, get_ingredients_stops, get_kitchen_performance, get_delivery_efficiency, get_cooking_time, get_orders_on_shelf, get_delivery_speed, get_couriers_status, get_delivery_awaiting_time, get_lfl_data
from utils.data_utils import get_user_subscriptions, get_user_data
from utils.menu_utils import _create_menu_buttons
import logging

logging.basicConfig(level=logging.DEBUG)

def check_user_authorized(user_id):
    """Проверяет, авторизован ли пользователь."""
    user_data = get_user_data(user_id)
    if user_data and "token" in user_data:
       return True
    return False


def subs(bot, message, units_data):
    if not check_user_authorized(message.chat.id):
       bot.send_message(message.chat.id, "Вы не авторизованы!")
       return
    if units_data:
        inline_kb = telebot.types.InlineKeyboardMarkup(row_width=2)
        user_subs = get_user_subscriptions(message.from_user.id)
        for unit_name, unit_id in units_data.items():
             is_subscribed = unit_name in user_subs
             text = f"🟢 {unit_name}" if is_subscribed else f"🔴 {unit_name}"
             callback_data = f"sub_unit:{unit_id}"
             inline_kb.add(telebot.types.InlineKeyboardButton(text=text, callback_data=callback_data))

        bot.send_message(message.chat.id, "Выберите пиццерии:", reply_markup=inline_kb)
    else:
        bot.send_message(message.chat.id, "Ошибка получения данных о пиццериях")

def day_revenue(bot, message, user_units):
  if not check_user_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Вы не авторизованы!")
        return
  if not user_units:
    bot.send_message(message.chat.id, "Нет доступа к пиццериям")
    return
  token = get_user_data(message.chat.id)['token']
  stroke = 'Выручка | Неделю назад\n'
  for unit in user_units:
        unit_id = unit['id']
        sales_data = get_daily_sales(token, unit_id)
        if sales_data:
            stroke += f"{unit['name']} | {sales_data['revenue']} | {sales_data['revenueChangePercent']}\n"
  bot.send_message(message.chat.id, stroke, disable_notification=True)

def all_stops(bot, message, user_units):
  if not check_user_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Вы не авторизованы!")
        return
  if not user_units:
    bot.send_message(message.chat.id, "Нет доступа к пиццериям")
    return
  token = get_user_data(message.chat.id)['token']
  for unit in user_units:
      unit_id = unit['id']
      stops_data = get_ingredients_stops(token, unit_id)
      if stops_data and len(stops_data) > 0:
        stroke = f"{unit['name']}\nCтопы ингредиентов:\n\n"
        for el in stops_data:
            stroke += f"{el['productOrIngredientName']} | {el['durationMinutes']} мин\n"
        bot.send_message(message.chat.id, stroke, disable_notification=True)
      else:
        bot.send_message(message.chat.id, f"{unit['name']}\nВ данной пиццерии стопов нет", disable_notification=True)

def kitchen_performance(bot, message, user_units):
   if not check_user_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Вы не авторизованы!")
        return
   if not user_units:
        bot.send_message(message.chat.id, "Нет доступа к пиццериям")
        return
   token = get_user_data(message.chat.id)['token']
   stroke = 'Выручка / Продуктов в час\n'
   for unit in user_units:
      unit_id = unit['id']
      kitchen_data = get_kitchen_performance(token, unit_id)
      if kitchen_data:
         stroke += f"{unit['name']} | {kitchen_data['revenue']} | {kitchen_data['productsPerHour']}\n"
   bot.send_message(message.chat.id, stroke, disable_notification=True)

def delivery_performance(bot, message, user_units):
  if not check_user_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Вы не авторизованы!")
        return
  if not user_units:
    bot.send_message(message.chat.id, "Нет доступа к пиццериям")
    return
  token = get_user_data(message.chat.id)['token']
  stroke = 'Заказов на курьера | за поездку\n'
  for unit in user_units:
    unit_id = unit['id']
    delivery_data = get_delivery_efficiency(token, unit_id)
    if delivery_data:
        stroke += f"{unit['name']} | {delivery_data['ordersPerCourier']} | {delivery_data['ordersPerTrip']}\n"
  bot.send_message(message.chat.id, stroke, disable_notification=True)

def cooking_time(bot, message, user_units):
    if not check_user_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Вы не авторизованы!")
        return
    if not user_units:
        bot.send_message(message.chat.id, "Нет доступа к пиццериям")
        return
    token = get_user_data(message.chat.id)['token']
    stroke = 'Время производства ресторан | доставка\n'
    for unit in user_units:
      unit_id = unit['id']
      cooking_time_data = get_cooking_time(token, unit_id)
      if cooking_time_data:
         stroke += f"{unit['name']} | {cooking_time_data['restaurant']} | {cooking_time_data['delivery']}\n"
    bot.send_message(message.chat.id, stroke, disable_notification=True)

def awaiting_orders(bot, message, user_units):
   if not check_user_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Вы не авторизованы!")
        return
   if not user_units:
        bot.send_message(message.chat.id, "Нет доступа к пиццериям")
        return
   token = get_user_data(message.chat.id)['token']
   stroke = 'Заказов на полке\n'
   for unit in user_units:
      unit_id = unit['id']
      awaiting_orders_data = get_orders_on_shelf(token, unit_id)
      if awaiting_orders_data:
          stroke += f"{unit['name']} | {awaiting_orders_data['value']}\n"
   bot.send_message(message.chat.id, stroke, disable_notification=True)


def delivery_speed(bot, message, user_units):
    if not check_user_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Вы не авторизованы!")
        return
    if not user_units:
        bot.send_message(message.chat.id, "Нет доступа к пиццериям")
        return
    token = get_user_data(message.chat.id)['token']
    stroke = 'Среднее время доставки\n'
    for unit in user_units:
      unit_id = unit['id']
      delivery_speed_data = get_delivery_speed(token, unit_id)
      if delivery_speed_data:
          stroke += f"{unit['name']} | {delivery_speed_data['minutes']}\n"
    bot.send_message(message.chat.id, stroke, disable_notification=True)


def delivery_status(bot, message, user_units):
   if not check_user_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Вы не авторизованы!")
        return
   if not user_units:
        bot.send_message(message.chat.id, "Нет доступа к пиццериям")
        return
   token = get_user_data(message.chat.id)['token']
   stroke = 'Курьеров всего / в очереди\n'
   for unit in user_units:
      unit_id = unit['id']
      courier_status_data = get_couriers_status(token, unit_id)
      if courier_status_data:
         courier_status = courier_status_data['couriers'][0]
         stroke += f"{unit['name']} | {courier_status['total']} / {courier_status['inQueue']}\n"
   bot.send_message(message.chat.id, stroke, disable_notification=True)


def delivery_awaiting_time(bot, message, user_units):
    if not check_user_authorized(message.chat.id):
        bot.send_message(message.chat.id, "Вы не авторизованы!")
        return
    if not user_units:
       bot.send_message(message.chat.id, "Нет доступа к пиццериям")
       return
    token = get_user_data(message.chat.id)['token']
    stroke = 'Время ожидания доставки\n'
    for unit in user_units:
      unit_id = unit['id']
      delivery_await_time = get_delivery_awaiting_time(token, unit_id)
      if delivery_await_time and len(delivery_await_time['averageAwaitingTime']) > 0:
          delivery_await_time_data = delivery_await_time['averageAwaitingTime'][0]
          stroke += f"{unit['name']} | {delivery_await_time_data['minutes']}\n"
    bot.send_message(message.chat.id, stroke, disable_notification=True)

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


@bot.callback_query_handler(func=lambda call: call.data == 'command_revisions')
def callback_revisions(call):
    """Обрабатывает callback для команды получения ревизий."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили ревизии.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_inventory')
def callback_inventory(call):
    """Обрабатывает callback для команды получения инвентаризации."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили инвентаризацию.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_write_off')
def callback_write_off(call):
    """Обрабатывает callback для команды получения списанного сырья."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили списанное сырье.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_rejected_products')
def callback_rejected_products(call):
    """Обрабатывает callback для команды получения забракованных продуктов."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили забракованные продукты.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_staff_food')
def callback_staff_food(call):
    """Обрабатывает callback для команды получения питания персонала."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили питание персонала.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_order_cancellations')
def callback_order_cancellations(call):
    """Обрабатывает callback для команды получения отмены заказов."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили отмены заказов.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_sales')
def callback_sales(call):
    """Обрабатывает callback для команды получения продаж."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    user_units = get_dodo_units(get_user_data(user_id)['token'])['units']
    day_revenue(bot, call.message, user_units)
@bot.callback_query_handler(func=lambda call: call.data == 'command_raw_material_consumption')
def callback_raw_material_consumption(call):
    """Обрабатывает callback для команды получения расхода сырья за период."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили расход сырья за период.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_raw_material_movements')
def callback_raw_material_movements(call):
    """Обрабатывает callback для команды получения перемещения сырья."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили перемещения сырья.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_raw_material_receipts')
def callback_raw_material_receipts(call):
    """Обрабатывает callback для команды получения приходов сырья."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили приходы сырья.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_raw_material_receipts_by_delivery')
def callback_raw_material_receipts_by_delivery(call):
    """Обрабатывает callback для команды получения приходов сырья по поставке."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили приходы сырья по поставке.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_delivery_to_receipt')
def callback_delivery_to_receipt(call):
    """Обрабатывает callback для команды получения перемещения сырья."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили перемещения сырья ->  поставки ->  поступления.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_stock_balances')
def callback_stock_balances(call):
    """Обрабатывает callback для команды получения складских остатков."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили складские остатки.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_customer_experience_rating')
def callback_customer_experience_rating(call):
    """Обрабатывает callback для команды получения рейтинга клиентского опыта."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили рейтинг клиентского опыта.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_standard_rating')
def callback_standard_rating(call):
    """Обрабатывает callback для команды получения рейтинга стандартов."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили рейтинг стандартов.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_customer_experience_rating_history')
def callback_customer_experience_rating_history(call):
    """Обрабатывает callback для команды получения истории рейтинга клиентского опыта."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили историю рейтинга клиентского опыта.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_standard_rating_history')
def callback_standard_rating_history(call):
    """Обрабатывает callback для команды получения истории рейтинга стандартов."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили историю рейтинга стандартов.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_recent_reviews')
def callback_recent_reviews(call):
    """Обрабатывает callback для команды получения недавних отзывов."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили недавние отзывы.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_customer_rating')
def callback_customer_rating(call):
    """Обрабатывает callback для команды получения рейтинга клиентов."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили рейтинг клиентов.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_delivery_statistics')
def callback_delivery_statistics(call):
    """Обрабатывает callback для команды получения статистики доставки."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили статистику доставки.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_late_delivery_certificates')
def callback_late_delivery_certificates(call):
    """Обрабатывает callback для команды получения сертификатов за опоздание."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили сертификаты за опоздание.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_courier_orders')
def callback_courier_orders(call):
    """Обрабатывает callback для команды получения заказов курьеров."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили заказы курьеров.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_delivery_sectors')
def callback_delivery_sectors(call):
    """Обрабатывает callback для команды получения секторов доставки."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили сектора доставки.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_stop_sales_by_sectors')
def callback_stop_sales_by_sectors(call):
    """Обрабатывает callback для команды получения стоп-продаж по секторам."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили стоп-продажи по секторам.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_new_customer_statistics')
def callback_new_customer_statistics(call):
    """Обрабатывает callback для команды получения статистики по новым клиентам."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили статистику по новым клиентам.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_unit_shifts')
def callback_unit_shifts(call):
    """Обрабатывает callback для команды получения смены заведений."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили смены заведений.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_monthly_goals')
def callback_monthly_goals(call):
    """Обрабатывает callback для команды получения целей на месяц."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили цели на месяц.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_employee_list')
def callback_employee_list(call):
    """Обрабатывает callback для команды получения списка сотрудников."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили список сотрудников.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_bonus_one_time')
def callback_bonus_one_time(call):
    """Обрабатывает callback для команды получения премий."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили премию единоразовую.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_bonus_hourly_rate')
def callback_bonus_hourly_rate(call):
    """Обрабатывает callback для команды получения премии к вознаграждению в час."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили премию к вознаграждению в час.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_bonus_position_hourly_rate')
def callback_bonus_position_hourly_rate(call):
    """Обрабатывает callback для команды получения премии по должности к вознаграждению в час."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили премию по должности к вознаграждению в час.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_bonuses')
def callback_bonuses(call):
    """Обрабатывает callback для команды получения премий."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили премии.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_new_rewards')
def callback_new_rewards(call):
    """Обрабатывает callback для команды получения новых вознаграждений."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили вознаграждения (новое).")
@bot.callback_query_handler(func=lambda call: call.data == 'command_search_employees')
def callback_search_employees(call):
    """Обрабатывает callback для команды поиска сотрудников."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили поиск сотрудников.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_search_employee_birthdays')
def callback_search_employee_birthdays(call):
    """Обрабатывает callback для команды поиска дней рождения сотрудников."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили поиск дней рождения сотрудников.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_employee_info')
def callback_employee_info(call):
    """Обрабатывает callback для команды получения информации о сотруднике."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили информацию о сотруднике.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_manager_contacts')
def callback_manager_contacts(call):
    """Обрабатывает callback для команды получения контактов руководителей."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили контакты руководителей.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_employee_shifts_by_unit')
def callback_employee_shifts_by_unit(call):
    """Обрабатывает callback для команды получения смен сотрудников по пиццериям."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили смены сотрудников (по пиццериям).")
@bot.callback_query_handler(func=lambda call: call.data == 'command_employee_shifts_by_id')
def callback_employee_shifts_by_id(call):
    """Обрабатывает callback для команды получения смен сотрудников по идентификаторам."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили смены сотрудников (по идентификаторам).")
@bot.callback_query_handler(func=lambda call: call.data == 'command_close_shift')
def callback_close_shift(call):
    """Обрабатывает callback для команды закрытия смены."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили закрытие смены.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_couriers_on_shift')
def callback_couriers_on_shift(call):
    """Обрабатывает callback для команды получения курьеров на смене."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили курьеров на смене.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_schedules')
def callback_schedules(call):
    """Обрабатывает callback для команды получения расписаний."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили расписания.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_create_schedules')
def callback_create_schedules(call):
    """Обрабатывает callback для команды создания расписаний."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили создание расписаний.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_schedule_forecast')
def callback_schedule_forecast(call):
    """Обрабатывает callback для команды получения прогноза расписаний."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили прогноз расписаний.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_employee_positions')
def callback_employee_positions(call):
    """Обрабатывает callback для команды получения должностей сотрудников."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили должности сотрудников.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_employee_position_history')
def callback_employee_position_history(call):
    """Обрабатывает callback для команды получения истории должностей сотрудников."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили историю должностей сотрудников.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_opportunity_map')
def callback_opportunity_map(call):
    """Обрабатывает callback для команды получения карты возможностей."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили карту возможностей.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_open_vacancies_count')
def callback_open_vacancies_count(call):
    """Обрабатывает callback для команды получения количества открытых вакансий."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили количество открытых вакансий.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_open_vacancies')
def callback_open_vacancies(call):
    """Обрабатывает callback для команды получения открытых вакансий."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили открытые вакансии.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_order_issue_time')
def callback_order_issue_time(call):
    """Обрабатывает callback для команды получения времени выдачи заказа."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили время выдачи заказа.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_tracking_metrics_summary')
def callback_tracking_metrics_summary(call):
    """Обрабатывает callback для команды получения сводных метрик с трекинга."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили сводные метрики с трекинга.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_order_issue_statistics')
def callback_order_issue_statistics(call):
    """Обрабатывает callback для команды получения статистики выдачи заказов."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили статистику выдачи заказов.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_productivity')
def callback_productivity(call):
    """Обрабатывает callback для команды получения производительности."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
       return
    bot.answer_callback_query(call.id)
    user_units = get_dodo_units(get_user_data(user_id)['token'])['units']
    kitchen_performance(bot, call.message, user_units)
@bot.callback_query_handler(func=lambda call: call.data == 'command_stop_sales_by_channels')
def callback_stop_sales_by_channels(call):
    """Обрабатывает callback для команды получения стоп-продаж по каналам продаж."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили стоп-продажи по каналам продаж.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_stop_sales_by_ingredients')
def callback_stop_sales_by_ingredients(call):
    """Обрабатывает callback для команды получения стоп-продаж по ингредиентам."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    user_units = get_dodo_units(get_user_data(user_id)['token'])['units']
    all_stops(bot, call.message, user_units)
@bot.callback_query_handler(func=lambda call: call.data == 'command_stop_sales_by_products')
def callback_stop_sales_by_products(call):
    """Обрабатывает callback для команды получения стоп-продаж по продуктам."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили стоп-продажи по продуктам.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_unit_load_by_orders')
def callback_unit_load_by_orders(call):
    """Обрабатывает callback для команды получения нагрузки на заведение по заказам."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили нагрузку на заведение по заказам.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_unit_load_by_products')
def callback_unit_load_by_products(call):
    """Обрабатывает callback для команды получения нагрузки на заведение по продуктам."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили нагрузку на заведение по продуктам.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_daily_sales_by_unit')
def callback_daily_sales_by_unit(call):
    """Обрабатывает callback для команды получения дневных продаж по заведениям."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    user_units = get_dodo_units(get_user_data(user_id)['token'])['units']
    day_revenue(bot, call.message, user_units)
@bot.callback_query_handler(func=lambda call: call.data == 'command_monthly_sales_by_unit')
def callback_monthly_sales_by_unit(call):
    """Обрабатывает callback для команды получения месячных продаж по заведениям."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
        return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили месячные продажи по заведениям.")
@bot.callback_query_handler(func=lambda call: call.data == 'command_sales_by_unit_for_period')
def callback_sales_by_unit_for_period(call):
    """Обрабатывает callback для команды получения продаж по заведениям за период."""
    user_id = call.message.chat.id
    if not check_user_authorized(user_id):
      return
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Вы запросили продажи по заведениям за период.")

@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def main_menu_callback(call):
    """Обрабатывает callback для кнопки 'Главное меню'."""
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    user_data = get_user_data(user_id)
    markup = _create_menu_buttons(user_data)
    bot.send_message(user_id, "Выберите раздел:", reply_markup=markup)