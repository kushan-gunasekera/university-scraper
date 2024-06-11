import json
import logging
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests
import xlsxwriter
from bs4 import BeautifulSoup

logging.basicConfig(format='[%(asctime)s] %(levelname)s:%(message)s [%(filename)s/%(funcName)s:%(lineno)d:%(threadName)s]\n', level=logging.INFO)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
MAIN_DOMAIN = 'https://catalogue.uci.edu'
UNIVERSITY = 'University of CA Irvine'


def get_courses():
    logging.info('getting urls')
    r = requests.get(f'{MAIN_DOMAIN}/allcourses/', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find('div', id='atozindex').find_all('a')

    courses = []
    for tag in course_tags:
        if not tag.get('href'):
            continue
        courses.append(tag['href'])
    logging.info(f'{len(courses)} urls found')
    return courses


def get_course(url):
    logging.info(f'loading {url}')
    r = requests.get(f'{MAIN_DOMAIN}{url}', headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    course_tags = soup.find_all('div', class_='courseblock')
    courses = {}
    if not course_tags:
        return courses

    for tag in course_tags:
        title_tag = tag.find('p', class_='courseblocktitle')
        if not title_tag:
            logging.error(f'no title found for {url}')
            break
        text = title_tag.text
        parts = text.split(".", 2)
        course_code = parts[0].strip().replace('\xa0', ' ')
        course_name = parts[1].strip().replace('\xa0', ' ')
        courses[course_code] = {
            'course_code': course_code,
            'course_name': course_name,
        }

        desc_div_tag = tag.find('div', class_='courseblockdesc')
        if not desc_div_tag:
            logging.warning(f'no courseblockdesc tag found for {url}')
            continue
        desc_p_tag = desc_div_tag.find('p')
        if not desc_p_tag:
            logging.warning(
                f'no p tag found in found for {course_code}|{course_name}'
            )
            continue
        course_description = desc_p_tag.text.strip().replace('\xa0', ' ')
        courses[course_code]['course_description'] = course_description

    logging.info(f'{len(courses)} courses found for {url}')
    return courses


def main():
    full_courses = {}
    urls = get_courses()

    with ThreadPoolExecutor(max_workers=50) as executor:
        for i in as_completed(executor.submit(get_course, url) for url in urls):
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
