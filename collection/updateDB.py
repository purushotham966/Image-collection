import json
import requests
from pymongo import MongoClient
import boto3
import json

success = 0
fail = 0
i = 0
def updatedb(bucketname):
    global i
    try:
        srv = "mongodb+srv://Krishna:bkiXbKDjiZx1OXf5@cluster0.g1xd9.mongodb.net/test?authSource=admin"
        client = MongoClient(srv)
        db_name = "image-collection2"
        db = client[db_name]
        collection_name = "restaurant_images"
        collection = db[collection_name]
    except Exception as e:
        print("Exception in mongo connection -", e)
    else:
        try:
            s3_client = boto3.client("s3", region_name="us-east-1")
            s3_client.download_file(
                bucketname, "Restaurant.json", "/tmp/Restaurant.json")
            with open("/tmp/Restaurant.json") as f:
                data = json.load(f)
            print(len(data))
        except Exception as e:
            print("Exception in json file -", e)
        else:
            for rest in data:
                try:
                    update_db(rest,bucketname,collection)
                except Exception as e:
                    print(f"Exception in {rest} - {e}")

def ListFiles(bucketname, client, key):
    """List files in specific S3 URL"""
    response = client.list_objects(Bucket=bucketname, Prefix=key)
    for content in response.get('Contents', []):
        yield content.get('Key')


def update_db(rest, bucketname, collection):
    print("in second function\n")
    global success,fail
    URLS = []
    restId = rest["restaurantId"]
    s3_url = f"https://{bucketname}.s3.amazonaws.com/"
    s3_client = boto3.client("s3", region_name="us-east-1")
    file_list = ListFiles(bucketname, s3_client, f"{restId}/Restaurant/")
    
    try:
        for file in file_list:
            if ".jpg" in file:
                I_id = file.split("/")[2].replace(".jpg", "")
                d = {
                    "_id": I_id,
                    "imageUrl": s3_url + file,
                    "restaurantId": restId,
                    "ImageId": I_id,
                    "userId" : "60142409180a780290b48346",
                    "postedBy" : "USER"
                }
                URLS.append(d)
    except Exception as e:
        print(f"Exception in {restId} - {e}")
    try:
        collection.insert_many(URLS)
        success += 1
        print(success+fail)
    except Exception as e:
        fail += 1
        print(f"{fail} Exception in updating document - {e}")
        print(success+fail)

