# configuration file, contains the essential info for instances and load balancer
import os

image_id = 'ami-0a1a1906efbd4c711'
key_pair = 'Allen_A2'
security_group = 'launch-wizard-1'
#user_data = '''Content-Type: multipart/mixed; boundary="//"
#MIME-Version: 1.0

#--//
#Content-Type: text/cloud-config; charset="us-ascii"
#MIME-Version: 1.0
#Content-Transfer-Encoding: 7bit
#Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
#cloud_final_modules:
#- [scripts-user, always]

#--//
#Content-Type: text/x-shellscript; charset="us-ascii"
#MIME-Version: 1.0
#Content-Transfer-Encoding: 7bit
#Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
#cd /home/ubuntu/Desktop
#./start.sh
#--//'''
elb_arn = 'arn:aws:elasticloadbalancing:us-east-1:011441637402:loadbalancer/app/allena2ELB/5360f782e6428bc4'
elb_dns = 'allena2ELB-168220349.us-east-1.elb.amazonaws.com'
elb_name = 'allena2ELB'
target_group_arn = 'arn:aws:elasticloadbalancing:us-east-1:011441637402:targetgroup/allena2/c1b769c7b4575737'
target_group_dimension = 'targetgroup/allena2/c1b769c7b4575737'

ELB_dimension = 'app/loadbalancer/3a7654beb0b62d6f'
iam_arn = 'arn:aws:iam::767240586870:instance-profile/S3FullAccess'

worker_group = 'usergroup'  # placement group for workers
manager_group = 'managergroup'  # placement group for managers

# INSTANCE_ID = 'i-027a3b0141ec3303f'
# ZONE = 'us-east-1f'
BUCKET_NAME = 'allena2'

class Config(object):
    SECRET_KEY = 'ECE1779'
    SQLALCHEMY_DATABASE_URI = 'mysql://allen_admin:lu19920218@allen-ece1779-a1.c7mezzt0p0rf.us-east-1.rds.amazonaws.com/dbname'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


