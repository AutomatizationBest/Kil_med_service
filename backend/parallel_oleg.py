import time
from concurrent.futures import ThreadPoolExecutor
from info import ASSIST_FIND_EQUAL_ID, ASSIST_CODE_DEFINE, API_KEY
import pandas as pd
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from oleg_table import (ChatGPTSession, define_device_code,
                        get_data_for_oleg, logger)
from rzerrors import RZErrors
import asyncio


client = OpenAI(api_key=API_KEY)


country_synonyms = {
    "кнр": "китай",
    "china": "китай",
    "россия": "россия",  # Пример для других стран
    # Добавьте другие синонимы по необходимости
}

def normalize_country(country_name):
    """Приведение названия страны к стандартному формату."""
    country_name = country_name.lower().strip()
    return country_synonyms.get(country_name, country_name)



def transfer_data_roszdrav_part(input_data_part):
    options = Options()
    options.add_argument('--headless')  
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    session_equal = ChatGPTSession(assistant_id=ASSIST_FIND_EQUAL_ID, client=client)
    session_code = ChatGPTSession(assistant_id=ASSIST_CODE_DEFINE, client=client)


    # service = Service(ChromeDriverManager().install())
    driver = webdriver.Firefox(options=options)
    
    output_data_part = input_data_part.copy()
    output_data_part['Комментарий'] = ''
    driver.get('https://roszdravnadzor.gov.ru/services/misearch')

    for index, row in output_data_part.iterrows():
        error = RZErrors()
        device_name = row['Наименование предлагаемого оборудования']
        code = define_device_code(session=session_code, device_name=device_name)
        firm = None
        if code.lower() == 'none':
            firm = row['Производитель']
            code = device_name
            logger.warning(f'Код для {device_name} не найден. Осуществляю поиск по производителю: {firm}')
            
        try:
            info = get_data_for_oleg(session_equal, driver, code, device_name, firm=firm)
        except Exception as e:
            logger.warning(f"Error processing {device_name}: {e}")
            info = None
        
        if info is not None:
            output_data_part.at[index, 'Рег.номер'] = info.get('regnum')
            output_data_part.at[index, 'Дата рег.'] = info.get('regdate')
            output_data_part.at[index, 'ОКПД2/ОКП'] = info.get('okpd2okp')
            output_data_part.at[index, 'Наименование оборудования (по разрешительным документам)'] = info.get('device_name')
            output_data_part.at[index, 'Страна производства (по разрешительным документам)'] = info.get('country')
            output_data_part.at[index, 'Производитель (по разрешительным документам)'] = info.get('manufacturer_name')

            model = info.get('model')
            
            if model is None:
                error()
                output_data_part.at[index, 'Комментарий'] += error.model_not_found
            else:
                output_data_part.at[index, 'Наименование оборудования (по разрешительным документам)'] += f'\nвариант исполнения: {model}'
            try:
                if normalize_country(output_data_part.at[index, 'Страна происхождения']) != normalize_country(output_data_part.at[index, 'Страна производства (по разрешительным документам)']):
                    error()
                    output_data_part.at[index, 'Комментарий'] += error.country_mismatch
            except Exception as e:
                logger.exception(e)
                
    driver.quit()
    return output_data_part


def parallel_transfer_data_roszdrav(base : str, output_path : str, num_threads : int = 4) -> pd.DataFrame:
    
    
    # session_equal = ChatGPTSession(assistant_id=ASSIST_FIND_EQUAL_ID, client=client)
    # session_code = ChatGPTSession(assistant_id=ASSIST_CODE_DEFINE, client=client)

    input_data = pd.read_excel(base)
    chunk_size = len(input_data) // num_threads
    if chunk_size == 0:
        chunk_size = 1
    input_data_chunks = [input_data[i:i + chunk_size] for i in range(0, len(input_data), chunk_size)]
    
    output_data_chunks = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for chunk in input_data_chunks:
            futures.append(executor.submit(transfer_data_roszdrav_part, chunk))
        
        for future in futures:
            output_data_chunks.append(future.result())
    
    final_output_data = pd.concat(output_data_chunks, ignore_index=True)
    # final_output_data.to_excel(output_path, merge_cells=True, float_format="%.2f", index_label='№ п/п')
    
    return final_output_data


def merge_chunks(chunk_outputs, final_output):
    combined_data = pd.DataFrame()

    for chunk_output in chunk_outputs:
        data = pd.read_excel(chunk_output)
        combined_data = pd.concat([combined_data, data], ignore_index=True)
    
    combined_data.to_excel(final_output, merge_cells=True, float_format="%.2f", index_label='№ п/п')


def make_oleg_file(kp_path : str):
    import os
    init_time = time.time()
    # kp_path = 'devices_oleg_short.xlsx'
    upload_folder = os.path.abspath('uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Абсолютный путь к файлу
    output_path = os.path.join(upload_folder, 'output_devices_oleg_test_all_3.xlsx')

    output_data = parallel_transfer_data_roszdrav(kp_path, output_path, num_threads=10)
    output_data.to_excel(output_path, merge_cells=True, float_format="%.2f", index_label='№ п/п')
    logger.info(f"Data transferred and saved to {output_path}")

    logger.info(f"ОБЩЕЕ ВРЕМЯ: {time.time() - init_time} сек")
    # print(output_path)
    return output_path
