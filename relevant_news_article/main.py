import requests
from bs4 import BeautifulSoup
import json
import os
import feedparser
from datetime import datetime
from thefuzz import fuzz
from sentence_transformers import SentenceTransformer, util
import torch

# Load a lightweight semantic model
print("Loading AI Model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_clients(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return []
    with open(file_path, 'r') as f:
        return json.load(f)

def scrape_bbc_news():
    url = "https://www.bbc.com/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all(['h2', 'h3'], {'data-testid': 'card-headline'})
        if not headlines: headlines = soup.find_all(['h2', 'h3'])
        results = []
        for h in headlines:
            text = h.get_text(strip=True)
            parent_a = h.find_parent('a')
            if parent_a and parent_a.has_attr('href'):
                link = parent_a['href']
                if link.startswith('/'): link = f"https://www.bbc.com{link}"
                if text and link: results.append({"title": text, "link": link, "source": "BBC News"})
        return results
    except Exception as e:
        print(f"Error scraping BBC: {e}")
        return []

def get_rss_news(feed_url, source_name):
    try:
        feed = feedparser.parse(feed_url)
        results = []
        for entry in feed.entries:
            results.append({
                "title": entry.title,
                "link": entry.link,
                "source": source_name
            })
        return results
    except Exception as e:
        print(f"Error reading {source_name} feed: {e}")
        return []

def collect_all_news():
    all_articles = []
    print("Fetching BBC News...")
    all_articles.extend(scrape_bbc_news())
    print("Fetching TechCrunch RSS...")
    all_articles.extend(get_rss_news("https://techcrunch.com/feed/", "TechCrunch"))
    print("Fetching The Verge RSS...")
    all_articles.extend(get_rss_news("https://www.theverge.com/rss/index.xml", "The Verge"))
    print("Fetching Hacker News RSS...")
    all_articles.extend(get_rss_news("https://news.ycombinator.com/rss", "Hacker News"))
    return all_articles

def get_personalized_news(clients, articles, fuzzy_threshold=85, semantic_threshold=0.38):
    if not articles: return {}
    article_titles = [a['title'] for a in articles]
    article_embeddings = model.encode(article_titles, convert_to_tensor=True)
    
    personalized_results = {}
    for client in clients:
        keywords = set()
        goals = []
        keywords.update([i.lower() for i in client.get("features", {}).get("interests", [])])
        keywords.add(client.get("features", {}).get("profession", "").lower())
        for entity in client.get("related_entities", []):
            keywords.add(entity.get("features", {}).get("interest", "").lower())
            keywords.add(entity.get("features", {}).get("profession", "").lower())
            keywords.add(entity.get("features", {}).get("focus", "").lower())
        for goal in client.get("goals", []):
            goals.append(goal.get("description", ""))
            keywords.add(goal.get("features", {}).get("category", "").lower())
        keywords = {k for k in keywords if k}
        
        client_context = f"{client['name']} is interested in {', '.join(keywords)}. Goals: {', '.join(goals)}."
        client_embedding = model.encode(client_context, convert_to_tensor=True)
        cosine_scores = util.cos_sim(client_embedding, article_embeddings)[0]
        
        matched_articles = []
        for i, article in enumerate(articles):
            title_lower = article['title'].lower()
            best_fuzzy_score = 0
            for kw in keywords:
                score = fuzz.partial_ratio(kw, title_lower)
                if score > best_fuzzy_score: best_fuzzy_score = score
            
            semantic_score = cosine_scores[i].item()
            if (best_fuzzy_score >= fuzzy_threshold) or (semantic_score >= semantic_threshold):
                article_copy = article.copy()
                article_copy['fuzzy_score'] = best_fuzzy_score
                article_copy['semantic_score'] = round(semantic_score * 100, 2)
                matched_articles.append(article_copy)
        
        matched_articles.sort(key=lambda x: (x['semantic_score'] + (x['fuzzy_score']/2)), reverse=True)
        personalized_results[client['name']] = matched_articles
        
    return personalized_results

def save_log(results):
    os.makedirs("logs", exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = f"logs/news_log_{date_str}.json"
    
    log_data = {
        "date": datetime.now().isoformat(),
        "clients": results
    }
    
    with open(file_path, 'w') as f:
        json.dump(log_data, f, indent=2)
    print(f"\nResults saved to: {file_path}")

def main():
    clients = load_clients("clients_data.json")
    articles = collect_all_news()
    
    print(f"\nAnalyzing {len(articles)} articles from multiple sources...\n")
    personalized = get_personalized_news(clients, articles)
    
    # Pre-processing for clean logs and output
    final_output = {}
    for client_name, news in personalized.items():
        seen_titles = set()
        client_news = []
        for article in news:
            if article['title'] not in seen_titles:
                client_news.append(article)
                seen_titles.add(article['title'])
            if len(client_news) >= 5: break
        final_output[client_name] = client_news

    # Display results
    for client_name, news in final_output.items():
        print(f"=== RELEVANT NEWS FOR {client_name.upper()} ===")
        if news:
            for i, article in enumerate(news, 1):
                print(f"{i}. [{article['source']}] {article['title']}")
                print(f"   Link: {article['link']}")
                print(f"   Relevance: {article['semantic_score']}% AI | {article['fuzzy_score']}% Fuzzy\n")
        else:
            print("No specifically relevant news found today.\n")

    # Save to daily log
    save_log(final_output)

if __name__ == "__main__":
    main()
