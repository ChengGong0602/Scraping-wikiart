import scrapy
from scrapy import Request 
from scrapy.loader import ItemLoader
from image_downloader.items import ImageDownloaderItem
import chompjs
from math import ceil

class WikiartSpider(scrapy.Spider):
    name = 'wikiart'
    allowed_domains = ['wikiart.org']
    start_urls = ['https://www.wikiart.org/en/paintings-by-style/minimalism?select=featured#!#filterName:featured,viewType:masonry']

    def __init__(self):
        self.url_template = 'https://www.wikiart.org/en/paintings-by-style/minimalism?select=featured&json=2&layout=new&page={}&resultType=masonry'

    def parse(self, response):
        initial_data = response.xpath('//div[@class="artworks-by-dictionary"]/@ng-init').get()
        data_object = chompjs.parse_js_object(initial_data, json_params={'strict': False})
        total_images = data_object['initialPortion']['itemsCount']
        for page_id in range(1,self.get_total_pages(total_images) + 1):
            yield Request(
                self.url_template.format(page_id),
                callback=self.parse_images,
                dont_filter=True
            )
    
    def parse_images(self,response):
        loader = ItemLoader(ImageDownloaderItem(),response)
        loader.add_value('image_urls',[painting['image'] for painting in response.json()["Paintings"]])
        yield loader.load_item()




    def get_total_pages(self,total_images):
        return ceil(total_images/60)