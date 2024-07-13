# Adelphi University
import itertools
import re
import json
import math
import random
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests
import xlsxwriter
from bs4 import BeautifulSoup
from lxml import html

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://catalog.hillsdale.edu'
UNIVERSITY = 'Hillsdale College'


def get_courses():
    def get_data(response):
        data = None
        for i in response.json():
            if i.get('command') == 'insert' and i.get(
                    'method') == 'replaceWith':
                data = i.get('data')
                break
        return data

    def format_response(data):
        obj = {}
        soup = BeautifulSoup(data, 'html.parser')
        course_tags = soup.find_all('span', class_='field-content')
        for tag in course_tags:
            a_tags = tag.find_all('a')
            code = a_tags[0].text.replace('\n', '').strip()
            title = a_tags[1].text.replace('\n', '').strip()
            url = f'{MAIN_DOMAIN}{a_tags[0].get("href")}'
            print(f'{code} - {title} | {url}')

            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            desc = soup.find('div', 'field field--name-field-description field--type-text-long field--label-hidden field__item')
            if desc:
                desc = desc.text.strip().replace('\xa0', ' ')
            obj[code] = {
                'course_code': code,
                'course_name': title,
                'course_description': desc,
            }
        return obj

    # Base URL
    url = f'{MAIN_DOMAIN}/views/ajax'

    # Query parameters
    params = {
        '_wrapper_format': 'drupal_ajax',
        'view_name': 'courses',
        'view_display_id': 'page_1',
        'view_args': '',
        'view_path': '/courses',
        'view_base_path': 'courses',
        'view_dom_id': '692a231b2f8c69c17aee4173e094acdbf9e7c0b8b6908d82007d4e1405966693',
        'pager_element': '0',
        'page': '0',
        '_drupal_ajax': '1',
        'ajax_page_state[theme]': 'hillsdale',
        'ajax_page_state[theme_token]': '',
        'ajax_page_state[libraries]': 'eJxljuEOgjAMhF9oWuWFlrIVmXSroUXg7WVEDcY_zfW7a3ohNJfmCmFSk-xC8GGgmExGOGjPSc2rrUxaM7QYjQV542VQ-CM100kxjzOpZIK6vHX1HrHzJsIt7m8Oa3Wtp-3kI75ka5mpTK5PzBqRCW4sLfKp9krl5nRVowwtKrlnollhn2e84_IDssSJ6QVwaWDU'
    }

    # Headers
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,si;q=0.7',
        'cookie': 'OptanonConsent=isGpcEnabled=0&datestamp=Fri+Jul+12+2024+18%3A20%3A47+GMT%2B0530+(India+Standard+Time)&version=202310.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CBG16%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false',
        'priority': 'u=1, i',
        'referer': 'https://catalog.hillsdale.edu/courses',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    # Make the request
    response = requests.get(url, headers=headers, params=params)
    data = get_data(response)
    soup = BeautifulSoup(data, 'html.parser')
    total_pages = int(soup.find('li', 'pager__item pager__item--last').find('a').get('href').split('=')[-1]) + 1
    print(f'{0}/{total_pages}')

    courses = {**format_response(data)}
    for i in range(1, total_pages):
        print(f'{i}/{total_pages}')
        params['page'] = i
        response = requests.get(url, headers=headers, params=params)
        data = get_data(response)
        courses = {**courses, **format_response(data)}
    return courses


def main():
    full_courses = get_courses()

    with open(f'{UNIVERSITY}.json', 'w') as json_file:
        json.dump(full_courses, json_file, indent=4)

    header = ['course_code', 'course_name', 'course_description']
    workbook = xlsxwriter.Workbook(f'{UNIVERSITY}.xlsx')
    worksheet = workbook.add_worksheet()
    for col, header_name in enumerate(header):
        worksheet.write(0, col, header_name)

    row = 1
    for value in full_courses.values():
        worksheet.write(row, 0, value.get('course_code'))
        worksheet.write(row, 1, value.get('course_name'))
        worksheet.write(row, 2, value.get('course_description'))
        row += 1

    workbook.close()


if __name__ == '__main__':
    main()
