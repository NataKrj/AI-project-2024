from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from multiprocessing import Pool
import numpy as np
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def process_companies(company_chunk):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    base_url = "https://kbopub.economie.fgov.be/kbopub/zoeknaamfonetischform.html"
    result_chunk = []
    successful_count = 0
    
    for company_name in company_chunk:
        try:
            driver.get(base_url)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            search_box = wait.until(EC.presence_of_element_located((By.ID, "searchWord")))
            search_box.clear()
            search_box.send_keys(company_name)
            
            search_button = wait.until(EC.element_to_be_clickable((By.NAME, "actionNPRP")))
            search_button.click()
            
            
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            no_result_message = soup.find("h1", string=re.compile(r"No result found for this search term.", re.IGNORECASE))

            if no_result_message:
                print(f"No result for {company_name}")
                result_chunk.append({
                    'CompanyName': company_name,
                    'Status': "not found",
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                continue  
            
            
            rows = soup.select('#onderneminglistfonetisch tbody tr') 
            
            status = "N/A"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for row in rows:
                name_cell = row.find('td', class_='benaming').text.strip()
                if name_cell.lower() == company_name.lower():
                    status_cell = row.find_all('td')[1].text.strip()
                    status = re.sub(r'\s+', ' ', status_cell).strip()
                    successful_count += 1
                    break
            
            result_chunk.append({'CompanyName': company_name, 'Status': status, 'Timestamp': timestamp})

        except (NoSuchElementException, TimeoutException) as e:
            print(f"Element issue on {company_name}: {e}")
            result_chunk.append({'CompanyName': company_name, 'Status': "Element Issue", 'Timestamp': "N/A"})
        except Exception as e:
            print(f"General failure on {company_name}: {e}")
            result_chunk.append({'CompanyName': company_name, 'Status': "General Failure", 'Timestamp': "N/A"})

    driver.quit()
    return result_chunk, successful_count

if __name__ == '__main__':
    start_time = datetime.now()
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    company_list = pd.read_csv('company_listTEST.csv', encoding='latin-1', sep=';')['Name']
    num_workers = 10  
    
    
    company_chunks = np.array_split(company_list, num_workers)

    with Pool(num_workers) as pool:
        
        results = pool.map(process_companies, company_chunks)

    
    all_results = [item[0] for item in results]
    successful_count = sum(item[1] for item in results)  

    result_df = pd.DataFrame([item for sublist in all_results for item in sublist])
    result_df.to_csv('company_status_report_async.csv', index=False)

    end_time = datetime.now()
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total time taken: {end_time - start_time}")
    print(f"Total successfully found statuses: {successful_count}")
