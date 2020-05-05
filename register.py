from flask import Flask
from flask import render_template # to render our html page
from flask import request # to get user input from form
import hashlib # included in Python library, no need to install
import psycopg2 # for database connection
import datetime

app = Flask(__name__)
t_host = "pgserver.mah.se"
t_port = "5432"
t_dbname = "aj9200"
t_user = "aj9200"
t_pw = "73do0621"
db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user, password=t_pw)
db_cursor = db_conn.cursor()

@app.route("/")

def showForm():
    # show our html form to the user
    t_message = "Python and Postgres Registration Application"
    return render_template("register.html", message = t_message)
@app.route("/loginform")
def loginform():
    t_message = "Login Form"
    return render_template("sign_in.html",message=t_message)

@app.route("/register", methods=["POST","GET"])
def register():
    # get user input from the html form
    t_email = request.form.get("t_Email")
    t_password = request.form.get("t_Password")
    print(t_email)
    print(t_password)
    print("ehjhj")
    # check for blanks
    if t_email == "":
        t_message = "Please fill in your email address"
        return render_template("register.html", message = t_message)

    if t_password == "":
        t_message = "Please fill in your password"
        return render_template("register.html", message = t_message)

    # hash the password they entered
    t_hashed = hashlib.sha256(t_password.encode())
    t_password = t_hashed.hexdigest()

  

    # We take the time to build our SQL query string so that
    #   (a) we can easily & quickly read it
    #   (b) we can easily & quickly edit or add/remote lines
    #   The more complex the query, the greater the benefits
    s = "INSERT INTO public.users "
    s += "("
    s += "  t_email"
    s += ", t_password"
    s += ", b_enabled"
    s += ") VALUES ("
    s += " '" + t_email + "'"
    s += ",'" + t_password + "'"
    s += ",'true'"
    s += ")"
    # Warning: this format allows for a user to try to insert
    #   potentially damaging code, commonly known as "SQL injection".
    #   In a later article we will show some methods for
    #   preventing this.

    # Here we are catching and displaying any errors that occur
    #   while TRYing to commit the execute our SQL script.
    db_cursor.execute(s)
    try:
        db_conn.commit()
    except psycopg2.Error as e:
        t_message = "Database error: " + e + "/n SQL: " + s
        return render_template("register.html", message = t_message)

    t_message = "Your user account has been added."
    return render_template("register.html", message = t_message)

@app.route("/sign_in", methods=["POST","GET"])
def sign_in():
    t_stage = request.args.get("stage")
    ID_user = request.args.get("ID_user")
    t_email = request.form.get("t_email", "")

    print(t_stage)
    # The test for "reset" we see here will become relevant later in this article series.
    if t_stage == "login" or t_stage == "reset":
        t_password = request.form.get("t_password", "")

    # Check for email field left empty
    if t_email == "":
        # "forgot" test below is for later part of our multi-part article, fine here for now:
        if t_stage == "forgot":
            t_message = "Reset Password: Please fill in your email address"
        else:
            t_message = "Login: Please fill in your email address"
        # If empty, send user back, along with a message
        return render_template("sign_in.html", message = t_message)

    # Check for password field left empty
    # Note we are checking the t_stage variable to see if they are signing in or they forgot their password
    #   If they forgot their password, we don't want their password here. We only want their email address
    #   so we can send them a link in the next part of this article.
    # In both 1st stage and 3rd, we harvest password, so t_stage is "login" or "reset"
    if (t_stage == "login" or t_stage == "reset") and t_password == "":
        t_message = "Login: Please fill in your password"
        # If empty, send user back, along with a message
        return render_template("sign_in.html", message = t_message)

    # In both 1st stage and 3rd, we harvest password, so t_stage is "login" or "reset"
    if t_stage == "login" or t_stage == "reset":
        # Hash the password
        t_hashed = hashlib.sha256(t_password.encode())
        t_password = t_hashed.hexdigest()

    # Get user ID from PostgreSQL users table
    s = ""
    s += "SELECT id FROM users"
    s += " WHERE"
    s += " ("
    s += " t_email ='" + t_email + "'"
    if t_stage != "login":
        s += " AND"
        s += " t_password = '" + t_password + "'"
    s += " AND"
    s += " b_enabled = true"
    s += " )"

    db_cursor.execute(s)

    # Here we catch and display any errors that occur
    #   while TRYing to commit the execute our SQL script.
    try:
        array_row = db_cursor.fetchone()
    except psycopg2.Error as e:
        t_message = "Database error: " + e + "/n SQL: " + s
        return render_template("sign_in.html", message = t_message)

    # Cleanup our database connections

    print (array_row)
    ID_user = array_row[0]

    # If they have used the link in the email we sent them then t_stage is "reset"
    # if t_stage == "reset":
        # IMPORTANT
        # In a later part of this article series we will add code here
        # IMPORTANT

    # First stage. They have filled in username and password, so t_stage is "login"
    if t_stage == "login":
        # UPDATE the database with a logging of the date of the visit
        s = ""
        s += "UPDATE users SET"
        s += " d_visit_last = '" + str(datetime.datetime.now()) + "'"
        s += "WHERE"
        s += "("
        s += " ID=" + str(ID_user) + ""
        s += ")"
        # IMPORTANT WARNING: this format allows for a user to try to insert
        #   potentially damaging code, commonly known as "SQL injection".
        #   In a later article we will show some methods for
        #   preventing this.

        # Here we are catching and displaying any errors that occur
        #   while TRYing to commit the execute our SQL script.
        db_cursor.execute(s)
        try:
            db_conn.commit()
        except psycopg2.Error as e:
            t_message = "Login: Database error: " + e + "/n SQL: " + s
            return render_template("sign_in.html", message = t_message)
        db_cursor.close()

        # Redirect user to the rest of your application
        return "success!!"
# this is for command line testing
if __name__ == "__main__":
    app.run(debug=True)