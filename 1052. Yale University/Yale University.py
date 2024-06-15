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
MAIN_DOMAIN = 'https://courses.yale.edu'
UNIVERSITY = 'Yale University'
COMPLETED_COURSES = []

try:
    with open('completed_courses.txt', 'r') as file:
        content = file.read()
        for i in content.splitlines():
            COMPLETED_COURSES.append(i)
except FileNotFoundError:
    print("The file 'completed_courses.txt' does not exist. Skipping processing.")


def get_courses():
    r = requests.get(f'{MAIN_DOMAIN}/?srcdb=201602&stat=A', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('select', id='crit-srcdb').find_all('option')

    courses = []
    for tag in course_tags:
        url = tag.get('value')
        courses.append(url)

    return list(set(courses))


def get_description(srcdb, result):
    try:
        course = {
            result['code']: {
                'course_code': result['code'],
                'course_name': result['title']
            }
        }
        linked_crns = result.get('linked_crns')
        srcdb_ = result.get('srcdb')
        crn = result.get('crn')
        code = result.get('code')
        data = {"group": f"code:{code}", "key": f"crn:{crn}", "srcdb": srcdb_, "matched": f"crn:{linked_crns}"}
        r = requests.post(f'{MAIN_DOMAIN}/api/?page=fose&route=details', headers=HEADERS, data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':'))))
        course[result['code']]['course_description'] = r.json().get('description')
        course[result['code']]['course_professor'] = result.get('instr')
        return f'{srcdb}|{result["code"]}', course
    except Exception as e:
        print(f'Error: {e}')
        return None, None


def get_course(srcdb):
    print(srcdb)
    data = {"other":{"srcdb":srcdb},"criteria":[{"field":"stat","value":"A"}]}
    HEADERS['Referer'] = f'{MAIN_DOMAIN}/?srcdb={srcdb}&stat=A'
    r = requests.post(f'{MAIN_DOMAIN}/api/?page=fose&route=search&stat=A', headers=HEADERS, data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':'))))
    courses = {}
    results = r.json().get('results', [])
    if not results:
        print(f'No results | {srcdb}')
        return courses

    print(f'results: {len(results)} | {srcdb}')
    final_results = {}
    for result in results:
        if f'{srcdb}|{result["code"]}' not in COMPLETED_COURSES:
            final_results[result['code']] = result

    print(f'final results: {len(final_results)} | {srcdb}')
    files_keys = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_description, srcdb, result) for result in final_results.values()):
            file_key, desc_details = i.result()
            if file_key and desc_details:
                files_keys.append(file_key)
                courses = {**courses, **desc_details}

    with open('completed_courses.txt', 'a') as file:
        for file_key in files_keys:
            file.write(f'{file_key}\n')

    print(f'{len(courses)} courses in {srcdb}\n')
    return courses


def main():
    # get_course('202401')
    full_courses = {}
    course_srcdb = get_courses()
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, srcdb) for srcdb in course_srcdb):
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