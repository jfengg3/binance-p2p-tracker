import asyncio
import ticker
import statistics
from forex_python.converter import CurrencyRates
from pyppeteer import launch

c = CurrencyRates()

# testing purposes
get_Ticker = input('Get a ticker: ')
get_Fiat = input('Select a fiat: ')
get_Amt = int(input('Amt of money: '))

async def main():
    
    browser = await launch()
    page = await browser.newPage()
    
    # Select ticker to buy/sell
    await page.goto('https://p2p.binance.com/en')
    await page.waitForSelector(("main > div.css-1u2nsrt > div > div > div.css-8f6za > div > div:nth-child({})").format(ticker.ticker[get_Ticker]))
    await page.click(("main > div.css-1u2nsrt > div > div > div.css-8f6za > div > div:nth-child({})").format(ticker.ticker[get_Ticker]))

    await page.waitFor(1000)

    # Select fiat
    await page.waitForSelector('#C2Cfiatfilter_searhbox_fiat')
    await page.click('#C2Cfiatfilter_searhbox_fiat')

    await page.waitFor(1000)

    await page.waitForSelector(('#{}').format(get_Fiat))
    await page.click(('#{}').format(get_Fiat))
    
    await page.waitFor(2000)

    # Scraping through pagination indexes
    ## Evaluate a single page first
    async def evaluateCall(page):
        await page.waitFor(1000)
        prices_data = []
        evaluatePage = await page.evaluate('''() => {
            
            elements = Array.from(document.querySelectorAll("main > div.css-16g55fu > div > div.css-vurnku > div"))
            return elements.map(element => element.childNodes[0].innerText)

        }''')

        for orders in evaluatePage:
            price = orders.splitlines()
            prices_data.append(float(price[4].replace(",","")))
        
        print(prices_data)

        return prices_data

    ## Going through > 1 pages
    async def scrape(page):
        global results
        results = []
        nextButton = await page.JJ("main > div.css-16g55fu > div > div.css-kwfbf > div > button[aria-label='Next page']:not([disabled])")
        count = 0
        singlePage = True

        while (len(nextButton) == 1 or singlePage):
            count+=1
            singlePage = False
            await page.waitFor(1000)
            print("paged index: %d" % (count))
            results = results + (await evaluateCall(page))
            nextButton = await page.JJ("main > div.css-16g55fu > div > div.css-kwfbf > div > button[aria-label='Next page']:not([disabled])")

            if (len(nextButton) > 0 and singlePage == False):
                await page.click("button[aria-label='Next page']:not([disabled])")
        
        print(results)
        return results
    
    await scrape(page)

    ## Calculating Prices
    print("Lowest Price: " + '{:.{}f}'.format(results[0], 2))
    print("Median Price: " + '{:.{}f}'.format(statistics.median(results), 2))
    print("Highest Price: " + '{:.{}f}'.format(results[-1], 2))
    print("Total Offers: %d" % (len(results)))

    print("Current Rate: " + str(c.get_rate('USD', 'SGD')))
    # Transaction fees if you were to buy through p2p instead
    ### Against real-time exchange rate
    gains = (get_Amt / results[0]) - (get_Amt / c.get_rate('USD', 'SGD'))
    print(gains)
    
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())