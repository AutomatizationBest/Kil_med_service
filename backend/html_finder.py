from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver




def get_value_by_xpath(driver, xpath):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text.strip()
    except:
        return None
    
    
def get_value_by_param(soup: BeautifulSoup, param_name):
        param = soup.find('td', text=param_name)
        if param:
            # Возвращаем следующий <td> с исходным HTML, включая <br> теги
            return param.find_next_sibling('td').decode_contents().strip()  # Получаем HTML-код без изменений
        return None
    
def find_reg_params(html : str, driver : webdriver):
    test_html = html
    test_html = test_html.replace('<br>', '[space]')

    soup_br = BeautifulSoup(test_html, 'html.parser')

    html_without_br = html.replace('<br>', '')
    soup = BeautifulSoup(html_without_br, 'html.parser')

    # Функция для поиска значения по имени параметра


    # Извлечение параметров
    device_name = get_value_by_param(soup_br, 'Наименование медицинского изделия').split('[space]')[0]

    regnum = get_value_by_param(soup, 'Регистрационный номер медицинского изделия').split('\xa0')[0]
    regdate = get_value_by_param(soup, 'Дата государственной регистрации медицинского изделия')
    manufacturer_name = get_value_by_param(soup, 'Наименование организации - производителя медицинского изделия или организации - изготовителя медицинского изделия')
    okpd2okp = get_value_by_param(soup, 'ОКП/ОКПД2')

    # Извлечение страны из места нахождения
    manufacturer_location = get_value_by_param(soup, 'Место нахождения организации - производителя медицинского изделия или организации - изготовителя медицинского изделия')


    if manufacturer_location:
        # Извлекаем страну (всё, что после запятой)
        country = manufacturer_location.split(',')[1].strip()
    else:
        country = None
        
    return {'regnum' : regnum, 'regdate' : regdate, 'okpd2okp' : okpd2okp, 'device_name' : device_name, 'manufacturer_name' : manufacturer_name,
            'manufacturer_location' : manufacturer_location, 'country' : country}
        
        
def get_info_from_table(html : str, models : bool = False) -> dict:
    soup = BeautifulSoup(html, 'html.parser')

    rows_data : dict = {}
    
    if models:
        
        tbody = soup.find('tbody')
        for i, row in enumerate(tbody.find_all('tr')):
            row_data : dict = {}
            cells = row.find_all('td')
            unique_id : str = cells[0].text.strip()
            rows_data[i] = {}
            rows_data[i]['full_model'] = cells[1].text.strip()

    else:
        
        for row in soup.find_all('tr')[1:]:
            row_data : dict = {}
            id_to_click = row.get('id')
            cells = row.find_all('td')
            unique_id = cells[0].text.strip()
            
            rows_data[unique_id] = {}
            rows_data[unique_id]['id_to_click'] = id_to_click
            rows_data[unique_id]['registration_number'] = cells[1].text.strip()
            rows_data[unique_id]['registration_date'] = cells[2].text.strip()
            rows_data[unique_id]['expiry_date'] = cells[3].text.strip()
            rows_data[unique_id]['product_description'] = cells[4].get('title')
            rows_data[unique_id]['firm'] = cells[8].text.strip()
            rows_data[unique_id]['data_link'] = cells[0].get('data-src')
        
        
    return rows_data


def finder2(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Сбор всех строк таблицы
    rows = soup.find_all('tr')

    # Переменная для хранения результатов
    data = {}

    # Функция для извлечения данных
    def extract_data(rows):
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 2:  # Убедимся, что есть 2 столбца (ключ и значение)
                key = cells[0].get_text(strip=True, separator=" ").replace("\n", " ")
                value = cells[1].get_text(strip=True)
                data[key] = value

    # Применение функции к таблице
    extract_data(rows)

    # Пример доступа к нужным данным
    registration_number = data.get("Регистрационный номер медицинского изделия", "Не найдено")
    organization_name = data.get("Наименование организации – производителя медицинского изделия", "Не найдено")

    print(f"Регистрационный номер: {registration_number}")
    print(f"Наименование организации: {organization_name}")