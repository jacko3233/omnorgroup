from flask import Flask, request, redirect, url_for, render_template, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'change-me'
DB_NAME = 'data.db'
BRAND = os.environ.get('APP_BRAND', 'HireSoft')

@app.context_processor
def inject_brand():
    return {'brand': BRAND}

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
    return render_template('index.html', jobs=jobs, hires=hires)

@app.route('/job/add', methods=['POST'])
def add_job():
    name = request.form['name']
    description = request.form.get('description','')
    con = sqlite3.connect(DB_NAME)
    con.execute('INSERT INTO jobs (name, description) VALUES (?, ?)', (name, description))
    con.commit()
    con.close()
    return redirect(url_for('index'))


@app.route('/job/<int:job_id>')
def job_detail(job_id):
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    job = con.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
    hires = con.execute('SELECT * FROM hires WHERE job_id=?', (job_id,)).fetchall()
    con.close()
    if not job:
        flash('Job not found')
        return redirect(url_for('index'))
    return render_template('job_detail.html', job=job, hires=hires)


@app.route('/job/<int:job_id>/close', methods=['POST'])
def close_job(job_id):
    con = sqlite3.connect(DB_NAME)
    con.execute("UPDATE jobs SET status='Closed' WHERE id=?", (job_id,))
    con.commit()
    con.close()
    flash('Job closed')
    return redirect(url_for('job_detail', job_id=job_id))


@app.route('/job/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    con = sqlite3.connect(DB_NAME)
    con.execute('DELETE FROM hires WHERE job_id=?', (job_id,))
    con.execute('DELETE FROM jobs WHERE id=?', (job_id,))
    con.commit()
    con.close()
    flash('Job deleted')
    return redirect(url_for('index'))


@app.route('/hire/<int:hire_id>/delete', methods=['POST'])
def delete_hire(hire_id):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    job_id = cur.execute('SELECT job_id FROM hires WHERE id=?', (hire_id,)).fetchone()
    if job_id:
        job_id = job_id[0]
    cur.execute('DELETE FROM hires WHERE id=?', (hire_id,))
    con.commit()
    con.close()
    flash('Hire deleted')
    if job_id:
        return redirect(url_for('job_detail', job_id=job_id))
    return redirect(url_for('index'))

@app.route('/job/<int:job_id>/hire', methods=['POST'])
def add_hire(job_id):
    item = request.form['item']
    rate = float(request.form['rate'])
    on_hire = request.form['on_hire']
    con = sqlite3.connect(DB_NAME)
    con.execute(
        'INSERT INTO hires (job_id, item_name, daily_rate, on_hire) VALUES (?,?,?,?)',
        (job_id, item, rate, on_hire),
    )
    con.commit()
    con.close()
    return redirect(url_for('job_detail', job_id=job_id))

@app.route('/hire/<int:hire_id>/off', methods=['POST'])
def off_hire(hire_id):
    off_date = request.form['off_hire']
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    hire = cur.execute(
        'SELECT job_id, on_hire, daily_rate FROM hires WHERE id=?', (hire_id,)
    ).fetchone()
    job_id = hire[0]
    days = (datetime.fromisoformat(off_date) - datetime.fromisoformat(hire[1])).days + 1
    cost = days * hire[2]
    cur.execute(
        'UPDATE hires SET off_hire=?, cost=? WHERE id=?', (off_date, cost, hire_id)
    )
    con.commit()
    con.close()
    flash('Hire closed. Total cost £{:.2f}'.format(cost))
    return redirect(url_for('job_detail', job_id=job_id))

init_db()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
