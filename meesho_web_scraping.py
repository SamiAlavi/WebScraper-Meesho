# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from msedge.selenium_tools import Edge, EdgeOptions

from math import ceil
from random import choice

#--------------- file reading ---------------#
def readProgress():
  try:
    with open('progress.txt','r',encoding='utf8') as f:
      index, start = f.read().split(',')
    print('\nGetting progress from progress.txt')
  except:
    print('\n======== Scraping from the start ========')
    index, start = 0, 1
  return int(index), int(start)

def readRoutes(driver):
  try:
    with open('routes.txt','r',encoding='utf8') as f:
      all_routes = f.read().split(',')
    print('\nGetting routes from routes.txt')
  except:
    print('\n======== Scraping routes from urls ========')
    all_routes = getRoutes()
    writeRoutes(driver,all_routes)
  return all_routes

def readPages(driver, main_url, all_routes):
  try:
    with open('pages.txt','r',encoding='utf8') as f:
      all_pages = f.read().split(',')
    print('\nGetting pages from pages.txt')
    [print(all_routes[i],all_pages[i]) for i in range(len(all_routes))]
  except:
    print('\n======== Scraping page numbers from urls ========')
    all_pages = getMaxPage(driver,main_url,all_routes)
    writePages(all_pages)
  all_pages = [int(i) for i in all_pages]
  return all_pages

#--------------- file writing ---------------#
def writeProgress(index, page):
  '''
    index : index of tab in all_tabs
    page : from which page of index tab to start scraping from
  '''
  with open('progress.txt','w',encoding='utf8') as f:
    f.write(f'{index},{page}')

def writeRoutes(all_routes):
  '''
    all_routes : all tabs of the domain
  '''
  with open('routes.txt','w',encoding='utf8') as f:
    f.write(','.join(all_routes))

def writePages(all_pages):
  '''
    all_pages : all pages of all tabs
  '''
  with open('pages.txt','w',encoding='utf8') as f:
    f.write(','.join(all_pages))

def writeCSV(fname, titles, prod_urls, images, costs, desc):
  '''
    fname : file name.csv
    titles : list of products' titles
    images : list of products' images
    costs : list of products' costs
    desc : list of products' descriptions
  '''
  sep1 = ';'  # for columns
  sep2 = '~'  # for description
  buffer = ''
  for i in range(len(titles)):
    description = sep2.join(desc[i])
    buffer+=f'{titles[i]}{sep1}{prod_urls[i]}{sep1}{images[i]}{sep1}{costs[i]}{sep1}{description}\n'      
  with open(fname+'.csv','a+',encoding='utf8') as f:
    f.write(buffer)

#--------------- scraping ---------------#
def getRoutes(driver):
  routes = list()
  main = 'https://meesho.com/ethnicwear-women/pl/5v80d?page=1'
  driver.get(main)
  htmltext = driver.page_source
  soup = BeautifulSoup(htmltext,features="html.parser").select('a[role=tab]')
  for tag in soup:
    routes.append(tag['href'])
  return routes

def getMaxPage(driver, main_url, all_routes):
  '''
    main_url : domain url
    all_routes : all tabs in the domain url
  '''
  all_pages = list()
  for route in all_routes:
    driver.get(main_url+route)
    htmltext = driver.page_source
    soup = BeautifulSoup(htmltext, features="html.parser").select('div.plp-desc')[0].get_text().split(' ')
    pages = str(ceil(int(soup[-2])/20)) # total pages
    print(route,pages)
    all_pages.append(pages)
  return all_pages
    
def getDescription(driver, prod_url):
  '''
    prod_url : product url/page
  '''
  desc = list()

  driver.get(prod_url)
  htmltext = driver.page_source
  soup = BeautifulSoup(htmltext, features="html.parser").select('span.pre')

  # for each description line
  for tag in soup:
    desc.append(tag.get_text()+tag.next_sibling.get_text())
  return desc

def scrape(driver, main_url, all_routes, all_pages, index, start):
  '''
    main_url : domain url
    all_routes : all tabs in the domain url
    all_pages : total pages for each tab
    index : which tab to start from
    start : which page of the tab to start from
  '''
  for index in range(index,len(all_routes)):
    route = all_routes[index]
    total = all_pages[index]+1
    fname = route.split('/')[1]
    print(f'{route} => {start}/{total}')

    # for each page
    for i in range(start,total):
      images, titles, prod_urls  = list(),list(),list()
      costs, desc_header, desc = list(),list(),list()
      
      driver.get(f'{main_url}{route}?page={i}')
      htmltext = driver.page_source
      soup = BeautifulSoup(htmltext, features="html.parser").select('a.plp-card-desktop')
      
      # if page not found, break and go to next tab
      if len(soup)==0:
        break
      # for each product (20 products per page)
      for tag in soup:
        child = tag.div
        images.append(child.img['src'])  # image
        child = child.next_sibling
        titles.append(child.get_text())  # title
        costs.append(child.next_sibling.div.get_text()) # cost
        prod_urls.append(main_url+tag['href'])
        temp1 = getDescription(driver,prod_urls[-1]) # description
        desc.append(temp1)
      
      writeCSV(fname,titles,prod_urls,images,costs,desc)
      writeProgress(index,i+1)    
    start = 1

#--------------- config ---------------#
def webDriverConfig(agent):
  driver_path = 'msedgedriver.exe'
  #options to make selenium faster
  prefs = {'profile.default_content_setting_values': {'images': 2, 
          'plugins': 2, 'popups': 2, 'geolocation': 2, 
          'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2, 
          'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 
          'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 
          'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2, 
          'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2, 
          'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 
          'durable_storage': 2}}
  options = EdgeOptions()
  options.use_chromium = True
  options.add_argument("--start-maximized")
  options.add_argument(f"user-agent={agent}")
  options.headless = True # comment this line to visualize page visiting
  options.add_experimental_option("prefs", prefs)
  
  driver = Edge(driver_path,options=options)
  return driver

#-----------------------------------------------------------------------#
main_url = 'https://meesho.com'

user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
]

agent = choice(user_agents)
driver = webDriverConfig(agent)
all_routes = readRoutes(driver)
all_pages = readPages(driver,main_url,all_routes)
index, start = readProgress()

print(f'{agent}\nStarting from {main_url+all_routes[index]}?page={start}')

scrape(driver, main_url, all_routes, all_pages, index, start)
driver.close()
