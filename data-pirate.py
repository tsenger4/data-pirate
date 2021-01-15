import scrapy
from decouple import config
from cep import Cep
from datetime import datetime
from monitor import SpiderCloseMonitorSuite
import jsonlines
import uuid


class DataPirateSpider(scrapy.Spider):

    @property
    def dataset_all(self):
        return self._dataset_all

    @dataset_all.setter
    def dataset_all(self, value):
        self._dataset_all = value

    name = 'data_pirate'
    dataset_all = []
    cep = Cep()
    execution_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

    URL_BASE = config('URL_BASE')
    DIR_EXPORT = config('DIR_EXPORT')
    DIR_LOG = config('DIR_LOG')
    SPIDERMON_TELEGRAM_SENDER_TOKEN = config('SPIDERMON_TELEGRAM_SENDER_TOKEN')
    SPIDERMON_TELEGRAM_RECIPIENTS = config('SPIDERMON_TELEGRAM_RECIPIENTS')

    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'HTTPCACHE_ENABLED': True,  # only for dev env
        'LOG_STDOUT': True,  # only for dev env,
        'LOG_LEVEL': 'INFO',  # to only display errors
        'LOG_FORMAT': '%(levelname)s: %(message)s',
        'LOG_FILE': r'./{}/{}_{}.txt'.format(DIR_LOG, name, execution_datetime),
        'SPIDERMON_ENABLED': True,
        'EXTENSIONS': {
            'spidermon.contrib.scrapy.extensions.Spidermon': 500,
        },
        'SPIDERMON_SPIDER_CLOSE_MONITORS': (
            'monitor.SpiderCloseMonitorSuite',
        ),
        'SPIDERMON_MIN_ITEMS': 10,
        'SPIDERMON_UNWANTED_HTTP_CODES_MAX_COUNT': 10,
        'SPIDERMON_UNWANTED_HTTP_CODES': [301, 400, 407, 429, 500, 502, 503, 504, 523, 540, 541],
        'SPIDERMON_ADD_FIELD_COVERAGE': True,
        'SPIDERMON_TELEGRAM_SENDER_TOKEN': SPIDERMON_TELEGRAM_SENDER_TOKEN,
        'SPIDERMON_TELEGRAM_RECIPIENTS': [SPIDERMON_TELEGRAM_RECIPIENTS],
        'SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_OK_MESSAGES': True,
        'SPIDERMON_TELEGRAM_NOTIFIER_INCLUDE_ERROR_MESSAGES': True
    }

    start_urls = [
        URL_BASE
    ]

    def parse(self, response):
        # Discard semantic error on first element option on UF select
        # inputs_UF = response.xpath('//select[@name="UF"]/option[not(@value = "")]/text()').getall()
        inputs_UF = ['AC', 'AL']

        index_loop = 0
        dataset = []

        for input_uf in inputs_UF:
            index_loop = 0
            dataset = []
            yield scrapy.http.FormRequest.from_response(
                response,
                formname='Geral',
                formdata={
                    'UF': input_uf,
                },
                callback=self.parse_uf_data,
                meta={
                    'index_uf': input_uf,
                    'index_loop': index_loop,
                    r'dataset_{}'.format(input_uf): dataset
                },
                dont_filter=True
            )

    def closed(self, reason):
        if reason == 'finished':
            self.export_jsonl()
        else:
            return

    def parse_uf_data(self, response):
        index_uf = response.meta.get('index_uf')
        index_loop = response.meta.get('index_loop')
        dataset = response.meta.get(r'dataset_{}'.format(index_uf))

        # first pagination has two tables with same .class
        if (not response.xpath('//form[@name="Anterior"]').extract_first()):
            table_rows = response.css(
                'table.tmptabela:nth-of-type(2) tr:nth-child(n+3)')
        else:
            table_rows = response.css('table.tmptabela tr:nth-child(n+3)')

        for table_row in table_rows:
            td_table_row = table_row.css('td::text').extract()
            td_table_row = self.parse_extracted_table_row(
                td_table_row, index_uf, index_loop)

            # case not valid ceps
            if not td_table_row:
                continue

            yield {"data": td_table_row}
            dataset.append(td_table_row)
            index_loop += 1

        if response.xpath('//form[@name="Proxima"]').extract_first():
            yield scrapy.http.FormRequest.from_response(
                response,
                formname='Proxima',
                formdata={
                    'UF': response.xpath('//form[@name="Proxima"]/input[@name="UF"]/@value').extract_first(),
                    'Localidade': response.xpath('//form[@name="Proxima"]/input[@name="Localidade"]/@value').extract_first(),
                    'Bairro': response.xpath('//form[@name="Proxima"]/input[@name="Bairro"]/@value').extract_first(),
                    'qtdrow': response.xpath('//form[@name="Proxima"]/input[@name="qtdrow"]/@value').extract_first(),
                    'pagini': response.xpath('//form[@name="Proxima"]/input[@name="pagini"]/@value').extract_first(),
                    'pagfim': response.xpath('//form[@name="Proxima"]/input[@name="pagfim"]/@value').extract_first(),
                },
                callback=self.parse_uf_data,
                meta={
                    'index_uf': index_uf,
                    'index_loop': index_loop,
                    r'dataset_{}'.format(index_uf): dataset
                },
                dont_filter=True
            )
        else:
            self.parse_uf_collect_end(dataset, index_uf)

    def parse_extracted_table_row(self, td_table_row, index_uf, index_loop):
        uf_pattern = r"{}-{}".format(index_uf.lower(), index_loop)
        id_table_row = self.generate_id(uf_pattern)

        # remove unnecessary " " on begin of raw str range
        cep_raw_range = td_table_row[1][1:]
        td_table_row[1] = cep_raw_range

        cep_start_range, cep_end_range = cep_raw_range.split(" a ")

        if not self.cep.validate(cep_start_range) or not self.cep.validate(cep_end_range):
            return False

        td_table_row.insert(0, cep_end_range)
        td_table_row.insert(0, cep_start_range)
        td_table_row.insert(0, id_table_row)
        td_table_row.insert(0, uf_pattern)
        td_table_row.insert(0, index_uf)
        return td_table_row

    def parse_uf_collect_end(self, dataset, index_uf):
        self.dataset_all += dataset
        self.export_jsonl_uf(dataset, index_uf)

    def export_jsonl_uf(self, dataset, index_uf):
        with jsonlines.open(r'./{}/cep_{}_{}.jsonl'.format(self.DIR_EXPORT, index_uf, self.execution_datetime), 'a') as writer:
            writer.write_all(dataset)

    def export_jsonl(self):
        with jsonlines.open(r'./{}/cep_{}.jsonl'.format(self.DIR_EXPORT, self.execution_datetime), 'a') as writer:
            writer.write_all(self.dataset_all)

    def generate_id(self, base_string):
        return uuid.uuid3(uuid.NAMESPACE_DNS, base_string).hex
