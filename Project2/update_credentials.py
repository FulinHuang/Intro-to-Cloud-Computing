import requests
#import json
import os

output_path = "/home/ubuntu/.aws"
output_name = "credentials"

#with open ('metadata.json') as json_file:
#    data = json.load(json_file)

r = requests.get('http://169.254.169.254/latest/meta-data/iam/security-credentials/S3_RDS_FULL')
data = r.json()

access_key_id = data["AccessKeyId"]
secret_access_key = data["SecretAccessKey"]
token = data["Token"]

with open(os. path. join(output_path, output_name),"w+") as output_file:
    output_file.write('[default]\n')
    output_file.write('aws_access_key_id='+access_key_id+'\n')
    output_file.write('aws_secret_access_key='+secret_access_key+'\n')
    output_file.write('aws_session_token='+token+'\n')
print('AWS credential is updated.')
# [default]
# aws_access_key_id=ASIAXEBISTHMVLRT42PQ
# aws_secret_access_key=Fqm41YCJ632TTuiX+HbwJzVuQSS5Shp+rQWX7gSP
# aws_session_token=FwoGZXIvYXdzEBYaDISVQVdrMF
