from flask import Flask, session, render_template, request, send_from_directory, url_for, redirect, flash, g, escape
import psycopg2
import os
import smtplib

app = Flask(__name__)
app.secret_key = b'_5dg#y2L"F4Q87sjz\n\xec]/'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
conn = psycopg2.connect(dbname = "kladr", user = "aj9099", password="0obetr9j",host="pgserver.mah.se")
cursor = conn.cursor()

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/wardrobe.html')
def user_wardrobe():
    if 'username' in session:
        
        cursor.execute("""
        SELECT filename from wardrobe
        WHERE id = %s;
            """ % escape(session['username']))

        articles=[] 
        for data in cursor:
            articles.append(data[0])
        message = ""
        if len(articles) == 0:
            message = "Du har inga plagg tillagda i din garderob!"
    
        return render_template('wardrobe.html',path = articles, message = message)
    
    message = "Du är inte inloggad!"
    return render_template('wardrobe.html',path = [], message = message)    
    # conn.close()

@app.route('/wardrobe.html')
def wardrobe():
    cursor.execute("""
    SELECT filename from wardrobe where id = %s;
        """%(escape(session['username'])))
    articles=[] 
    for data in cursor:
        articles.append(data[0])
    message = "Du är inte inloggad!"
    
    return render_template('wardrobe.html',path = articles, message = message)
    # conn.close()
    

@app.route('/insert.html',  methods=["POST","GET"])
def insert():
    if 'username' in session:
    
        target = os.path.join(APP_ROOT, 'images/'+ escape(session['username']))
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
            cursor.execute("INSERT INTO wardrobe (filename,type,comment,colour,id) values ('%s','%s', '%s','%s',%s);"% (filename,value,comment,colour,escape(session['username']))) 
            conn.commit()
            # conn.close()
            flash('Plagg tillagt!')
            return redirect(request.args.get("next") or url_for("wardrobe"))

    # return send_from_directory("images", filename, as_attachment=True)
    return render_template('insert.html')

@app.route('/remove/<filename>', methods=["POST","GET"])
def remove(filename):
    
    target = os.path.join(APP_ROOT, 'images/'+ escape(session['username']))
    destination = "/".join([target, filename])
    print ("Remove", destination)
    os.remove(destination)

    cursor.execute("""
        DELETE from outfit_article
        WHERE article_name = '%s' and id = %s;
    """ % (filename,escape(session['username'])))
    
    cursor.execute("""
        DELETE from wardrobe
        WHERE filename = '%s' and id = %s;
    """ % (filename,escape(session['username'])))

    conn.commit()
    # conn.close()
    
    flash('Plagg borttaget!')
    return wardrobe()


@app.route('/edit/<filename>')
@app.route('/insert/<filename>')
def send_image(filename):
    return send_from_directory("images/"+escape(session['username']), filename)

@app.route('/wardrobe/<value>')
def filter(value):

    cursor.execute("""select filename from wardrobe WHERE (type ='%s' OR colour='%s') and id = %s;"""%(value, value,escape(session['username'])))
    articles=[]
    for data in cursor:
        articles.append(data[0])
    # conn.close()

    return render_template('wardrobe.html',path = articles)

@app.route('/outfits.html')
def outfits():
    
    articles = []
    if 'username' in session:
        cursor.execute("""
        SELECT filename from wardrobe where id = %s;
        """ % (escape(session['username'])))
        articles=[] 
        for data in cursor:
            articles.append(data[0])

    return render_template('outfits.html',path = articles)   


@app.route("/list_outfits")
def list_outfits():
    if 'username' in session:
        cursor.execute("""
            select name from outfit where id = %s;
        """ % (escape(session['username'])))

        outfit_names = [] #lista pa alla outfit namn

        for name in cursor:
            outfit_names.append(name[0])

        all_outfits = []

        for outfit_name in outfit_names:
            cursor.execute("""
                select article_name from outfit_article
                where outfit_name = '%s' and user_outfit_id = %s;
            """ % (outfit_name,escape(session['username'])))
            temp = []
            #temp.append(outfit_name)
            for article in cursor:
                temp.append(article[0])
            all_outfits.append(temp)
        print(all_outfits)
        print(outfit_names)
        return render_template("list.html", outfits = all_outfits, names=outfit_names)
    return render_template('list.html', outfits=[], names = [])
#prova att ha tva listor, en med namn och en med outfits

