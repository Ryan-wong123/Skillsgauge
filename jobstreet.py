import asyncio
from pyppeteer import launch
import pandas as pd
from datetime import datetime, timedelta
import re
import os

current_datetime = datetime.now()
csvfile = "job_street_scrape.csv"

async def calculate_date(date_extracted):
    match = re.match(r"Posted (\d+)([dhm]) ago", date_extracted)

    if match:
        number = int(match.group(1))
        unit = match.group(2)

        if unit == 'd':
            calculated_date = current_datetime - timedelta(days=number)
        elif unit == 'h':
            calculated_date = current_datetime - timedelta(hours=number)
        elif unit == 'm':
            calculated_date = current_datetime
        else:
            raise ValueError("Unsupported unit in relative time format")
    else:
        raise ValueError("Unsupported relative time format")

    print(calculated_date.date())
    return calculated_date.date()

async def get_element_content(card, selector):
    parent = await card.querySelector(selector)
    content_js = await parent.getProperty("textContent")
    content = await content_js.jsonValue()
    return content

def write_to_csv(new_scrape_df, csvfile):
    if os.path.isfile(csvfile):
        new_scrape_df.to_csv(csvfile, mode='a', index=False, header=False)
    else:
        new_scrape_df.to_csv(csvfile, index=False)

async def job_street_scraper():
    urls = [
        "https://sg.jobstreet.com/jobs-in-information-communication-technology",
        "https://sg.jobstreet.com/jobs-in-engineering",
        "https://sg.jobstreet.com/jobs-in-banking-financial-services",
        "https://sg.jobstreet.com/jobs-in-administration-office-support",
        "https://sg.jobstreet.com/jobs-in-healthcare-medical"
    ]

    browser = await launch({
        'headless': True,
        'args': [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--remote-debugging-port=9222'
        ],
        'executablePath': '/usr/bin/chromium-browser',
    })

    page = await browser.newPage()
    job_street_df = pd.DataFrame(columns=["Job Id", "Job URL", "Job Title", "Company", "Job Industry", "Job Sub Industry",
                                          "Job Description", "Job Employment Type", "Job Minimum Experience", "Job Salary Range",
                                          "Skills", "Job Posting Date", "Location"])

    for url in urls:
        await page.goto(url)
        await page.setViewport({"width": 1920, "height": 1080})
        current_page = 1
        page_count = 4
        total_scrape_count = 0
        total_cards = 0

        side_page = await page.waitForSelector("[data-automation='splitViewJobDetailsWrapper']", {"visible": True})

        if side_page == None:
            print("side page not found")
            await browser.close()
            return None

        while current_page <= page_count:
            cards = await page.querySelectorAll("[data-automation='jobTitle']")
            card_count = 0

            for card in cards:
                if await card.querySelector("span[data-automation='urgentAdBadge']"):
                    continue

                await card.click()
                await page.waitFor(500)

                try:
                    detail_card = await page.waitForSelector("div[data-automation='jobDetailsPage']", {"visible": True, "timeout": 10000})
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
                    continue

                try:
                    title = await get_element_content(detail_card, "h1[data-automation='job-detail-title'] > a")
                except Exception as e:
                    title = None

                try:
                    link_parent = await detail_card.querySelector("h1[data-automation='job-detail-title'] > a")
                    link_js = await link_parent.getProperty("href")
                    link = await link_js.jsonValue()
                    job_id = re.search(r"(?<=job\/)(\d+)(?=\?)", link)
                    job_id = job_id.group(1)
                except Exception as e:
                    link = None

                try:
                    company = await get_element_content(detail_card, "span[data-automation='advertiser-name']")
                except Exception as e:
                    company = None

                try:
                    location = await get_element_content(detail_card, "span[data-automation='job-detail-location']")
                except Exception as e:
                    location = None

                try:
                    industry_all = await get_element_content(detail_card, "span[data-automation='job-detail-classifications'] > a")
                    industry = re.search(r"\((.*?)\)", industry_all)
                    sub_industry = industry_all.strip(industry.group(0))
                    industry = industry.group(0)
                except Exception as e:
                    industry = None
                    sub_industry = None

                try:
                    work_type = await get_element_content(detail_card, "span[data-automation='job-detail-work-type']")
                except Exception as e:
                    work_type = None

                try:
                    salary = await get_element_content(detail_card, "span[data-automation='job-detail-salary']")
                except Exception as e:
                    salary = None

                try:
                    date_posted = await detail_card.xpath("//span[contains(text(), 'Posted')]")
                    date_posted_text = await page.evaluate('(element) => element.textContent', date_posted[0])
                    date_posted_text = await calculate_date(date_posted_text)
                except Exception as e:
                    date_posted_text = None

                try:
                    description = await get_element_content(detail_card, "div[data-automation='jobAdDetails']")
                except Exception as e:
                    description = None

                job_street_df = job_street_df.append({"Job Id": job_id, "Job Title": title, "Job URL": link,
                                                      "Company": company, "Location": location, "Job Industry": industry,
                                                      "Job Sub Industry": sub_industry, "Job Employment Type": work_type,
                                                      "Job Salary Range": salary, "Job Posting Date": date_posted_text,
                                                      "Job Description": description}, ignore_index=True)
                card_count += 1

            print(f"Total cards: {len(cards)}")
            print(f"Total scrape: {card_count}")
            total_cards += len(cards)
            total_scrape_count += card_count

            next_link = await page.querySelector("li > a[title='Next']")
            await next_link.click()
            current_page += 1
            await page.waitFor(2000)

        print(f"Total cards scraped: {total_cards}")
        print(f"Total jobs scraped: {total_scrape_count}")

    await browser.close()
    write_to_csv(job_street_df, csvfile)
    return "success"

if __name__ == '__main__':
    try:
        asyncio.run(job_street_scraper())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Ensure that we close the event loop cleanly
        if not asyncio.get_event_loop().is_closed():
            asyncio.get_event_loop().close()
