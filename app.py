from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from analysis import initialiseDataFrame, analyseData
from werkzeug.utils import secure_filename
import io
import os

UPLOAD_FOLDER = "uploads"  # This can be a temporary directory if supported by Render
ALLOWED_EXTENSIONS = {"xlsx"}

geoVar = None
tempoVar = None
dealTypeVar = None

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["POST","GET"])
def homePage():
    global geoVar
    global tempoVar
    global dealTypeVar

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            try:
                df = initialiseDataFrame(file)
                stat_headings = ["Transaction Count", "Transaction Value Mean", "Transaction Value STD", "Transaction Value Min", "Transaction Value Max"]
                geoVar = analyseData(df, "geographicalRegion", ["Geographical Region"] + stat_headings)
                
                tempoVar = analyseData(df, "declaredDate", ["Month"] + stat_headings)

                dealTypeVar = analyseData(df, "dealAttributes", ["Deal Type"] + stat_headings)

                return redirect(url_for('insightPage', filename=secure_filename(file.filename)))
                # return redirect(url_for('insightPage', filename=file.filename))
            except Exception as e:
                print(e)
                return render_template("home.html", errorMessage=f"An error occurred with the file given: {e}. Please submit another spreadsheet of the right format.")
    
    return render_template("home.html")

@app.route("/insights/<filename>")
def insightPage(filename):
    return render_template("insights.html", filename=filename, geoTable=geoVar.to_html(),\
                            tempoTable=tempoVar.to_html(), dealTypeTable=dealTypeVar.to_html())

@app.route("/download/")
def downloadFile():
    # You may need to adjust this function depending on where the file is stored
    # For Render, it might be stored in a temporary directory or cloud storage
    try:
        # Example: Directly serve file from memory (not recommended for large files)
        with open(os.path.join(app.config["UPLOAD_FOLDER"], "result.xlsx"), "rb") as f:
            return send_file(io.BytesIO(f.read()), as_attachment=True, download_name="result.xlsx")

        # Example: Redirect to a cloud storage URL
        # cloud_storage_url = get_cloud_storage_url(filename)
        # return redirect(cloud_storage_url)

        # Placeholder: return a message for simplicity
        # return f"Download endpoint for {filename}"

    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run()