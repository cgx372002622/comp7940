import requests
from bs4 import BeautifulSoup


def scrape_movies(query):
    # 构造查询的URL
    url = f'https://movie.douban.com/subject_search?search_text={query}&cat=1002'

    # 添加请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    print(response.status_code)  # 输出HTTP响应状态码
    print(response.text)  # 输出页面内容

    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取电影数据
    movies = []
    for movie_element in soup.select('.item-root'):
        title = movie_element.select_one('.title-text').text.strip()
        rating = movie_element.select_one('.rating_nums').text.strip()
        description = movie_element.select_one('.desc').text.strip()

        movie = {
            'title': title,
            'rating': rating,
            'description': description
        }
        movies.append(movie)

    return movies
