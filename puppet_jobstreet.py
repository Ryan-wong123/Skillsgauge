# add requirement when success
# pyppeteer

import asyncio
from pyppeteer import launch



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





async def job_street_scraper():
    url = "https://sg.jobstreet.com/jobs-in-information-communication-technology"
    browser = await launch({"headless": False, "args" :['--start-maximized']}, executablePath='Win_x64_1181217_chrome-win/chrome-win/chrome.exe')

    page = await browser.newPage()
    await page.goto(url)
    # TODO: next time to calculate screen size and auto enter para

    await page.setViewport({"width": 1500, "height": 4000})



    ## get HTML
    #htmlContent = await page.content()

    #wait for detail page to open
    side_page = await page.waitForSelector("[data-automation='splitViewJobDetailsWrapper']", {"visible": True})


    if side_page == None:
        print(" side page not found ")
        await browser.close()
        return None


    print("side detected")
    cards = await page.querySelectorAll("[data-automation='normalJob']")
    #print(card)

    #html_content = await page.evaluate('''(element) => element.outerHTML''', first_card[0])
    #print(html_content)

    # working but violate
    #card_link = await card[0].querySelector("a")


    #TODO: loop cards in page
    # TODO: save variable into pandas


    for card in cards:
        await card.click()
        # wait for 0.5 s
        await page.waitFor(500)
        try:
            # wait for side detail to appear
            detail_card = await page.waitForSelector("div[data-automation='jobDetailsPage']", {"visible": True})

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

        try:
            # company name section
            company = await get_element_content(detail_card,"span[data-automation='advertiser-name']")
            print(company)

        except Exception as e:
            print(f"An error occurred: {str(e)}")

        try:
            # location section
            location = await get_element_content(detail_card,"span[data-automation='job-detail-location']")
            print(location)

        except Exception as e:
            print(f"An error occurred: {str(e)}")


        try:
            # work type section
            work_type = await get_element_content(detail_card,"span[data-automation='job-detail-work-type']")
            print(work_type)


        except Exception as e:
            print(f"An error occurred: {str(e)}")


        try:
            # salary section
            salary = await get_element_content(detail_card,"span[data-automation='job-detail-salary']")
            print(salary)

        except Exception as e:
            print(f"An error occurred: {str(e)}")


        try:
            # date posted section
            date_posted = await get_element_content(detail_card,"span._1unphw40.tcmsgw4z._1siu89c0._1siu89c1._1siu89c22._9b1ltu4._1siu89c7")
            print(date_posted)

        except Exception as e:
            print(f"An error occurred: {str(e)}")


        try:
            # description section
            description = await get_element_content(detail_card,"div[data-automation='jobAdDetails']")
            print(description)

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    await browser.close()
    return "success"




response = asyncio.run(job_street_scraper())
print(response)





