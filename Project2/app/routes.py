from app import app
from flask import render_template, url_for, redirect, flash, jsonify, make_response, request
from app import app, db
from app.AutoScaleDB import AutoScaleDB
from app import awsManager
from app import auto_scaler
from app import AutoScaleDB
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
import schedule

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
    running_instances = awsmanager.get_user_instances('running')
    for instance in running_instances:
        instance_ids.append(instance.id)
    num_instance = len(instance_ids)
    max_instance = 8

    if num_instance < max_instance:
        awsmanager.create_new_instance()
    else:
        print('Full work load!')
    return redirect(url_for('worker_control'))


@app.route('/decrease_workers', methods=['GET', 'POST'])
def decrease_workers():
    instance_ids = []
    running_instances = awsmanager.get_user_instances('running')
    for instance in running_instances:
        instance_ids.append(instance.id)
    num_instance = len(instance_ids)
    min_instance = 1

    if num_instance > min_instance:
        awsmanager.remove_instance(instance_ids[0])
    else:
        print("Cannot remove: min work load")
        instances_new = awsmanager.get_user_instances('running')

        inst_id_new = []
        for instance in instances_new:
            inst_id_new.append(instance.id)
        print('Our worker pool has', len(inst_id_new), "instances running currently.")
    return redirect(url_for('worker_control'))


# @app.before_first_request
# # Automatically check if any instance exists.
# # Resize the worker pool size to 1
# # If no instance exists, create one
# # If more than one instance, delete to one
# def auto_check():
#     print('Initiating first check...')
#
#     instances = awsmanager.get_user_instances('running')
#     inst_id = []
#
#     for instance in instances:
#         inst_id.append(instance.id)
#
#     print("There are ", len(inst_id), " running instances")
#
#     if len(inst_id) > 1:
#         print('We currently have {} instance running, will shrink to 1...'.format(len(inst_id)))
#         for i in range(1, len(inst_id)):
#             awsmanager.remove_instance(inst_id[i])
#             print('This instance: {} has been removed successfully.'.format(inst_id[i]))
#
#     elif len(inst_id) == 0:
#         print('No running instances exist, we are create an instance...')
#         awsmanager.create_new_instance()
#
#
#     else:
#         print('Our worker pool has 1 instance running currently, initiating done.')


#@app.before_first_request
def db_init():
    # db_value = AutoScaleDB(
    #     cpu_max=70,
    #     cpu_min=20,
    #     ratio_expand=2,
    #     ratio_shrink=0.5,
    #     timestamp=datetime.now())
    # db.session.add(db_value)
    # db.session.commit()
    # print("Database is initialized")

    schedule.every(1).minutes.do(auto_scaler.auto_scaler())

# Manually set the threshold and ratio for auto scaling, and save in database
@app.route("/auto_scale_input", methods=['GET', 'POST'])
def auto_scale():
    if request.method == 'POST':
        threshold_max = request.form['threshold_max']
        threshold_min = request.form['threshold_min']
        ratio_expand = request.form['ratio_expand']
        ratio_shrink = request.form['ratio_shrink']

        u1 = AutoScaleDB(cpu_max=threshold_max,
                         cpu_min=threshold_min,
                         ratio_expand=ratio_expand,
                         ratio_shrink=ratio_shrink)
        db.session.add(u1)
        db.session.commit()  # add to the database

        return render_template("auto_scale_input.html", success = True)
    else:
        return render_template("auto_scale_input.html")

# Display DNS of Load Balancer
@app.route('/DNSloadbalancer')
def DNSloadbalancer():
    print('The DNS name of the load balancer is displayed...')
    return render_template("DNSloadbalancer.html")