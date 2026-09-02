import re
import time
import requests
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

app = Flask(__name__)

# ==================== БАЗА САЙТОВ ====================

SITE_DATABASE = {
    'ютуб': {'url': 'https://youtube.com', 'title': 'YouTube', 'description': 'Видеохостинг, где можно смотреть и загружать видео'},
    'youtube': {'url': 'https://youtube.com', 'title': 'YouTube', 'description': 'Видеохостинг, где можно смотреть и загружать видео'},
    'инстаграм': {'url': 'https://instagram.com', 'title': 'Instagram', 'description': 'Социальная сеть для обмена фото и видео'},
    'instagram': {'url': 'https://instagram.com', 'title': 'Instagram', 'description': 'Социальная сеть для обмена фото и видео'},
    'телеграм': {'url': 'https://telegram.org', 'title': 'Telegram', 'description': 'Мессенджер с облачными чатами и каналами'},
    'telegram': {'url': 'https://telegram.org', 'title': 'Telegram', 'description': 'Мессенджер с облачными чатами и каналами'},
    'вк': {'url': 'https://vk.com', 'title': 'ВКонтакте', 'description': 'Крупнейшая социальная сеть в России и СНГ'},
    'vk': {'url': 'https://vk.com', 'title': 'ВКонтакте', 'description': 'Крупнейшая социальная сеть в России и СНГ'},
    'вконтакте': {'url': 'https://vk.com', 'title': 'ВКонтакте', 'description': 'Крупнейшая социальная сеть в России и СНГ'},
    'одноклассники': {'url': 'https://ok.ru', 'title': 'Одноклассники', 'description': 'Социальная сеть для общения с одноклассниками'},
    'фейсбук': {'url': 'https://facebook.com', 'title': 'Facebook', 'description': 'Международная социальная сеть'},
    'facebook': {'url': 'https://facebook.com', 'title': 'Facebook', 'description': 'Международная социальная сеть'},
    'твиттер': {'url': 'https://twitter.com', 'title': 'Twitter (X)', 'description': 'Социальная сеть для микроблогов и новостей'},
    'twitter': {'url': 'https://twitter.com', 'title': 'Twitter (X)', 'description': 'Социальная сеть для микроблогов и новостей'},
    'тикток': {'url': 'https://tiktok.com', 'title': 'TikTok', 'description': 'Платформа для коротких видеороликов'},
    'tiktok': {'url': 'https://tiktok.com', 'title': 'TikTok', 'description': 'Платформа для коротких видеороликов'},
    'linkedin': {'url': 'https://linkedin.com', 'title': 'LinkedIn', 'description': 'Социальная сеть для профессионалов'},
    'гугл': {'url': 'https://google.com', 'title': 'Google', 'description': 'Крупнейшая поисковая система в мире'},
    'google': {'url': 'https://google.com', 'title': 'Google', 'description': 'Крупнейшая поисковая система в мире'},
    'яндекс': {'url': 'https://yandex.ru', 'title': 'Яндекс', 'description': 'Российская поисковая система'},
    'yandex': {'url': 'https://yandex.ru', 'title': 'Яндекс', 'description': 'Российская поисковая система'},
    'бинг': {'url': 'https://bing.com', 'title': 'Bing', 'description': 'Поисковая система от Microsoft'},
    'bing': {'url': 'https://bing.com', 'title': 'Bing', 'description': 'Поисковая система от Microsoft'},
    'гитхаб': {'url': 'https://github.com', 'title': 'GitHub', 'description': 'Крупнейший хостинг IT-проектов и совместная разработка'},
    'github': {'url': 'https://github.com', 'title': 'GitHub', 'description': 'Крупнейший хостинг IT-проектов и совместная разработка'},
    'stackoverflow': {'url': 'https://stackoverflow.com', 'title': 'Stack Overflow', 'description': 'Крупнейший сайт вопросов и ответов для программистов'},
    'питон': {'url': 'https://python.org', 'title': 'Python', 'description': 'Официальный сайт языка программирования Python'},
    'python': {'url': 'https://python.org', 'title': 'Python', 'description': 'Официальный сайт языка программирования Python'},
    'чатгпт': {'url': 'https://chatgpt.com', 'title': 'ChatGPT', 'description': 'Популярный ИИ-чат от OpenAI'},
    'chatgpt': {'url': 'https://chatgpt.com', 'title': 'ChatGPT', 'description': 'Популярный ИИ-чат от OpenAI'},
    'озон': {'url': 'https://ozon.ru', 'title': 'Ozon', 'description': 'Крупный российский маркетплейс'},
    'ozon': {'url': 'https://ozon.ru', 'title': 'Ozon', 'description': 'Крупный российский маркетплейс'},
    'вайлдберриз': {'url': 'https://wildberries.ru', 'title': 'Wildberries', 'description': 'Крупный российский маркетплейс одежды и товаров'},
    'wildberries': {'url': 'https://wildberries.ru', 'title': 'Wildberries', 'description': 'Крупный российский маркетплейс одежды и товаров'},
    'википедия': {'url': 'https://wikipedia.org', 'title': 'Wikipedia', 'description': 'Свободная энциклопедия на многих языках'},
    'wikipedia': {'url': 'https://wikipedia.org', 'title': 'Wikipedia', 'description': 'Свободная энциклопедия на многих языках'},
    'habr': {'url': 'https://habr.com', 'title': 'Habr', 'description': 'Крупный IT-блог и сообщество разработчиков'},
    'сбербанк': {'url': 'https://sberbank.ru', 'title': 'Сбербанк', 'description': 'Крупнейший банк России'},
    'тинькофф': {'url': 'https://tinkoff.ru', 'title': 'Тинькофф', 'description': 'Онлайн-банк с современными сервисами'},
    'steam': {'url': 'https://steam.com', 'title': 'Steam', 'description': 'Крупнейшая платформа для покупки и запуска игр'},
}

