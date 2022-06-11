import scrapy
from scrapy.loader import ItemLoader
from college_scraper.items import CollegeItem
from bs4 import BeautifulSoup


class CollegeScraper(scrapy.Spider):
    name = 'college'

    def start_requests(self):
        url = 'https://www.collegedekho.com/get_institutes_ajax'
        i = 0
        while True:
            yield scrapy.FormRequest(url=url, callback=self.parse, method='POST', formdata={'page': str(i)})
            i += 1

    def parse(self, response):
        info_list = response.css('div.collegeinfo')
        if len(info_list) < 1:
            raise scrapy.exceptions.CloseSpider(reason='No More Data Found')

        for college in info_list:
            url = 'https://www.collegedekho.com/colleges/courses-' + college.xpath('div[2]/h2/a/@href').get().strip()[10:]
            yield scrapy.Request(url, callback=self.parse_college)

    def parse_college(self, response):
        # Xpath to details
        name = '//div[@class="CollegedekhoHeader_collegeDetails__A3JD3"]/div[2]/h1/text()'
        other = '//div[@class="CollegedekhoHeader_collegeDetailFlex__zJww2"]/ul[2]/'
        course_path = '//div[@class="collegeCourses_couresFeeBlock__Lwy__"]'
        course_data = self.course_parse(response.xpath(course_path).extract())

        loader = ItemLoader(item=CollegeItem(), response=response)
        loader.add_xpath('college_name', name)
        loader.add_xpath('location', other+'li[1]/span/text()[2]')
        loader.add_xpath('type', other+'li[2]/span/text()')
        loader.add_xpath('approved_by', other+'li[3]/span/text()[2]')
        loader.add_value('courses_offered', course_data)
        yield loader.load_item()

    def course_parse(self, data):
        details = {}
        for course in data:
            res = BeautifulSoup(course, 'html.parser')
            c_name = res.find('h3').text
            programs = res.find_all('div', 'collegeCourses_courseContainer__sulMm')

            prog_details = {}
            for program in programs:
                program_name = program.find('td', 'collegeCourses_courseNameData__0AKYo').text
                program_fee = program.find('td', 'collegeCourses_coursePriceData__MSoXb').text.replace('₹ ', '')
                try:
                    program_fee = int(program_fee)
                except ValueError:
                    program_fee = 0

                prog_details[program_name] = program_fee
            details[c_name] = prog_details
        return details
