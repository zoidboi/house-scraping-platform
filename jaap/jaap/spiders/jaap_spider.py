import scrapy


class JaapScraper(scrapy.Spider):
    name = "Jaap"
    jaap_prefix = 'https://www.jaap.nl/'

    def start_requests(self):
        urls = [
            '1'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        for property in response.css('div.property'):
            url = property.css('a.property-inner::attr(href)').get()

            if url is not None:
                listItem = {
                    'id': property.css('div.property::attr(id)').get(),
                    'url': url,
                    'address': property.css('h2.property-address-street::text').get() + " " + property.css(
                        'div.property-address-zipcity::text').get(),
                    'price': property.css('div.property-price::text').get(),
                    'price_type': property.css('span.pricetype::text').get(),
                    'features': property.css('div.property-feature::text').getall(),
                }

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_detail_page,
                    meta={'item': listItem}
                )

        bottom_navigation = response.css('div.bottom-navigation')
        next_page = bottom_navigation.css('a[rel="next"]::attr(href)').get()

        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_detail_page(self, response):
        item = response.meta.get('item', {})
        item['building'] = {}
        item['building']['images'] = {}

        characteristics = response.css('div.kenmerken')
        house_values = response.css('div.woningwaarde')

        # Start images loop
        for num, image in enumerate(response.css('div.photo'), start=1):
            image_url = image.css('img::attr(data-lazy-load-src)').get()

            # ignore spacer images
            if image_url != '/Content/Images/spacer.gif':
                item['building']['images'][str(num)] = image_url

        # Start characteristics loop.
        for tr in characteristics.xpath('./table//tr'):
            name = tr.css('td.name')
            name_value = name.css('div.no-dots::text').get()
            value_value = name.xpath('./following-sibling::td/text()').get()

            if name_value is not None:
                if name_value == 'Type':
                    item['building']['type'] = value_value
                elif name_value == 'Bouwjaar':
                    item['building']['build_year'] = value_value
                elif name_value == 'Woonoppervlakte':
                    item['building']['living_area'] = value_value
                elif name_value == 'Inhoud':
                    item['building']['volume'] = value_value
                elif name_value == 'Perceeloppervlakte':
                    item['building']['plot_area'] = value_value
                elif name_value == 'Bijzonderheden':
                    item['building']['specialties'] = value_value
                elif name_value == 'Isolatie':
                    item['building']['isolation'] = value_value
                elif name_value == 'Verwarming':
                    item['building']['heating'] = value_value
                elif name_value == 'Energielabel (geschat)':
                    item['building']['energy_label_estimated'] = value_value
                elif name_value == 'Energieverbruik (geschat)':
                    item['building']['energy_usage_estimated'] = value_value
                elif name_value == 'Kamers':
                    item['building']['rooms'] = value_value
                elif name_value == 'Slaapkamers':
                    item['building']['bedrooms'] = value_value
                elif name_value == 'Sanitaire voorzieningen':
                    item['building']['sanitation'] = value_value
                elif name_value == 'Keuken':
                    item['building']['kitchen'] = value_value
                elif name_value == 'Staat schilderwerk':
                    item['building']['state_of_painting_outside'] = value_value
                elif name_value == 'Tuin':
                    item['building']['garden'] = value_value
                elif name_value == 'Uitzicht':
                    item['building']['view'] = value_value
                elif name_value == 'Balkon':
                    item['building']['balcony'] = value_value
                elif name_value == 'Garage':
                    item['building']['garage'] = value_value

        # Start house value loop
        for tr in house_values.xpath('./table//tr'):
            name = tr.css('td.name')
            name_value = name.css('div.no-dots::text').get()
            value_value = name.xpath('./following-sibling::td/text()').get()

            if name_value is not None:
                if name_value == 'Geplaatst op':
                    item['building']['since']: value_value
                elif name_value == 'Oorspronkelijke vraagprijs':
                    item['original_price'] = value_value
                elif name_value == 'Daling / stijging vraagprijs':
                    item['price_change'] = value_value
                elif name_value == 'Prijs per m²':
                    item['price_per_m2'] = value_value
                elif name_value == 'Tijd in de verkoop':
                    item['time_in_sale'] = value_value

        item['seller_name'] = response.css('div.broker-name::text').get()

        return item
