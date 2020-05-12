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
    '''Metod som skicka tillbaka template index.html'''
    return render_template('index.html')


@app.route('/wardrobe.html')
def wardrobe():
    '''metod som visar upp garderoben med en specifik användares artiklar'''
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
    
    message = "Du är inte inloggad! Om du vill se din garderob så skapa ett konto ovan!"
    return render_template('wardrobe.html',path = [], message = message)    
    # conn.close()
    

@app.route('/insert.html',  methods=["POST","GET"])
def insert():
    '''Metod som lägger till en användares plagg i garderoben och i en mapp med användarens namn.'''
            
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
           
            try:           
                upload.save(destination)
                value = request.form.get("type")
                comment = request.form.get("comment")
                colour = request.form.get("colour")
                cursor.execute("INSERT INTO wardrobe (filename,type,comment,colour,id) values ('%s','%s', '%s','%s',%s);"% (filename,value,comment,colour,escape(session['username']))) 
                conn.commit()
                flash('Plagg tillagt!')
                return redirect(request.args.get("next") or url_for("wardrobe"))
            except:
                conn.rollback()
                flash('Plagg kunde inte läggas till!') 
                return redirect(request.args.get("next") or url_for("wardrobe"))
  
            # conn.close()
           

    # return send_from_directory("images", filename, as_attachment=True)
    return render_template('insert.html')

@app.route('/remove/<filename>', methods=["POST","GET"])
def remove(filename):
    '''metod som tar bort en artikel från garderoben och från användarens mapp'''
    target = os.path.join(APP_ROOT, 'images/'+ escape(session['username']))
    destination = "/".join([target, filename])
    print ("Remove", destination)
   
    try:
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
    except:
        conn.rollback()
        flash('Plagg kunde inte tas bort!')
        return wardrobe()

@app.route('/edit/<filename>')
@app.route('/insert/<filename>')
def send_image(filename):
    '''metod som returnerar en bild från en mapp'''
    return send_from_directory("images/"+escape(session['username']), filename)

@app.route('/wardrobe/<value>')
def filter(value):
    '''metod som visar upp artiklar av en specifik typ eller färg från en viss användare'''
    cursor.execute("""select filename from wardrobe WHERE (type ='%s' OR colour='%s') and id = %s;"""%(value, value,escape(session['username'])))
    articles=[]
    for data in cursor:
        articles.append(data[0])
    # conn.close()

    return render_template('wardrobe.html',path = articles)

@app.route('/outfits.html')
def outfits():
    '''metod för att användaren ska kunna lägga till en outfit. Den visar alla artiklar som kan läggas till i en outfit'''
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
    ''' metod som listar alla outfits'''
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
@app.route('/list_outfits/<value>')
def filter_outfit(value):
    if 'username' in session:
        cursor.execute("""
            select name from outfit where (type = '%s' OR season = '%s') AND id = %s;
        """ % (value,value,escape(session['username'])))

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

    '''metod som visar upp artiklar av en specifik typ eller färg från en viss användare'''
    cursor.execute("""select filename from wardrobe WHERE (type ='%s' OR colour='%s') and id = %s;"""%(value, value,escape(session['username'])))
    articles=[]
    for data in cursor:
        articles.append(data[0])
    # conn.close()

    return render_template('wardrobe.html',path = articles)
