from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/salvador")
def salvador():
    return "Hello, Salvador"

@app.route("/bootstrapTest")
def bootstrapTest():
    return render_template("bootstrapTest.html")
    
if __name__ == "__main__":
    app.run(debug=True)