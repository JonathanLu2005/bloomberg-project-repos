import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from dataAnalysis import initialiseDataFrame
from werkzeug.utils import secure_filename
import shutil

UPLOAD_FOLDER = "uploads" 
ALLOWED_EXTENSIONS = {"xlsx"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_uploads_folder():
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

@app.route("/", methods=["POST", "GET"])
def homePage():
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
                clear_uploads_folder()
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                print(f"File saved at: {file_path}")

                df = initialiseDataFrame(file_path)
                result_filename = "Result.xlsx"
                result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
                df.to_excel(result_path, index=False)
                print(f"Result file saved at: {result_path}")
                return redirect(url_for('insightPage', filename=result_filename))
            except Exception as e:
                return render_template("home.html", errorMessage=f"An error occurred with the file given: {e}. Please submit another spreadsheet of the right format.")
    
    return render_template("home.html")

@app.route("/insights/<filename>")
def insightPage(filename):
    return render_template("insights.html", filename=filename)

@app.route("/download/<filename>")
def downloadFile(filename):
    try:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        print(f"Downloading file from: {file_path}")
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)