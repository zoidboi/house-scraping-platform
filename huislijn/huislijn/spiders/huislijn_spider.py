import scrapy
import re


class HuislijnScraper(scrapy.Spider):
    name = "Huislijn"
    huislijn_prefix = 'https://www.huislijn.nl'

    def start_requests(self):
        urls = [
            'https://www.huislijn.nl/koopwoning/nederland?order=created%20desc'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        for object in response.css('div.object-panel'):
            url = object.css('a:nth-child(1)::attr(href)').get()
            id_regex = re.search("/(\d+)/", url)

            if url is not None:
                listItem = {
                    'id': id_regex.group(1),
                    'url': self.huislijn_prefix + url,
                    'address': object.css('h2.object-street::text').get() + " " + object.css(
                        'h3.object-location::text').get(),
                    'price': object.css('div.object-price::text').get(),
                }

                yield scrapy.Request(
                    url=self.huislijn_prefix + url,
                    callback=self.parse_detail_page,
                    meta={'item': listItem}
                )

        bottom_navigation = response.css('hl-pagination')
        next_page = bottom_navigation.css('a[rel="next"]::attr(href)').get()

        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_detail_page(self, response):
        item = response.meta.get('item', {})
        item['building'] = {}

        image_div = response.css('div.media-slots')
        item['building']['images'] = image_div.css('img::attr(src)').getall()

        seller_div = response.css('div.object-sections-makelaar')

        realtor_name = seller_div.css('h3::text').get()
        if realtor_name is None:
            broker_logo_div = seller_div.css('div.broker-logo')
            if broker_logo_div is not None:
                realtor_name = broker_logo_div.css('img::attr(alt)').get()  # realtor name fallback

        item['realtor_name'] = realtor_name

        realtor_url = seller_div.css('a.text-success::attr(href)').get()
        if realtor_url is not None:
            id_regex = re.search("/(\d+)", realtor_url)
            item['realtor_id'] = id_regex.group(1)
            item['realtor_url'] = self.huislijn_prefix + realtor_url

        characteristics = response.css('table.kenmerken')

        for tr in characteristics.xpath('./tbody//tr'):
            property = tr.css('td.property-name')
            property_name = property.css('td.property-name::text').get()
            property_value = property.xpath('./following-sibling::td/text()').get()

            if property_name is not None:
                property_name = property_name.strip()
                if property_name == 'Soort woning':
                    item['building']['house_type'] = property_value
                elif property_name == 'Bouwjaar':
                    item['building']['build_year'] = property_value
                elif property_name == 'Aantal kamers':
                    item['building']['rooms'] = property_value
                elif property_name == 'Woon oppervlakte':
                    item['building']['living_area'] = property_value
                elif property_name == 'Inhoud woonhuis':
                    item['building']['volume'] = property_value
                elif property_name == 'Aantal verdiepingen':
                    item['building']['number_of_floors'] = property_value
                elif property_name == 'Vloer isolatie':
                    item['building']['floor_isolation'] = property_value
                elif property_name == 'Tuin':
                    item['building']['garden'] = property_value
                elif property_name == 'Garage':
                    item['building']['garage'] = property_value
                elif property_name == 'CV ketel':
                    item['building']['boiler'] = property_value
                elif property_name == 'Dak type':
                    item['building']['roof_type'] = property_value
                elif property_name == 'Tuin patio':
                    item['building']['garden_patio'] = property_value
                elif property_name == 'Hellend dak':
                    item['building']['pitched_roof'] = property_value
                elif property_name == 'Perceel oppervlakte':
                    item['building']['plot_area'] = property_value
                elif property_name == 'CV ketel combi':
                    item['building']['boiler_combination'] = property_value
                elif property_name == 'CV ketel water':
                    item['building']['boiler_water'] = property_value
                elif property_name == 'Glas isolatie':
                    item['building']['glass_isolation'] = property_value
                elif property_name == 'Muur isolatie':
                    item['building']['wall_isolation'] = property_value
                elif property_name == 'Garage inpandig':
                    item['building']['indoor_garage'] = property_value
                elif property_name == 'CV ketel eigendom':
                    item['building']['owns_boiler'] = property_value
                elif property_name == 'Kwaliteit object':
                    item['building']['quality_object'] = property_value
                elif property_name == 'Kabel aansluiting':
                    item['building']['cable_connection'] = property_value
                elif property_name == 'Aantal slaapkamers':
                    item['building']['bedrooms'] = property_value
                elif property_name == 'Onderhoud binnen goed':
                    item['building']['maintenance_state_inside_good'] = property_value
                elif property_name == 'Onderhoud buiten goed':
                    item['building']['maintenance_state_outside_good'] = property_value
                elif property_name == 'Mechanische ventilatie':
                    item['building']['mechanical_ventilation'] = property_value

        return item
