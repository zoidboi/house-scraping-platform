import scrapy
import json


class FundaScraper(scrapy.Spider):
    name = "Funda"
    funda_prefix = "https://www.funda.nl"

    def start_requests(self):
        urls = [
            # 'https://www.funda.nl/koop/heel-nederland/sorteer-datum-af/'
            'https://www.funda.nl/koop/maastricht/50000-200000/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        for ol in response.css('ol.search-results'):
            for li in ol.css('li.search-result'):
                url = self.funda_prefix + li.css('a[data-object-url-tracking="resultlist"]::attr(href)').get()
                listItem = {
                    'id': li.css(
                        'a[data-object-url-tracking="resultlist"]::attr(data-search-result-item-anchor)').get(),
                    'url': url,
                    'address': li.css('h2.search-result__header-title::text').get() + " " + li.css(
                        'h4.search-result__header-subtitle::text').get(),
                    'price': li.css('span.search-result-price::text').get(),
                    'realtor': li.css('span.search-result-makelaar-name::text').get(),
                    'realtor_url': self.funda_prefix + li.css('a.search-result-makelaar::attr(href)').get()
                }

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_detail_page,
                    meta={'item': listItem}
                )

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_detail_page(self, response):
        item = response.meta.get('item', {})
        item['building'] = {}

        for dt in response.css('dt'):
            dt_value = dt.css('::text').get()
            dt_value = dt_value.lstrip().rstrip()
            dd_value = dt.xpath('./following-sibling::dd/text()').get()

            if dd_value is not None:
                if dt_value == 'Bijdrage VvE':
                    item['vve_costs'] = dd_value
                elif dt_value == 'Aangeboden sinds':
                    item['since'] = dd_value
                elif dt_value == 'Vraagprijs per m²':
                    item['building']['price_per_m2'] = dd_value
                elif dt_value == 'Soort woonhuis':
                    item['building']['building_type'] = dd_value
                elif dt_value == 'Soort appartement':
                    item['building']['building_type'] = dd_value
                elif dt_value == 'Soort bouw':
                    item['building']['build_type'] = dd_value
                elif dt_value == 'Bouwjaar':
                    item['building']['build_year'] = dd_value
                elif dt_value == 'Specifiek':
                    item['building']['building_specific'] = dd_value
                elif dt_value == 'Soort dak':
                    item['building']['roof_type'] = dd_value
                elif dt_value == 'Wonen':
                    item['building']['living_m2'] = dd_value
                elif dt_value == 'Inhoud':
                    item['building']['total_m3'] = dd_value
                elif dt_value == 'Aantal kamers':
                    item['building']['rooms'] = dd_value
                elif dt_value == 'Aantal badkamers':
                    item['building']['bathrooms'] = dd_value
                elif dt_value == 'Badkamervoorzieningen':
                    item['building']['bathroom_appliances'] = dd_value
                elif dt_value == 'Aantal woonlagen':
                    item['building']['floors'] = dd_value
                elif dt_value == 'Gelegen op':
                    item['building']['located_on_floor'] = dd_value
                elif dt_value == 'Voorzieningen':
                    item['building']['appliances'] = dd_value
                elif dt_value == 'Ligging':
                    item['building_position'] = dd_value
                elif dt_value == 'Balkon/dakterras':
                    item['building']['balcony_terrace'] = dd_value
                elif dt_value == 'Soort parkeergelegenheid':
                    item['building']['parking'] = dd_value

        item['building']['energy_label'] = response.css('span.energielabel::text').get()
        item['images'] = response.css('img.media-viewer-item-content::attr(data-lazy)').getall()
        item['description'] = response.css('div[data-object-description-body]::text').get()

        marketing_url = response.css('div[data-object-market-insight]::attr(data-endpoint-url)').get()

        if marketing_url is not None:
            yield scrapy.Request(
                url=self.funda_prefix + marketing_url,
                callback=self.parse_marketing_endpoint,
                meta={'item': item}
            )
        else:
            yield item

    def parse_marketing_endpoint(self, response):
        item = response.meta.get('item', {})
        json_response = json.loads(response.text)

        if json_response['AverageAskingPriceNeighbourhood']:
            item['building']['average_neighborhood_price'] = json_response['AverageAskingPriceNeighbourhood']
        if json_response['AverageAskingPricePerM2Neighbourhood']:
            item['building']['average_neighborhood_price_per_m2'] = json_response['AverageAskingPricePerM2Neighbourhood']
        if json_response['AverageAskingPriceCity']:
            item['building']['average_city_price'] = json_response['AverageAskingPriceCity']
        if json_response['AverageAskingPricePerM2City']:
            item['building']['average_city_price_per_m2'] = json_response['AverageAskingPricePerM2City']
        if json_response['NumberOfSoldProperties']:
            item['building']['number_of_properties_sold'] = json_response['NumberOfSoldProperties']

        yield item