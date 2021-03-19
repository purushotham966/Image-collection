import boto3

bucket = "image-collection-foodvyberestaurantimagebucket-p0hdyzhm29gm"
s3_client = boto3.client("s3", region_name="us-east-1")
while True:
    list = s3_client.list_objects(Bucket=bucket)
    l = list['Contents']
    
    count = 0
    for o in l:
        # if 'RestId' in o['Key']:
            # s3_client.delete_object(Bucket=bucket, Key=o['Key'])
        count += 1
            
    print(count)
     
