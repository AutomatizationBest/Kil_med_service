import pandas as pd
from datetime import datetime
import re
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from html_finder import get_info_from_table, find_reg_params

import time
from openai import OpenAI
import logging

# client = OpenAI(api_key=API_KEY)

ros_zdrav_nadzor_url = 'https://roszdravnadzor.gov.ru/services/misearch'


logger = logging.getLogger(name='GPT_Service')
logging.basicConfig(level=logging.INFO, filename='test_output.log')
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING) 
# ASSIST_FIND_EQUAL_ID = 'asst_qGPbX4gRfgZfi4jxMz3LiUHP'

def cut_string(string: str):
    array = string.split()
    array = array[:-1]
    return ' '.join(array)

def pretty_print(messages):
    
    logger.info("# Messages")
    user_assist_mess = {}
    for m in messages:
        # print(f"{m.role}: {m.content[0].text.value}")
        user_assist_mess[m.role] = m.content[0].text.value
        answer = m.content[0].text.value
    for role, item in user_assist_mess.items():
        logger.info(f"{role}: {item}")
    return answer


class ChatGPTSession:
    def __init__(self, client, assistant_id, previous_rounds=[]):
        self.client = client
        self.assistant_id = assistant_id

        self.thread = client.beta.threads.create()
        self.thread_id = self.thread.id
            
        logger.info(f'Initializing: {self.thread_id}')

    def create_msg(self, user_msg):
        message_create = self.client.beta.threads.messages.create(
            role="user",
            thread_id=self.thread_id,
            content=f"{user_msg}"
        )

    def thread_running(self):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id
        )
        return run

    def get_response(self, thread_id):
        return self.client.beta.threads.messages.list(thread_id=thread_id, order="asc")
    
    
    def ask_assistant(self, user_msg):
        self.create_msg(user_msg)
        run = self.thread_running()
       
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run




def choose_target(data : dict,  base_input : str, session_equal : ChatGPTSession, firm : str = None):
    counter = 0
    
    if len(data) == 1:
        
        for i, key in enumerate(data.keys()):
            return key
         
    else:
        
        # session = ChatGPTSession(client=client, assistant_id=ASSIST_FIND_EQUAL_ID)
        
        if len(base_input) > 200:
            base_input = base_input[0:200]
        if firm is not None:
            message = f'Изначальное оборудование: "{base_input}". Производитель: {firm}\nСписок оборудования:\n'
        else:
            message = f'Изначальное оборудование: "{base_input}".\nСписок оборудования:\n'

        for i, key in enumerate(data.keys()):
            if data[key]['expiry_date'] == 'Бессрочно':
                description = data[key]['product_description']
                firm_name = data[key]['firm']
                # print("1DECS", description)
                # print('1LEN', key, len(description))
                if len(description) > 200:
                    description = description[0:200]
                    # print("1DECS2", description)
                # print('1LEN2', key, len(description))
                if firm is not None:
                    message += f'ID: {key}, Производитель: {firm_name}, Описание: "{description.strip()}"\n'
                else:
                    message += f'ID: {key}, Описание: "{description.strip()}"\n'
                counter += 1
            else:
                
                try:
                    date = pd.to_datetime(data[key]['expiry_date'], dayfirst=True)

                    if date > datetime.now():
                        description = data[key]['product_description']
                        
                        # print("DECS", description)
                        # print('LEN', key, len(description))
                        
                        if len(description) > 200:
                            description = description[0:200]
                            # print("DECS2", description)
                            
                        # print('LEN2', key, len(description))
                        
                        if firm is not None:
                            message += f'ID: {key}, Производитель: {firm_name}, Описание: "{description.strip()}"\n'
                        else:
                            message += f'ID: {key}, Описание: "{description.strip()}"\n'                        
                        counter += 1
                        
                    else:
                        continue
                except:
                    continue
        
        if counter == 1:
            return key
        
        logger.info(f"MESSAGE equal {session_equal.thread.id}\n")
        session_equal.ask_assistant(user_msg=message)
        
        answer = pretty_print(session_equal.get_response(session_equal.thread.id))
        return answer


