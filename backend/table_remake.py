from urllib.parse import quote

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager


def get_code_from_string(text, pattern = r"ОКПД2: \s*(.+)"):
    
    match = re.search(pattern, text)
    if match:
        result = match.group(1)
        return result

    else:
        return text
    
def cut_string(string: str):
    array = string.split()
    array = array[:-1]
    return ' '.join(array)


def get_data_with_selenium(name, driver):
    # driver = webdriver.Chrome()
    driver.refresh()
    driver.implicitly_wait(5) 
    try:
        
        encoded_name = quote(name)
        
    except TypeError:
        return ['', '', '']
    
    url = f"https://nevacert.ru/reestry/med-reestr?query={encoded_name}&order=desc&sort=_score"
    driver.get(url)

    try: 
    # hover_element = WebDriverWait(driver, 10).until(
    #     EC.visibility_of_element_located((By.CLASS_NAME, 'details-float'))
    # )
    

        reg_num_element = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.col.col-reg_num a'))
        )
        regnum = reg_num_element.text  
        # print("Registration Number:", regnum)
        
        reg_date_element = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.col.col-reg_date a'))
        )
        regdate = reg_date_element.text 
        # print("Registration Date:", regdate)
        
        
        code_element = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.col.col-product_code a'))
        )
        okpd2 = code_element.text 
        # print("OKPD2:", okpd2)
        
        return [regnum, regdate, okpd2]
        
    
    

    except Exception as e:
        print("Error during web navigation or element extraction:", e)
    

    # finally:
    #     driver.quit()
        # return [regnum, regdate, okpd2]
        


# get_data_with_selenium('ТУМБА МЕДИЦИНСКАЯ МД ТП-3')

import re
import time

import pandas as pd
from openai import OpenAI

from chatgpt_session import ChatGPTSession, pretty_print
from info import API_KEY, ASSIST_OKPD2


def transfer_data_kp_to_spec(kp_path, spec_path, output_path):
    client = OpenAI(api_key=API_KEY)
    session = ChatGPTSession(assistant_id=ASSIST_OKPD2, client=client)

    kp_data = pd.read_excel(kp_path)
    specification_data = pd.DataFrame()


    specification_data['Наименование оборудования в соответствии с запросом Заказчика'] = kp_data['Наименование оборудования (оснащения)']
    specification_data['Наименование Оборудования (марка, модель, и другое)'] = kp_data['Наименование от ГМК Киль']

    

    specification_data['Количество, в ед.'] = kp_data['Кол-во']
    specification_data['Цена за ед., руб.'] = kp_data['Цена продажи']


    specification_data['Общая стоимость, руб.'] = specification_data['Количество, в ед.'] * specification_data['Цена за ед., руб.']
    specification_data['Ед. измерения'] = 'штука'
    specification_data['Ставка НДС'] = kp_data['Ставка НДС'].astype(str)
    specification_data['regnum'] = ''
    specification_data['regdate'] = ''
    specification_data['okpd2'] = ''
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # service = Service(GeckoDriverManager().install(), log_path='geckodriver.log')
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(options=options, service=service)
    # specification_data.reset_index(inplace=True)
    for index, row in kp_data.iterrows():
        if row['Наименование от ГМК Киль'] is not None and row['Ставка НДС'] != 0.2 and row['Наименование от ГМК Киль'] != 'Наименование от ГМК Киль':
            print(row['Наименование от ГМК Киль'])
            name_to_parse = row['Наименование от ГМК Киль']

            info = None
            while info is None:
                info = get_data_with_selenium(name_to_parse, driver=driver)
                if info is not None:
                    specification_data.at[index, 'regnum'] = info[0]
                    specification_data.at[index, 'regdate'] = info[1]
                    specification_data.at[index, 'okpd2'] = info[2]
                    break
                name_to_parse = cut_string(name_to_parse)

                        
            print(info)
        elif row['Наименование от ГМК Киль'] is not None and row['Ставка НДС'] == 0.2 and row['Наименование от ГМК Киль'] != 'Наименование от ГМК Киль':
            gpt_time = time.time()
            session.ask_assistant(f"Дай код ОКПД2(найди наиболее подходящий) для: '{row['Наименование от ГМК Киль']}'")
            answer = pretty_print(session.get_response(session.thread.id))
            answer = get_code_from_string(text=answer)
            specification_data.at[index, 'okpd2'] = answer
            print(f"Время определения ОКПД2 для {row['Наименование от ГМК Киль']}: {time.time() - gpt_time}")
    specification_data.to_excel(output_path, merge_cells=True, float_format="%.2f", index_label='№ п/п')

    print(f"Data transferred and saved to {output_path}")
    return output_path

# init_time = time.time()
# kp_path = 'kp.xlsx' 
# spec_path = 'spec.xlsx'  
# output_path = 'specification.xlsx' 

# transfer_data(kp_path, spec_path, output_path)
# print(f"ОБЩЕЕ ВРЕМЯ: {time.time() - init_time} сек")
