import requests
#import json
import os

output_path = "/home/ubuntu/.aws"
output_name = "credentials"

#with open ('metadata.json') as json_file:
#    data = json.load(json_file)

r = requests.get('somepath')
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

