from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from dataAnalysis import initialiseDataFrame
from werkzeug.utils import secure_filename
import io

UPLOAD_FOLDER = "uploads"  # This can be a temporary directory if supported by Render
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
            try:
                df = initialiseDataFrame(file)
                return redirect(url_for('insightPage', filename=file.filename))
            except Exception as e:
                return render_template("home.html", errorMessage=f"An error occurred with the file given: {e}. Please submit another spreadsheet of the right format.")
    
    return render_template("home.html")

@app.route("/insights/<filename>")
def insightPage(filename):
    return render_template("insights.html", filename=filename)

@app.route("/download/<filename>")
def downloadFile(filename):
    # You may need to adjust this function depending on where the file is stored
    # For Render, it might be stored in a temporary directory or cloud storage
    try:
        # Example: Directly serve file from memory (not recommended for large files)
        # with open(os.path.join(app.config["UPLOAD_FOLDER"], filename), "rb") as f:
        #     return send_file(io.BytesIO(f.read()), as_attachment=True, download_name=filename)

        # Example: Redirect to a cloud storage URL
        # cloud_storage_url = get_cloud_storage_url(filename)
        # return redirect(cloud_storage_url)

        # Placeholder: return a message for simplicity
        return f"Download endpoint for {filename}"

    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)