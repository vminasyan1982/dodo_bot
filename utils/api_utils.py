import requests
from config import DODO_API_URL, DODO_API_TOKEN
import json
import logging

logging.basicConfig(level=logging.DEBUG)


def get_dodo_units(token):
    url = f"{DODO_API_URL}/api/v1/units"
    headers = {"Authorization": f"Bearer {token}"}
    logging.debug(f"Запрос списка пиццерий: URL: {url}, Заголовки: {headers}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        units = {}
        for unit in data['units']:
            units[unit['name']] = unit['id']
        logging.debug(f"Получены данные о пиццериях: {units}")
        return {"units":units}
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении списка пиццерий: {e}")
        logging.error(f"Response status code: {response.status_code}")
        logging.error(f"Response content: {response.text}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка декодирования JSON: {e}")
        logging.error(f"Response content: {response.text}")
        return None
    except KeyError as e:
        logging.error(f"Ошибка: ключ не найден в ответе: {e}")
        logging.error(f"Response content: {response.text}")
        return None


def get_user_info(token):
    url = f"https://auth.dodois.io/connect/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении данных пользователя: {e}")
        return None

def get_daily_sales(token, unit_id):
     url = f"{DODO_API_URL}/api/v1/reports/sales/daily?unit_ids={unit_id}"
     headers = {"Authorization": f"Bearer {token}"}
     try:
         response = requests.get(url, headers=headers)
         response.raise_for_status()
         data = response.json()
         if data and data['sales']:
            return  {"revenue":data['sales'][0]['revenue'], "revenueChangePercent":data['sales'][0]['revenueChangePercent']}
         return None
     except requests.exceptions.RequestException as e:
         logging.error(f"Ошибка при получении ежедневных продаж: {e}")
         return None


def get_ingredients_stops(token, unit_id):
    url = f"{DODO_API_URL}/api/v1/reports/stop-sales/ingredients?unit_ids={unit_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['stopSales']
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении стоп-продаж ингредиентов: {e}")
        return None

def get_kitchen_performance(token, unit_id):
    url = f"{DODO_API_URL}/api/v1/reports/production-efficiency?unit_ids={unit_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and data['productionEfficiencies']:
          return {"revenue":data['productionEfficiencies'][0]['revenue'], "productsPerHour":data['productionEfficiencies'][0]['productsPerHour']}
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении производительности кухни: {e}")
        return None

def get_delivery_efficiency(token, unit_id):
    url = f"{DODO_API_URL}/api/v1/reports/delivery-efficiency?unit_ids={unit_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and data['deliveryEfficiencies']:
           return {"ordersPerCourier":data['deliveryEfficiencies'][0]['ordersPerCourier'], "ordersPerTrip":data['deliveryEfficiencies'][0]['ordersPerTrip'] }
        return None
    except requests.exceptions.RequestException as e:
         logging.error(f"Ошибка при получении эффективности доставки: {e}")
         return None

def get_cooking_time(token, unit_id):
    url = f"{DODO_API_URL}/api/v1/reports/production/cooking-time?unit_ids={unit_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and data['cookingTime']:
           return {"restaurant":data['cookingTime'][0]['restaurantAverageMinutes'], "delivery":data['cookingTime'][0]['deliveryAverageMinutes']}
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении времени приготовления: {e}")
        return None

def get_orders_on_shelf(token, unit_id):
    url = f"{DODO_API_URL}/api/v1/reports/production/orders-on-shelf?unit_ids={unit_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and data['ordersOnShelf']:
           return {"value":data['ordersOnShelf'][0]['value']}
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении заказов на полке: {e}")
        return None

def get_delivery_speed(token, unit_id):
    url = f"{DODO_API_URL}/api/v1/reports/delivery-speed?unit_ids={unit_id}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and data['deliverySpeed']:
          return {"minutes":data['deliverySpeed'][0]['averageDeliverySpeedMinutes']}
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении скорости доставки: {e}")
        return None

    def get_couriers_status(token, unit_id):
         url = f"{DODO_API_URL}/api/v1/reports/delivery/couriers-status?unit_ids={unit_id}"
         headers = {"Authorization": f"Bearer {token}"}
         try:
             response = requests.get(url, headers=headers)
             response.raise_for_status()
             return response.json()
         except requests.exceptions.RequestException as e:
             logging.error(f"Ошибка при получении статуса курьеров: {e}")
             return None

    def get_delivery_awaiting_time(token, unit_id):
        url = f"{DODO_API_URL}/api/v1/reports/delivery/awaiting-time?unit_ids={unit_id}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
           response = requests.get(url, headers=headers)
           response.raise_for_status()
           return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при получении времени ожидания доставки: {e}")
            return None

    def get_lfl_data(token, unit_ids):
        if not isinstance(unit_ids, dict):
            return None, None
        if not unit_ids:
            return None, None
        ids = list(unit_ids.values())
        url = f"{DODO_API_URL}/api/v1/reports/sales/daily?unit_ids={','.join(map(str, ids))}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data and data['sales'] and len(data['sales']) > 0:
                total_lfl = 0
                for item in data['sales']:
                  if 'revenueChangePercent' in item and item['revenueChangePercent']:
                     total_lfl += item['revenueChangePercent']
                avg_lfl = total_lfl / len(data['sales'])
                lfl_icon = "⬆️" if avg_lfl > 0 else "⬇️"
                return f"{avg_lfl:.1f}%", lfl_icon
            else:
                 return "Нет данных", "❓"
        except requests.exceptions.RequestException as e:
          logging.error(f"Ошибка при получении данных LFL: {e}")
          return None, None