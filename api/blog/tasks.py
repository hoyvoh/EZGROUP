from celery import shared_task
import requests
import pandas as pd
from bs4 import BeautifulSoup
from .models import Post, UserSession, Image
from django.utils import timezone


def get_new_posts(url="https://cafef.vn/bat-dong-san.chn"):
    response = requests.get(url)
    
    if not response.text:
        print("Failed to retrieve the webpage content")
        return []

    bs = BeautifulSoup(response.text, 'html.parser')

    list_focus_main = bs.find('div', {'class': 'list-focus-main'})
    if not list_focus_main:
        print("Failed to find the main list of links on the page.")
        return []

    links = [link['href'] for link in list_focus_main.find_all('a', href=True)]
    pages = []

    for link in links:
        try:
            page_response = requests.get(link)
            if page_response.status_code == 200:
                pages.append(page_response.text)
            else:
                print(f"Failed to retrieve page: {link}")
        except requests.RequestException as e:
            print(f"Error fetching the page {link}: {e}")
    
    news = []
    
    for page in pages:
        bs = BeautifulSoup(page, 'html.parser')
        page_content = bs.find('div', {'class': 'left_cate totalcontentdetail'})
        
        if not page_content:
            print("Failed to find the page content.")
            continue

        bs = BeautifulSoup(str(page_content), 'html.parser')

        title = bs.find('h1', {'class': 'title'}).get_text().strip() if bs.find('h1', {'class': 'title'}) else ''
        date = bs.find('span', {'class': 'pdate'}).get_text().strip() if bs.find('span', {'class': 'pdate'}) else ''
        cate = bs.find('a', {'class': 'cat'}).get_text().strip() if bs.find('a', {'class': 'cat'}) else ''
        
        content_div = bs.find('div', {'class': 'w640 fr clear'})
        content = '[SEP]'.join(paragraph.strip() for paragraph in content_div.get_text().split('\n') if paragraph.strip()) if content_div else ''
        
        imgs = '[SEP]'.join([img['src'] for img in bs.find_all('img') if 'src' in img.attrs])
        labs = '[SEP]'.join([img['title'] for img in bs.find_all('img') if 'title' in img.attrs])
        
        block = BeautifulSoup(str(bs.find('div', {'class': 't-contentdetail content_source'})), 'html.parser')
        author = block.find('p', {'class': 'author'}).get_text().strip() if block.find('p', {'class': 'author'}) else ''
        source = block.find('p', {'class': 'source'}).get_text().strip() if block.find('p', {'class': 'source'}) else ''
        
        new = {
            'title': title,
            'date': date,
            'category': cate,
            'content': content,
            'images': imgs,
            'labels': labs,
            'author': author,
            'source': source
        }

        news.append(new)
    
    return news


@shared_task
def update_news():
    posts = get_new_posts()

    for data in posts:
        if Post.objects.filter(title=data['title']).exists():
            print(f"Post with title '{data['title']}' already exists. Skipping...")
            continue

        anonymous_session, created = UserSession.objects.get_or_create(
            is_anonymous=True,
            session_token="anonymous_" + str(timezone.now().timestamp())
        )

        post = Post(
                title=data['title'],
                content=data['content'],
                category=data['category'],
                author_session=anonymous_session,
                author_name=f'{data['author']} | {data['source']}',  # Since it's an anonymous user
                author_email=f'{data['author']}.{data['source']}@ezmail.com',  # No real email
            )
        post.save()

        image_urls = data['images'].split('[SEP]') 
        image_labels = data['labels'].split('[SEP]')
        
        for img_url, label in zip(image_urls, image_labels):
            
            image = Image(
                post=post,
                image_url=img_url,
                label=label
            )
            image.save()
        