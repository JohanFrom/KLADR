from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def hello():
    return render_template('index.html')

@app.route('/wardrobe.html')
def wardrobe():
    conn = psycopg2.connect(dbname = "aj9200", user = "aj9200", password="73do0621",host="pgserver.mah.se")
    cursor = conn.cursor()
    cursor.execute("select * from kvitto")
    kvitto =[]
    for records in cursor:
        kvitto.append([records[0],records[1],records[2],records[3],records[4],records[5]])
    return render_template('wardrobe.html',wardrobe=kvitto)

@app.route('/insert.html')
def insert():
    return render_template('insert.html')

@app.route('/trends.html')
def trends():
    return render_template('trends.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)