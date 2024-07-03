# Adelphi University
import itertools
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
MAIN_DOMAIN = 'https://www.amherst.edu'
UNIVERSITY = 'Amherst College'


def get_course(department_path, semester):
    full_url = f'{MAIN_DOMAIN}{department_path}/{semester}'
    print(full_url)
    r = requests.get(full_url, headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    data = {}
    for i in soup.find_all('div', 'coursehead'):
        h3_tag = i.find('h3')
        if not h3_tag:
            print(f'no h3_tag --> department_path: {department_path} | semester: {semester}')
            continue
        h3_text = h3_tag.text
        if not h3_text:
            print(f'no h3_text --> department_path: {department_path} | semester: {semester}')
            continue
        h3_split = h3_text.strip().split(' ', 1)
        if len(h3_split) != 2:
            print(f'no h3_split --> department_path: {department_path} | semester: {semester}')
            continue

        course_code, course_name = h3_split
        # data[f'{semester}|{course_code}'] = course_name
        # data[course_code] = course_name
        data[course_code] = {
            'course_code': course_code,
            'course_name': course_name,
        }

        course_url = h3_tag.find('a')
        profs = []
        if course_url:
            full_url = f'{MAIN_DOMAIN}{course_url.get("href")}'
            req = requests.get(full_url, headers=HEADERS)
            soup_res = BeautifulSoup(req.content, 'html.parser')
            description_h4 = soup_res.find('h4', string='Description')
            if description_h4:
                # Find the next p tag after the h4 tag
                description_p = description_h4.find_next('p').text
                data[course_code]['course_description'] = description_p
                a_tags = soup_res.find_all('a')

                for k in a_tags:
                    if k.get('href') and k.get('href').startswith('/people') and k.text not in ['Main Contacts', 'Contact Us']:
                        profs.append(k.text)
        else:
            for j in i.find_all('a'):
                if j.get('href') and j.get('href').startswith('/people') and j.text not in ['Main Contacts', 'Contact Us']:
                    profs.append(j.text)
        data[course_code]['course_professor'] = ', '.join(profs)


    return data


def get_departments_and_semesters():
    data = {}
    # print(f'page_number: {page_number}')

    r = requests.get(f'{MAIN_DOMAIN}/academiclife/departments/anthropology_sociology/courses', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    department_select = soup.find('select', id='curriculum-department')
    options = department_select.find_all('option')
    department_names_and_values = [option['value'] for option in options]

    semester_select = soup.find('select', id='curriculum-termid')
    options = semester_select.find_all('option')
    semester_values = [option['value'] for option in options]

    return list(itertools.product(department_names_and_values, semester_values))


def main():
    # get_course('/academiclife/departments/american_studies/courses', '2122S')
    full_courses = {}
    departments_and_semester = get_departments_and_semesters()
    print(f'all combinations: {len(departments_and_semester)}')

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, *details) for details in departments_and_semester):
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
