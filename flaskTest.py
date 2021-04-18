from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/move")
def salvador():
    return render_template("movingTest.html")

@app.route("/chester")
def bootstrapTest():
    return render_template("bootstrapTest.html")
    
if __name__ == "__main__":
    app.run(debug=True)