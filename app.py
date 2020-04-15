from flask import Flask, render_template, request, send_from_directory, url_for
import psycopg2
import os
import smtplib

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/wardrobe.html')
def wardrobe():
    conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT filename from wardrobe;
    """)
    stuff=[]
    for data in cursor:
        stuff.append(data[0])
    
    return render_template('wardrobe.html',path = stuff)
    conn.close()
    
    

@app.route('/insert.html',  methods=["POST","GET"])
def insert():
    conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
    cursor = conn.cursor()

    target = os.path.join(APP_ROOT, 'images/')
    print(target)
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("Accept incoming file:", filename)
        print ("Save it to:", destination)
        upload.save(destination)
        # with open (destination,'rb') as f:
        #     blob = f.read()
        # binary = psycopg2.Binary(blob)
        value = request.form.get("type")
        comment = request.form.get("comment")
        cursor.execute("INSERT INTO wardrobe (filename,type,comment) values ('%s','%s', '%s');"% (filename,value,comment) )
        conn.commit()
        conn.close()

    # return send_from_directory("images", filename, as_attachment=True)
    # return render_template("complete.html", image_name=filename)
    return render_template('insert.html')

@app.route('/insert/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

@app.route('/wardrobe/<value>')
def filter(value):
    conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
    cursor = conn.cursor()

    cursor.execute("""select filename from wardrobe WHERE type ='%s';"""%(value))
    stuff=[]
    for data in cursor:
        stuff.append(data[0])
    conn.close()

    return render_template('wardrobe.html',path = stuff)

@app.route('/edit.html/<filename>',methods=["POST","GET"])
def edit(filename):
    conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
    cursor = conn.cursor()

    cursor.execute("""SELECT filename, type, comment from wardrobe where filename = '%s';"""%(filename))
    for data in cursor:
        image = data[0]
        value = data[1]
        comment = data[2]

    target = os.path.join(APP_ROOT, 'images/')
    print(target)

    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        file = upload.filename
        destination = "/".join([target, file])
        print ("Accept incoming file:", file)
        print ("Save it to:", destination)
        upload.save(destination)
        # with open (destination,'rb') as f:
        #     blob = f.read()
        # binary = psycopg2.Binary(blob)
        newvalue = request.form.get("type")
        newcomment = request.form.get("comment")
        cursor.execute("UPDATE wardrobe SET filename = '%s' ,type = '%s' ,comment = '%s' WHERE filename = '%s';"% (file,newvalue,newcomment,image))
        conn.commit()
        conn.close()
    print(image, value, comment)

    return render_template('edit.html', image = image, value = value, comment = comment)

@app.route('/edit/<filename>')
def update_image(filename):
    return send_from_directory("images", filename)

@app.route('/trends.html')
def trends():
    return render_template('trends.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)