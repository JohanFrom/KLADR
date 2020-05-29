__author__ = "Johan From, Alva Karlborg, Laura Barba, Rebecka Persson" 

from flask import Flask, session, render_template, request, send_from_directory, url_for, redirect, flash, escape
from random import randint
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
    '''metod som skicka tillbaka template index.html'''
    return render_template('index.html')

@app.route('/wardrobe.html')
def wardrobe():
    '''metod som visar upp garderoben med en specifik användares artiklar'''
    if 'username' in session:
        
        try:
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
        except:
            message = "Plaggen gick inte att visas upp!"

        return render_template('wardrobe.html',articles = articles, message = message)
    else:
        message = "Välkommen till KLÄDR! Logga in eller skapa ett konto för att se din garderob!"
        return render_template('wardrobe.html',articles = [], message = message)    
    
@app.route('/insert.html',  methods=["POST","GET"])
def insert():
    '''metod som lägger till en användares artikel i garderoben och i en mapp med användarens namn.'''
            
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
                cursor.execute("""
                    INSERT 
                    INTO wardrobe (filename,type,comment,colour,id) 
                    VALUES ('%s','%s','%s','%s',%s);
                """% (filename,value,comment,colour,escape(session['username']))) 
                conn.commit()
                flash('Artikeln är tillagd!')
                return redirect(request.args.get("next") or url_for("wardrobe"))
            except:
                conn.rollback()
                flash('Artikeln kunde inte läggas till!') 
                return redirect(request.args.get("next") or url_for("wardrobe"))
  
        return render_template('insert.html')

    else:
        return wardrobe()


@app.route('/remove/<filename>', methods=["POST","GET"])
def remove(filename):
    '''metod som tar bort en artikel från garderoben och från användarens mapp'''
    target = os.path.join(APP_ROOT, 'images/'+ escape(session['username']))
    destination = "/".join([target, filename])
    print ("Remove", destination)
   
    try:

        cursor.execute("""
            DELETE from outfit_article
            WHERE article_name = '%s' AND id = %s;
        """ % (filename,escape(session['username'])))
        
        cursor.execute("""
            DELETE from wardrobe
            WHERE filename = '%s' AND id = %s;
        """ % (filename,escape(session['username'])))

        cursor.execute("""
            SELECT name
            FROM outfit
            WHERE id = %s;
        """ % (escape(session['username'])))

        outfit_names = cursor.fetchall()
        print(outfit_names)

        for name in outfit_names:
            cursor.execute("""
                SELECT article_name
                FROM outfit_article
                WHERE outfit_name = '%s' AND user_outfit_id = %s;
            """ %(name[0], escape(session['username'])))

            outfit_articles = cursor.fetchall()

            if len(outfit_articles) == 0:
                cursor.execute("""
                    DELETE FROM outfit
                    WHERE name = '%s' AND id = %s;
                """ % (name[0], escape(session['username'])))
        os.remove(destination)

        conn.commit()
        
        flash('Artikeln är borttagen!')
        return wardrobe()
    except:
        conn.rollback()
        flash('Artikeln kunde inte tas bort!')
        return wardrobe()

@app.route('/edit/<filename>')
@app.route('/insert/<filename>')
def send_image(filename):
    '''metod som returnerar en bild från en mapp'''
    return send_from_directory("images/"+escape(session['username']), filename)

@app.route('/wardrobe/<value>')
def filter(value):
    '''metod som visar upp artiklar av en specifik typ eller färg från en viss användare'''
    try:

        cursor.execute("""
            SELECT filename 
            FROM wardrobe 
            WHERE (type ='%s' OR colour='%s') AND id = %s;
        """%(value, value,escape(session['username'])))

        articles=[]
        for data in cursor:
            articles.append(data[0])

        return render_template('wardrobe.html',articles = articles)
    except:
        conn.rollback()      
        flash('Det gick inte att filtrera på vald typ eller färg!')
        return wardrobe()

@app.route("/show_article/<filename>")
def show_article(filename):
    '''metoden visar upp vald artikel med bild och kommentar'''
    try:
        if 'username' in session:
            cursor.execute("""
            SELECT filename, comment
            FROM wardrobe
            WHERE filename = '%s' AND id = %s
            """ % (filename, escape(session["username"])))

            for data in cursor:
                article_name = data[0]
                article_comment = data[1]
            return render_template("show_article.html", article = article_name, comment = article_comment)
        else:
            return wardrobe()
    except:
        conn.rollback()
        flash("Det gick inte att visa artikeln!")
        return wardrobe()


