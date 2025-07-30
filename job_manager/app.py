from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = 'data.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'Open'
);
CREATE TABLE IF NOT EXISTS hires (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    item_name TEXT,
    daily_rate REAL,
    on_hire DATE,
    off_hire DATE,
    cost REAL,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);
"""

def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.executescript(SCHEMA)
    con.commit()
    con.close()


@app.route('/')
def index():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    jobs = con.execute('SELECT * FROM jobs').fetchall()
    hires = con.execute('SELECT * FROM hires').fetchall()
    con.close()
    return render_template_string(TEMPL_INDEX, jobs=jobs, hires=hires)

@app.route('/job/add', methods=['POST'])
def add_job():
    name = request.form['name']
    description = request.form.get('description','')
    con = sqlite3.connect(DB_NAME)
    con.execute('INSERT INTO jobs (name, description) VALUES (?,?)', (name, description))
    con.commit()
    con.close()
    return redirect(url_for('index'))

@app.route('/job/<int:job_id>/hire', methods=['POST'])
def add_hire(job_id):
    item = request.form['item']
    rate = float(request.form['rate'])
    on_hire = request.form['on_hire']
    con = sqlite3.connect(DB_NAME)
    con.execute('INSERT INTO hires (job_id, item_name, daily_rate, on_hire) VALUES (?,?,?,?)', (job_id,item,rate,on_hire))
    con.commit()
    con.close()
    return redirect(url_for('index'))

@app.route('/hire/<int:hire_id>/off', methods=['POST'])
def off_hire(hire_id):
    off_date = request.form['off_hire']
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    hire = cur.execute('SELECT on_hire, daily_rate FROM hires WHERE id=?', (hire_id,)).fetchone()
    days = (datetime.fromisoformat(off_date) - datetime.fromisoformat(hire[0])).days + 1
    cost = days * hire[1]
    cur.execute('UPDATE hires SET off_hire=?, cost=? WHERE id=?', (off_date,cost,hire_id))
    con.commit()
    con.close()
    return redirect(url_for('index'))

TEMPL_INDEX = """
<!doctype html>
<title>Job Management</title>
<h1>Jobs</h1>
<form method=post action="/job/add">
Name: <input name=name required>
Description: <input name=description>
<input type=submit value="Add Job">
</form>
{% for j in jobs %}
  <h2>{{j['name']}} - {{j['status']}}</h2>
  <p>{{j['description']}}</p>
  <h3>Hire Items</h3>
  <ul>
  {% for h in hires %}
    {% if h['job_id']==j['id'] %}
      <li>{{h['item_name']}} @ {{h['daily_rate']}}/day from {{h['on_hire']}} to {{h['off_hire'] or 'ongoing'}} cost: {{h['cost'] or 'TBD'}}
        {% if not h['off_hire'] %}
          <form style="display:inline" method=post action="/hire/{{h['id']}}/off">
          Off-hire date: <input name=off_hire type=date required>
          <input type=submit value="Close">
          </form>
        {% endif %}
      </li>
    {% endif %}
  {% endfor %}
  </ul>
  <form method=post action="/job/{{j['id']}}/hire">
  Item: <input name=item required>
  Rate per day: <input name=rate type=number step=0.01 required>
  On-hire date: <input name=on_hire type=date required>
  <input type=submit value="Add Hire">
  </form>
{% endfor %}
"""
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
