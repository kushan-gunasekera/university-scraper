import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import as_completed

import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
UNIVERSITY = 'University of CA Los Angeles (UCLA)'
URL = 'https://www.ratemycourses.io'
BUILD_ID = 'fG4JZWmRlzqXURCUGqzz1'
NAME = 'ucla'


def get_final_data(obj):
    course_id = obj.get('id')
    number_of_reviews = obj.get('numberOfReviews')
    course = {
        'code': obj.get('code'),
        'name': obj.get('name'),
        'overall': obj.get('overallRating'),
        'easiness': obj.get('easyRating'),
        'interest': obj.get('interestingRating'),
        'usefulness': obj.get('usefulRating'),
        'review_count': number_of_reviews,
        'reviews': [],
    }
    if not number_of_reviews:
        return course

    reviews = []
    response = requests.get(f'{URL}/_next/data/{BUILD_ID}/{NAME}/course/{course_id}.json?uni={NAME}&id={course_id}', headers=HEADERS)
    for review in response.json().get('pageProps').get('course').get('reviews'):
        reviews.append(review)
    course['reviews'] = reviews
    return course


def get_courses():
    response = requests.get(f'{URL}/_next/data/{BUILD_ID}/{NAME}.json?uni={NAME}', headers=HEADERS)
    return response.json().get('pageProps').get('initialCourses')


def main():
    courses = []
    courses_obj = get_courses()
    with ThreadPoolExecutor(max_workers=50) as executor:
        for i in as_completed(executor.submit(get_final_data, course) for course in courses_obj):
            courses.append(i.result())

    with open(f'{UNIVERSITY} RateMyCourses.json', 'w') as json_file:
        json.dump(courses, json_file, indent=4)


if __name__ == '__main__':
    main()
