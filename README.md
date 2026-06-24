# Real Estate Scraper

A Python web scraper for [imovirtual.com](https://www.imovirtual.com/) that mimics real user 
behavior to collect property listings and export results to CSV or Google Sheets.

## Features

- **Human-like browsing** — simulates scrolling, form filling, pagination, and dynamic content 
  handling via Playwright
- **Configurable filters** — search by transaction type (rent/buy), property type 
  (apartments, houses, etc.), and location
- **Structured deduplicated data collection** — extracts title, URL, price, location, area, typology, 
  bathrooms, floor, description, and listing date
- **Flexible output** — export to CSV or directly to a Google Spreadsheet via the Google API
- **Robust execution** — built-in error handling, action logging, and screenshot capture

## Tech Stack

- Python
- Playwright
- Google Sheets API