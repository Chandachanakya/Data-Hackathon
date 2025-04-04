from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__, template_folder="templates")
UPLOAD_FOLDER = "uploads"
CLEANED_FOLDER = "cleaned"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

def clean_data(df):
    """Cleans the uploaded dataset"""
    df.drop_duplicates(inplace=True)  # Remove duplicates
    df.dropna(inplace=True)  # Remove missing values
    
    # Remove outliers using IQR method
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        df = df[(df[col] >= Q1 - 1.5 * IQR) & (df[col] <= Q3 + 1.5 * IQR)]
    
    return df

@app.route("/", methods=["GET", "POST"])
def index():
    cleaned_data_html = None
    if request.method == "POST":
        uploaded_file = request.files["file"]
        
        if uploaded_file.filename == "":
            return "No file selected", 400

        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(file_path)
        
        # Detect file type
        file_ext = uploaded_file.filename.split(".")[-1].lower()
        
        if file_ext == "csv":
            df = pd.read_csv(file_path)
        elif file_ext in ["xls", "xlsx"]:
            df = pd.read_excel(file_path)
        elif file_ext == "xml":
            df = pd.read_xml(file_path)
        else:
            return "Unsupported file format", 400
        
        cleaned_df = clean_data(df)
        
        # Save cleaned file
        cleaned_file_path = os.path.join(CLEANED_FOLDER, f"cleaned_{uploaded_file.filename}")
        cleaned_df.to_csv(cleaned_file_path, index=False)

        # Convert to HTML for display
        cleaned_data_html = cleaned_df.to_html(classes="table table-bordered table-striped", index=False)

    return render_template("index.html", cleaned_data=cleaned_data_html)

@app.route("/download")
def download():
    files = os.listdir(CLEANED_FOLDER)
    if files:
        return send_file(os.path.join(CLEANED_FOLDER, files[-1]), as_attachment=True)
    return "No cleaned files available", 400

if __name__ == "__main__":
    app.run(debug=True)
