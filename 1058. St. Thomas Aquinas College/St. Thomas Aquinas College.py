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
MAIN_DOMAIN = 'https://stacssb.stac.edu:4443'
UNIVERSITY = 'St. Thomas Aquinas College'


def get_terms():
    # print(f'page_number: {page_number}')
    r = requests.get(f'{MAIN_DOMAIN}/PROD/bwckschd.p_disp_dyn_sched', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('td', class_='dedefault').find_all('option')

    terms = []
    for tag in course_tags:
        value = tag.get('value')
        if not value:
            continue
        terms.append(value)
    return terms


def get_subjects(term):
    print(f'get_subjects: {term}')
    data = {'p_calling_proc': 'bwckschd.p_disp_dyn_sched', 'p_term': term}
    r = requests.post(f'{MAIN_DOMAIN}/PROD/bwckgens.p_proc_term_date', headers=HEADERS, data=data)
    soup = BeautifulSoup(r.content, 'html.parser')
    subject_tags = soup.find('td', class_='dedefault').find_all('option')

    subjects = []
    for tag in subject_tags:
        value = tag.get('value')
        if not value:
            continue
        subjects.append(value)
    return itertools.product([term], subjects)


def get_courses(term, subject):
    HEADERS['Content-Type'] = 'application/x-www-form-urlencoded'
    print(f'{term} | {subject}')
    courses = {}
    data = {
        'term_in': term,
        'sel_subj': subject,
        'sel_day': 'dummy',
        'sel_schd': '%',
        'sel_insm': '%',
        'sel_camp': '%',
        'sel_levl': 'dummy',
        'sel_sess': 'dummy',
        'sel_instr': '%',
        'sel_ptrm': '%',
        'sel_attr': '%',
        'sel_crse': '',
        'sel_title': '',
        'sel_from_cred': '',
        'sel_to_cred': '',
        'begin_hh': '0',
        'begin_mi': '0',
        'begin_ap': 'a',
        'end_hh': '0',
        'end_mi': '0',
        'end_ap': 'a'
    }
    try:
        data = urllib.parse.quote_plus(json.dumps(data, separators=(',', ':')))
        files = {
            'term_in': (None, term),
            'sel_subj': (None, subject),
            'sel_day': (None, 'dummy'),
            'sel_schd': (None, '%'),
            'sel_insm': (None, '%'),
            'sel_camp': (None, '%'),
            'sel_levl': (None, 'dummy'),
            'sel_sess': (None, 'dummy'),
            'sel_instr': (None, '%'),
            'sel_ptrm': (None, '%'),
            'sel_attr': (None, '%'),
            'sel_crse': (None, ''),
            'sel_title': (None, ''),
            'sel_from_cred': (None, ''),
            'sel_to_cred': (None, ''),
            'begin_hh': (None, '0'),
            'begin_mi': (None, '0'),
            'begin_ap': (None, 'a'),
            'end_hh': (None, '0'),
            'end_mi': (None, '0'),
            'end_ap': (None, 'a')
        }
        data = f'term_in={term}&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj={subject}&sel_crse=&sel_title=&sel_insm=%25&sel_from_cred=&sel_to_cred=&sel_camp=%25&sel_ptrm=%25&sel_instr=%25&sel_attr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a'
        r = requests.post(f'{MAIN_DOMAIN}/PROD/bwckschd.p_get_crse_unsec', headers=HEADERS, data=data)
        # r = requests.post(f'{MAIN_DOMAIN}/PROD/bwckschd.p_get_crse_unsec', headers=HEADERS, files=files)
        soup = BeautifulSoup(r.content, 'html.parser')
        course_tags = soup.find_all('th', class_='ddtitle')

        if not course_tags:
            print(f'course_tags not found for {term} | {subject}')
            return courses

        for course_tag in course_tags:
            a_tag = course_tag.find('a')
            if not a_tag:
                print(f'a_tag not found for {term} | {subject}')
                continue
            split_items = a_tag.text.strip().split('-', 2)
            if not len(split_items) >= 3:
                print(f'split_items not found for {term} | {subject} | {a_tag.text}')
                continue
            title, _, code = split_items
            description_row = course_tag.find_parent('tr').find_next_sibling('tr')
            first_sentence = ''
            if description_row:
                description = description_row.find('td', class_='dddefault').text.strip()
                # Extract the first sentence of the description
                first_sentence = re.split(r'(?<=[.!?])\s+', description)[0]
            # courses[code.strip()] = title.strip()
            courses[code.strip()] = {
                'course_code': code.strip(),
                'course_name': title.strip(),
                'course_description': first_sentence,
            }
    except Exception as e:
        print(f'error {term} | {subject}')

    return courses


def main():
    # get_terms()
    # get_course('999999')
    # course_urls = get_courses()
    full_courses = {}
    terms_n_subjects = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_subjects, term) for term in get_terms()):
            terms_n_subjects.extend(i.result())
            # for x in i.result():
            #     terms_n_subjects.extend(x)
    # print(terms_n_subjects)
    # print(terms_n_subjects[0])
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_courses, term, subject) for term, subject in terms_n_subjects):
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
