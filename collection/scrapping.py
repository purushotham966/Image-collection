from bs4 import BeautifulSoup
import re
import urllib.parse
from urllib.parse import urlparse, urljoin
import requests
from facebook_scraper import get_posts
import time
import random
import os
import numpy as np
import tflite_runtime.interpreter as tflite
from PIL import Image, ImageOps
from io import BytesIO

m = 1
user_agent_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
]
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Dnt": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": None
}

buffer = random.randint(0, 100)
file_name = "/tmp/model_unquant.tflite"
interpreter = None
input_details = None
output_details = None

def create_folders(restId):
    global input_details, interpreter, output_details
    try:
        interpreter = tflite.Interpreter(model_path=file_name)
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        interpreter.allocate_tensors()
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    except Exception as e:
        print("Interpreter Problem", e)

    try:
        os.mkdir(f"/tmp/Food{restId}")
        os.mkdir(f"/tmp/Menu{restId}")
        os.mkdir(f"/tmp/Restaurant{restId}")
    except Exception as e:
        print("Exception occured while creating folders", e)


def classification(img_content, restId, quality):

    global input_details, interpreter, input_details, output_details, buffer
    x = {0: "Food", 1: "Non-Food", 2: "Menu", 3: "Restaurant"}

    try:
        image = BytesIO(img_content)
        image_temp = BytesIO(img_content)
        image = Image.open(image)
        image = image.resize((224, 224))
        imag = np.reshape(image, [1, 224, 224, 3])
        imag = np.array(imag, dtype=np.float32)
        img = (imag.astype(np.float32) / 127.0) - 1
    except Exception as e:
        print(f'image not "RGB" format {e}')

    else:
        interpreter.set_tensor(input_details[0]['index'], img)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        presentTime = str(time.time_ns())
        ImageId = f"Image{presentTime}" + str(buffer).zfill(3)
        buffer = (buffer + random.randint(0, 200)) % 1000
        l = list(output_data[0])
        index = l.index(max(l))
        if index == 0:
            food_folder = "/tmp/" + x[index] + restId + "/"
            image_temp = Image.open(image_temp)
            image_temp.save(food_folder + ImageId + ".jpg", quality=quality)
            print(f"{ImageId} saved in {food_folder} folder")

        elif index == 2:
            menu_folder = "/tmp/" + x[index] + restId + "/"
            image_temp = Image.open(image_temp)
            image_temp.save(menu_folder + ImageId + ".jpg")
            print(f"{ImageId} saved in {menu_folder} folder")

        elif index == 3:
            Restaurant_folder = "/tmp/" + x[index] + restId + "/"
            image_temp = Image.open(image_temp)
            image_temp.save(Restaurant_folder + ImageId + ".jpg")
            print(f"{ImageId} saved in {Restaurant_folder} folder")


def get_image(pf, ul, resID):
    i = 1
    headers = {'User-Agent': 'Mozilla/5.0'}
    flag = 1
    try:
        for post in get_posts(pf):
            try:
                a = post['image']
            except Exception as e:
                print(e)
                continue

            if a == None:
                continue
            url = f"{a}"
            flag = 0
            try:
                r = requests.get(url, headers=headers, timeout=30)
                size = int(r.headers['content-length']) / 1000
                if size > 25 and size < 3000:
                    classification(r.content, resID, 'web_maximum')
                elif size >= 3000:
                    print(r.status_code)
                    classification(r.content, resID, 75)
            except Exception as e:
                print(e + "error in creating file")
                continue
        if flag:
            scrap_image(ul, resID)

    except Exception as e:
        scrap_image(ul, resID)


def scrap_image(url, resID):
    i = 1
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        images = soup.find_all("img")
        urls = []
        for image in images:
            if image.has_attr('src'):
                u = image["src"]
                newUrl = urljoin(url, u)
                urls.append(newUrl)

        for link in urls:
            try:
                if "static.wixstatic.com" in link:
                    p = link.find(".png")
                    link = link[:p+4]

                r = requests.get(link, headers=headers, timeout=30)
                size = int(r.headers['content-length']) / 1000
                if r.status_code == 200 and size > 25 and size < 3000:
                    print(r.status_code)
                    classification(r.content, resID, 'web_maximum')
                elif size >= 3000:
                    print(r.status_code)
                    classification(r.content, resID, 75)
                else:
                    print(f"{link} generated {r.status_code}")

            except Exception as e:
                print(f"{link} - {e}")
    except Exception as e:
        print(f"{url} failed to load - {e}")


def Searching_url(query, temp):

    global headers, user_agent_list, m
    if temp:
        url = 'https://www.google.com/search?' + \
            urllib.parse.urlencode({'q': query})
    else:
        url = 'http://www.google.com/search?' + \
            urllib.parse.urlencode({'q': 'facebook.com/' + query})

    try:
        user_agent = random.choice(user_agent_list)
        headers['User-Agent'] = user_agent
        page = requests.get(url, headers=headers, verify=False, timeout=60)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            a = soup.find_all('a')
            for j in a:
                try:
                    k = j.get('href')
                    m = re.search("(?P<url>https?://[^\s]+)", k)
                    n = m.group(0)
                    rul = n.split('&')[0]
                    domain = urlparse(rul)
                    if (re.search('google.com', domain.netloc)):
                        continue
                    elif not temp and (re.search('facebook.com', domain.netloc)):
                        return rul
                    else:
                        return rul
                except Exception as e:
                    continue
    except Exception as e:
        print(e)
        time.sleep(m)
        m *= 2
        if m > 248:
            return None
        return Searching_url(query, temp)


def getImage(restName, restId, area, website):

    create_folders(restId)
    print("Begining fetching urls...")
    urls = []
    if website:
        urls.append(website)
    else:
        web_query = f'"{restName}" {area}'
        web = Searching_url(web_query, True)
        if web:
            urls.append(web)

    facebook_query = f"{restName} {area}"
    response = Searching_url(facebook_query, False)
    if response:
        urls.append(response)

    s = set(urls)

    print(restName, ": urls:", s)
    for url in s:
        if "facebook" in url:
            print("Begining fetching images from facebook...")
            a = url.split('/')
            get_image(a[3], url, restId)
            print("fetched images from facebook")
        else:
            print("Begining fetching images from website...")
            scrap_image(url, restId)
            print("fetched images from website")

    return "Yes"