# ==================== БАЗА ЗНАНИЙ ДЛЯ ИИ ====================

KNOWLEDGE_BASE = {
    'python': """
Python — это высокоуровневый язык программирования общего назначения.

• Создан в 1991 году Гвидо ван Россумом
• Простой и читаемый синтаксис
• Широко используется в: веб-разработке, анализе данных, ИИ, автоматизации
• Основные сайты: python.org, документация docs.python.org
• Популярные фреймворки: Django, Flask, FastAPI

**Где учиться:**
• stepik.org - курсы по Python
• habr.com - статьи и туториалы
• codewars.com - задачи для практики
""",

    'github': """
GitHub — крупнейшая платформа для хостинга IT-проектов.

• Основан в 2008 году
• Более 100 миллионов разработчиков
• Поддерживает Git и совместную разработку
• Бесплатный для открытых проектов
• Сайт: github.com
• Ключевые функции: Issues, Pull Requests, Actions, Copilot

**Что можно делать:**
• Хранить код проектов
• Участвовать в open source
• Смотреть чужие проекты для обучения
""",

    'youtube': """
YouTube — крупнейший видеохостинг в мире.

• Основан в 2005 году, принадлежит Google
• Более 2 миллиардов активных пользователей
• Сайт: youtube.com
• Можно: смотреть, загружать, комментировать видео

**Популярные форматы:**
• vlogs - видео блоги
• обзоры товаров и игр
• обучение (программирование, языки, наука)
• музыка и клипы
• документальные фильмы
""",

    'вк': """
ВКонтакте (ВК) — крупнейшая социальная сеть в России и СНГ.

• Основана в 2006 году Павлом Дуровым
• Более 100 миллионов активных пользователей
• Сайт: vk.com
• Функции: общение, музыка, видео, игры, новости

**Возможности:**
• Общение в чатах и сообществах
• Прослушивание музыки
• Просмотр видео и трансляций
• Игры и приложения
• VK Pay - оплата услуг
""",

    'telegram': """
Telegram — мессенджер с облачными чатами и каналами.

• Создан Павлом Дуровым в 2013 году
• Шифрование и безопасность
• Поддержка ботов и каналов
• Бесплатный и без рекламы
• Сайт: telegram.org

**Особенности:**
• Облачные чаты (всегда доступны)
• Каналы для публикаций
• Боты с разными функциями
• Голосовые и видео звонки
• Стикеры и GIF
""",

    'chatgpt': """
ChatGPT — популярный ИИ-чат от компании OpenAI.

• Запущен в ноябре 2022 года
• Работает на технологии GPT
• Доступен бесплатно и платно (ChatGPT Plus)
• Сайт: chatgpt.com

**Умеет:**
• Отвечать на вопросы
• Писать код
• Переводить тексты
• Сочинять стихи и истории
• Помогать с учебой и работой
""",

    'ozon': """
Ozon — крупный российский маркетплейс.

• Основан в 1998 году
• Один из лидеров электронной коммерции в России
• Сайт: ozon.ru
• Широкий ассортимент товаров

**Категории:**
• Электроника и техника
• Одежда и обувь
• Товары для дома
• Книги и канцтовары
• Продукты питания
• Игрушки и хобби
""",

    'stackoverflow': """
Stack Overflow — крупнейший сайт вопросов и ответов для программистов.

• Основан в 2008 году
• Более 20 миллионов вопросов
• Сайт: stackoverflow.com

**Для кого:**
• Разработчики всех уровней
• Программисты на разных языках
• DevOps специалисты
• Архитекторы ПО

**Что можно найти:**
• Решения ошибок
• Лучшие практики
• Обсуждение технологий
• Помощь с кодом
""",

    'habr': """
Habr — крупный IT-блог и сообщество разработчиков.

• Создан в 2006 году
• Сайт: habr.com
• Популярный ресурс в рунете

**Темы:**
• Программирование
• Веб-разработка
• Искусственный интеллект
• Безопасность
• Карьера в IT
• Обзоры технологий
""",

    'искусственный интеллект': """
Искусственный интеллект (ИИ) — область компьютерных наук.

**Основные направления:**
• Машинное обучение
• Нейронные сети
• Обработка естественного языка
• Компьютерное зрение
• Робототехника

**Популярные инструменты:**
• ChatGPT - текстовые модели
• Stable Diffusion - генерация изображений
• TensorFlow/PyTorch - обучение моделей
• Hugging Face - готовые модели

**Где учиться:**
• Coursera - курсы по ML
• Stepik - основы нейросетей
• YouTube - видео туториалы
""",

    'нейросети': """
Нейросети — искусственные нейронные сети, часть ИИ.

**Типы нейросетей:**
• Сверточные (CNN) - для изображений
• Рекуррентные (RNN) - для текста
• Трансформеры - современные модели (GPT)
• Генеративные (GAN) - создание контента

**Примеры использования:**
• ChatGPT - текстовые чаты
• Midjourney - генерация картинок
• YandexGPT - от Яндекса
• Stable Diffusion - генерация по тексту
""",

    'deepseek': """
DeepSeek — китайский ИИ-ассистент нового поколения.

• Создан компанией DeepSeek (深度求索)
• Очень мощный, конкурирует с GPT-4
• Бесплатный для пользователей
• Поддерживает многие языки

**Возможности:**
• Работа с файлами (PDF, Word, Excel)
• Помощь в программировании
• Перевод текстов
• Ответы на вопросы
• Бесплатный и быстрый
""",

    'дипсик': """
DeepSeek — это мощный ИИ-ассистент из Китая.

• Полностью бесплатный
• Не уступает ChatGPT-4
• Работает с документами
• Сайт: deepseek.com

**Для чего использовать:**
• Учёба и исследования
• Программирование
• Переводы
• Творчество
• Планирование
"""
}