@app.route('/show_outfit/<outfit>')
def show_outfit(outfit):
    cursor.execute("""
                select article_name from outfit_article
                where outfit_name = '%s' and user_outfit_id = %s;
            """ % (outfit,escape(session['username'])))
    
    outfit_articles = []
    for article in cursor:
        outfit_articles.append(article[0])
    
    print(outfit_articles)

    cursor.execute("""
        select comment
        from outfit
        where name = '%s' and id = %s; 
        
        """ % (outfit, escape(session['username'])))
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
        where outfit_name = '%s' and user_outfit_id = %s; 
        
        """ % (outfit,escape(session['username'])))
    
    outfit_articles = []
    for article in cursor:
        outfit_articles.append(article[0])   


    cursor.execute("""
        select comment
        from outfit
        where name = '%s' and id = %s; 
        
        """ % (outfit,escape(session['username'])))
    for record in cursor:
        comment = record[0]
    
    cursor.execute("""
        SELECT filename from wardrobe where id = %s;

        """ % (escape(session['username'])))
    wardrobe=[] 
    for data in cursor:
        wardrobe.append(data[0])

    return render_template('edit_outfit.html', wardrobe=wardrobe, comment=comment, outfit_articles=outfit_articles, outfit=outfit)

@app.route('/edit_outfit_form/<outfit>', methods=["POST","GET"])
def edit_outfit_form(outfit):
    cursor.execute("""
        DELETE
        FROM outfit_article
        WHERE outfit_name ='%s' and user_outfit_id = %s;
    """ % (outfit, escape(session['username'])))


    new_outfit = request.form.get("name")
    new_comment = request.form.get("comment")
    cursor.execute("""
        UPDATE outfit
        SET name = '%s' , comment = '%s' WHERE name = '%s'and id = %s;
    """ % (new_outfit,new_comment,outfit, escape(session['username'])))
    article_names = request.form.getlist("article")

    for name in article_names:
        cursor.execute("""
            insert into outfit_article (outfit_name,article_name, id, user_outfit_id)
            values ('%s','%s',%s,%s);
        """ % (new_outfit,name,escape(session['username']),escape(session['username'])))
    conn.commit()

    return redirect(url_for('show_outfit', outfit = new_outfit))

@app.route('/remove_outfit/<outfit>',methods = ["POST","GET"])
def remove_outfit(outfit):
    cursor.execute("""
    DELETE
    FROM outfit_article
    WHERE outfit_name = '%s' and user_outfit_id = %s;
    """ % (outfit, escape(session['username'])))

    cursor.execute("""
    DELETE
    FROM outfit
    WHERE name = '%s' and user_outfit_id = %s;
    """ % (outfit,escape(session['username'])))

    conn.commit()
    return redirect(url_for('list_outfits'))


@app.route('/add_outfit', methods=["POST","GET"])
def add_outfit():
    article_names = request.form.getlist("article")

    outfit_name = request.form.get("named-outfit")
    outfit_comment = request.form.get("comment-outfit")
    cursor.execute("""insert into outfit (name,comment,id) values('%s','%s',%s);""" % (outfit_name, outfit_comment,escape(session['username'])))

    
    for name in article_names:
        cursor.execute("""
            insert into outfit_article (outfit_name,article_name, id, user_outfit_id)
            values ('%s','%s',%s,%s);
        """ % (outfit_name,name, escape(session['username']),escape(session['username'])))
    print (article_names)
    conn.commit()
    return redirect(url_for("wardrobe"))


@app.route('/edit.html/<filename>',methods=["POST","GET"])
def edit(filename):

    cursor.execute("""SELECT filename, type, comment, colour from wardrobe where filename = '%s' and id = %s;"""%(filename,escape(session['username'])))
    for data in cursor:
        image = data[0]
        value = data[1]
        comment = data[2]
        colour = data[3]

    target = os.path.join(APP_ROOT, 'images/'+escape(session['username']))
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
        cursor.execute("UPDATE wardrobe SET filename = '%s' ,type = '%s' ,comment = '%s', colour ='%s' WHERE filename = '%s' and id = %s;"% (file,newvalue,newcomment,newcolour,image, escape(session['username'])))
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

    flash('Mail skickat!')
    return render_template('about.html')

@app.route('/register.html')
def register():
    return render_template('register.html')

@app.route('/register.html', methods = ["GET", "POST"])
def register_account():
    email_register = request.form.get("email-account")
    password_register = request.form.get("password-account")

    cursor.execute("""
            insert into user_account (email, password)
            values ('%s','%s');
        """ % (email_register, password_register))

    conn.commit()
    
    return redirect(url_for("login_page"))

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/login.html', methods = ["GET", "POST"])
def login():
    error = None
    if request.method == 'POST':

        email = request.form['email-account']

        cursor.execute("""
            SELECT * from user_account
            WHERE email = '%s'
        """ % (email))
        user_list = cursor.fetchone()
        if user_list is None:
            print("wrong email")
            error = 'Wrong email or password'
        else:
            print(user_list)            
            if (email != user_list[1]) \
                    or request.form['password-account'] != user_list[2]:
                error = 'Invalid Credentials. Please try again.'
            else:
                session["username"] = user_list[0]
                session['logged_in'] = True
                flash('You were logged in.')
                return redirect(url_for('user_wardrobe'))
    return render_template('login.html', error = error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop("username", None)
    flash('You were logged out.')
    return redirect(url_for('wardrobe'))


if __name__ == '__main__':
    app.run(debug=True)