import sqlite3
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import datetime

##global variable
global_db_counter=0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global global_db_counter
    global_db_counter=global_db_counter+1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):  
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    app.logger.info(f"{datetime.datetime.now()}, Selected post with id:{post_id} has been retrieved !")
    return post


# Function to tget the total count of the posts
def get_total_posts_count():
    connection = get_db_connection()
    total_count_posts= connection.execute('SELECT COUNT(*) from posts').fetchone()
    return total_count_posts[0]


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info(f"{datetime.datetime.now()}, All the posts have been retrieved for display !")
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# heathz: get the health of the application
@app.route('/healthz')
def get_health():
    app.logger.info(f"{datetime.datetime.now()},Health Request is succesful")
    return app.response_class(status=200, response=json.dumps({"result":"OK - healthy"}), mimetype='application/json')


# metrics: get the metrics of the application
#Example output: {"db_connection_count": 1, "post_count": 7}
@app.route('/metrics')
def get_metrics():
    app.logger.info(f"{datetime.datetime.now()}, Metrics Request is succesful")
    total_posts_count= get_total_posts_count()
    app.logger.info(f"{datetime.datetime.now()},db connection count is {global_db_counter}")
    app.logger.info(f"{datetime.datetime.now()},The total count of the posts is {total_posts_count}")
    return app.response_class(status=200, response=json.dumps({"db_connection_count":global_db_counter,"total_posts_count":total_posts_count}), mimetype="application/json")

# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
