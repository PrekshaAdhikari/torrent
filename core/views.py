from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import os
from django.views.decorators.csrf import csrf_exempt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Create your views here.
#@csrf_exempt
def Home(request):
    context={}
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        keyword = keyword.replace(" ","-")
        folder = request.GET.get('folder')

        USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        LANGUAGE = "en-US,en;q=0.5"
        session = requests.Session()
        session.headers['User-Agent'] = USER_AGENT
        session.headers['Accept-Language'] = LANGUAGE
        session.headers['Content-Language'] = LANGUAGE
        try:
            response = session.get(f'https://www.limetorrents.info/search/all/{keyword}/seeds/1/')
            soup = BeautifulSoup(response.content, "lxml")
            try:
                pages = soup.find("div", {"class":"search_stat"})
                total = pages.findAll("a")[-2]
                total_pages = int(total.text) 
            except:
                total_pages = 1
            print(total_pages)
            for x in range(1, total_pages + 1):
                all_url = "https://www.limetorrents.info/search/all/{}/seeds/{}/".format(keyword,x)
                print(all_url)
                response1 = requests.Session().get(all_url)
                soup1 = BeautifulSoup(response1.content, "lxml") 
                table = soup1.find("table", {"class":"table2"})
                all_tr = table.findAll("div", {"class":"tt-name"})
                for tr in all_tr:
                    href = tr.findAll("a")[1]
                    Href = href["href"]
                    name = href.text
                    #print(name)
                    new_url = "https://www.limetorrents.info" + Href
                    #print(new_url)
                    response2 = requests.Session().get(new_url)
                    soup2 = BeautifulSoup(response2.content, "lxml") 
                    link_div = soup2.find("div", {"class":"downloadarea"})
                    link_ = link_div.find("a")
                    link = link_["href"].split("?")[0].replace("http", "https")
                    link_name = link.split("/")[-1]
                    #print(link)
                    chrome_option = Options()
                    chrome_option.add_argument("--headless")
                    CHROME_DRIVER_PATH = "/home/pratik/Documents/chromedriver"
                    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_option)            
                    driver.get("https://itorrents.org/")
        
                    values = driver.get_cookies()
                    cookie = {
                        '__cfduid': values[0]['value'],
                        'cf_chl_1': values[1]['value'],
                        'cf_clearance':'2943ad7f42f9ce884ead16029b3b505d579d0dca-1601737940-0-1z37982202z7e9cdee8zf9e7f95-150',
                        'cf_chl_prog': 'x15'
                    }
                    
                    new_header = {
                        'authority': 'itorrents.org',
                        'scheme': 'https',
                       
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        # 'Cookie': '__cfduid=dddff03b7324848d444cce32206c6c2901601656107',
                        # ; cf_clearance=2943ad7f42f9ce884ead16029b3b505d579d0dca-1601737940-0-1z37982202z7e9cdee8zf9e7f95-150; _ga=GA1.2.614813655.1601705508; _gid=GA1.2.1182535361.1601705508; cf_chl_1=fe781464726f4a8; cf_chl_prog=x15',
                        'Cookie': "__cfduid="+cookie['__cfduid']+";cf_clearance="+cookie['cf_clearance']+";cf_chl_1="+cookie['cf_chl_1']+";cf_chl_prog="+cookie['cf_chl_prog'],
                        'Upgrade-Insecure-Requests': '1'
                    }
                    
                    sess = requests.session()
                    print("Received Torrent Url:", link)
                    print("Hitting Request to torrent url...")
                    try:
                        response = sess.get(link, headers=new_header)
                        print(response.status_code)
                        if response.status_code == 200:
                            filename = link.split('?')[0].split("/")[-1]
                            print("Saving torrent file.....")
                            with open(filename, 'wb') as file:
                                file.write(response.content)
                            print("Saved....")
                        else:
                            print("****COOKIE ERROR********")
                    except Exception as error:
                        print(error)
                        print('******error in torrent url*****')

                    sess.close()
                        

                    #try:
                        #r = requests.get(link)
                    #except Exception:
                        #print(".........Error getting response .........")
                        #pass

                    dirName = folder.split("/")[0]
                    if not os.path.exists(dirName):
                        os.mkdir(dirName)
                    else:    
                      pass
                    file_name = "{}/{}".format(dirName,link_name )


                    #open(file_name, 'wb').write(r.content)

            context["status"] ="Download Sucessful."

        except Exception as ex:
            print(ex)
            context["status"] ="No file to download."

        print(context)


    return render(request,"home.html",{'context': context})
