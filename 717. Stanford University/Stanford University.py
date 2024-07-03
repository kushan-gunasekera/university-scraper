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
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://explorecourses.stanford.edu/'
UNIVERSITY = 'Stanford University'


def get_years():
    r = requests.get(f'{MAIN_DOMAIN}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    years_tags = soup.find('table', id='years').find_all('a')

    years = []
    for tag in years_tags:
        value = tag.get('href')
        if value and value != '#':
            years.append(value)
    years.append(MAIN_DOMAIN)
    return years


def get_subjects(url):
    print(f'subjects url: {url}')
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    subject_tags = soup.find('div', id='mainContent').find_all('a')

    subjects = []
    for tag in subject_tags:
        value = tag.get('href')
        if not value:
            continue
        parsed_url = urlparse(value)
        query_params = parse_qs(parsed_url.query)
        query_params.pop('filter-term-Summer', None)
        new_query_string = urlencode(query_params, doseq=True)
        new_url = urlunparse(parsed_url._replace(query=new_query_string))
        subjects.append(new_url)
    return subjects


def get_courses(url):
    print(f'courses url: {url}')
    MAIN_URL = f'{MAIN_DOMAIN}{url}'
    r = requests.get(MAIN_URL, headers=HEADERS)
    course_tags = []
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags_by_class = soup.find_all('div', class_='searchResult')
    course_tags_by_id = soup.find_all('div', id='searchResults')
    course_tags.extend(course_tags_by_class)
    course_tags.extend(course_tags_by_id)
    courses = {}
    if not course_tags:
        print(f'courses not found: {MAIN_URL}')
        return courses
    for tag in course_tags:
        code = tag.find('span', class_='courseNumber')
        title = tag.find('span', class_='courseTitle')
        if not (code and title):
            print(f'code: {code} | title: {title}')
            continue
        code = code.text.strip()
        if code.endswith(':'):
            code = code[:-1]
        title = title.text.strip()
        courses[code] = {
            'course_code': code,
            'course_name': title,
            'course_description': tag.find('div', class_='courseDescription').text.strip(),
        }
        try:
            courses[code]['course_professor'] = ', '.join(i.text.strip() for i in tag.find_all('a', class_='instructorLink'))
        except:
            pass
    return courses


def main():
    # get_courses('/search;jsessionid=xxcre33erej3qc364yofnhv7?view=catalog&academicYear=20192020&page=0&q=IIS&filter-departmentcode-IIS=on&filter-coursestatus-Active=on')
    years = get_years()
    full_courses = {}
    subjects = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_subjects, url) for url in years):
            subjects.extend(i.result())

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, url) for url in subjects):
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