def get_data_for_oleg(session_equal : ChatGPTSession, driver : webdriver, find_id : str, name : str,
                      url=ros_zdrav_nadzor_url, firm : str = None) -> dict:
    answer = {}
    driver.get(url)
    time.sleep(3)
    
    
    # ПОИСК
    def input_and_find(find_id : str = find_id):
        
        input_label = driver.find_element(by=By.ID, value='id_q_mi_label_application')
        input_label.click()
        input_label.clear()
        input_label.send_keys(find_id)
        driver.find_element(by=By.CLASS_NAME, value='search-form-simple-submit').click()
        time.sleep(5)
        table_selenium = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.ID, 'DataTables_Table_1'))
        )

        table_selenium = driver.find_element(by=By.ID, value='DataTables_Table_1')

        return table_selenium.get_attribute('outerHTML'), table_selenium
    
    table_html, table_selenium = input_and_find()
    table = get_info_from_table(table_html)
    name_to_find = name

    # ТАБЛИЦА
    while table is None:

        table_html, table_selenium = input_and_find(name_to_find)
        table = get_info_from_table(table_html)
        if table is not None:
            break
        
        name_to_find = cut_string(name_to_find)
        if len(name_to_find.split(' ')) <= 3:
            logger.warning(f'Длина наименования {name} <= 3 - пропускаю поиск')
            return None
    id_to_click = choose_target(table, name, session_equal, firm)
    # id_to_click = '23887'
    
    
    logger.info(f"ID_TO_CLICK: {id_to_click}")
    
    id_value = table[id_to_click]['id_to_click']

    id_value = driver.find_element(by=By.ID, value=id_value)

    # кликаем на строку в таблице, чтобы появилось новое окно
    try: 
        td_element = id_value.find_element(by=By.TAG_NAME, value='td')
        
        td_element.click()

    except:
        driver.execute_script("arguments[0].scrollIntoView(true);", table_selenium)
        td_element = id_value.find_element(by=By.TAG_NAME, value='td')
        
        td_element.click()
        
    modal = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'fancybox-slide--current'))
    )
    
    
    time.sleep(6)
    table_params_html = driver.execute_script("return document.querySelector('.fancybox-slide--current .table-type-3').outerHTML;")
    
    params = find_reg_params(table_params_html, driver)
    
    # МОДЕЛИ
    
    models_table_xpath_pattern = '//div[contains(@id, "DataTables_Table_") and contains(@id, "_wrapper")]'
    models_table = driver.find_element(by=By.XPATH, value=models_table_xpath_pattern)
    models_table = models_table.get_attribute("outerHTML")
    info = get_info_from_table(models_table, models=True)
    model = define_right_model(info, find_id)
    
    if model is None:
        params['model'] = None
    else:
        params['model'] = info[model]['full_model']
        
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")

    # driver.quit()
    
    return params


def define_device_code(session : ChatGPTSession, device_name : str) -> str:
    
    session.ask_assistant(user_msg=device_name)
    answer = session.get_response(session.thread.id)
    answer = pretty_print(answer)
    return answer
    
    
def define_right_model(data : dict, initial_code : str) -> int:
    
    for key, item in data.items():
        if initial_code.lower() in item['full_model'].lower():
            return key
    
    return None


# data = {0: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: EI1-2'}, 1: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: EI2-2'}, 2: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: GI11-2'}, 3: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: GI12-2'}, 4: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: GI2-2'}, 5: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: GI7-2'}, 6: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: LI15-2'}, 7: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: LI20-2'}, 8: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: LI27-2'}, 9: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: LI5-2'}, 10: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: RI28-2'}, 11: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: RI40-2'}, 12: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: SI4-2'}, 13: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: SI6-2'}, 14: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели: SI6R-2'}, 15: {'full_model': 'Инкубаторы лабораторные Shellab с принадлежностями и без принадлежностей, модели:\xa0GI6-2'}}

# print(define_right_model(data=data, initial_code='G2-2'))
# options = Options()
# # options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')

# service = Service(GeckoDriverManager().install())

# driver = webdriver.Firefox(options=options, service=service)

# code_session = ChatGPTSession(client=client, assistant_id=ASSIST_CODE_DEFINE)

# code = define_device_code(code_session, 'Прибор для упаковки медицинских изделий методом термосварки hm 800 DC')
# print(get_data_for_oleg(driver, code, 'Прибор для упаковки медицинских изделий методом термосварки hm 800 DC'))



