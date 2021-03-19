import json
import requests
import time
import concurrent.futures
from concurrent.futures import ALL_COMPLETED
import math


def genRows(data):
    for rest in data:
        yield rest

def api_call(rest):
    global url, head
    body = {
        "flag" : True,
        "restName": rest["name"],
        "area": rest["area"],
        "restId": rest["restaurantId"],
        "website":  rest["website"]
    }
    r = requests.request("POST", url, headers=head, data=json.dumps(body))
    return r.status_code

def download_images(data):
    totalrows = len(data)
    print(totalrows)
    threads = 100
    correct = 0
    rest = genRows(data)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for _ in range(math.ceil(totalrows / threads)):
            if totalrows > threads:
                k = threads
                totalrows -= threads
                print("total rows remaining: ", totalrows)
            else:
                k = totalrows

            try:
                future = [executor.submit(api_call, next(rest)) for i in range(k)]
                time.sleep(10)
                for thread in future:
                    try:
                        statusCode = thread.result()
                        if statusCode == 200:
                            correct += 1
                    except StopIteration as e:
                        break
                    except Exception as e:
                        print(e)
            except StopIteration as e:
                break
            except Exception as e:
                if (concurrent.futures.wait(future, timeout=None, return_when=ALL_COMPLETED)):
                    break

def updateDatabase():
    global url, head
    body = {
        "flag": False
    }
    r = requests.request("POST", url, headers=head, data=json.dumps(body))
    print(r.status_code)

if __name__ == '__main__':

    # with open("Restaurant.json") as file:
    #     data = json.load(file)

    url = "https://xqankxb325.execute-api.us-east-1.amazonaws.com/Prod/collection"

    head = {
        "InvocationType": "Event",
        'Content-Type': "application/json"
    }

    # download_images(data)
    updateDatabase()



    