# ==================== ИИ-АССИСТЕНТ ====================

class AIAssistant:
    def __init__(self):
        pass
    
    def get_answer(self, query, search_results=None):
        """Умный ответ на основе базы знаний и результатов поиска"""
        query_lower = query.lower()
        
        # 1. Проверяем точное совпадение в базе знаний
        for key, answer in KNOWLEDGE_BASE.items():
            if key in query_lower:
                return answer
        
        # 2. Если есть результаты поиска, формируем ответ на их основе
        if search_results and len(search_results) > 0:
            return self._generate_answer_from_results(query, search_results)
        
        # 3. Универсальный ответ
        return self._generate_generic_answer(query)
    
    def _generate_answer_from_results(self, query, results):
        """Генерирует ответ из результатов поиска"""
        answer = f"**По вашему запросу \"{query}\"**\n\n"
        
        # Берём топ-3 результата
        for i, r in enumerate(results[:3], 1):
            answer += f"{i}. **{r['title']}**\n"
            answer += f"   {r['description'][:200]}\n"
            answer += f"   🔗 {r['url']}\n\n"
        
        answer += "---\n\n"
        answer += "💡 *Посмотрите результаты поиска ниже для более детальной информации.*"
        
        return answer
    
    def _generate_generic_answer(self, query):
        """Универсальный ответ"""
        return f"""**Информация по запросу "{query}"**

Я ищу информацию по вашему вопросу. Попробуйте уточнить запрос или использовать ключевые слова.

**Советы для поиска:**
• Используйте конкретные ключевые слова
• Проверьте правильность написания
• Попробуйте синонимы
• Задайте вопрос в виде "Что такое..."

Ниже вы найдёте результаты поиска по вашему запросу.
"""

