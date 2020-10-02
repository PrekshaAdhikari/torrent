from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import os
from django.views.decorators.csrf import csrf_exempt

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
            pages = soup.find("div", {"class":"search_stat"})
            total = pages.findAll("a")[-2]
            total_pages = int(total.text) 
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
                    link = link_["href"]
                    print(link)
                    try:
                        r = requests.get(link)
                    except Exception:
                        print(".........Error getting response .........")
                        pass

                    dirName = folder.split("/")[0]
                    if not os.path.exists(dirName):
                        os.mkdir(dirName)
                    else:    
                      pass
                    folder = "{}/{}".format(dirName,Href)

                    open(folder, 'wb').write(r.content)

            context["status"] ="Download Sucessful."

        except:
            context["status"] ="No file to download."

        print(context)




    return render(request,"home.html",{'context': context})
