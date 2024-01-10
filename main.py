import csv
import aiohttp
import asyncio
from bs4 import BeautifulSoup


async def fetch_and_write_page(session, url, page_number, csv_writer):
    url = f"{url}?shownProducts=108&singlePage={page_number}"
    async with session.get(url) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')
        await extract_and_write_data(session, soup, csv_writer)


async def extract_and_write_data(session, soup, csv_writer):
    product_tiles = soup.select('.product-list-tile')
    rows = []

    for product_tile in product_tiles:
        product_image_url = product_tile.select_one('img')['src']
        product_name = product_tile.select_one('.product-list-tile__info h3').text.strip()
        product_url = f"https://www.bauhaus.info/{product_tile.select_one('a')['href']}"

        async with session.get(product_url) as response:
            product_soup = BeautifulSoup(await response.text(), 'lxml')
            product_description = (product_soup
                                    .select_one(".product-detail-block-description__collapse p")
                                    .text)

        rows.append([product_name, product_image_url, product_description])

    csv_writer.writerows(rows)


async def scrape_bauhaus_website(url_entered):
    csv_file = open('bauhaus_products.csv', 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Product Name', 'Product Image URL', 'Product Description'])

    async with aiohttp.ClientSession() as session:
        html = await session.get(url_entered)
        soup = BeautifulSoup(await html.text(), 'lxml')
        number_of_products_on_page = soup.select_one(".pagination-show-more__result")
        max_number = int(number_of_products_on_page.text.split(" ")[-2])

        if max_number > 108:
            max_pages = (max_number // 32) + 1
            tasks = [fetch_and_write_page(session, url_entered, i, csv_writer) for i in range(2, max_pages + 1)]
            await asyncio.gather(*tasks)
        else:
            html = await session.get(url_entered+"?shownProducts=108")
            soup = BeautifulSoup(await html.text(), 'lxml')
            await extract_and_write_data(session, soup, csv_writer)

    csv_file.close()

if __name__ == "__main__":
    url_str = input('Enter the link\n')
    print("Scraping started...")
    asyncio.run(scrape_bauhaus_website(url_str))
    print("Scraping ended!")
