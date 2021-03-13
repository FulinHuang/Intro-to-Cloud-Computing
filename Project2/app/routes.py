from app import app
from flask import render_template, url_for, redirect, flash, jsonify, make_response, request
from app import app, db
from app import manager
import matplotlib.pyplot as plt
import io
import base64
import boto3
from app import config
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import time
import requests

# from app.form import autoscalingForm, Photo, User

# Worker list page: select each running instance and show the details in worker_list.html
@app.route('/worker_list')
def worker_list():
    instance = manager.select_running_inst()
    return render_template('worker_list.html', instance_list=instance)


@app.route('/')
@app.route('/home')
def home():
    plt.switch_backend('agg') #Allen - resolve plt runtime error
    #    x_axis, inst_num = 5, 5 #test
    x_axis, inst_num = manager.number_workers()
    plt.plot(x_axis, inst_num, marker='+')
    plt.xlabel('Time (minutes)', fontsize=10)
    plt.ylabel('Instance number', fontsize=10)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    buffer = b''.join(buf)
    b2 = base64.b64encode(buffer)  # Encode and decode image
    instance_num_image = b2.decode('utf-8')
    return render_template('home.html', instance_num=instance_num_image)


# Plot the CPU utilization and HTTP request for each running instance
@app.route('/<instance_id>', methods=['GET', 'POST'])
def view(instance_id):
    plt.switch_backend('agg') #Allen - resolve plt runtime error
    time_list, cpu_list = manager.inst_CPU(instance_id)
    list_time, http_list = manager.inst_HTTP(instance_id)
    plt.plot(time_list, cpu_list, 'k', marker='+')
    plt.xlabel('Time (minutes)', fontsize=10)
    plt.ylabel('CPU utilization (%)', fontsize=10)
    buf_CPU = io.BytesIO()
    plt.savefig(buf_CPU, format='png')
    plt.close()
    buf_CPU.seek(0)
    buffer = b''.join(buf_CPU)
    b2 = base64.b64encode(buffer)
    CPU_img = b2.decode('utf-8')

    plt.plot(list_time, http_list, 'k', marker='+')
    plt.xlabel('Time (minutes)', fontsize=10)
    plt.ylabel('Http request(Count)', fontsize=10)
    buf_HTTP = io.BytesIO()
    plt.savefig(buf_HTTP, format='png')
    plt.close()
    buf_HTTP.seek(0)
    buffer2 = b''.join(buf_HTTP)
    b3 = base64.b64encode(buffer2)
    HTTP_img = b3.decode('utf-8')

    return render_template('workers.html', instance_id=instance_id, CPU_img=CPU_img, HTTP_img=HTTP_img)


# Worker control page: increase workers or decrease workers
@app.route('/worker_control')
def worker_control():
    title = 'Worker Control'
    return render_template('worker_control.html', title=title)


@app.route('/increase_workers', methods=['GET', 'POST'])
def increase_workers():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[

            {'Name': 'placement-group-name',
             'Values': [config.worker_group]},

            {'Name': 'instance-state-name',
             'Values': ['running']},  # filter running instances

            {'Name': 'image-id',
             'Values': [config.image_id]},
        ]
    )


@app.route('/decrease_workers', methods=['GET', 'POST'])
def decrease_workers():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[

            {'Name': 'placement-group-name',
             'Values': [config.worker_group]},

            {'Name': 'instance-state-name',
             'Values': ['running']},

            {'Name': 'image-id',
             'Values': [config.image_id]},
        ]
    )
    # Select the running instances
    inst_id = []
    for instance in instances:
        inst_id.append(instance.id)

    # If there are more than one running instances, remove the oldest one
    if len(inst_id) > 1:
        inst_Id = inst_id[0]  # instance ID of the removing instance
        print('Deregistering instance-ID:', inst_Id)
        elb = boto3.client('elbv2')
        elb.deregister_targets(
            TargetGroupArn=config.target_group_arn,
            Targets=[
                {
                    'Id': inst_Id,
                },
            ]
        )

        waiter = elb.get_waiter('target_deregistered')
        waiter.wait(
            TargetGroupArn=config.target_group_arn,
            Targets=[
                {
                    'Id': inst_Id,
                },
            ],
        )
        print('Instance-ID: ', inst_Id, 'is deregistered!')

        print('Terminating instance-ID:', inst_Id)
        # Check whether the instance can be found by its ID
        instance = ec2.instances.filter(InstanceIds=[inst_Id])
        if instance is not None:
            for inst in instance:
                inst.terminate()
                # Waits until the instance is terminated
                inst.wait_until_terminated(
                    Filters=[
                        {
                            'Name': 'instance-id',
                            'Values': [inst.id]
                        },
                    ],
                )
                print('Instance-ID: ', inst.id, ' is terminated')

    return redirect(url_for('worker_control'))
