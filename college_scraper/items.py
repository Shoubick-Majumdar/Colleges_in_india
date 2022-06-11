# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader.processors import TakeFirst, MapCompose


def name_correction(name):
    name = name.replace('Courses & Fees Structure', '').replace('2022', '')
    name = name.replace('21', '').replace('22', '').strip()
    return name

class CollegeItem(Item):
    college_name = Field(
        input_processor=MapCompose(name_correction),
        output_processor=TakeFirst()
    )
    location = Field(output_processor=TakeFirst())
    type = Field(output_processor=TakeFirst())
    approved_by = Field(output_processor=TakeFirst())
    courses_offered = Field()
