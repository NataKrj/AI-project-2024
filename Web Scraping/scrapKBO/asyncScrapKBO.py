from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import re
from datetime import datetime
from multiprocessing import Pool
import numpy as np
from time import sleep

def process_companies(company_chunk):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 45)

    base_url = "https://kbopub.economie.fgov.be/kbopub/zoeknaamfonetischform.html?lang=en"
    result_chunk = []
    successful_count = 0

    company_types = [
    "VZW", "BVBA", "BV", "NV", "CV", "CVBA", "SPRL", "SCRL", "ASBL",
    "Comm.V", "SComm", "VOF", "SNC", "GIE", "AIE", "SE", "Partnership"
]
    def clean_company_name(company_name):
        return re.sub(r'\b(?:' + '|'.join(company_types) + r')\b', '', company_name, flags=re.IGNORECASE).strip()

    sleep_time = 15
    for company_name in company_chunk:
        try:
            clean_name = clean_company_name(company_name)
            driver.get(base_url)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            sleep(sleep_time)
            search_box = wait.until(EC.presence_of_element_located((By.ID, "searchWord")))
            search_box.clear()
            search_box.send_keys(clean_name)

            checkbox = driver.find_element(By.ID, "filterEnkelActieve")
            if checkbox.is_selected():
                checkbox.click()

            search_button = wait.until(EC.element_to_be_clickable((By.NAME, "actionNPRP")))
            search_button.click()
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                if "no result found for this search term.".lower() in page_text.lower():
                    print(f"No result for {company_name}")
                    result_chunk.append({
                        'OriginalCompanyName': company_name,
                        'CleanedCompanyName': clean_name,
                        'Status': "No result found for this search term",
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    continue
            except NoSuchElementException:
                pass 

            rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#onderneminglistfonetisch tbody tr')))
            status = "not found in KBO data table"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for row in rows:
                name_cell = row.find_element(By.CLASS_NAME, 'benaming').text.strip()
                if name_cell.lower() == clean_name.lower():
                    status_cell = row.find_elements(By.TAG_NAME, 'td')[1].text.strip()
                    status = re.sub(r'\s+', ' ', status_cell).strip()
                    successful_count += 1
                    break

            result_chunk.append({
                'OriginalCompanyName': company_name,
                'CleanedCompanyName': clean_name,
                'Status': status,
                'Timestamp': timestamp
            })

        except (NoSuchElementException, TimeoutException, Exception) as e:
            print(f"Failed to process {company_name}")
            result_chunk.append({
                'OriginalCompanyName': company_name,
                'CleanedCompanyName': clean_name,
                'Status': "error",
                'Timestamp': "N/A"
            })

    driver.quit()
    return result_chunk, successful_count


if __name__ == '__main__':
    start_time = datetime.now()
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    company_list = pd.read_csv('random_sample_2500_5.csv', encoding='latin-1', sep=',')['Name']
    num_workers = 5

    company_chunks = np.array_split(company_list, num_workers)
    with Pool(num_workers) as pool:
        results = pool.map(process_companies, company_chunks)
    all_results = [item[0] for item in results]
    successful_count = sum(item[1] for item in results)
    result_df = pd.DataFrame([item for sublist in all_results for item in sublist])
    result_df.to_csv('company_status_random_sample_2500_5.csv', index=False)

    end_time = datetime.now()
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time taken: {end_time - start_time}")
    print(f"Total successfully found statuses: {successful_count}")