import json
import logging
import math
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests
from bs4 import BeautifulSoup
import time
import random

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
logging.basicConfig(format='[%(asctime)s] %(levelname)s:%(message)s [%(filename)s/%(funcName)s:%(lineno)d:%(threadName)s]\n', level=logging.INFO)
MAIN_DOMAIN = 'https://www.niche.com'
UNIVERSITY = 'Harvard University'


def run():
    data = {}
    r = requests.get(f'{MAIN_DOMAIN}/colleges/harvard-university/', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    tags = soup.find('div', class_='overall-grade__niche-grade')

    # report_card
    report_card = {}
    overall_niche_grade = tags.find('span', class_='visually-hidden').next_sibling.strip()
    report_card['overall_niche_grade'] = overall_niche_grade

    items = soup.find_all('li', class_='ordered__list__bucket__item')
    grades = {}
    for item in items:
        label = item.find('div', class_='profile-grade__label').get_text(
            strip=True)
        grade = item.find('div', class_='niche__grade').find(string=True, recursive=False).strip()
        grade_split = grade.split(' ')
        if len(grade_split) == 2:
            grade = f'{grade_split[0]}-'
        grades[label.lower()] = grade
    report_card['grades'] = grades

    # tags
    tags = soup.find_all('a', class_='search-tags__wrap__list__tag__a')
    tags_list = [tag.get_text(strip=True) for tag in tags]

    net_price = soup.find('section', id='cost').find('div', class_='profile__bucket--1').find('div', class_='scalar__value').find('span').get_text(strip=True)
    average_total_aid = soup.find('section', id='cost').find('div', class_='profile__bucket--2').find_all('div', class_='scalar--three')[0].find('div', class_='scalar__value').find('span').get_text(strip=True)
    students_receiving_aid = soup.find('section', id='cost').find('div', class_='profile__bucket--2').find_all('div', class_='scalar--three')[1].find('div', class_='scalar__value').find('span').get_text(strip=True)
    cost = {
        'net_price': net_price,
        'average_total_aid': average_total_aid,
        'students_receiving_aid': students_receiving_aid,
    }

    script_tag = soup.find('script', id='dataLayerTag')
    script_content = script_tag.string.strip()
    json_data = json.loads(script_content[len('dataLayer = '):])
    entity_guid = json_data[0].get('entityGuid', None)

    reviews = {}
    r = requests.get(f'{MAIN_DOMAIN}/api/entity-reviews-histogram/?e={entity_guid}&page=2&limit=20', headers=HEADERS)
    total = r.json().get('total')
    review_histogram = r.json().get('reviewHistogram')
    review_chart = {
        'excellent': review_histogram.get(5),
        'very_good': review_histogram.get(4),
        'average': review_histogram.get(3),
        'poor': review_histogram.get(2),
        'terrible': review_histogram.get(1),
    }
    reviews['total'] = total
    reviews['review_chart'] = review_chart

    all_reviews = []
    total_pages = math.ceil(total / 20)
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_reviews, entity_guid, page_number) for page_number in range(1, total_pages)):
            all_reviews.extend(i.result())
    reviews['all_reviews'] = all_reviews

    data['report_card'] = report_card
    data['tags'] = tags_list
    data['cost'] = cost
    data['reviews'] = reviews
    return data


