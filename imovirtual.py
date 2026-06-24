from playwright.async_api import async_playwright
from playwright.async_api import expect
from datetime import datetime, timedelta, timezone
import traceback
from html_to_markdown import convert
import re

class ImovirtualParserJob():
        
    async def parse_post(self, page, post_link):
        """ Parse post item: go to post page, collect data, go back """
        try:
            post_data = {}
            await post_link.scroll_into_view_if_needed()
            await post_link.click()
            await page.wait_for_timeout(2_000)
            
            post_data['title'] = await page.locator('[data-sentry-element="Title"]').nth(0).inner_text()
            print(f"Parsing post: {post_data['title']}")
            post_data['url'] = page.url
            price = await page.get_by_label("Price").first.inner_text()
            post_data['price'] = price.replace('\xa0', '')
            post_data['location'] = await page.locator('[data-sentry-component="MapLink"]').inner_text()
            grids = page.locator('[data-sentry-element="ItemGridContainer"]')
            area = await grids.filter(has_text="Area").all()
            if len(area):
                area_text = await area[0].locator('div').nth(1).inner_text()
                post_data['area'] = area_text.replace('\xa0', '')

            typology = await grids.filter(has_text="Typology").all()
            if len(typology):
                post_data['typology'] = await typology[0].locator('div').nth(1).inner_text()

            bath = await grids.filter(has_text="Number of bathrooms").all()
            if len(bath):
                post_data['bath'] = await bath[0].locator('div').nth(1).inner_text()

            floor = await grids.filter(has_text="Floor").all()
            if len(floor):
                post_data['floor'] = await floor[0].locator('div').nth(1).inner_text()

            post_data['description'] = await page.locator('[data-sentry-element="DescriptionWrapper"]').nth(0).inner_text()
            
            last_updated = await page.locator('p').filter(has_text="Last update:").inner_text()
            post_data['last_updated'] = last_updated.replace('Last update: ', '')
            
            go_back = await page.locator('[data-cy="breadcrumb-go-back-button"]').all()
            if len(go_back):
                await go_back[0].click()
                await page.wait_for_timeout(1_000)
            return post_data
        except Exception as e:
            trace = traceback.format_exc() 
            print("Error while parsing post: ")
            print(trace)
            await page.screenshot(path="err_post.png", full_page=True)
            return None
        

    async def parse_list(self, page, list):
        """ Parse list with posts """
        posts = []
        try:
            items = await list.locator('li').filter(visible=True).all()
            for item in items:
                link = item.locator('[data-cy="listing-item-link"]')
                post = await self.parse_post(page, link)
                if post is not None:
                    posts.append(post)
            return posts
        except Exception as e:
            trace = traceback.format_exc()
            print("Error while parsing list: ")
            print(trace)
            await page.screenshot(path="err_list.png", full_page=True)
            return posts
        
    async def parse_target_page(self, page):
        """ Parse target page with pagination """
        posts = []
        try:
            # Find element with results
            houses_list = await page.locator('[data-cy="search.listing.organic"]').all()
            if len(houses_list):
                # Find pagination element
                pagination = await page.locator('[data-cy="nexus-pagination-component"]').all()
                if len(pagination):
                    # Get page count
                    pages = await pagination[0].locator('li').all()
                    last_page = await pages[-2].inner_text()
                    page_count = int(last_page)
                    print(f"Pages: {page_count}")
                    for i in range (0, page_count - 1):
                        houses_list = await page.locator('[data-cy="search.listing.organic"]').all()
                        posts += await self.parse_list(page, houses_list[0])
                        next_page = await page.get_by_label("Go to next Page").all()
                        if len(next_page):
                            await next_page[0].click()
                            await page.wait_for_timeout(1_000)
                        else:
                            break
                else:
                    # Parse only one page
                    print(f"Pages: 1")
                    posts += await self.parse_list(page, houses_list[0])
            return posts
        except Exception as e:
            trace = traceback.format_exc()
            print("Error while parsing target page: ")
            print(trace)
            await page.screenshot(path="err_target_parse.png", full_page=True)
            return posts
        
    async def go_to_target_page(self, page, type, home_type, location):
        """ Go to index https://www.imovirtual.com/en and set filters """
        try:
            # Go to index page
            await page.goto("https://www.imovirtual.com/en")
            accept_btn = page.locator("#onetrust-accept-btn-handler")
            await accept_btn.click()
            await page.screenshot(path="index.png", full_page=True)
            if type:
                # Select search type (rent or sale)
                transaction = page.locator("#transaction-dropdown")
                await transaction.click()
                if type == 'arrendar' or type == 'rent':
                    await page.get_by_label("For rent").click()
                elif type == 'comprar' or type == 'sale' or type == 'buy':
                    await page.get_by_label("For sale").click()
            if home_type:
                # Select property type (apartment, house, garage etc)
                # Open dropdown
                estate = page.locator("#estate-dropdown")
                await estate.click()
                estate_dropdown = page.locator("#estate-dropdown-controls")
                await page.wait_for_timeout(1_000)
                # Find option
                search = await estate_dropdown.get_by_text(re.compile(home_type, re.IGNORECASE)).all()
                if len(search) > 0:
                    await search[0].click()
                else:
                    print("Error while trying go to target page:")
                    print("Problem with home_type")
                    await page.screenshot(path="err_target.png", full_page=True)
                    return False
            if location:
                # Open dropdown
                location_input_btn = await page.locator('[data-cy="search.form.location.button"]').all()
                if len(location_input_btn):
                    await location_input_btn[0].click()
                    await expect(page.locator('#location-search-input')).to_be_visible()
                    location_input = page.locator("#location-search-input")
                    # Fill text
                    await location_input.fill(location)
                    await page.wait_for_timeout(3_000)
                    list = page.locator('#location-search-controls')
                    # Select the first option
                    location_element = await list.locator("div").nth(0).locator('[data-cy="tree-item-clickable"]').all()
                    if len(location_element):
                        await location_element[0].click()
                        confirm_location = page.locator('#confirm-location-search')
                        await confirm_location.click()
            # Submit filters
            submit = page.locator("#search-form-submit")
            await submit.click()
            await page.wait_for_timeout(5_000)
            await page.screenshot(path="target.png", full_page=True)
            return True
        
        except Exception as e:
            trace = traceback.format_exc()
            print("Error while trying go to target page: ")
            print(trace)
            await page.screenshot(path="err_target.png", full_page=True)
            return False

        
    async def collect(self, type, home_type, location, callback):
        """ Collect real estate data from https://www.imovirtual.com/ """
        async with async_playwright() as p:
            print("Started imovirtual parser")

            chromium = p.chromium
            iphone = p.devices["iPhone 15"]
            browser = await chromium.launch()
            context = await browser.new_context(**iphone, permissions=['clipboard-read', 'clipboard-write'], java_script_enabled=True)
            await context.grant_permissions(['clipboard-read', 'clipboard-write'])
            page = await context.new_page()
            # Go to target page with filters
            result_target = await self.go_to_target_page(page, type, home_type, location)
            if result_target:
                # Parse posts
                result = await self.parse_target_page(page)
                # Deduplicate data
                data_set = set()
                unique_result = []
                for item in result:
                    if item['url'] not in data_set:
                        data_set.add(item['url'])
                        unique_result.append(item)
                # Return results
                await callback(result)