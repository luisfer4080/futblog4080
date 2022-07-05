from flask import Flask, render_template


# Create Flask instance

app = Flask(__name__)

# Start the creation of routes

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user=name)

# Create error pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def internal_server_errpr(e):
    return render_template("500.html"), 500



