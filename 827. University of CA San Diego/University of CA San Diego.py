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
MAIN_DOMAIN = 'https://catalog.ucsd.edu'


def get_courses():
    r = requests.get(f'{MAIN_DOMAIN}/front/courses.html', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find_all('a')

    courses = []
    for tag in course_tags:
        url = tag.get('href')
        if not (url and url.startswith('../courses')):
            continue
        courses.append(url)

    return courses


def get_course(url):
    r = requests.get(f'{MAIN_DOMAIN}{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    descriptions_tags = soup.find_all('p', class_='course-descriptions')
    descriptions = [tag.text for tag in descriptions_tags]

    course_tags = soup.find_all('p', class_='course-name')
    courses = {}
    if not course_tags:
        return courses

    text = None
    try:
        for tag in course_tags:
            text = tag.text
            parts = text.split(".", 1)
            if len(parts) != 2:
                parts = text.split(":", 1)

            course_code = parts[0].strip()
            course_name = parts[1].strip()
            courses[course_code] = {
                'course_code': course_code,
                'course_name': course_name,
            }
    except Exception as e:
        print(url)
        print(text)
        print(e)
        print()

    for count, code in enumerate(courses):
        try:
            courses[code]['course_description'] = descriptions[count]
        except Exception as error:
            print(f'{error} | {url}')

    return courses


def main():
    course_urls = get_courses()
    full_courses = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, course_url[2:]) for course_url in course_urls):
            full_courses = {**full_courses, **i.result()}

    with open('University of CA San Diego.json', 'w') as json_file:
        json.dump(full_courses, json_file, indent=4)

    header = ['course_code', 'course_name', 'course_description']
    workbook = xlsxwriter.Workbook('University of CA San Diego.xlsx')
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
