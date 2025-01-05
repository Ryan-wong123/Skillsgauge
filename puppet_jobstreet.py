# add requirement when success
# pyppeteer

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
        # Extract the number and unit (days or hours)
        number = int(match.group(1))
        unit = match.group(2)

        # Calculate the date based on the unit
        if unit == 'd':  # Days ago
            calculated_date = current_datetime - timedelta(days=number)
        elif unit == 'h':  # Hours ago
            calculated_date = current_datetime - timedelta(hours=number)

        elif unit == 'm':  # Hours ago
            calculated_date = current_datetime
        else:
            raise ValueError("Unsupported unit in relative time format")
    else:
        raise ValueError("Unsupported relative time format")




    print(calculated_date.date())
    return calculated_date.date()




async def print_html_content(page, element):

    html_content = await page.evaluate('''(element) => element.outerHTML''', element)
    print(html_content)



async def get_element_content(card, selector):

    # function to extract element content
    parent = await card.querySelector(selector)
    # return js handler and convert to py string cant merge as need to be awaited
    content_js = await parent.getProperty("textContent")
    content = await content_js.jsonValue()
    #print(content)
    return content


def write_to_csv(new_scrape_df, csvfile):

    # check if csv file exist
    if os.path.isfile(csvfile):
        new_scrape_df.to_csv(csvfile, mode='a', index=False, header=False)

    else:
        new_scrape_df.to_csv(csvfile, index=False)