@app.route('/outfits.html')
def add_outfit_page():
    '''metod för att användaren ska kunna lägga till en outfit. Den visar alla artiklar som kan läggas till i en outfit'''
    try:
        articles = []
        if 'username' in session:
            cursor.execute("""
                SELECT filename 
                FROM wardrobe 
                WHERE id = %s;
            """ % (escape(session['username'])))
            articles=[] 
            for data in cursor:
                articles.append(data[0])

        return render_template('add_outfit.html',articles = articles)   
    except:
        conn.rollback()
        return wardrobe()


@app.route("/list_outfits")
def list_outfits():
    ''' metod som listar alla outfits'''

    #Lägg till att det står "Inga outfits tillagda" ifall det inte finns några outfits att visa

    try:

        if 'username' in session:
            cursor.execute("""
                SELECT name 
                FROM outfit 
                WHERE id = %s;
            """ % (escape(session['username'])))

            outfit_names = [] #lista pa alla outfit namn

            for name in cursor:
                outfit_names.append(name[0])

            all_outfits = []

            for outfit_name in outfit_names:
                cursor.execute("""
                    SELECT article_name 
                    FROM outfit_article
                    WHERE outfit_name = '%s' AND user_outfit_id = %s;
                """ % (outfit_name,escape(session['username'])))
                temp = []
                for article in cursor:
                    temp.append(article[0])
                all_outfits.append(temp)
            print(all_outfits)
            print(outfit_names)
            return render_template("list_outfits.html", outfits = all_outfits, names=outfit_names)
        else:
            return wardrobe()
    except:
        conn.rollback()
        flash('Det gick inte att visa outfits!')
        return wardrobe()

@app.route('/list_outfits/<value>')
def filter_outfit(value):
    '''metod för att filtrera outfits'''
    try:

        if 'username' in session:
            cursor.execute("""
                SELECT name 
                FROM outfit 
                WHERE (type = '%s' OR season = '%s') AND id = %s;
            """ % (value,value,escape(session['username'])))

            outfit_names = [] #lista pa alla outfit namn

            for name in cursor:
                outfit_names.append(name[0])

            all_outfits = []

            for outfit_name in outfit_names:
                cursor.execute("""
                    SELECT article_name 
                    FROM outfit_article
                    WHERE outfit_name = '%s' AND user_outfit_id = %s;
                """ % (outfit_name,escape(session['username'])))

                temp = []
                for article in cursor:
                    temp.append(article[0])
                all_outfits.append(temp)
            print(all_outfits)
            print(outfit_names)
            return render_template("list_outfits.html", outfits = all_outfits, names=outfit_names)
        else:
            return wardrobe()
    except:
        conn.rollback()
        flash('Det gick inte att filtrera!')
        return wardrobe()

@app.route('/show_outfit/<outfit>')
def show_outfit(outfit):
    '''metod som visar en specifik outfit'''
    try:

        cursor.execute("""
            SELECT article_name 
            FROM outfit_article
            WHERE outfit_name = '%s' AND user_outfit_id = %s;
        """ % (outfit,escape(session['username'])))
        
        outfit_articles = []
        for article in cursor:
            outfit_articles.append(article[0])
        
        print(outfit_articles)

        cursor.execute("""
            SELECT comment
            FROM outfit
            WHERE name = '%s' AND id = %s; 
        """ % (outfit, escape(session['username'])))

        for data in cursor:
            comment = data[0]
        print(comment)

        return render_template('show_outfit.html', comment = comment, outfit_articles = outfit_articles, outfit=outfit)
    
    except:
        conn.rollback()
        flash('Det gick inte att visa outfiten!')
        return wardrobe()


@app.route('/edit_outfit/<outfit>', methods=["POST","GET"])
def edit_outfit(outfit):
    '''metod för att visa en outfit som ska redigeras, fyller i formuläret med rätt data'''
    try:

        cursor.execute("""
            SELECT article_name 
            FROM outfit_article 
            WHERE outfit_name = '%s' AND user_outfit_id = %s;
        """ % (outfit,escape(session['username'])))
        
        outfit_articles = []
        for article in cursor:
            outfit_articles.append(article[0])   


        cursor.execute("""
            SELECT comment,type,season
            FROM outfit
            WHERE name = '%s' AND id = %s; 
        """ % (outfit,escape(session['username'])))

        for data in cursor:
            comment = data[0]
            outfit_type = data[1]
            season = data[2]
        
        cursor.execute("""
            SELECT filename 
            FROM wardrobe 
            WHERE id = %s;
        """ % (escape(session['username'])))

        wardrobe=[] 
        for data in cursor:
            wardrobe.append(data[0])

        return render_template('edit_outfit.html', wardrobe=wardrobe, comment=comment, outfit_articles=outfit_articles, outfit=outfit, type = outfit_type, season = season)
    except:
        conn.rollback()
        flash('Det gick inte att genomföra redigeringen!')
        return wardrobe()

