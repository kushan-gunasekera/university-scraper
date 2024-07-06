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
MAIN_DOMAIN = 'https://dukehub.duke.edu'
UNIVERSITY = 'Duke University'


def get_courses(term):
    print(term)
    course_url = 'https://dukehub.duke.edu/psc/CSPRD01/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=DUKEU&term={term}&date_from=&date_thru=&subject=&subject_like=&catalog_nbr=&start_time_equals=&start_time_ge=&end_time_equals=&end_time_le=&days=&campus=&location=&x_acad_career=&acad_group=&rqmnt_designtn=&instruction_mode=&keyword=&class_nbr=&acad_org=&enrl_stat=O&crse_attr=&crse_attr_value=&instructor_name=&instr_first_name=&session_code=&units=&trigger_search=&page={page_number}'
    desc_url = 'https://dukehub.duke.edu/psc/CSPRD01/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassDetails?institution={institution}&term={term}&class_nbr={class_nbr}'
    courses = {}
    count = 1
    while True:
        print(f'term: {term} | count: {count}')
        r = requests.get(course_url.format(term=term, page_number=count), headers=HEADERS)
        data = r.json()
        if not data:
            break
        for i in data:
            code = f'{i.get("subject")} {i.get("catalog_nbr")}'
            title = i.get('descr')
            courses[code] = title
            institution = i.get('campus')
            termm = i.get('strm')
            class_nbr = i.get('class_nbr')
            print(f'institution: {institution} | termm: {termm} | class_nbr: {class_nbr}')
            r = requests.get(desc_url.format(institution=institution, term=termm, class_nbr=class_nbr), headers=HEADERS)
            desc_data = r.json()
            desc = desc_data.get('section_info', {}).get('catalog_descr', {}).get('crse_catalog_description')
            inscturators = [
                j.get('name')
                for j in i.get('instructors', [])
                if j.get('name') != '-'
            ]
            courses[code] = {
                'course_code': code,
                'course_name': title,
                'course_description': desc,
                'course_professor': ', '.join(inscturators),
            }
        count += 1
    return courses


def main():
    full_courses = {}
    terms = [
        1505, 1510, 1525, 1530, 1540, 1545, 1550, 1565, 1570, 1580, 1585,
        1590, 1605, 1610, 1620, 1625, 1630, 1645, 1650, 1660, 1665, 1670,
        1685, 1690, 1700, 1705, 1710, 1725, 1730, 1740, 1745, 1750, 1765,
        1770, 1780, 1785, 1790, 1805, 1810, 1820, 1825, 1830, 1845, 1850,
        1860, 1865, 1870, 1885, 1890, 1900
    ]

    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, term) for term in terms):
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
