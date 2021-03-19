#!/bin/bash

# direct to the project folder
cd /home/ubuntu/Desktop/userapp2.0

# open the virtual environment and run the script
source venv/bin/activate

#awscli configurations(no longer used)
#curl https://169.254.169.254/latest/meta-data/iam/security-credentials/S3_RDS_FULL #> metadata.json

python update_credentials.py

gunicorn -w 8 -b 0.0.0.0:5000 run:app

# close the venv after termination
deactivate

echo Have a nice day!


