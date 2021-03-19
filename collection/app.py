import json
import scrapping
import boto3
import os
import numpy as np
import tflite_runtime.interpreter as tflite
from PIL import Image, ImageOps
import updateDB


bucketname = os.environ['bucketname']
s3_client = boto3.client("s3", region_name="us-east-1")

def upload_objects(restId):
    global s3_client,bucketname 
    food_path = f"/tmp/Food{restId}/"
    rest_path = f"/tmp/Restaurant{restId}/"
    menu_path = f"/tmp/Menu{restId}/"

    directory_name_food = f"{restId}/Food/"
    directory_name_rest = f"{restId}/Restaurant/"
    directory_name_menu = f"{restId}/Menu/"

    s3_client.put_object(Bucket=bucketname, Key=f"{directory_name_food}")
    s3_client.put_object(Bucket=bucketname, Key=f"{directory_name_rest}")
    s3_client.put_object(Bucket=bucketname, Key=f"{directory_name_menu}")

    try:
        files = os.listdir(food_path)
        for file in files:
            s3_client.upload_file(food_path+file, bucketname, f"{directory_name_food}{file}")
    except Exception as e:
        print("Exception in food directory", e)
        
    try:
        files = os.listdir(rest_path)
        for file in files:
            s3_client.upload_file(rest_path+file, bucketname, f"{directory_name_rest}{file}")
    except Exception as e:
        print("Exception in restaurant directory", e)
    try:
        files = os.listdir(menu_path)
        for file in files:
            s3_client.upload_file(menu_path+file, bucketname,
                                  f"{directory_name_menu}{file}")
    except Exception as e:
        print("Exception in Menu directory", e)

def lambda_handler(event, context):
    print(event)
    global s3_client,bucketname
    flag = event["flag"]

    if flag:
        restName = event['restName']
        area = event['area']
        restId = event['restId']
        website = event['website']

        file_name = "/tmp/model_unquant.tflite"

        try:
            with open(file_name, 'wb') as f:
                s3_client.download_fileobj(bucketname, f'classification_model/model_unquant.tflite', f)
        except Exception as e:
            print("model file not found",e)

        else:
            try:
                scrapping.getImage(restName, restId, area, website)
            except Exception as e:
                print("Exception in scrapping function", e)
            
            try:
                upload_objects(restId)
            except Exception as e:
                print("Exception in uploading files to s3 bucket",e)
    else:
        try:
            print("Updating mongodb...")
            updateDB.updatedb(bucketname)
        except Exception as e:
            print("Exception in updateDB function -",e)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "updated changes",
        }),
    }
