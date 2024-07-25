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
MAIN_DOMAIN_1 = 'https://catalog.muhlenberg.edu/content.php?catoid=12&catoid=12&navoid=244&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1&filter%5B3%5D=1&filter%5Bcpage%5D={page_number}#acalog_template_course_filter'
UNIVERSITY = 'Muhlenberg College'


def get_courses(domain, page_number):
    print(f'page_number: {page_number}')
    course_url = domain.format(page_number=page_number)
    r = requests.get(course_url, headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('table', class_='table_default').find_all('a')

    courses = {}
    for tag in course_tags:
        if not str(tag.get('href')).startswith('preview_course_nopop.php?'):
            continue
        text = tag.text.strip().replace('\xa0', ' ')
        tag_split = text.split(' - ', 1)
        if len(tag_split) == 2:
            code = tag_split[0]
            title = tag_split[1]
            desc = None
            url = f'http://catalog.muhlenberg.edu/{tag.get("href")}'
            print(f'description: {code} - {title} | {url} ')
            res = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(res.content, 'html.parser')
            desc_list = []
            try:
                for i in soup.find('h1', id='course_preview_title').next_siblings:
                    if not i.name and i:
                        # desc += str(i.text)
                        _text = i.text.strip()
                        if _text:
                            desc_list.append(i.text.strip())
                desc = ' '.join(desc_list).strip()
            except Exception as error:
                print(f'ERROR: {course_url} | {code} - {title}')
            courses[code] = {
                'course_code': code,
                'course_name': title,
                'course_description': desc,
            }
    return courses


def main():
    # get_courses(5)
    # for page_number in range(1, 52):
    #     get_courses(page_number)
    full_courses = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_courses, MAIN_DOMAIN_1, page_number) for page_number in range(1, 14)):
            full_courses = {**full_courses, **i.result()}

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