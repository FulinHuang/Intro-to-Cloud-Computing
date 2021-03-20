from app import app, db
from app.AutoScaleDB import AutoScaleDB
from app import awsManager 
from sqlalchemy import desc
import schedule
from datetime import datetime


manager = awsManager.Manager()

def get_data():
    autoDb = AutoScaleDB.query.order_by(desc(AutoScaleDB.id)).first()
    return autoDb


def auto_scaler():
    print("Running auto scaler")

    autoDb = get_data()
    instance_ids = []

    running_instances = manager.get_user_instances('running')
    avg_threshold = manager.avg_cpu(running_instances)

    for instance in running_instances:
        instance_ids.append(instance.id)

    num_instance = len(instance_ids)


    valid = manager.valid_for_autoscale()
    print(valid)

    max_instance = 8
    min_instance = 1

    print("There are {} running instances".format(num_instance))

    if valid:

        print("Valid for autoscaling")
        print("avg cpu is ", avg_threshold)

        if avg_threshold > autoDb.cpu_max and num_instance < max_instance:

            print(datetime.now(), " threshold larger than cpu max - increase worker")
            manager.increase_worker(autoDb.ratio_expand, num_instance, max_instance)


        elif avg_threshold < autoDb.cpu_min and num_instance > min_instance:
            print(datetime.now(), " threshold smaller than cpu min - decrease worker")
            manager.decrease_worker(autoDb.ratio_shrink, instance_ids, num_instance, min_instance)

        else:
            print(datetime.now(), " Nothing changed")
    else:
        print(datetime.now(), " There are some pending or unhealthy instances."
                              " Autoscaler does not increase/decrease worker at this time")



