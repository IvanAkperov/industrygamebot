import json
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, lik"
                  "e Gecko) Chrome/108.0.0.0 YaBrowser/23.1.2.987 Yowser/2.5 Safari/537.36",
    "Referer": "https://stopgame.ru/",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"

}
url = "https://stopgame.ru/news"


def get_news():
    req = requests.get(url, headers=headers, timeout=2)
    soup = BeautifulSoup(req.text, "html.parser")
    content = soup.find_all("div", class_="item article-summary")
    news_dict = {}
    for items in content:
        link = "https://stopgame.ru/" + items.find("a").get("href")
        desk = items.find("div", class_="article-description").find("div", class_="caption caption-bold"). \
            find("a").get_text(strip=True)
        date = items.find("div", class_="article-description").find("div", class_="info").find \
            ("span", class_="info-item timestamp").get_text(strip=True)
        comments_section = "https://stopgame.ru/" + items.find("div", class_="article-description"). \
            find("div", class_="info").find("span", class_="info-item comments").find("a").get("href")
        news_id = str(link).split("/")[5]
        news_dict[news_id] = {"url": link, "description": desk, "date": date, "comments": comments_section}
    with open("game_news.json", "w", encoding="utf-8") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)
    return content


def check_new_content():
    with open("game_news.json", "r", encoding="utf-8") as new_file:
        news_dict = json.load(new_file)

    fresh_news = {}
    check_update = get_news()
    for content in check_update:
        link = "https://stopgame.ru/" + content.find("a").get("href")
        news_id = str(link).split("/")[5]
        if news_id in news_dict:
            continue
        else:
            desk = content.find("div", class_="article-description").find("div", class_="caption caption-bold"). \
                find("a").get_text(strip=True)
            date = content.find("div", class_="article-description").find("div", class_="info").find \
                ("span", class_="info-item timestamp").get_text(strip=True)
            comments_section = "https://stopgame.ru/" + content.find("div", class_="article-description"). \
                find("div", class_="info").find("span", class_="info-item comments").find("a").get("href")
            news_dict[news_id] = {
                "url": link,
                "description": desk,
                "date": date,
                "comments": comments_section
            }
            fresh_news[news_id] = {
                "url": link,
                "description": desk,
                "date": date,
                "comments": comments_section
            }
    with open("game_news.json", "w", encoding="utf-8") as file:
        json.dump(news_dict, file, indent=4, ensure_ascii=False)

    return fresh_news


def main():
    # get_news()
    check_new_content()


if __name__ == '__main__':
    main()
