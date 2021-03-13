import boto3
from app import app, db
from app.AutoScaleDB import AutoScaleDB
from app import awsManager
from sqlalchemy import desc


manager = awsManager.Manager()

def get_data():
    autoDb = AutoScaleDB.order_by(desc(AutoScaleDB.id)).first()
    return autoDb


def auto_scaler():
    autoDb = auto_scaler()

    avg_threshold = 0  # TODO: change it to average cpu

    instance_ids = []
    running_instances = manager.get_user_instances('running')

    for instance in running_instances:
        instance_ids.append(instance.id)

    num_instance = len(instance_ids)

    max_instance = 8
    min_instance = 1

    if avg_threshold > autoDb.cpu_max and num_instance < max_instance:
        manager.increase_worker(autoDb.ratio_expand, num_instance, max_instance)


    elif avg_threshold < autoDb.cpu_min and num_instance > min_instance:
        manager.decrease_worker(autoDb.ratio_shrink, instance_ids, num_instance, min_instance)

    else:
        print("No change")



if __name__ ==   '__main__':
    auto_scaler()
    # TODO: Schedule time

