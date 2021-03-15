from app import app
from flask import render_template, url_for, redirect, flash, jsonify, make_response, request
from app import app, db
from app import manager
from app import awsManager
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

awsmanager = awsManager.Manager()


# from app.form import autoscalingForm, Photo, User

# Worker list page: select each running instance and show the details in worker_list.html
@app.route('/worker_list')
def worker_list():
    instance = awsmanager.get_user_instances('running')
    return render_template('worker_list.html', instance_list=instance)


@app.route('/')
@app.route('/home')
def home():
    plt.switch_backend('agg') #Allen - resolve plt runtime error
    #    x_axis, inst_num = 5, 5 #test
    x_axis, inst_num = awsmanager.number_workers()
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
    time_list, cpu_list = awsmanager.inst_CPU(instance_id)
    list_time, http_list = awsmanager.inst_HTTP(instance_id)
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
    instance_ids = []
    running_instances = manager.get_user_instances('running')
    for instance in running_instances:
        instance_ids.append(instance.id)
    num_instance = len(instance_ids)
    max_instance = 8

    if num_instance < max_instance:
        awsManager.create_new_instance()
    else:
        print('Full work load!')
    redirect(url_for('worker_control'))



@app.route('/decrease_workers', methods=['GET', 'POST'])
def decrease_workers():
    instance_ids = []
    running_instances = manager.get_user_instances('running')
    for instance in running_instances:
        instance_ids.append(instance.id)
    num_instance = len(instance_ids)
    min_instance = 1

    if num_instance > min_instance:
        awsManager.remove_instance(instance_ids[0])
    else:
        print("Cannot remove: min work load")

    return redirect(url_for('worker_control'))
