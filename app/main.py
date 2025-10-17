from flask import Flask, request, render_template
import pymysql
import os
import math

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "nyc311")
PER_PAGE = 20

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def home():
    return render_template("search.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    page = int(request.args.get('page', 1))
    borough = request.form.get('borough')
    complaint_type = request.form.get('complaint_type')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    query = "SELECT * FROM service_requests WHERE 1=1"
    count_query = "SELECT COUNT(*) as total FROM service_requests WHERE 1=1"
    params = []

    if borough:
        query += " AND borough=%s"
        count_query += " AND borough=%s"
        params.append(borough)
    if complaint_type:
        query += " AND complaint_type=%s"
        count_query += " AND complaint_type=%s"
        params.append(complaint_type)
    if start_date and end_date:
        query += " AND created_datetime BETWEEN %s AND %s"
        count_query += " AND created_datetime BETWEEN %s AND %s"
        params += [start_date, end_date]

    query += " ORDER BY created_datetime DESC LIMIT %s OFFSET %s"
    params += [PER_PAGE, PER_PAGE*(page-1)]

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.execute(count_query, params[:-2])  # exclude limit/offset for count
            total = cursor.fetchone()['total']

    total_pages = math.ceil(total / PER_PAGE) if total else 1
    return render_template("results.html", results=results, page=page, total_pages=total_pages)

@app.route("/aggregate")
def aggregate():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT borough, COUNT(*) as count FROM service_requests GROUP BY borough")
            data = cursor.fetchall()
    return render_template("aggregate.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
