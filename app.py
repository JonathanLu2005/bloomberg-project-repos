# Import libraries
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from dataAnalysis import initialiseDataFrame, analyseData
from werkzeug.utils import secure_filename
import io
import os

# Uploaded files goes to uploads and only accept excel spreadsheets
UPLOAD_FOLDER = "uploads"  
ALLOWED_EXTENSIONS = {"xlsx"}

# Variables to hold the analysis for insights
geoVar = None
tempoVar = None
dealTypeVar = None

# Create flask app
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'

# Ensure it has the right extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home page
@app.route("/", methods=["POST","GET"])
def homePage():
    # Globalise variables to change and use later on
    global geoVar
    global tempoVar
    global dealTypeVar

    # If receive a file (POST)
    if request.method == 'POST':

        # Verifying if file has been uploaded
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        # Holds all file
        file = request.files['file']

        # If no file sent, allows user to re submit
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        # If file has been sent and has right extension
        if file and allowed_file(file.filename):
            try:
                # Clean and prepare file as a dataframe
                df = initialiseDataFrame(file)

                # Headings for statistics of each category
                stat_headings = ["Transaction Count", "Transaction Value Mean", "Transaction Value STD", "Transaction Value Min", "Transaction Value Max"]
                
                # Calls analyseData in dataAnalysis to get the relevant processed data into format for tables
                geoVar = analyseData(df, "geographicalRegion", ["Geographical Region"] + stat_headings)
                
                tempoVar = analyseData(df, "declaredDate", ["Month"] + stat_headings)

                dealTypeVar = analyseData(df, "dealAttributes", ["Deal Type"] + stat_headings)

                # Go to insightPage app route to put the results onto tables
                return redirect(url_for('insightPage', filename=secure_filename(file.filename)))
            except Exception as e:
                # Otherwise if cannot be processed, return the exception error caught
                return render_template("home.html", errorMessage=f"An error occurred with the file given: {e}. Please submit another spreadsheet of the right format.")
    
    # If no post method, then return the generic home page
    return render_template("home.html")

# For the analysis
@app.route("/insights/<filename>")
def insightPage(filename):
    # Receive results from home, then return the insights page with the provided data analysed
    return render_template("insights.html", filename=filename, geoTable=geoVar.to_html(),\
                            tempoTable=tempoVar.to_html(), dealTypeTable=dealTypeVar.to_html())

# Allows users to download file
@app.route("/download/")
def downloadFile():
    # Retrieve result from uploads and provide to user
    try:
        with open(os.path.join(app.config["UPLOAD_FOLDER"], "result.xlsx"), "rb") as f:
            return send_file(io.BytesIO(f.read()), as_attachment=True, download_name="result.xlsx")

    # If error then return exception
    except Exception as e:
        return str(e)

# Ensure app runs
if __name__ == "__main__":
    app.run()