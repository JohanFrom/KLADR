from flask import Flask, render_template, request, send_from_directory, url_for, redirect
import psycopg2
import os
import smtplib

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
cursor = conn.cursor()

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/wardrobe.html')
def wardrobe():
    # conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
    # cursor = conn.cursor()

    cursor.execute("""
    SELECT filename from wardrobe;
    """)
    articles=[] 
    for data in cursor:
        articles.append(data[0])
    
    return render_template('wardrobe.html',path = articles)
    # conn.close()
    
    

@app.route('/insert.html',  methods=["POST","GET"])
def insert():
    # conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
    # cursor = conn.cursor()

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


        value = request.form.get("type")
        comment = request.form.get("comment")
        colour = request.form.get("colour")
        cursor.execute("INSERT INTO wardrobe (filename,type,comment,colour) values ('%s','%s', '%s','%s');"% (filename,value,comment,colour) )
        conn.commit()
        # conn.close()
        return redirect(request.args.get("next") or url_for("wardrobe"))

    # return send_from_directory("images", filename, as_attachment=True)
    return render_template('insert.html')

@app.route('/remove/<filename>', methods=["POST","GET"])
def remove(filename):
    # conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
    # cursor = conn.cursor()
    
    target = os.path.join(APP_ROOT, 'images/')
    destination = "/".join([target, filename])
    print ("Remove", destination)
    os.remove(destination)

    cursor.execute("""
        DELETE from outfit_article
        WHERE article_name = '%s';
    """ % (filename))
    
    cursor.execute("""
        DELETE from wardrobe
        WHERE filename = '%s';
    """ % (filename))

    conn.commit()
    # conn.close()
    
    return wardrobe()


@app.route('/edit/<filename>')
@app.route('/insert/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

@app.route('/wardrobe/<value>')
def filter(value):
    # conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
    # cursor = conn.cursor()

    cursor.execute("""select filename from wardrobe WHERE type ='%s' OR colour='%s';"""%(value, value))
    articles=[]
    for data in cursor:
        articles.append(data[0])
    # conn.close()

    return render_template('wardrobe.html',path = articles)

@app.route('/outfits.html')
def outfits():
    # conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
    # cursor = conn.cursor()
    cursor.execute("""
    SELECT filename from wardrobe;
    """)
    articles=[] 
    for data in cursor:
        articles.append(data[0])

    return render_template('outfits.html',path = articles)   


@app.route("/list_outfits")
def list_outfits():
    cursor.execute("""
        select name from outfit;
    """)
    outfit_names = [] #lista pa alla outfit namn

    for name in cursor:
        outfit_names.append(name[0])

    all_outfits = []

    for outfit_name in outfit_names:
        cursor.execute("""
            select article_name from outfit_article
            where outfit_name = '%s';
         """ % (outfit_name))
        temp = []
        #temp.append(outfit_name)
        for article in cursor:
            temp.append(article[0])
        all_outfits.append(temp)
    print(all_outfits)
    print(outfit_names)
    return render_template("list.html", outfits = all_outfits, names=outfit_names)
#prova att ha tva listor, en med namn och en med outfits

@app.route('/show_outfit/<outfit>')
def show_outfit(outfit):
    cursor.execute(
        """
        select article_name 
        from outfit_article 
        where outfit_name = '%s'; 
        
        """ % (outfit))
    
    outfit_articles = []
    for article in cursor:
        outfit_articles.append(article[0])
    
    print(outfit_articles)

    cursor.execute("""
        select comment
        from outfit
        where name = '%s'; 
        
        """ % (outfit))
    for record in cursor:
        comment = record[0]
    print(comment)

    return render_template('show_outfit.html', comment = comment, outfit_articles = outfit_articles, outfit=outfit)


@app.route('/edit_outfit/<outfit>', methods=["POST","GET"])
def edit_outfit(outfit):
    cursor.execute(
        """
        select article_name 
        from outfit_article 
        where outfit_name = '%s'; 
        
        """ % (outfit))
    
    outfit_articles = []
    for article in cursor:
        outfit_articles.append(article[0])   


    cursor.execute("""
        select comment
        from outfit
        where name = '%s'; 
        
        """ % (outfit))
    for record in cursor:
        comment = record[0]
    
    cursor.execute("""
        SELECT filename from wardrobe;

        """)
    wardrobe=[] 
    for data in cursor:
        wardrobe.append(data[0])

    return render_template('edit_outfit.html', wardrobe=wardrobe, comment=comment, outfit_articles=outfit_articles, outfit=outfit)

@app.route('/edit_outfit_form/<outfit>', methods=["POST","GET"])
def edit_outfit_form(outfit):
    cursor.execute("""
        DELETE
        FROM outfit_article
        WHERE outfit_name ='%s';
    """ % (outfit))


    new_outfit = request.form.get("name")
    new_comment = request.form.get("comment")
    cursor.execute("""
        UPDATE outfit
        SET name = '%s' , comment = '%s' WHERE name = '%s';
    """ % (new_outfit,new_comment,outfit))
    article_names = request.form.getlist("article")

    for name in article_names:
        cursor.execute("""
            insert into outfit_article 
            values ('%s','%s');
        """ % (new_outfit,name))
    conn.commit()

    return redirect(url_for('show_outfit', outfit = new_outfit))


@app.route('/add_outfit', methods=["POST","GET"])
def add_outfit():
    article_names = request.form.getlist("article")

    outfit_name = request.form.get("name")
    outfit_comment = request.form.get("comment")
    cursor.execute("""insert into outfit (name,comment) values('%s','%s');""" % (outfit_name, outfit_comment))

    
    for name in article_names:
        cursor.execute("""
            insert into outfit_article 
            values ('%s','%s');
        """ % (outfit_name,name))
    print (article_names)
    conn.commit()
    return redirect(url_for("wardrobe"))


@app.route('/edit.html/<filename>',methods=["POST","GET"])
def edit(filename):
    # conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
    # cursor = conn.cursor()

    cursor.execute("""SELECT filename, type, comment, colour from wardrobe where filename = '%s';"""%(filename))
    for data in cursor:
        image = data[0]
        value = data[1]
        comment = data[2]
        colour = data[3]

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
        newcolour = request.form.get("colour")
        cursor.execute("UPDATE wardrobe SET filename = '%s' ,type = '%s' ,comment = '%s', colour ='%s' WHERE filename = '%s';"% (file,newvalue,newcomment,newcolour,image))
        conn.commit()
        # conn.close()
        return redirect(request.args.get("next") or url_for("wardrobe"))

    print(image, value, comment)

    return render_template('edit.html', image = image, value = value, comment = comment, colour = colour)


@app.route('/trends.html')
def trends():
    return render_template('trends.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/about.html', methods = ["GET", "POST"])
def sendemail():
    user_text = request.form.get("text-input")
    user_email = "kladr2020@gmail.com"
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login("kladr2020@gmail.com", "kladr2020april")
    server.sendmail("kladr2020@gmail.com", user_email, user_text.encode("utf-8"))
    print(user_email, user_text)

    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)