@app.route("/save_outfit/<outfit>")
def save_outfit(outfit):
    '''metod för att spara en outfit'''
    try:
        cursor.execute("""
            SELECT filename 
            FROM wardrobe 
            WHERE id = %s;
        """ % (escape(session['username'])))

        wardrobe=[] 
        for data in cursor:
            wardrobe.append(data[0])
        print(wardrobe)
        return render_template('edit_outfit.html', wardrobe=wardrobe, comment="None", outfit_articles=outfit, outfit=" ", type = "None", season = "None")
    except:
        conn.rollback()
        flash('Det gick inte att spara outfiten!')
        return wardrobe()

@app.route('/edit_outfit_form/<outfit>', methods=["POST","GET"])
def edit_outfit_form(outfit):
    '''metod som redigerar en outfit'''
    try:
        cursor.execute("""
            DELETE
            FROM outfit_article
            WHERE outfit_name ='%s' AND user_outfit_id = %s;
        """ % (outfit, escape(session['username'])))


        updated_outfit_name = request.form.get("name")
        updated_comment = request.form.get("comment")
        updated_type = request.form.get("type")
        updated_season = request.form.get("season")

        cursor.execute("""
            UPDATE outfit
            SET name = '%s' , comment = '%s', type = '%s', season = '%s' 
            WHERE name = '%s'AND id = %s;
        """ % (updated_outfit_name, updated_comment, updated_type, updated_season, outfit, escape(session['username'])))
        
        article_names = request.form.getlist("article")

        for name in article_names:
            cursor.execute("""
                INSERT INTO outfit_article (outfit_name,article_name, id, user_outfit_id)
                VALUES ('%s','%s',%s,%s);
            """ % (updated_outfit_name, name, escape(session['username']), escape(session['username'])))
        conn.commit()
        if(outfit == " "):
            flash('Outfit sparad!')
        else:
            flash('Outfit redigerad!')
        return redirect(url_for('show_outfit', outfit = updated_outfit_name))
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
            WHERE outfit_name = '%s' AND user_outfit_id = %s;
        """ % (outfit, escape(session['username'])))

        cursor.execute("""
            DELETE
            FROM outfit
            WHERE name = '%s' AND id = %s;
        """ % (outfit,escape(session['username'])))

        conn.commit()
        flash('Outfit borttagen!')
        return redirect(url_for('list_outfits'))
    except:
        conn.rollback()
        flash('Outfit kunde inte tas bort!')
        return wardrobe()

@app.route('/add_outfit', methods=["POST","GET"])
def add_outfit():
    '''metod för att lägga till en outfit'''
    try:
        article_names = request.form.getlist("article")

        outfit_name = request.form.get("name")
        outfit_comment = request.form.get("comment")
        outfit_season = request.form.get("season")
        outfit_type = request.form.get("type")
        cursor.execute("""
            INSERT INTO outfit (name,comment,id, type, season) 
            VALUES ('%s','%s',%s,'%s','%s');
        """ % (outfit_name, outfit_comment,escape(session['username']),outfit_type,outfit_season))
        
        for name in article_names:
            cursor.execute("""
                INSERT INTO outfit_article (outfit_name,article_name, id, user_outfit_id)
                VALUES ('%s','%s',%s,%s);
            """ % (outfit_name,name, escape(session['username']),escape(session['username'])))

        print (article_names)
        conn.commit()
        flash('Outfit tillagd!')
        return redirect(url_for("list_outfits"))
    except:
        conn.rollback()
        flash('Outfit kunde inte läggas till!')
        return wardrobe()


@app.route('/generate')
def generate():
    '''metod för att generera en outfit'''
    random = randint(1,2)
    try:    
        jacket = generate_jacket()
                
        shoe = generate_shoes()
            
        if random == 1:
            top = generate_top()
                
            bottom = generate_bottoms()

            outfit = [jacket,shoe,top,bottom]
            print(outfit)
        else:
            body = generate_full_body()
            outfit = [jacket,shoe,body]
            print(outfit)
            
        return render_template ('show_outfit.html',outfit_articles = outfit, outfit=" ")
    except:
        conn.rollback()
        print(random)
        flash('Outfit kunde inte genereras!')
        return wardrobe()

@app.route("/generate/<filename>")
def generate_from_article(filename):
    '''metod som genererar en outfit utifrån en viss artikel'''
    
    #Lägg till try-except
    
    random = randint(1,2)
        
    bottoms = generate_bottoms()
    shoes = generate_shoes()
    jacket = generate_jacket()
    top = generate_top()
    body = generate_full_body()

    cursor.execute("""
            SELECT type
            FROM wardrobe
            WHERE filename = '%s' AND id = %s
        """ % (filename, escape(session['username'])))
    for data in cursor:
        article_type = data[0]
        
    if article_type == 'Playsuit' or article_type == 'Klänning' or article_type == 'Jumpsuit':
        outfit = [filename,shoes,jacket]

    elif article_type == 'Byxor' or article_type == 'Shorts' or article_type == 'Jeans' or article_type == 'Sweatpants' or article_type == 'Kjol' or article_type == 'Leggings':
        outfit = [filename,top,shoes,jacket]
            
    elif article_type == 'T-shirt' or article_type == 'Linne' or article_type == 'Skjorta' or article_type == 'Stickat' or article_type == 'Hoodie' or article_type == 'Kofta':
        outfit = [filename,bottoms,shoes,jacket]

    elif article_type == 'Lång jacka' or article_type == 'Kort jacka' or article_type == 'Kappa-Rock' or article_type == 'Regnjacka':
        if random == 1:
            outfit = [filename,bottoms,shoes,top]
        else:
            outfit = [filename,body,shoes]
    else:
        if random == 1:
            outfit = [filename,bottoms,jacket,top]
        else:
            outfit = [filename,body,jacket]
    return render_template ('show_outfit.html', outfit_articles = outfit, outfit=" ")


def generate_shoes():
    '''metoden genererar slumpmässigt fram skor ifrån databasen'''
    cursor.execute("""
        SELECT filename 
        FROM wardrobe 
        WHERE id = %s
        AND (type = 'Sneakers' OR type ='Klackar' OR type = 'Kängor' OR type = 'Stövlar' OR type = 'Sandaler') 
        ORDER BY random();
    """ % (escape(session['username'])))

    for data in cursor:
        shoe = data[0]
    return shoe

def generate_full_body():
    '''metoden genererar slumpmässigt fram en helkroppsartikel ifrån databasen'''
    cursor.execute("""
        SELECT filename 
        FROM wardrobe 
        WHERE id = %s
        AND (type = 'Playsuit' OR type = 'Klänning' OR type = 'Jumpsuit') 
        ORDER BY random();
     """ % (escape(session['username'])))
    for data in cursor:
        body = data[0]
    
    return body

def generate_bottoms():
    '''metoden genererar slumpmässigt fram nederdel ifrån databasen'''
    cursor.execute("""
        SELECT filename 
        FROM wardrobe 
        WHERE id = %s
        AND ( type = 'Byxor' OR type = 'Shorts' OR type = 'Jeans' OR type = 'Sweatpants' OR type = 'Kjol' OR type = 'Leggings') 
        ORDER BY random();
    """ % (escape(session['username'])))
    for data in cursor:
        bottom = data[0]
    return bottom

def generate_top():
    '''metoden genererar slumpmässigt fram överdel ifrån databasen'''
    cursor.execute("""
        SELECT filename 
        FROM wardrobe 
        WHERE id = %s
        AND (type = 'T-shirt' OR type='Linne' OR type ='Skjorta' OR type = 'Stickat' OR type = 'Hoodie' OR type = 'Kofta') 
        ORDER BY random();
    """ % (escape(session['username'])))
    for data in cursor:
        top = data[0]
    return top

def generate_jacket():
    '''metoden genererar slumpmässigt fram ytterkläder ifrån databasen'''
    cursor.execute("""
        SELECT filename 
        FROM wardrobe 
        WHERE id = %s   
        AND (type = 'Lång jacka' OR type = 'Kort jacka' OR type = 'Kappa-Rock' OR type = 'Regnjacka') 
        ORDER BY random();         
    """ % (escape(session['username'])))

    for data in cursor:
        jacket = data[0]
    return jacket

@app.route('/edit.html/<filename>',methods=["POST","GET"])
def edit(filename):
    '''metod för att redigera en artikel'''
    try:
        cursor.execute("""
            SELECT filename, type, comment, colour 
            FROM wardrobe
            WHERE filename = '%s' AND id = %s;
        """% (filename,escape(session['username'])))
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
            updated_value = request.form.get("type")
            updated_comment = request.form.get("comment")
            updated_colour = request.form.get("colour")

            cursor.execute("""
                UPDATE wardrobe 
                SET filename = '%s' ,type = '%s' ,comment = '%s', colour ='%s' 
                WHERE filename = '%s' AND id = %s;
            """% (file, updated_value, updated_comment, updated_colour, image, escape(session['username'])))

            conn.commit()
            flash('Artikeln redigerad!')
            return redirect(request.args.get("next") or url_for("wardrobe"))
    except:
        conn.rollback()
        flash('Artikeln kunde inte redigeras!')
        return wardrobe()


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

        flash('E-mailet skickades!')
        return render_template('about.html')
    except:
        flash('E-mailet kunde inte skickas!')
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
        firstname_register = request.form.get("first-name")
        lastname_register = request.form.get("last-name")
        gender_register = request.form.get("gender")
        cursor.execute("""
            SELECT email 
            FROM user_account;
        """)
        accounts = []
        for data in cursor:
            accounts.append(data[0])
        if email_register not in accounts:
            print(cursor.fetchall())
            print(accounts)
            cursor.execute("""
                INSERT INTO user_account (email, password, acc_firstname, acc_lastname, acc_gender)
                VALUES ('%s','%s','%s','%s','%s');
            """ % (email_register, password_register, firstname_register, lastname_register, gender_register))

            conn.commit()
            
            return redirect(url_for("login_page"))
        else:
            flash('E-mailen används redan')
            return render_template('register.html')
    except:
        conn.rollback()
        flash('Kontot kunde inte skapas!')
        return render_template('register.html')

@app.route('/profile.html')
def show_profile():
    '''metod för att visa en användares profil'''
    try:

        if 'username' in session:
            cursor.execute("""
                SELECT acc_firstname, acc_lastname, acc_gender, email, password 
                FROM user_account 
                WHERE id = %s;
            """%(escape(session['username'])))

            for data in cursor:
                firstname = data[0]
                lastname = data[1]
                gender = data[2]
                email = data[3]
                password = data[4]

        return render_template ('profile.html', firstname = firstname, lastname = lastname, gender = gender, email = email, password = password)
    
    except:
        conn.rollback()
        flash('Det gick inte att visa användarprofilen!')
        return wardrobe()
        

@app.route('/profile.html', methods = ["GET", "POST"])
def update_profile():
    '''metod för att uppdatera en användares profil'''
    try:

        if 'username' in session:
            email = request.form.get('email-account')
            password = request.form.get('password-account')
            firstname = request.form.get("first-name")
            lastname = request.form.get("last-name")
            gender = request.form.get("gender")

            cursor.execute("""
                UPDATE user_account 
                SET email = '%s', password = '%s', acc_firstname = '%s', acc_lastname = '%s', acc_gender = '%s' 
                WHERE id = %s;
            """ % (email, password, firstname, lastname, gender, escape(session['username'])))

            conn.commit()
            flash('Användarprofilen är uppdaterad!')

    except:
        flash('Användarprofilen gick inte att uppdatera!')
        conn.rollback()

    return wardrobe()

@app.route('/login.html')
def login_page():
    '''metod för att returnera login.html'''

    #Lägg till flash meddelanden, "kontot är skapat"
    return render_template('login.html')

@app.route('/login.html', methods = ["GET", "POST"])
def login():
    '''metod för att logga in'''
    
    message = None
    if request.method == 'POST':

        email = request.form['email-account']

        cursor.execute("""
            SELECT * 
            FROM user_account
            WHERE email = '%s'
        """ % (email))
        user_list = cursor.fetchone()
        if user_list is None:
            print("wrong email")
            message = 'Fel mail eller lösenord'
        else:
            print(user_list)            
            if (email != user_list[1]) \
                    or request.form['password-account'] != user_list[2]:
                message = 'Fel mail eller lösenord'
            else:
                session["username"] = user_list[0]
                session['logged_in'] = True
                flash('Du är inloggad!')
                return redirect(url_for('wardrobe'))
        return render_template('login.html', message = message)

@app.route('/logout')
def logout():
    '''metod för att logga ut'''
    session.pop('logged_in', None)
    session.pop("username", None)
    flash('Du är utloggad!')
    return redirect(url_for('wardrobe'))


if __name__ == '__main__':
    app.run(debug=True)