import datetime
import io
import re
import json
import pytesseract
from PIL import Image
from flask import Flask, request, render_template, redirect, url_for, session

from tesseract_pack import data_here

tesseract_loc = data_here

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\\n\\xec]/'


@app.route("/")
def home():
    return render_template("index.html", title="Card Reader")


@app.route("/scanner", methods=["GET", "POST"])
def scan_file():
    if request.method == "POST":
        start_time = datetime.datetime.now()

        image_data = request.files["file"].read()

        text = pytesseract.image_to_string(Image.open(io.BytesIO(image_data)))

        print("Found data:", text)

        phoneNums = re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", text)
        emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
        # attempt to use regular expressions to parse out names/titles (not
        # necessarily reliable)
        nameExp = r"^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}"
        names = re.findall(nameExp, text)

        # address_regex = r'\d{1,3}[ \-]?\d{1,3}[ \-]?\d{1,3}[ \-]?\d{1,3}'
        regexp = "[0-9]{1,3} .+, .+, [A-Z]{2} [0-9]{5}"
        address = re.findall(regexp, text)
        # address = re.findall(address_regex, text)
        # t=text
        # place = locationtagger.find_locations(text = t)
        data = {
            "text": text,
            "phones": phoneNums,
            "emails": emails,
            "names": names,
            "address": address,
        }

        session["data"] = {
            "text": json.dumps(data),
            "time": str((datetime.datetime.now() - start_time).total_seconds()),
        }

        return redirect(url_for("result"))


@app.route("/result")
def result():
    if "data" in session:
        data = session["data"]
        return render_template(
            "result.html",
            title="Result",
            time=data["time"],
            text=data["text"],
            words=len(data["text"].split(" ")),
        )
    else:
        return "Wrong request method."


@app.route("/api", methods=["GET", "POST"])
def main():
    res = "process file are not found"
    if request.method == "POST":
        image_data = request.files["file"].read()
        f = io.BytesIO(image_data)
        print(f)
        text = pytesseract.image_to_string(Image.open(io.BytesIO(image_data)))
        print("Found data:", text)
        phoneNums = re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", text)
        emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
        # attempt to use regular expressions to parse out names/titles (not
        # necessarily reliable)
        nameExp = r"^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}"
        names = re.findall(nameExp, text)

        # address_regex = r'\d{1,3}[ \-]?\d{1,3}[ \-]?\d{1,3}[ \-]?\d{1,3}'
        regexp = "[0-9]{1,3} .+, .+, [A-Z]{2} [0-9]{5}"
        address = re.findall(regexp, text)
        # address = re.findall(address_regex, text)
        # t=text
        # place = locationtagger.find_locations(text = t)
        data = {
            "text": text,
            "phones": phoneNums,
            "emails": emails,
            "names": names,
            "address": address,
        }

        return json.dumps(data)
    else:
        return res


@app.route("/health")
def chk():
    return ""


if __name__ == "__main__":
    # Setup Tesseract executable path
    path = tesseract_loc  # + "\\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = path
    # print(path)
    app.run(debug=True)