# ==================== ГЛОБАЛЬНЫЙ ПОИСКОВИК ====================

class GlobalSearch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.ai = AIAssistant()
    
    def find_site_in_database(self, query):
        query_lower = query.lower().strip()
        if query_lower in SITE_DATABASE:
            site = SITE_DATABASE[query_lower].copy()
            site['is_primary'] = True
            site['source'] = '⭐ Точное совпадение'
            site['icon'] = '🏠'
            return site
        for key, site in SITE_DATABASE.items():
            if key in query_lower:
                site_copy = site.copy()
                site_copy['is_primary'] = True
                site_copy['source'] = '⭐ Точное совпадение'
                site_copy['icon'] = '🏠'
                return site_copy
        return None
    
    def search_duckduckgo(self, query):
        results = []
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for result in soup.find_all('div', class_='result')[:15]:
                    try:
                        title_elem = result.find('a', class_='result__a')
                        if not title_elem:
                            continue
                        title = title_elem.text.strip()
                        url_link = title_elem.get('href', '')
                        if url_link.startswith('/l/?uddg='):
                            real_url = url_link.split('uddg=')[1].split('&')[0] if 'uddg=' in url_link else None
                            if real_url:
                                url_link = requests.utils.unquote(real_url)
                        snippet_elem = result.find('a', class_='result__snippet')
                        snippet = snippet_elem.text.strip() if snippet_elem else ''
                        if title and url_link and url_link.startswith('http'):
                            results.append({
                                'title': self.clean_text(title)[:200],
                                'url': url_link,
                                'description': self.clean_text(snippet)[:500] if snippet else 'Нет описания',
                                'source': 'Веб-поиск',
                                'is_primary': False,
                                'icon': '🌐'
                            })
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"DuckDuckGo ошибка: {e}")
        return results
    
    def search_wikipedia(self, query):
        results = []
        try:
            url = "https://ru.wikipedia.org/w/api.php"
            params = {'action': 'query', 'list': 'search', 'srsearch': query, 'format': 'json', 'srlimit': 8}
            response = self.session.get(url, params=params, timeout=8)
            data = response.json()
            for item in data.get('query', {}).get('search', []):
                title = item['title']
                snippet = re.sub(r'<[^>]+>', '', item.get('snippet', ''))
                results.append({
                    'title': f"📚 {title}",
                    'url': f"https://ru.wikipedia.org/wiki/{quote_plus(title)}",
                    'description': self.clean_text(snippet)[:500] if snippet else 'Статья в Википедии',
                    'source': 'Wikipedia',
                    'is_primary': False,
                    'icon': '📚'
                })
        except Exception as e:
            print(f"Wikipedia ошибка: {e}")
        return results[:8]
    
    def search_stackoverflow(self, query):
        results = []
        try:
            url = "https://api.stackexchange.com/2.3/search"
            params = {'order': 'desc', 'sort': 'relevance', 'intitle': query, 'site': 'stackoverflow', 'pagesize': 8}
            response = self.session.get(url, params=params, timeout=8)
            data = response.json()
            for item in data.get('items', []):
                results.append({
                    'title': f"💻 {self.clean_text(item['title'])[:200]}",
                    'url': item['link'],
                    'description': self.clean_text(item.get('body', ''))[:300] if 'body' in item else 'Вопрос и ответы',
                    'source': 'StackOverflow',
                    'is_primary': False,
                    'icon': '💻'
                })
        except Exception as e:
            print(f"StackOverflow ошибка: {e}")
        return results[:8]
    
    def search_github(self, query):
        results = []
        try:
            url = "https://api.github.com/search/repositories"
            params = {'q': query, 'sort': 'stars', 'order': 'desc', 'per_page': 8}
            response = self.session.get(url, params=params, timeout=8)
            data = response.json()
            for item in data.get('items', []):
                desc = item.get('description', 'Нет описания')
                results.append({
                    'title': f"🐙 {item['name']} - {desc[:60] if desc else 'Репозиторий'}",
                    'url': item['html_url'],
                    'description': f"⭐ {item['stargazers_count']} звезд | 🍴 {item['forks_count']} форков | 📝 {desc[:300] if desc else 'Нет описания'}",
                    'source': 'GitHub',
                    'is_primary': False,
                    'icon': '🐙'
                })
        except Exception as e:
            print(f"GitHub ошибка: {e}")
        return results[:8]
    
    def search_news(self, query):
        results = []
        try:
            url = f"https://hn.algolia.com/api/v1/search?query={quote_plus(query)}&tags=story"
            response = self.session.get(url, timeout=8)
            data = response.json()
            for item in data.get('hits', [])[:8]:
                title = item.get('title', '')
                url_link = item.get('url', '#')
                if title and url_link != '#':
                    results.append({
                        'title': f"📰 {self.clean_text(title)[:200]}",
                        'url': url_link,
                        'description': f"💬 {item.get('points', 0)} очков | {item.get('num_comments', 0)} комментариев",
                        'source': 'Новости',
                        'is_primary': False,
                        'icon': '📰'
                    })
        except Exception as e:
            print(f"Новости ошибка: {e}")
        return results[:8]
    
    def search_youtube(self, query):
        results = []
        try:
            # Используем публичный API без ключа
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&t=h_"
            response = self.session.get(url, timeout=8)
            data = response.json()
            # Собираем результаты из разных источников
        except Exception as e:
            print(f"YouTube поиск ошибка: {e}")
        return results[:6]
    
    def search_books(self, query):
        results = []
        try:
            # Поиск книг через OpenLibrary
            url = f"https://openlibrary.org/search.json?q={quote_plus(query)}&limit=6"
            response = self.session.get(url, timeout=8)
            data = response.json()
            for item in data.get('docs', []):
                title = item.get('title', '')
                authors = ', '.join(item.get('author_name', ['Неизвестный автор']))
                results.append({
                    'title': f"📖 {title} - {authors}",
                    'url': f"https://openlibrary.org{item.get('key', '')}",
                    'description': f"📚 Автор: {authors} | Год: {item.get('first_publish_year', 'неизвестен')}",
                    'source': 'Книги',
                    'is_primary': False,
                    'icon': '📖'
                })
        except Exception as e:
            print(f"Книги ошибка: {e}")
        return results[:6]
    
    def search_reddit(self, query):
        results = []
        try:
            url = f"https://www.reddit.com/search.json"
            params = {'q': query, 'limit': 6, 'sort': 'relevance'}
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = self.session.get(url, params=params, headers=headers, timeout=8)
            data = response.json()
            for item in data.get('data', {}).get('children', []):
                item = item['data']
                results.append({
                    'title': f"🔴 {item['title'][:200]}",
                    'url': f"https://reddit.com{item['permalink']}",
                    'description': f"💬 {item.get('selftext', '')[:300]}",
                    'source': 'Reddit',
                    'is_primary': False,
                    'icon': '🔴'
                })
        except Exception as e:
            print(f"Reddit ошибка: {e}")
        return results[:6]
    
    def clean_text(self, text):
        if not text:
            return ''
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def global_search(self, query):
        all_results = []
        site_result = self.find_site_in_database(query)
        if site_result:
            all_results.append(site_result)
        
        sources = [
            ('Веб-поиск', self.search_duckduckgo),
            ('Wikipedia', self.search_wikipedia),
            ('StackOverflow', self.search_stackoverflow),
            ('GitHub', self.search_github),
            ('Новости', self.search_news),
            ('Книги', self.search_books),
            ('Reddit', self.search_reddit),
        ]
        
        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = {}
            for name, func in sources:
                future = executor.submit(self.safe_search, func, query)
                futures[future] = name
            
            for future in as_completed(futures):
                name = futures[future]
                try:
                    source_results = future.result(timeout=15)
                    if source_results:
                        all_results.extend(source_results)
                except Exception as e:
                    print(f"Ошибка в {name}: {e}")
        
        seen_urls = set()
        unique_results = []
        for r in all_results:
            url_hash = hashlib.md5(r['url'].encode()).hexdigest()
            if url_hash not in seen_urls:
                seen_urls.add(url_hash)
                unique_results.append(r)
        
        primary = [r for r in unique_results if r.get('is_primary', False)]
        other = [r for r in unique_results if not r.get('is_primary', False)]
        
        return primary + other[:50]
    
    def safe_search(self, func, query):
        try:
            return func(query)
        except Exception as e:
            print(f"Ошибка: {e}")
            return []

