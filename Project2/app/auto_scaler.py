from app import app, db
from app.AutoScaleDB import AutoScaleDB
from app import awsManager 
from datetime import datetime


manager = awsManager.Manager()

def get_data():
   db.session.commit()  # update the database, otherwise we cannot get the latest value
   autoDb = db.session.query(AutoScaleDB).order_by(AutoScaleDB.id.desc()).first()
   cpu_max = autoDb.cpu_max
   cpu_min = autoDb.cpu_min
   ratio_expand = autoDb.ratio_expand
   ratio_shrink = autoDb.ratio_shrink

   if cpu_max is None or cpu_max == '' or float(cpu_max) <= 0:
       cpu_max = 80
   if cpu_min is None or cpu_min == '' or float(cpu_min) <= 0:
       cpu_min = 10
   if ratio_expand is None or ratio_expand == '' or float(ratio_expand) <= 0:
       ratio_expand = 2
   if ratio_shrink is None or ratio_shrink == '' or float(ratio_shrink) <= 0:
       ratio_shrink = 0.5

   db_value = AutoScaleDB(
       cpu_max=cpu_max,
       cpu_min=cpu_min,
       ratio_expand=ratio_expand,
       ratio_shrink=ratio_shrink,
       timestamp=datetime.now())
   db.session.add(db_value)
   db.session.commit()

   autoDb = db.session.query(AutoScaleDB).order_by(AutoScaleDB.id.desc()).first()

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

    print(datetime.now(), " There are {} running instances".format(num_instance))

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