async def job_street_scraper():


    urls = ["https://sg.jobstreet.com/jobs-in-information-communication-technology",
            "https://sg.jobstreet.com/jobs-in-engineering",
            "https://sg.jobstreet.com/jobs-in-banking-financial-services",
            "https://sg.jobstreet.com/jobs-in-administration-office-support",
            "https://sg.jobstreet.com/jobs-in-healthcare-medical"
            ]
    """
    testing url 
    urls = ["https://sg.jobstreet.com/jobs-in-engineering",


            ]
    """
    browser = await launch({
    'headless': True,
    'args': [
        '--no-sandbox',
        '--disable-dev-shm-usage'
    ],
    'executablePath': '/usr/bin/chromium-browser',  # Ensure this path is correct
    })

    page = await browser.newPage()

    # setup pandas

    job_street_df = pd.DataFrame(columns=["Job Id", "Job URL", "Job Title", "Company", "Job Industry", "Job Sub Industry",
                                          "Job Description", "Job Employment Type","Job Minimum Experience", "Job Salary Range",
                                          "Skills", "Job Posting Date", "Location"])

    for url in urls:

        # setup section
        #url = "https://sg.jobstreet.com/jobs-in-information-communication-technology"

        await page.goto(url)
        await page.setViewport({"width": 1920, "height": 1080})
        current_page = 1
        page_count = 4
        total_scrape_count = 0
        total_cards = 0

        ## get HTML
        #htmlContent = await page.content()

        #wait for detail page to open
        side_page = await page.waitForSelector("[data-automation='splitViewJobDetailsWrapper']", {"visible": True})

        if side_page == None:
            print(" side page not found ")
            await browser.close()
            return None

        print("side detected")

        while current_page <= page_count:
            #cards = await page.querySelectorAll("[data-automation='normalJob']")
            cards = await page.querySelectorAll("[data-automation='jobTitle']")
            #html_content = await page.evaluate('''(element) => element.outerHTML''', first_card[0])
            #print(html_content)
            card_count = 0

            for card in cards:
                card_list = []
                #await print_html_content(page,card)

                # error handle urgent hiring causing link to another page
                #TODO: future check how to solve this issue
                if await card.querySelector("span[data-automation='urgentAdBadge']"):
                    continue

                await card.click()
                # wait for 0.5 s
                await page.waitFor(500)

                try:
                    # wait for side detail to appear
                    detail_card = await page.waitForSelector("div[data-automation='jobDetailsPage']", {"visible": True, "timeout": 10000})

                except Exception as e:
                    print(f"An error occurred: {str(e)}")
                    print(" detail page not open")
                    continue

                print("detail page open")

                try:
                    # title section
                    title = await get_element_content(detail_card,"h1[data-automation='job-detail-title'] > a")
                    print(title)

                except Exception as e:
                    print(f"An error occurred: {str(e)}")
                    title = None

                try:
                    # link section and Job ID section
                    # function to extract element content
                    link_parent = await detail_card.querySelector("h1[data-automation='job-detail-title'] > a")

                    # return js handler and convert to py string cant merge as need to be awaited
                    link_js = await link_parent.getProperty("href")
                    link = await link_js.jsonValue()
                    #print(link)

                    job_id = re.search(r"(?<=job\/)(\d+)(?=\?)", link)
                    job_id = job_id.group(1)
                    print(job_id)

                except Exception as e:
                    print(f"An error occurred: {str(e)}")
                    link = None

                try:
                    # company name section
                    company = await get_element_content(detail_card,"span[data-automation='advertiser-name']")
                    #print(company)

                except Exception as e:
                    print(f"An error occurred : {str(e)}")
                    company = None

                try:
                    # location section
                    location = await get_element_content(detail_card,"span[data-automation='job-detail-location']")
                    #print(location)

                except Exception as e:
                    print(f"An error occurred with location: {str(e)}")
                    location = None

                try:
                    #TODO: sub industry having issue extracting
                    industry_all = await get_element_content(detail_card, "span[data-automation='job-detail-classifications'] > a")
                    print(industry_all)

                    # re to extract sub industry and industry

                    industry = re.search(r"\((.*?)\)" , industry_all)

                    sub_industry = industry_all.strip(industry.group(0))
                    industry = industry.group(0)
                    print(sub_industry)
                    print(industry)

                except Exception as e:
                    print(f"An error occurred with industry: {str(e)}")
                    industry = None
                    sub_industry = None

                try:
                    # work type section
                    work_type = await get_element_content(detail_card,"span[data-automation='job-detail-work-type']")
                    #print(work_type)

                except Exception as e:
                    print(f"An error occurred with work type: {str(e)}")
                    work_type = None

                try:
                    # salary section
                    salary = await get_element_content(detail_card,"span[data-automation='job-detail-salary']")
                    #print(salary)

                except Exception as e:
                    print(f"An error occurred with salary: {str(e)}")
                    salary = None

                try:
                    # date posted section
                    #date_posted = await get_element_content(detail_card,"span[data-automation='jobListingDate']")
                    #print(date_posted)

                    date_posted = await detail_card.xpath("//span[contains(text(), 'Posted')]")
                    date_posted_text = await page.evaluate('(element) => element.textContent', date_posted[0])
                    print(date_posted_text)

                    date_posted_text = await calculate_date(date_posted_text)

                except Exception as e:
                    print(f"An error occurred with date posted: {str(e)}")
                    date_posted_text = None

                try:
                    # description section
                    description = await get_element_content(detail_card,"div[data-automation='jobAdDetails']")
                    #print(description)

                except Exception as e:
                    print(f"An error occurred desc: {str(e)}")
                    description = None

                job_data = {"Job Id": job_id, "Job Title": title, "Job URL": link,
                            "Company": company, "Location": location, "Job Industry": industry, 
                            "Job Sub Industry": sub_industry, "Job Employment Type": work_type,
                            "Job Salary Range": salary, "Job Posting Date": date_posted_text, 
                            "Job Description": description}

                job_street_df = pd.concat([job_street_df, pd.DataFrame([job_data])], ignore_index=True)

                card_count += 1

            # page scrape analysis ====================
            print("===============================PAGE ANAlYSIS =============================================")
            print("Total card: ", len(cards))
            print("Total scrape:", card_count)
            total_cards += len(cards)
            total_scrape_count += card_count

            # next page section

            next_link = await page.querySelector("li > a[title='Next']")
            await next_link.click()
            current_page +=1
            # wait to allow page to load
            await page.waitFor(2000)
            print("next paged")

        # full scrape analysis
        print("=============================== FULL ANAlYSIS =============================================")
        print("total card: ", total_cards)
        print("total scrape:", total_scrape_count)

    await browser.close()
    write_to_csv(job_street_df, csvfile)
    return "success"

response = asyncio.run(job_street_scraper())
print(response)