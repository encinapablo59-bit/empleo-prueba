import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def scrape_computrabajo():
    jobs = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url = 'https://www.computrabajo.com.ar/trabajo-de-puerto-madryn'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        for article in soup.find_all('article', limit=10):
            try:
                title_elem = article.find('a', {'class': lambda x: x and 'js-o-link' in x})
                if not title_elem: continue
                
                title = title_elem.get_text(strip=True)
                link = 'https://www.computrabajo.com.ar' + title_elem['href']
                company = article.find('p', {'class': lambda x: x and 'fs16' in x})
                company = company.get_text(strip=True) if company else 'No especificado'
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': 'Puerto Madryn, Chubut',
                    'description': title[:100] + '...',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'url': link,
                    'source': 'Computrabajo'
                })
            except: continue
        time.sleep(2)
    except: pass
    return jobs

def scrape_bumeran():
    jobs = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        url = 'https://www.bumeran.com.ar/empleos-en-puerto-madryn.html'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        for item in soup.find_all('div', {'data-testid': 'job-item'}, limit=10):
            try:
                title_elem = item.find('h3')
                link_elem = item.find('a')
                if not title_elem or not link_elem: continue
                
                title = title_elem.get_text(strip=True)
                link = 'https://www.bumeran.com.ar' + link_elem['href'] if link_elem['href'].startswith('/') else link_elem['href']
                company_elem = item.find('p', {'data-testid': 'job-company'})
                company = company_elem.get_text(strip=True) if company_elem else 'No especificado'
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': 'Puerto Madryn, Chubut',
                    'description': title[:100] + '...',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'url': link,
                    'source': 'Bumeran'
                })
            except: continue
        time.sleep(2)
    except: pass
    return jobs

def remove_duplicates(jobs):
    seen = set()
    unique_jobs = []
    for job in jobs:
        identifier = (job['title'].lower(), job['company'].lower())
        if identifier not in seen:
            seen.add(identifier)
            unique_jobs.append(job)
    return unique_jobs

def main():
    all_jobs = []
    
    print("Scraping Computrabajo...")
    all_jobs.extend(scrape_computrabajo())
    
    print("Scraping Bumeran...")
    all_jobs.extend(scrape_bumeran())
    
    all_jobs = remove_duplicates(all_jobs)
    all_jobs.sort(key=lambda x: x['date'], reverse=True)
    
    output = {
        'last_update': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'total_jobs': len(all_jobs),
        'jobs': all_jobs[:30]
    }
    
    with open('jobs.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {len(all_jobs)} ofertas guardadas en jobs.json")

if __name__ == '__main__':
    main()
