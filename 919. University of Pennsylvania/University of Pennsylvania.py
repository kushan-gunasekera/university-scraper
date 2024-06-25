import itertools
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests
import xlsxwriter
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://courses.upenn.edu'
UNIVERSITY = 'University of Pennsylvania'


def get_courses_n_modes():
    print('get_courses_n_modes')
    r = requests.get(f'{MAIN_DOMAIN}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')

    semester = []
    semester_tags = soup.find('select', id='crit-srcdb').find_all('option')
    for tag in semester_tags:
        url = tag.get('value')
        semester.append(url)

    modes = []
    mode_tags = soup.find('select', id='crit-instmode').find_all('option')
    for tag in mode_tags:
        url = tag.get('value')
        if url:
            modes.append(url)

    return list(set(semester)), list(set(modes))


def get_description_n_professors(code, crn, srcdb):
    print(f'get_description_n_professors --> {code} | {crn} | {srcdb}')
    description = None
    professor_list = []

    for i in crn:
        data = {
            "group": f"code:{code}",
            "key": f"crn:{i}",
            "srcdb": srcdb
        }
        r = requests.post(
            url=f'{MAIN_DOMAIN}/api/?page=fose&route=details',
            headers=HEADERS,
            data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':')))
        )
        results = r.json()
        professors_tags = results.get('instructordetail_html')
        soup = BeautifulSoup(professors_tags, 'html.parser')
        professors_tags = soup.find_all('div', class_='instructor-detail')
        if professors_tags:
            for professor_tag in professors_tags:
                professor_list.append(professor_tag.text.strip())

        if not description:
            description = results.get('description').strip()

    return code, description, ', '.join(professor_list)


def get_course(semester, mode):
    print(f'get_course --> {semester} | {mode}')
    data = {"other":{"srcdb":semester},"criteria":[{"field":"instmode","value":mode}]}
    r = requests.post(f'{MAIN_DOMAIN}/api/?page=fose&route=search&instmode={mode}', headers=HEADERS, data=urllib.parse.quote_plus(json.dumps(data, separators=(',', ':'))))
    courses = {}
    results = r.json().get('results', [])
    if not results:
        print(f'No results | {semester} | {mode}')
        return courses

    print(f'results: {len(results)} | {semester} | {mode}')
    desc_n_inst = {}
    srcdb_dict = {}
    for result in results:
        code = result['code']
        courses[code] = {
            'course_code': code,
            'course_name': result['title'],
        }
        srcdb_dict[code] = result['srcdb']
        if code not in desc_n_inst:
            desc_n_inst[code] = []
        desc_n_inst[code].append(result['crn'])

    print(f'{len(courses)} courses in {semester} | {mode}')
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in as_completed(executor.submit(get_description_n_professors, code, crn, srcdb_dict[code]) for code, crn in desc_n_inst.items()):
            code, description, course_professor = i.result()
            courses[code]['course_description'] = description
            courses[code]['course_professor'] = course_professor
    return courses


def main():
    semesters, modes = get_courses_n_modes()
    full_courses = {}
    with ThreadPoolExecutor(max_workers=1) as executor:
        for i in as_completed(executor.submit(get_course, semester, mode) for semester, mode in itertools.product(semesters, modes)):
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
