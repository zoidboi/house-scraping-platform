import scrapy
import re

class ParariusScraper(scrapy.Spider):
    name = 'Pararius'
    pararius_prefix = 'https://www.pararius.nl'

    def start_requests(self):
        urls = [
            'https://www.pararius.nl/koopwoningen/nederland'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        for list_item in response.css('li.search-list__item--listing'):
            url = list_item.css('a.listing-search-item__link--depiction::attr(href)').get()
            id_regex = re.search("/.*?/.*?/(.*?)/", url)

            if url is not None:
                realtor_div = response.css('div.listing-search-item__info')

                listItem = {
                    'id': id_regex.group(1),
                    'url': self.pararius_prefix + url,
                    'address': list_item.css('div.listing-search-item__location::text').get(),
                    'price': list_item.css('span.listing-search-item__price::text').get(),
                    'realtor_name': realtor_div.css('a.listing-search-item__link::text').get(),
                    'realtor_url': self.pararius_prefix + realtor_div.css('a.listing-search-item__link::attr(href)').get(),
                }

                yield scrapy.Request(
                    url=self.pararius_prefix + url,
                    callback=self.parse_detail_page,
                    meta={'item': listItem}
                )

        next_page = response.css('a.pagination__link--next::attr(href)').get()
        if next_page is not None:
            yield response.follow(self.pararius_prefix + next_page, self.parse)

    def parse_detail_page(self, response):
        item = response.meta.get('item', {})
        item['building'] = {}
        item['building']['images'] = {}
        for num, picture_div in enumerate(response.css('div.picture--media-carrousel')):
            item['building']['images'][str(num)] = picture_div.css('img.picture__image::attr(src)').get()

        offered_since_dd = response.css('dd.listing-features__description--offered_since')
        item['building']['since'] = offered_since_dd.css('span::text').get()

        status_dd = response.css('dd.listing-features__description--status')
        item['building']['status'] = status_dd.css('span::text').get()

        surface_dd = response.css('dd.listing-features__description--surface_area')
        item['building']['surface_area'] = surface_dd.css('span::text').get()

        volume_dd = response.css('dd.listing-features__description--volume')
        item['building']['volume'] = volume_dd.css('span::text').get()

        kvk_contribution_dd = response.css('dd.listing-features__description--monthly_contribution')
        item['building']['kvk_contribution'] = kvk_contribution_dd.css('span::text').get()

        kvk_reserve_funds_dd = response.css('dd.listing-features__description--reserve_fund')
        item['building']['kvk_reserve_funds'] = kvk_reserve_funds_dd.css('span::text').get()

        dwelling_type_dd = response.css('dd.listing-features__description--dwelling_type')
        item['building']['house_type'] = dwelling_type_dd.css('span::text').get()

        property_type_dd = response.css('dd.listing-features__description--property_types')
        item['building']['property_type'] = property_type_dd.css('span::text').get()

        construction_type_dd = response.css('dd.listing-features__description--construction_type')
        item['building']['construction_type'] = construction_type_dd.css('span::text').get()

        build_year_dd = response.css('dd.listing-features__description--construction_period')
        item['building']['construction_period'] = build_year_dd.css('span::text').get()

        number_of_rooms = response.css('dd.listing-features__description--number_of_rooms')
        item['building']['rooms'] = number_of_rooms.css('span::text').get()

        number_of_bedrooms = response.css('dd.listing-features__description--number_of_bedrooms')
        item['building']['bedrooms'] = number_of_bedrooms.css('span::text').get()

        number_of_bathrooms = response.css('dd.listing-features__description--number_of_bathrooms')
        item['building']['bathrooms'] = number_of_bathrooms.css('span::text').get()

        number_of_floors = response.css('dd.listing-features__description--number_of_floors')
        item['building']['floors'] = number_of_floors.css('span::text').get()

        facilities = response.css('dd.listing-features__description--facilities')
        item['building']['facilities'] = facilities.css('span::text').get()

        location = response.css('dd.listing-features__description--situations')
        item['building']['location'] = location.css('span::text').get()

        balcony = response.css('dd.listing-features__description--balcony')
        item['building']['balcony'] = balcony.css('span::text').get()

        garden = response.css('dd.listing-features__description--garden')
        item['building']['garden'] = garden.css('span::text').get()

        insulations = response.css('dd.listing-features__description--insulations')
        item['building']['insulations'] = insulations.css('span::text').get()

        heatings = response.css('dd.listing-features__description--heatings')
        item['building']['heatings'] = heatings.css('span::text').get()

        water_heatings = response.css('dd.listing-features__description--water_heatings')
        item['building']['water_heatings'] = water_heatings.css('span::text').get()

        boiler = response.css('dd.listing-features__description--heating_boiler')
        item['building']['boiler'] = boiler.css('span::text').get()

        storage = response.css('dd.listing-features__description--storage')
        item['building']['storage'] = storage.css('span::text').get()

        storage_description = response.css('dd.listing-features__description--description')
        item['building']['storage_description'] = storage_description.css('span::text').get()

        parking = response.css('dd.listing-features__description--parking')
        item['building']['parking'] = parking.css('span::text').get()

        garage = response.css('dd.listing-features__description--available')
        item['building']['has_garage'] = garage.css('span::text').get()

        return item