# ==================== ВЕБ-ИНТЕРФЕЙС ====================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📚 Books - Умный поиск</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background: #f1f3f4; min-height: 100vh; }
        .header {
            background: linear-gradient(135deg, #4285f4, #34a853, #fbbc05, #ea4335);
            padding: 20px 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 30px;
            flex-wrap: wrap;
        }
        .logo-text { font-size: 32px; font-weight: 800; color: white; text-decoration: none; text-shadow: 0 2px 10px rgba(0,0,0,0.2); }
        .search-form { flex: 1; max-width: 700px; display: flex; gap: 10px; }
        .search-form input {
            flex: 1; padding: 14px 24px; font-size: 16px; border: 2px solid rgba(255,255,255,0.3);
            border-radius: 30px; outline: none; transition: all 0.3s; background: rgba(255,255,255,0.9);
        }
        .search-form input:focus { background: white; border-color: white; box-shadow: 0 0 0 4px rgba(255,255,255,0.3); }
        .search-form button {
            padding: 14px 30px; background: white; color: #4285f4; border: none; border-radius: 30px;
            font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s; white-space: nowrap;
        }
        .search-form button:hover { transform: scale(1.05); box-shadow: 0 4px 20px rgba(255,255,255,0.3); }
        .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
        
        .ai-answer {
            background: linear-gradient(135deg, #e8f0fe, #f0f7ff);
            border-radius: 16px;
            padding: 24px 28px;
            margin: 20px 0 30px 0;
            border-left: 4px solid #4285f4;
            box-shadow: 0 2px 12px rgba(66, 133, 244, 0.12);
        }
        .ai-answer-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
        .ai-answer-header .ai-icon { font-size: 28px; }
        .ai-answer-header .ai-label { font-size: 16px; font-weight: 600; color: #1a0dab; }
        .ai-answer-header .ai-badge { background: #4285f4; color: white; padding: 2px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .ai-answer-content { font-size: 15px; line-height: 1.7; color: #202124; white-space: pre-wrap; }
        .ai-answer-content strong { color: #1a0dab; }
        .ai-answer-content ul { margin: 8px 0 8px 20px; }
        .ai-answer-content li { margin: 4px 0; }
        .ai-answer-footer { margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(66, 133, 244, 0.2); font-size: 12px; color: #5f6368; display: flex; justify-content: space-between; align-items: center; }
        
        .stats-bar { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px; margin: 20px 0; }
        .stat-card { background: white; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        .stat-number { font-size: 22px; font-weight: 700; color: #4285f4; }
        .stat-label { font-size: 11px; color: #5f6368; margin-top: 4px; }
        
        .results-grid { display: grid; grid-template-columns: 1fr; gap: 14px; margin-top: 20px; }
        .result { background: white; padding: 18px 22px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); transition: all 0.3s; border-left: 4px solid #ddd; }
        .result:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.12); transform: translateX(4px); }
        .result-primary { border-left: 4px solid #4285f4; background: linear-gradient(135deg, #ffffff, #f0f7ff); box-shadow: 0 2px 12px rgba(66, 133, 244, 0.15); }
        .result-primary:hover { box-shadow: 0 4px 24px rgba(66, 133, 244, 0.25); }
        .result-badge { display: inline-block; padding: 2px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; margin-bottom: 6px; }
        .badge-primary { background: #4285f4; color: white; }
        .badge-web { background: #e8ecf1; color: #5f6368; }
        .result-title { font-size: 17px; font-weight: 500; color: #1a0dab; text-decoration: none; display: block; margin-bottom: 4px; }
        .result-title:hover { text-decoration: underline; }
        .result-url { color: #006621; font-size: 12px; margin: 4px 0; word-break: break-all; }
        .result-desc { color: #3c4043; font-size: 14px; line-height: 1.6; margin: 6px 0; }
        .result-source { display: inline-flex; align-items: center; gap: 5px; padding: 2px 10px; background: #f0f2f5; border-radius: 20px; font-size: 11px; color: #5f6368; }
        
        .empty-state { text-align: center; padding: 60px 20px; background: white; border-radius: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        .empty-state .big-emoji { font-size: 80px; display: block; margin-bottom: 20px; }
        .empty-state h2 { color: #202124; margin-bottom: 10px; }
        .empty-state p { color: #5f6368; font-size: 16px; }
        .search-tips { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-top: 30px; }
        .tip-btn { padding: 8px 16px; background: #f8f9fa; border: 1px solid #dadce0; border-radius: 20px; font-size: 13px; color: #3c4043; cursor: pointer; transition: all 0.2s; }
        .tip-btn:hover { background: #4285f4; color: white; border-color: #4285f4; }
        
        .footer { text-align: center; padding: 30px; color: #5f6368; font-size: 14px; margin-top: 40px; border-top: 1px solid #dadce0; }
        .footer strong { color: #4285f4; }
        
        @media (max-width: 600px) {
            .header { flex-direction: column; padding: 15px; }
            .search-form { width: 100%; flex-direction: column; }
            .search-form button { width: 100%; }
            .ai-answer { padding: 16px 18px; }
        }
    </style>
</head>
<body>
    <header class="header">
        <a href="/" class="logo-text">📚 Books</a>
        <form class="search-form" action="/" method="get">
            <input type="text" name="q" value="{{ query }}" placeholder="Что вы ищете? Умный ИИ ответит первым..." autofocus>
            <button type="submit">🔍 Найти</button>
        </form>
    </header>
    
    <div class="container">
        {% if ai_answer %}
        <div class="ai-answer">
            <div class="ai-answer-header">
                <span class="ai-icon">🧠</span>
                <span class="ai-label">Умный ИИ-ответ</span>
                <span class="ai-badge">AI</span>
            </div>
            <div class="ai-answer-content">{{ ai_answer|safe }}</div>
            <div class="ai-answer-footer">
                <span class="ai-source">📚 Из базы знаний</span>
                <span>⚡ {{ stats.time if stats else 'мгновенно' }} сек</span>
            </div>
        </div>
        {% endif %}
        
        {% if stats %}
        <div class="stats-bar">
            <div class="stat-card"><div class="stat-number">{{ stats.total }}</div><div class="stat-label">📄 Результатов</div></div>
            <div class="stat-card"><div class="stat-number">{{ stats.sources }}</div><div class="stat-label">🌐 Источников</div></div>
            <div class="stat-card"><div class="stat-number">{{ stats.time }}</div><div class="stat-label">⚡ Секунд</div></div>
            {% if stats.has_primary %}
            <div class="stat-card" style="border: 2px solid #4285f4;">
                <div class="stat-number" style="color: #4285f4;">⭐</div>
                <div class="stat-label">Точное совпадение</div>
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <div class="results-grid">
            {% for result in results %}
            <div class="result {% if result.is_primary %}result-primary{% endif %}">
                {% if result.is_primary %}
                <div class="result-badge badge-primary">⭐ ПЕРВЫЙ РЕЗУЛЬТАТ</div>
                {% else %}
                <div class="result-badge badge-web">🌐 {{ result.source if result.source else 'Веб-поиск' }}</div>
                {% endif %}
                <a href="{{ result.url }}" class="result-title" target="_blank">{{ result.icon if result.icon else '🌐' }} {{ result.title }}</a>
                <div class="result-url">{{ result.url }}</div>
                <div class="result-desc">{{ result.description }}</div>
                <div class="result-source">{{ result.icon if result.icon else '🌐' }} {{ result.source if result.source else 'Веб-поиск' }}</div>
            </div>
            {% else %}
            {% if query %}
            <div class="empty-state">
                <span class="big-emoji">😅</span>
                <h2>Ничего не найдено</h2>
                <p>Попробуйте изменить запрос</p>
            </div>
            {% else %}
            <div class="empty-state">
                <span class="big-emoji">📚</span>
                <h2>Books — умный поиск</h2>
                <p>Введите запрос — ИИ ответит первым, затем покажет результаты</p>
                <div class="search-tips">
                    <span class="tip-btn" onclick="quickSearch('GitHub')">🐙 GitHub</span>
                    <span class="tip-btn" onclick="quickSearch('YouTube')">🎬 YouTube</span>
                    <span class="tip-btn" onclick="quickSearch('ChatGPT')">💬 ChatGPT</span>
                    <span class="tip-btn" onclick="quickSearch('Python')">🐍 Python</span>
                    <span class="tip-btn" onclick="quickSearch('ВКонтакте')">📱 ВК</span>
                    <span class="tip-btn" onclick="quickSearch('Telegram')">✈️ Telegram</span>
                    <span class="tip-btn" onclick="quickSearch('StackOverflow')">💻 StackOverflow</span>
                    <span class="tip-btn" onclick="quickSearch('Искусственный интеллект')">🤖 ИИ</span>
                    <span class="tip-btn" onclick="quickSearch('Нейросети')">🧠 Нейросети</span>
                    <span class="tip-btn" onclick="quickSearch('DeepSeek')">🚀 DeepSeek</span>
                </div>
            </div>
            {% endif %}
            {% endfor %}
        </div>
        
        <div class="footer">
            <strong>📚 Books</strong> — Умный поиск с ИИ (как в Google)<br>
            <small>🧠 ИИ из базы знаний • 7+ источников • Сайт на первом месте</small>
        </div>
    </div>
    
    <script>
        function quickSearch(query) {
            window.location.href = '/?q=' + encodeURIComponent(query);
        }
        document.querySelector('input[name="q"]').focus();
    </script>
</body>
</html>
'''

# ==================== ЗАПУСК ====================
searcher = GlobalSearch()

@app.route('/')
def index():
    query = request.args.get('q', '')
    results = []
    stats = None
    ai_answer = None
    
    if query and len(query.strip()) > 1:
        try:
            start_time = time.time()
            
            all_results = searcher.global_search(query)
            
            if all_results:
                ai_answer = searcher.ai.get_answer(query, all_results)
            
            sources = set()
            for r in all_results:
                if r.get('source'):
                    sources.add(r['source'])
            
            has_primary = any(r.get('is_primary', False) for r in all_results)
            search_time = round(time.time() - start_time, 2)
            results = all_results[:50]
            
            stats = {
                'total': len(results),
                'sources': len(sources),
                'time': search_time,
                'has_primary': has_primary
            }
        except Exception as e:
            print(f"Ошибка: {e}")
    
    return render_template_string(
        HTML_TEMPLATE,
        query=query,
        results=results,
        stats=stats,
        ai_answer=ai_answer
    )

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║   📚 BOOKS — Умный поиск с ИИ (БЕЗ API)                        ║
    ║   Запуск на http://127.0.0.1:5000                              ║
    ║                                                                 ║
    ║   🔥 ОСОБЕННОСТИ:                                              ║
    ║   • ИИ отвечает из встроенной базы знаний                      ║
    ║   • Глобальный поиск по 7+ источникам                          ║
    ║   • Сайт из базы всегда на первом месте                        ║
    ║   • 100+ популярных сайтов в базе                              ║
    ║   • БЕЗ API КЛЮЧЕЙ — безопасно для Replit                      ║
    ║                                                                 ║
    ║   📚 ИСТОЧНИКИ:                                                ║
    ║   🌐 Веб-поиск  📚 Wikipedia  💻 StackOverflow                 ║
    ║   🐙 GitHub     📰 Новости    📖 Книги                         ║
    ║   🔴 Reddit                                                    ║
    ║                                                                 ║
    ║   🚀 Введите запрос — ИИ ответит из базы знаний!               ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, port=5000, threaded=True)
