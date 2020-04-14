# Dependencies
import datetime as dt
import time
import requests
import re
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as bs

# Initialize splinter
def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=True)


def scrape():
    browser = init_browser()
    news_title,news_paragraph = mars_news(browser)
    
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "feature_image": feature_image(browser),
        "hemisphere": hemisphere(browser),
        "weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modify": dt.datetime.now()
    }
    #print(data)
    browser.quit()
    return data

# MARS NEWS
def mars_news(browser):
    news_url = "https://mars.nasa.gov/news/"
    browser.visit(news_url)
    
    browser.is_element_present_by_css("ul.item_list li.slide",wait_time = 0.5)
    html_news = browser.html
    news_soup = bs(html_news, "html.parser")
    
    try:
        slide_element = news_soup.select_one("ul.item_list li.slide")
        news_title = slide_element.find("div",class_="content_title").get_text()
        news_p = slide_element.find("div", class_="article_teaser_body").get_text()
        
    except AttributeError:
        return None,None
    
    return news_title, news_p

# MARS IMAGES
def feature_image(browser):
    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=category=Mars"
    browser.visit(jpl_url)
    full_image_element = browser.find_by_id("full_image")
    full_image_element.click()
    
    browser.is_element_present_by_text("more info", wait_time = 0.5)
    more_info_element = browser.links.find_by_partial_text("more info")
    more_info_element.click()
    
    img_html = browser.html
    img_soup = bs(img_html, "html.parser")
    img = img_soup.select_one("figure.lede a img")
    
    try:
        img_url_rel = img.get("src")
        
    except AttributeError:
        return None
    
    img_url = f"https://www.jpl.nasa.gov{img_url_rel}"

    # print(img_url)
    
    return img_url

# MARS WEATHER
def twitter_weather(browser):
    weather_url = "https://twitter.com/marswxreport?lang=en"
    # browser.visit(weather_url)
    response = requests.get(weather_url)
    time.sleep(5)
    # weather_html = browser.html
    # tweet_soup = bs(weather_html, "html.parser")
    # tweet_attrs = {"class": "tweet", "data-name": "Mars Weather"}
    # mars_weather_tweet = tweet_soup.find("div", attrs = tweet_attrs)
    tweet_soup = bs(response.text, 'html.parser')

    try:
        mars_weather = tweet_soup.find("div", class_= "js-tweet-text-container").text
    except AttributeError:
        pattern = re.compile(r"sol")
        mars_weather = tweet_soup.find("span", text = pattern).text
    return mars_weather

# MARS FACTS
def mars_facts():
    try:
        facts_df = pd.read_html("https://space-facts.com/mars/")[0]
    except BaseException:
        return None
    
    facts_df.columns = ["Property", "Value"]
    
    return facts_df.to_html(classes='table table-striped')

# MARS HEMISPHERES
def hemisphere(browser):
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)
    hemi_html = browser.html
    hemi_soup = bs(hemi_html, "html.parser")
    hemisphere_image_urls = []
    hemisph = hemi_soup.find_all("div", class_="description")

    for hemi in hemisph:
        title = hemi.find("h3").text
        next_page = hemi.find("a")["href"]
        browser.visit(f"https://astrogeology.usgs.gov{next_page}")
        html_hemi = browser.html
        soup_hemi = bs(html_hemi, "html.parser")
        img_url = soup_hemi.find("div", class_="downloads").find("a")["href"]
        hemisphere_image_urls.append({"title": title, "img_url": img_url})
        print(hemisphere_image_urls)
        
    return hemisphere_image_urls

if __name__ == '__main__':
    print(scrape())