def get_reviews(entity_guid, page_number):
    print(f'{page_number} page_number')
    time.sleep(random.randint(5, 10))
    reviews = []
    url = f'{MAIN_DOMAIN}/api/entity-reviews/?e={entity_guid}&page={page_number}&limit=20'
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,si;q=0.7',
        'content-type': 'application/json',
        # 'cookie': 'xid=7c88c162-4026-4c1a-b974-efb20440e127; enableGrafanaFaro=false; niche_cookieConsent=true; experiments=da_profile_cta%7Ccontrol%5E%5E%5E%240%7C1%5D; _pxhd=OSthpX9mz5g8nA7LalrPeBAhojMYWQDOBmwrp5aXl1uCSv49-O5ni3wPhxcMqHF5FkmmjXU9BW2KrevU6IKM2Q==:nHOG9mTrM6EOGFpcHkTX51j2DQT6w6rPa27ZygHs/modHkznABMy42Zlaycbu069TATYAdj2lh4meq/OoLO8tYNaUfOVNg7tMWvW-gNA89c=; pxcts=bd55cdfd-2de2-11ef-b205-8091b698ae20; _pxvid=b9b0725c-2de2-11ef-8521-9eb394670314; _px3=0a8afa0b8f1138510fceac3e3e57688bb5f9a422ef291fc0eb5c8b6c12c4315a:TcrhypkcZIzACunfslW/HSA3IR0xtXkyEm8H8RKf+asI6TacEjGfXZkxWMEufFVGfISFR1oKy4CKjkMHKxdd3A==:1000:SLWGUJlNx0oOFoeMbn832FME3BGebdOdWwQ9e1uWTgkBtPshBiklruLe6J4b6fB6sAL10oFDXHk6JD+rGc3xuVLElaAL5i9oFs+NnXS2sOy1NI4PCURw+JiiItIKd6W7I64aC/3KK17j9YrDusCJEY6RwVcc3qW1YN5LaGqQyyuHq/i6BFtna7o6yxvuhskMIyei3OrH2eqmaOViwHSUtfz452ByjQ4GIrZm6i8LePY=; navigation=%7B%22location%22%3A%7B%22guid%22%3A%22e08f5e71-b74a-4e28-ac28-8b4569dd5eef%22%2C%22type%22%3A%22State%22%2C%22name%22%3A%22Massachusetts%22%2C%22url%22%3A%22massachusetts%22%7D%2C%22navigationMode%22%3A%22full%22%2C%22vertical%22%3A%22colleges%22%2C%22mostRecentVertical%22%3A%22colleges%22%2C%22suffixes%22%3A%7B%22colleges%22%3A%22%2Fs%2Fmassachusetts%2F%22%2C%22graduate-schools%22%3A%22%2Fs%2Fmassachusetts%2F%22%2C%22k12%22%3A%22%2Fs%2Fmassachusetts%2F%22%2C%22places-to-live%22%3A%22%2Fs%2Fmassachusetts%2F%22%2C%22places-to-work%22%3A%22%2Fs%2Fmassachusetts%2F%22%7D%7D; recentlyViewed=entityHistory%7CentityName%7CHarvard%2BUniversity%7CentityGuid%7C2beca607-a07e-40a3-b6ae-c23b64decb5d%7CentityType%7CCollege%7CentityFragment%7Charvard-university%7CUniversity%2Bof%2BCalifornia%2B-%2BIrvine%7Cf6ebcd8a-6bf5-4c9a-bd92-bc675ff35532%7Cuniversity-of-california-irvine%7CHarvard%2BUniversity%7Cb511658d-95d9-4684-89c9-eabf96289df0%7CGradSchool%7CsearchHistory%7CMassachusetts%7Ce08f5e71-b74a-4e28-ac28-8b4569dd5eef%7CState%7Cmassachusetts%7CCalifornia%7Cb56d7c2d-d07e-4aa2-bcf6-925ecb0890f6%7Ccalifornia%7CBoston%2BArea%7C1fb5f13a-6673-4bc7-a0c2-fcb7e56d7831%7CMetroArea%7Cboston-metro-area%5E%5E%5E%240%7C%40%241%7C2%7C3%7C4%7C5%7C6%7C7%7C8%5D%7C%241%7C9%7C3%7CA%7C5%7C6%7C7%7CB%5D%7C%241%7CC%7C3%7CD%7C5%7CE%7C7%7C8%5D%5D%5D%7CF%7C%40%241%7CG%7C3%7CH%7C5%7CI%7C7%7CJ%5D%7C%241%7CK%7C3%7CL%7C5%7CI%7C7%7CM%5D%7C%241%7CN%7C3%7CO%7C5%7CP%7C7%7CQ%5D%5D%5D',
        'priority': 'u=1, i',
        'referer': 'https://www.niche.com/colleges/harvard-university/reviews/',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception('Could not get response')
    for i in response.json().get('reviews'):
        # print(i)
        # i.pop('categories', None)
        i.pop('guid', None)
        reviews.append(i)
    return reviews


def main():
    data = run()
    with open(f'{UNIVERSITY} Niche.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)


if __name__ == '__main__':
    main()
