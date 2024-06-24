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
import urllib.parse
import xmltodict

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://bulletin.columbia.edu'
UNIVERSITY = 'Columbia University'


def is_likely_name(input_string):
    words = input_string.split()
    return all(word.isalpha() for word in words)


def get_course(url):
    print(url)
    data = {"department":"","term":url,"level":"","held":"","begin":"","end":"","pl":"0","ph":"10","keywords":"","college":"CC"}
    criteria=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':')))
    r = requests.get(f'{MAIN_DOMAIN}/ribbit/index.cgi?page=shared-scopo-search.rjs&criteria={criteria}', headers=HEADERS)
    courses = {}
    for i in xmltodict.parse(r.content).get('results').get('result'):
        description_tag = i['description']
        soup = BeautifulSoup(description_tag, 'html.parser')

        description = ''
        description_tag = soup.find('p', class_='courseblockdesc')
        if description_tag:
            description = description_tag.get_text(strip=True)

        professor_tags = soup.find_all('td', class_='unifyRow1')
        professors = [i.text for i in professor_tags if is_likely_name(i.text)]
        courses[i['code']] = {
            'course_code': i['code'],
            'course_name': i['title'],
            'course_description': description,
            'course_professor': ', '.join(list(set(professors))),
        }
    return courses


def main():
    # get_courses()
    # get_course('999999')
    # course_urls = get_courses()
    course_urls = [1, 3]
    full_courses = {}
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, course_url) for course_url in course_urls):
            full_courses = {**full_courses, **i.result()}

    with open(f'{UNIVERSITY}.json', 'w') as json_file:
        json.dump(full_courses, json_file, indent=4)

    header = [
        'course_code', 'course_name', 'course_description', 'course_professor'
    ]
    workbook = xlsxwriter.Workbook(f'{UNIVERSITY}.xlsx')
    worksheet = workbook.add_worksheet()
    for col, header_name in enumerate(header):
        worksheet.write(0, col, header_name)

    row = 1
    for value in full_courses.values():
        worksheet.write(row, 0, value.get('course_code'))
        worksheet.write(row, 1, value.get('course_name'))
        worksheet.write(row, 2, value.get('course_description'))
        worksheet.write(row, 3, value.get('course_professor'))
        row += 1

    workbook.close()


if __name__ == '__main__':
    main()
