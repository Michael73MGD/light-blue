from flask import Flask, render_template
import time
app = Flask(__name__)

FEN = "FEN test"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/move")
def salvador():
    return render_template("movingTest.html")

@app.route("/chester")
def bootstrapTest():
    #return render_template("bootstrapTest.html")
    return render_template('bootstrapTest.html', FEN=FEN)   #{{FEN}}     to access in html

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    jsdata = request.form['javascript_data']
    return jsdata
    #in JS: 
    #$.post( "/postmethod", {
    #javascript_data: data 
    #});
if __name__ == "__main__":
    app.run(debug=True)