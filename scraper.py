import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

# Lista de User-Agents para rotar y evitar bloqueos
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
]

def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def scrape_computrabajo():
    jobs = []
    print("Iniciando scrape de Computrabajo...")
    try:
        url = 'https://www.computrabajo.com.ar/trabajo-de-puerto-madryn'
        r = requests.get(url, headers=get_headers(), timeout=15)
        
        if r.status_code != 200:
            print(f"Error en Computrabajo: Status {r.status_code}")
            return []

        soup = BeautifulSoup(r.content, 'html.parser')
        articles = soup.find_all('article')
        print(f"Encontrados {len(articles)} posibles artículos en Computrabajo")
        
        for article in articles[:15]:
            try:
                title_elem = article.find('a', {'class': lambda x: x and 'js-o-link' in x})
                if not title_elem: continue
                
                title = title_elem.get_text(strip=True)
                link = 'https://www.computrabajo.com.ar' + title_elem['href']
                
                # Buscar empresa
                company_elem = article.find('p', {'class': lambda x: x and 'fs16' in x})
                if not company_elem:
                    company_elem = article.find('a', {'class': 'fc_base'})
                
                company = company_elem.get_text(strip=True) if company_elem else 'Empresa Confidencial'
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': 'Puerto Madryn, Chubut',
                    'description': f"Oportunidad laboral para {title} en {company}. Postulate a través de Computrabajo.",
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'url': link,
                    'source': 'Computrabajo'
                })
            except Exception as e:
                print(f"Error parseando artículo de Computrabajo: {e}")
                continue
        
        time.sleep(random.uniform(2, 4))
    except Exception as e:
        print(f"Error general en Computrabajo: {e}")
    
    return jobs

def scrape_bumeran():
    jobs = []
    print("Iniciando scrape de Bumeran...")
    try:
        # Bumeran suele ser más difícil por el renderizado JS, 
        # pero probamos con el selector de items estático si existe
        url = 'https://www.bumeran.com.ar/empleos-en-puerto-madryn.html'
        r = requests.get(url, headers=get_headers(), timeout=15)
        
        if r.status_code != 200:
            print(f"Error en Bumeran: Status {r.status_code}")
            return []

        soup = BeautifulSoup(r.content, 'html.parser')
        items = soup.find_all('div', {'data-testid': 'job-item'})
        print(f"Encontrados {len(items)} items en Bumeran")
        
        for item in items[:15]:
            try:
                title_elem = item.find('h3')
                link_elem = item.find('a')
                if not title_elem or not link_elem: continue
                
                title = title_elem.get_text(strip=True)
                href = link_elem['href']
                link = 'https://www.bumeran.com.ar' + href if href.startswith('/') else href
                
                company_elem = item.find('p', {'data-testid': 'job-company'}) or item.find('div', {'data-testid': 'job-company'})
                company = company_elem.get_text(strip=True) if company_elem else 'Empresa Confidencial'
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': 'Puerto Madryn, Chubut',
                    'description': f"Buscamos {title}. Unite a nuestro equipo en {company}. Más detalles en Bumeran.",
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'url': link,
                    'source': 'Bumeran'
                })
            except Exception as e:
                print(f"Error parseando item de Bumeran: {e}")
                continue
                
        time.sleep(random.uniform(2, 4))
    except Exception as e:
        print(f"Error general en Bumeran: {e}")
    return jobs

def remove_duplicates(jobs):
    seen = set()
    unique_jobs = []
    for job in jobs:
        # Identificador único basado en título y empresa (simplificado)
        identifier = (job['title'].lower().strip(), job['company'].lower().strip())
        if identifier not in seen:
            seen.add(identifier)
            unique_jobs.append(job)
    return unique_jobs

def main():
    print(f"--- Inicio de Scrape: {datetime.now()} ---")
    all_jobs = []
    
    all_jobs.extend(scrape_computrabajo())
    all_jobs.extend(scrape_bumeran())
    
    initial_count = len(all_jobs)
    all_jobs = remove_duplicates(all_jobs)
    print(f"Duplicados eliminados: {initial_count - len(all_jobs)}")
    
    all_jobs.sort(key=lambda x: x['date'], reverse=True)
    
    output = {
        'last_update': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'total_jobs': len(all_jobs),
        'jobs': all_jobs[:50] # Aumentamos el límite a 50
    }
    
    with open('jobs.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Proceso finalizado. {len(all_jobs)} ofertas guardadas en jobs.json")

if __name__ == '__main__':
    main()

