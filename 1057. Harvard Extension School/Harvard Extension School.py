import json
import logging
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests
import xlsxwriter

logging.basicConfig(format='[%(asctime)s] %(levelname)s:%(message)s [%(filename)s/%(funcName)s:%(lineno)d:%(threadName)s]\n', level=logging.INFO)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://courses.dce.harvard.edu'
UNIVERSITY = 'Harvard Extension School'


def get_terms_and_schools():
    courses = (
        (202403, 'summer_school_adult_and_college'),
        (202403, 'summer_school_harvard_college'),
        (202403, 'summer_school_pre_college_program'),
        (202403, 'summer_school_secondary_school_program'),
        (202403, ''),
        (202402, ''),
        (202401, ''),
        (999924, ''),
    )

    return courses


def get_course(term, school):
    logging.info(f'getting courses for {school} on {term} term')
    data = {'other': {'srcdb': term}, 'criteria': []}
    if school:
        data['criteria'] = [{'field': school, 'value': 'Y'}]
    url = f'{MAIN_DOMAIN}/api/?page=fose&route=search&{school}=Y'
    separator = (',', ':')
    final_data = urllib.parse.quote_plus(json.dumps(data, separators=separator))
    r = requests.post(url, headers=HEADERS, data=final_data)

    courses = {}
    results = r.json().get('results', [])
    if not results:
        logging.info(f'No results | {term} | {school}')
        return courses

    logging.info(f'results: {len(results)} | {term} | {school}')
    for result in results:
        courses[result['custom_code']] = {
            'course_code': result['custom_code'].strip().replace('\xa0', ' '),
            'course_name': result['title'].strip().replace('\xa0', ' '),
        }
        data = {
            'group': f'custom_code:{result["custom_code"]}',
            'key': f'crn:{result["crn"]}',
            'matched': f'crn:{result["crn"]}',
            'srcdb': result["srcdb"],
        }
        url = f'{MAIN_DOMAIN}/api/?page=fose&route=details'
        final_data = urllib.parse.quote_plus(
            json.dumps(data, separators=separator)
        )
        r = requests.post(url, headers=HEADERS, data=final_data)
        description = r.json().get('description', '').strip().replace('\xa0', ' ')
        # instructures = r.json().get('allInGroup', [])
        courses[result['custom_code']]['course_description'] = description
        courses[result['custom_code']]['course_professor'] = result.get('instr')

    logging.info(f'{len(courses)} courses in {term} | {school}')
    return courses


def main():
    full_courses = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        for i in as_completed(executor.submit(get_course, term, school) for term, school in get_terms_and_schools()):
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
