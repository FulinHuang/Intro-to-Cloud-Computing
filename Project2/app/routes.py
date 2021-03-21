from app import app
from flask import render_template, url_for, redirect, request
from app import app, db
from app.user import User
from app.photo import Photo
from app.AutoScaleDB import AutoScaleDB
from app import awsManager
from app import auto_scaler
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import io
import base64
from app import config
from datetime import datetime, timedelta
import time
import requests
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import desc
import boto3

# Initialize variables
awsmanager = awsManager.Manager()
scheduler = BackgroundScheduler()
scheduler.daemonic = False
atexit.register(lambda: scheduler.shutdown())



# Home page
@app.route('/')
@app.route('/home')
def home():
    plt.switch_backend('agg') #Allen - resolve plt runtime error
    x_axis, inst_num = awsmanager.number_workers()

    #create the plot
    formatter = DateFormatter('%H:%M') # example '%Y-%m-%d %H:%M:%S'
    fig, ax = plt.subplots()
    plt.plot_date(x_axis, inst_num, marker='*', linestyle='-')
    plt.xlabel('Time', fontsize=10)
    plt.ylabel('Instance number', fontsize=10)
    ax.xaxis.set_major_formatter(formatter)
    ax.set_xlim([datetime.utcnow() - timedelta(hours=4.6), datetime.utcnow()- timedelta(hours=4)])
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
    # plot for CPU UTIL
    formatter = DateFormatter('%H:%M') # example '%Y-%m-%d %H:%M:%S'
    fig, ax = plt.subplots()
    plt.plot_date(time_list, cpu_list, marker='*', linestyle='-')
    #plt.plot(time_list, cpu_list, 'k', marker='+')
    plt.xlabel('Time', fontsize=10)
    plt.ylabel('CPU utilization (%)', fontsize=10)
    ax.xaxis.set_major_formatter(formatter)
    ax.set_xlim([datetime.utcnow() - timedelta(hours=4.6), datetime.utcnow() - timedelta(hours=4)])
    buf_CPU = io.BytesIO()
    plt.savefig(buf_CPU, format='png')
    plt.close()
    buf_CPU.seek(0)
    buffer = b''.join(buf_CPU)
    b2 = base64.b64encode(buffer)
    CPU_img = b2.decode('utf-8')

    # plot for HTTP REQ
    formatter = DateFormatter('%H:%M') # example '%Y-%m-%d %H:%M:%S'
    fig, ax = plt.subplots()
    plt.plot_date(list_time, http_list , marker='*', linestyle='-')
    #plt.plot(list_time, http_list, 'k', marker='+')
    plt.xlabel('Time (minutes)', fontsize=10)
    plt.ylabel('Http request(Count)', fontsize=10)
    ax.xaxis.set_major_formatter(formatter)
    ax.set_xlim([datetime.utcnow() - timedelta(hours=4.6), datetime.utcnow() - timedelta(hours=4)])
    buf_HTTP = io.BytesIO()
    plt.savefig(buf_HTTP, format='png')
    plt.close()
    buf_HTTP.seek(0)
    buffer2 = b''.join(buf_HTTP)
    b3 = base64.b64encode(buffer2)
    HTTP_img = b3.decode('utf-8')

    return render_template('workers.html', instance_id=instance_id, CPU_img=CPU_img, HTTP_img=HTTP_img)


# Display a list of workers & detail info
@app.route('/worker_list')
def worker_list():
    instance = awsmanager.get_user_instances('running')
    return render_template('worker_list.html', instance_list=instance)


# A page for user to increase or decrease a worker
@app.route('/worker_control')
def worker_control():
    title = 'Worker Control'
    return render_template('worker_control.html', title=title)


# Increase a worker
@app.route('/increase_workers', methods=['GET', 'POST'])
def increase_workers():
    running_ids = []
    pending_ids = []
    running_instances = awsmanager.get_user_instances('running')
    pending_instances = awsmanager.get_user_instances('pending')

    for instance in running_instances:
        running_ids.append(instance.id)
    for instance in pending_instances:
        pending_ids.append(instance.id)

    num_instance = len(running_ids) + len(pending_ids)
    max_instance = 8

    if num_instance < max_instance:
        awsmanager.create_new_instance()
    else:
        print('Full work load!')
    return redirect(url_for('worker_control'))


# Decrease a worker
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



# A page for user to add customized values to the auto scaler
@app.route("/auto_scale_input", methods=['GET', 'POST'])
def auto_scale_input():
    if request.method == 'POST':
        threshold_max = request.form['threshold_max']
        threshold_min = request.form['threshold_min']
        ratio_expand = request.form['ratio_expand']
        ratio_shrink = request.form['ratio_shrink']

        u1 = AutoScaleDB(cpu_max=threshold_max,
                         cpu_min=threshold_min,
                         ratio_expand=ratio_expand,
                         ratio_shrink=ratio_shrink,
                         timestamp=datetime.now())
        db.session.add(u1)
        db.session.commit()  # add to the database

        return render_template("auto_scale_input.html", success=True)
    else:
        return render_template("auto_scale_input.html")

# A page to display the DNS link
@app.route('/DNSloadbalancer')
def DNSloadbalancer():
    print('The DNS name of the load balancer is displayed...')
    return render_template("DNSloadbalancer.html")


# Terminate workers and stop manager
@app.route('/stop_terminate')
def stop_terminate():
    # Stop scheduling
    jobs = scheduler.get_jobs()
    jobs[0].remove()

    # Terminate worker and stop manager
    awsmanager.terminate_all()
    print('The manager instance has stopped.')

    return render_template("terminate_all.html")

# Delete all data
@app.route('/delete_data')
def remove_all_data():

    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(config.s3_name)
    bucket.objects.all().delete()
    # db.session.query(User).delete()
    User.query.filter(User.username != 'admin').delete()
    db.session.query(Photo).delete()
    db.session.query(AutoScaleDB).delete()
    db.session.commit()

    return render_template("delete_data.html")


# Check the # workers before launching the website
@app.before_first_request
def auto_check():
    print('Initializing')

    instances = awsmanager.get_user_instances('running')
    inst_id = []

    for instance in instances:
        inst_id.append(instance.id)

    print("There are ", len(inst_id), " running instances")


    if len(inst_id) == 0:
        print(datetime.now(), 'No running instances exist, we are create an instance...')
        awsmanager.create_new_instance()

    elif len(inst_id) > 1:
        print(datetime.now(), 'We currently have {} instance running, will shrink to 1...'.format(len(inst_id)))
        for i in range(1, len(inst_id)):
            awsmanager.remove_instance(inst_id[i])
            print(datetime.now(), 'This instance: {} has been removed successfully.'.format(inst_id[i]))

    else:
        print(datetime.now(), 'Our worker pool has 1 instance running currently, initiating done.')


    # Initialize the database & start auto-scaler before launching the website
    value = AutoScaleDB.query.order_by(desc(AutoScaleDB.id)).first()
    if value is None:
        db_value = AutoScaleDB(
            cpu_max=80,
            cpu_min=10,
            ratio_expand=2,
            ratio_shrink=0.5,
            timestamp=datetime.now())
        db.session.add(db_value)
        db.session.commit()
        print("Database is initialized")

    scheduler.add_job(auto_scaler.auto_scaler, trigger='interval', minutes=1, max_instances=60)
    scheduler.start()