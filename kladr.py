from bottle import run, route, template, static_file, request, error
from os import listdir
import psycopg2


@route("/")
def index():
    return template("index")

@route("/index.html")
def index():
    return template("index")

@route("/wardrobe.html")
def list_articles():
    conn = psycopg2.connect(dbname = "aj9200", user = "aj9200", password="73do0621",host="pgserver.mah.se")
    cursor = conn.cursor()
    cursor.execute("select * from kvitto")
    kvitto =[]
    for records in cursor:
        kvitto.append([records[0],records[1],records[2],records[3],records[4],records[5]])
    return template("wardrobe",wardrobe = kvitto)

@route("/insert.html")
def insert():
    return template("insert")

@route("/trends.html")
def trends():
    return template("trends")

@route("/about.html")
def about():
    return template("about")

@route("/static/<filename>")
def staticFile(filename):
    return static_file(filename,root="static")

@route("/wardrobe/<filename>")
def staticFile(filename):
    return static_file(filename,root="wardrobe")


run(host='127.0.0.2', port=8081)

