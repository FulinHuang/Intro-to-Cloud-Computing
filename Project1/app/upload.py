from flask import render_template
from app import app

import mysql.connector

@app.route('/upload',methods=['GET'])
def upload_fake():

    cnx = mysql.connector.connect(user='root ',
                                  password='lu19920218',
                                  host='127.0.0.1',
                                  database='estore')

    cursor = cnx.cursor()
    query = "SELECT * FROM customer"
    cursor.execute(query)
    view = render_template("upload.html",title="Test Table", cursor=cursor)
    cnx.close()
    return view
