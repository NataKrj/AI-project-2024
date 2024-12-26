import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import re
from requests.exceptions import RequestException, SSLError
import time
from urllib.parse import quote
import random


df = pd.read_csv('res_sample_KBO.csv', encoding='latin-1', sep=',')
#df = pd.read_csv('Offshore Leaks-entities.csv', low_memory=False, encoding='utf-8')
company_names = df['Name'][0:20].tolist()  # Processing the first 20 companies


keywords_score_30 = [
    "sanctions", "criminal", "crime", "corruption", "shell company", "offshore",
    "criminal case", "arrested", "fraud", "money laundering",
    "embezzlement", "terrorism financing", "bribery", "tax evasion",
    "illicit funds", "smuggling", "seized assets", "fines",
    "indictment", "prosecuted", "wanted", "scam", "scandal"
]

keywords_score_5 = [
    "court", "accusation", "penalty", "investigation",
    "insolvency", "violation", "debt", "blackmail", "lawsuit",
    "default", "litigation", "settlement", "audit", "suspicious",
    "foreclosure", "dispute", "breach", "illegal transaction",
    "arbitration", "compliance failure", "tax fraud"
]

keywords_score_minus_1 = ["stock"]  

score_no_words = 0


user_agents = [

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (iPad; CPU OS 13_2 like Mac OS X)"
]

def random_headers():
    return {
        "User-Agent": random.choice(user_agents)
    }


exclude_domains = [
    'dictionary.com', 'wiktionary.org', 'merriam-webster.com',
    'facebook.com', 'twitter.com', 'vimeo.com', 'youtube.com',
    'linkedin.com', 'reddit.com', 'quora.com', 'instagram.com',
    'tiktok.com', 'pinterest.com', 'justia.com'
]

def is_valid_url(url):
    return not any(domain in url for domain in exclude_domains)


def bing_search_scrape(company):
    query = f'"{company}"'
    url = f"https://www.bing.com/search?q={quote(query)}"
    time.sleep(random.uniform(3, 7))

    try:
        response = requests.get(url, headers=random_headers(), timeout=10)
        if response.status_code != 200:
            #print(f"Failed to fetch results for {company}: {response.status_code}")
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for g in soup.find_all('li', class_='b_algo'):
            link_tag = g.find('a')
            if not link_tag or 'href' not in link_tag.attrs:
                continue

            link = link_tag['href']
            title = g.find('h2').text if g.find('h2') else ""
            snippet = g.find('p').text if g.find('p') else ""

            if not is_valid_url(link):
                continue

            if title or snippet:
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
        return results
    except Exception as e:
        #print(f"Error scraping Bing for {company}: {e}")
        return []


dictionary_keywords = [
    "definition", "meaning", "dictionary", "thesaurus", "pronunciation"
]


def is_dictionary_page(soup):

    if soup.title and any(word in soup.title.text.lower() for word in dictionary_keywords):
        return True


    meta_description = soup.find("meta", {"name": "description"})
    if meta_description and any(word in meta_description.get("content", "").lower() for word in dictionary_keywords):
        return True


    for tag in soup.find_all(['h1', 'h2']):
        if any(word in tag.text.lower() for word in dictionary_keywords):
            return True

    return False



def extract_text_from_url(url, company_name):
    try:
        response = requests.get(url, headers=random_headers(), timeout=10)
        if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
            soup = BeautifulSoup(response.text, 'html.parser')


            if is_dictionary_page(soup):
                return "Dictionary content skipped"


            for script in soup(["script", "style", "header", "footer", "form", "nav"]):
                script.extract()
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()

           
            relevant_text = ""
            for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
                if company_name.lower() in tag.text.lower():
                    relevant_text += tag.text + " "

            if not relevant_text:
                relevant_text = ' '.join(soup.stripped_strings)

            return re.sub(r'\s+', ' ', relevant_text[:2000])
        else:
            return "Non-text content skipped"
    except (RequestException, SSLError) as e:
        return f"Request failed for {url}: {e}"


def calculate_score_with_reason(text, snippet, company_name):
    text_lower = text.lower()
    snippet_lower = snippet.lower()
    matching_keywords = []
    score = score_no_words


    def keyword_in_same_sentence(keyword):
        sentences = re.split(r'[.!?]', text_lower)
        for sentence in sentences:
            if company_name.lower() in sentence and keyword in sentence:
                return True
        return False


    def keyword_near_company(keyword):
        match = re.search(rf"\b{keyword}\b", text_lower)
        if match:
            window = text_lower[max(0, match.start() - 500):match.end() + 500]
            if company_name.lower() in window:
                return True
        return False

    
    for keyword in keywords_score_30:
        if keyword_in_same_sentence(keyword):
            matching_keywords.append(keyword)
            score += 30
        elif keyword_near_company(keyword) or keyword in snippet_lower:
            matching_keywords.append(keyword)
            score += 30

    
    for keyword in keywords_score_5:
        if keyword_in_same_sentence(keyword):
            matching_keywords.append(keyword)
            score += 5
        elif keyword_near_company(keyword) or keyword in snippet_lower:
            matching_keywords.append(keyword)
            score += 5

    
    for keyword in keywords_score_minus_1:
        if keyword_in_same_sentence(keyword):
            matching_keywords.append(keyword)
            score -= 1
        elif keyword_near_company(keyword) or keyword in snippet_lower:
            matching_keywords.append(keyword)
            score -= 1


   
    if not matching_keywords:
       for term in ["insolvency", "bankruptcy", "liquidation", "dissolved"]:
        if term in text_lower:
            score += 5
            matching_keywords.append(term)

    return score, matching_keywords or ["No relevant keywords"]


def process_company(company_name):
    results = bing_search_scrape(company_name)
    company_data = []

    for result in results:
        url = result['link']
        snippet = result['snippet']
        extracted_text = extract_text_from_url(url, company_name)

        if extracted_text != "Non-text content skipped":
            #extracted_text = clean_text(extracted_text)
            score, reasons = calculate_score_with_reason(extracted_text, snippet, company_name)
            company_data.append({
                'company': company_name,
                'url': url,
                'extracted_text': extracted_text[:300],
                'score': score,
                'matched_keywords': ', '.join(reasons)
            })
    return company_data


data = []
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(process_company, name): name for name in company_names}
    for future in as_completed(futures):
        data.extend(future.result())

df_results = pd.DataFrame(data)
df_results.to_csv('Step_3.2_company_analysis_with_scores.csv', index=False, encoding='utf-8', quoting=csv.QUOTE_ALL, escapechar='\\')

#print("Data saved successfully.")