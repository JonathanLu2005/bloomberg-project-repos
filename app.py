import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dataAnalysis import initialiseDataFrame
from werkzeug.utils import secure_filename

# Source - https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/

# Constructs a relative path to the folder where where excel files can be uploaded to
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {"xlsx"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["POST","GET"])
def homePage():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('insightPage',
                                    f=filename))
    
    return render_template("home.html")

@app.route("/insights/<f>")
def insightPage(f):
    try:
        df = initialiseDataFrame(os.path.join(UPLOAD_FOLDER, f))
        # could use get min, max, median, mean etc of the transaction value
        return str(df)
    except Exception as e:
        return f"An error occured with the file given:<br>{e}"
    
if __name__ == "__main__":
    app.run()