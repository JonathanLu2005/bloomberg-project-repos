import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from dataAnalysis import initialiseDataFrame
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {"xlsx"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["POST","GET"])
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
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print(file_path)

            try:
                df = initialiseDataFrame(file_path)
                result_filename = "Result.xlsx"
                result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
                df.to_excel(result_path, index=False)
                return redirect(url_for('insightPage', filename=result_filename))
            except Exception as e:
                return render_template("home.html", errorMessage=f"An error occurred with the file given: {e}. Please submit another spreadsheet of the right format.")
    
    return render_template("home.html")

@app.route("/insights/<filename>")
def insightPage(filename):
    # Optionally, you can perform additional processing or analysis here
    # For now, we'll just render the insights.html template
    return render_template("insights.html", filename=filename)

@app.route("/download/<filename>")
def downloadFile(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True)