@app.route('/show_outfit/<outfit>')
def show_outfit(outfit):
    '''metod som visar en specifik outfit'''
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
    '''metod för att visa en outfit som ska redigeras, fyller i formuläret med rätt data'''
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
        select comment,type,season
        from outfit
        where name = '%s' and id = %s; 
        
        """ % (outfit,escape(session['username'])))
    for record in cursor:
        comment = record[0]
        outfit_type = record[1]
        season = record[2]
    
    cursor.execute("""
        SELECT filename from wardrobe where id = %s;
        """ % (escape(session['username'])))
    wardrobe=[] 
    for data in cursor:
        wardrobe.append(data[0])

    return render_template('edit_outfit.html', wardrobe=wardrobe, comment=comment, outfit_articles=outfit_articles, outfit=outfit, type = outfit_type, season = season)

@app.route('/edit_outfit_form/<outfit>', methods=["POST","GET"])
def edit_outfit_form(outfit):
    '''metod som redigerar en outfit'''
    try:
        cursor.execute("""
            DELETE
            FROM outfit_article
            WHERE outfit_name ='%s' and user_outfit_id = %s;
        """ % (outfit, escape(session['username'])))


        new_outfit = request.form.get("name")
        new_comment = request.form.get("comment")
        new_type = request.form.get("type")
        new_season = request.form.get("season")
        cursor.execute("""
            UPDATE outfit
            SET name = '%s' , comment = '%s', type = '%s', season = '%s' WHERE name = '%s'and id = %s;
        """ % (new_outfit,new_comment,new_type,new_season,outfit, escape(session['username'])))
        article_names = request.form.getlist("article")

        for name in article_names:
            cursor.execute("""
                insert into outfit_article (outfit_name,article_name, id, user_outfit_id)
                values ('%s','%s',%s,%s);
            """ % (new_outfit,name,escape(session['username']),escape(session['username'])))
        conn.commit()

        return redirect(url_for('show_outfit', outfit = new_outfit))
    except:
        conn.rollback()
        flash('Outfiten kunde inte redigeras!')
        return wardrobe()

@app.route('/remove_outfit/<outfit>',methods = ["POST","GET"])
def remove_outfit(outfit):
    '''metod för att ta bort en outfit'''
    try:    
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
    except:
        conn.rollback()
        flash('outfit kunde inte tas bort!')
        return wardrobe()

@app.route('/add_outfit', methods=["POST","GET"])
def add_outfit():
    '''metod för att lägga till en outfit'''
    try:
        article_names = request.form.getlist("article")

        outfit_name = request.form.get("named-outfit")
        outfit_comment = request.form.get("comment-outfit")
        outfit_season = request.form.get("season")
        outfit_type = request.form.get("type")
        cursor.execute("""insert into outfit (name,comment,id, type, season) values('%s','%s',%s,'%s','%s');""" % (outfit_name, outfit_comment,escape(session['username']),outfit_type,outfit_season))

        
        for name in article_names:
            cursor.execute("""
                insert into outfit_article (outfit_name,article_name, id, user_outfit_id)
                values ('%s','%s',%s,%s);
            """ % (outfit_name,name, escape(session['username']),escape(session['username'])))
        print (article_names)
        conn.commit()
        return redirect(url_for("wardrobe"))
    except:
        conn.rollback()
        flash('outfit kunde inte läggas till!')
        return wardrobe()


@app.route('/edit.html/<filename>',methods=["POST","GET"])
def edit(filename):
    '''metod för att redigera en artikel'''
    try:
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
    except:
        conn.rollback()
        flash('Plagg kunde inte redigeras!')
        return wardrobe()


    print(image, value, comment)

    return render_template('edit.html', image = image, value = value, comment = comment, colour = colour)


@app.route('/trends.html')
def trends():
    '''metod för att returnera template trends.html'''
    return render_template('trends.html')

@app.route('/about.html')
def about():
    '''metod för att returnera template about.html'''
    return render_template('about.html')

@app.route('/about.html', methods = ["GET", "POST"])
def sendemail():
    '''metod för att skicka ett mail'''
    try:
        user_text = request.form.get("text-input")
        user_email = "kladr2020@gmail.com"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login("kladr2020@gmail.com", "kladr2020april")
        server.sendmail("kladr2020@gmail.com", user_email, user_text.encode("utf-8"))
        print(user_email, user_text)

        flash('Mail skickat!')
        return render_template('about.html')
    except:
        flash('Mail inte skickat!')
        return render_template('about.html')
        

@app.route('/register.html')
def register():
    '''metod för att skicka tillbaka template register.html'''
    return render_template('register.html')

@app.route('/register.html', methods = ["GET", "POST"])
def register_account():
    '''metod för att registrera en användare'''
    try:
        email_register = request.form.get("email-account")
        password_register = request.form.get("password-account")
        cursor.execute("""
            SELECT email from user_account;
        """)
        accounts = []
        for record in cursor:
            accounts.append(record[0])
        if email_register not in accounts:
            print(cursor.fetchall())
            print(accounts)
            cursor.execute("""
                    insert into user_account (email, password)
                    values ('%s','%s');
                """ % (email_register, password_register))

            conn.commit()
            
            return redirect(url_for("login_page"))
        else:
            flash('Email redan i användning')
            return render_template('register.html')
    except:
        conn.rollback()
        flash('Kontot kunde inte skapas!')
        return render_template('register.html')

@app.route('/login.html')
def login_page():
    '''metod för att returnera login.html'''
    return render_template('login.html')

@app.route('/login.html', methods = ["GET", "POST"])
def login():
    '''metod för att logga in'''
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
            error = 'Fel mail eller lösenord'
        else:
            print(user_list)            
            if (email != user_list[1]) \
                    or request.form['password-account'] != user_list[2]:
                error = 'Fel mail eller lösenord'
            else:
                session["username"] = user_list[0]
                session['logged_in'] = True
                flash('Du är inloggad!')
                return redirect(url_for('wardrobe'))
    return render_template('login.html', error = error)

@app.route('/logout')
def logout():
    '''metod för att logga ut'''
    session.pop('logged_in', None)
    session.pop("username", None)
    flash('Du är utloggad!')
    return redirect(url_for('wardrobe'))


if __name__ == '__main__':
    app.run(debug=True)
