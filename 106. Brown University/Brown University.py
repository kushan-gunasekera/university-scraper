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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://cab.brown.edu'
UNIVERSITY = 'Brown University'


def get_terms():
    r = requests.get(f'{MAIN_DOMAIN}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('select', id='crit-srcdb').find_all('option')

    courses = []
    course_tags.reverse()
    for tag in course_tags:
        url = tag.get('value')
        courses.append(url)

    return list(set(courses))


def get_description_n_professors(code, crn, srcdb):
    print(f'get_description --> {code} | {crn} | {srcdb}')
    data = {
        "group": f"code:{code}",
        "key": f"crn:{crn}",
        "srcdb": f"{srcdb}",
        "matched": f"crn:{crn}"
    }
    r = requests.post(
        f'{MAIN_DOMAIN}/api/?page=fose&route=details',
        headers=HEADERS,
        data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':')))
    )
    results = r.json()
    description = ''
    course_professor = ''
    if results:
        description = results.get('description')
        professors = results.get('instructordetail_html')
        soup = BeautifulSoup(professors, 'html.parser')
        instructor_name_tag = soup.find('div', class_='instructor-name')
        if instructor_name_tag:
            instructor_name_a_tags = instructor_name_tag.find_all('a') or []
            for i in instructor_name_a_tags:
                i.get_text()
            course_professor = ', '.join(i.get_text() for i in instructor_name_a_tags)
    return code, description, course_professor


def get_course(term):
    print(term)
    data = {"other":{"srcdb":term},"criteria":[{"field":"is_ind_study","value":"N"},{"field":"is_canc","value":"N"}]}
    r = requests.post(
        f'{MAIN_DOMAIN}/api/?page=fose&route=search&is_ind_study=N&is_canc=N',
        headers=HEADERS,
        data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':')))
    )
    courses = {}
    results = r.json().get('results', [])
    if not results:
        print(f'No results | {term}')
        return courses

    print(f'results: {len(results)} | {term}')
    meta_data = []
    for result in results:
        courses[result['code']] = {
            'course_code': result['code'],
            'course_name': result['title'],
            'course_description': None,
            'course_professor': None,
        }
        meta_data.append([
            result['code'], result['crn'], result['srcdb']
        ])

    print(f'{len(courses)} courses in {term}')
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_description_n_professors, code, crn, srcdb) for code, crn, srcdb in meta_data):
            code, description, course_professor = i.result()
            courses[code]['course_description'] = description
            courses[code]['course_professor'] = course_professor
    return courses


def main():
    # get_courses()
    # get_course('999999')
    terms = get_terms()
    full_courses = {}
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, term) for term in terms):
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
