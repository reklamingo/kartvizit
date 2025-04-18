
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_info(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    lines = text.split('\n')
    info = {
        "İsim": "",
        "Ünvan": "",
        "Şirket": "",
        "Telefon": "",
        "E-posta": "",
        "Adres": "",
        "Web": ""
    }
    for line in lines:
        if "@" in line:
            info["E-posta"] = line.strip()
        elif line.strip().lower().startswith("www") or ".com" in line:
            info["Web"] = line.strip()
        elif any(c.isdigit() for c in line) and '+' in line:
            info["Telefon"] += line.strip() + ' / '
        elif any(keyword in line.lower() for keyword in ["san.", "tic.", "a.ş", "ltd", "matbaa", "lojistik"]):
            info["Şirket"] = line.strip()
        elif info["İsim"] == "" and len(line.split()) <= 4 and line.strip() != "":
            info["İsim"] = line.strip()
        else:
            info["Adres"] += line.strip() + ' '
    return info

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist('files')
        records = []
        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            data = extract_info(filepath)
            records.append(data)
        df = pd.DataFrame(records)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'kartvizitler.xlsx')
        df.to_excel(output_path, index=False)
        return send_file(output_path, as_attachment=True)
    return '''
        <!doctype html>
        <title>Karttan Excel</title>
        <h1>Kartvizit Fotoğraflarını Yükle</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=files multiple>
          <input type=submit value="Excel'e Dönüştür">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
