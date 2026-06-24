import asyncio
from imovirtual import ImovirtualParserJob
from google_sheets import GoogleSheetSaver
import csv

class RealEstateScraperJob():

    export_type = ''
    csv_name = 'real-estate-demo.csv'
    spreadsheet_id = ''

    async def callback(self, data):
        """ Save result """
        if self.export_type and self.export_type == 'google':
            # Save to google spreadsheet
            sheet = GoogleSheetSaver()
            sheet.save(data, self.spreadsheet_id)
        else:
            # Save to csv
            keys = list(data[0].keys())
            with open(self.csv_name, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)

    async def parse_apartments(self, type, home_type, location):
        """ Run scraper """
        parser = ImovirtualParserJob()
        await parser.collect(type, home_type, location, self.callback)

    def run(self, type, home_type, location, export_type, spreadsheet_id):
        self.export_type = export_type
        if export_type and export_type == 'google':
            self.spreadsheet_id = spreadsheet_id
        asyncio.run(self.parse_apartments(type, home_type, location))