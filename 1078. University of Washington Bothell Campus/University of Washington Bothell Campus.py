# Adelphi University
import json
import urllib.parse
from os import listdir
from os.path import isfile, join
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests
import xlsxwriter

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://course-app-api.planning.sis.uw.edu'
CAMPUS = 'bothell'
UNIVERSITY = 'University of Washington Bothell Campus'

json_path = "./json-data"
Path(json_path).mkdir(parents=True, exist_ok=True)
json_paths = [f for f in listdir(json_path) if isfile(join(json_path, f))]
ALL_CODES = {}
for path in json_paths:
    with open(f'{json_path}/{path}', 'r') as openfile:
        json_object = json.load(openfile)
        ALL_CODES[json_object['course_code']] = json_object


def get_programs():
    r = requests.get(f'{MAIN_DOMAIN}/api/subjectAreas/', headers=HEADERS)
    return [i.get('code') for i in r.json() if i.get('campus') == CAMPUS]


def get_course(code):
    # code = 'VIET'
    print(code)
    courses = {}
    HEADERS['Cookie'] = 'sessionId=7f150ca21e57d5ea4eb32b44a02cc1609286b0e61f532ea76d831ae116525d1d'
    HEADERS['X-Csrf-Token'] = '19ddef372687d19444bdc2625bad0b1fe7d2b668a25655c61d345cfd3feca61b57d6822c909cb192c4035ee347d638527dafcc604d1044518c8363d81a2346d438bd0109d0af78f51f27b3a6f2b213d2f141880a20fd8a2e74842d80ba76523e734bbc06edb9e5553696960efb89bd71fb01c9128e7ce504392d868c701648dd'
    data = {
        "username": "GUEST",
        "requestId": "cfbe1306-d198-4117-97ee-973ab4fb9692",
        "sectionSearch": False,
        "instructorSearch": False,
        "queryString": code,
        "consumerLevel": "UNDERGRADUATE",
        "campus": "seattle"
    }
    r = requests.post(f'{MAIN_DOMAIN}/api/courses/', headers=HEADERS, json=data)
    recourd_count = len(r.json())
    print(f'{code} has {recourd_count} rows')
    for count, i in enumerate(r.json(), 1):
        profs = []
        code = i.get('code')
        if code in ALL_CODES.keys():
            courses[code] = ALL_CODES[code]
            print(f'skip {code}')
            continue
        course_id = i.get('id').split(':')[0]
        desc_url = f'{MAIN_DOMAIN}/api/courses/{urllib.parse.quote(code)}/details?courseId={course_id}'

        print(f'[{count}/{recourd_count}] {code} - {desc_url}')
        res = requests.get(desc_url, headers=HEADERS)
        desc = res.json().get('courseSummaryDetails', {}).get('courseDescription')
        for j in res.json().get('courseOfferingInstitutionList', []):
            for k in j.get('courseOfferingTermList', []):
                for l in k.get('activityOfferingItemList', []):
                    inst = l.get('instructor')
                    if inst:
                        profs.append(inst)
        profs = list(set(profs))
        courses[code] = {
            'course_code': code,
            'course_name': i.get('title'),
            'course_description': desc,
            'course_professor': ', '.join(profs),
        }
        with open(f"json-data/{code}.json", "w") as outfile:
            json.dump(courses[code], outfile)
            ALL_CODES[code] = courses[code]

    return courses


def main():
    full_courses = {}
    programs = get_programs()
    # print(len(urls))

    # with ThreadPoolExecutor(max_workers=1) as executor:
    #     for i in as_completed(executor.submit(get_course, code) for code in programs):
    #         full_courses = {**full_courses, **i.result()}

    for code in programs:
        full_courses = {**full_courses, **get_course(code)}

    # full_courses = {**full_courses, **old_courses}
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
