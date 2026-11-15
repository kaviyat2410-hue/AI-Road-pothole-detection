
from ultralytics import YOLO
from flask import Flask, request, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
import os
import cv2
import json
from datetime import datetime

REPORT_FILE = "reports.json"
app = Flask(__name__)
model = YOLO("best.pt")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Pothole Detection</title>
    <style>
        
         
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f3f7f5;
    color: #20352d;
    text-align: center;
}

.box {
    background: white;
    max-width: 850px;
    width: calc(100% - 30px);
    margin: 35px auto;
    padding: 35px;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(20, 70, 50, 0.10);
}

h1 {
    color: #176b55;
    font-size: 32px;
}

h2 {
    color: #176b55;
    margin-top: 30px;
}

h3 {
    color: #294d40;
}

p {
    line-height: 1.7;
}

button {
    background: #176b55;
    color: white;
    padding: 13px 22px;
    border: none;
    border-radius: 9px;
    cursor: pointer;
    font-size: 15px;
    font-weight: bold;
    transition: background 0.2s;
}

button:hover {
    background: #104b3c;
}

input[type="file"] {
    display: block;
    max-width: 100%;
    margin: 20px auto;
    padding: 12px;
    background: #f5f8f6;
    border: 1px solid #d5e3dc;
    border-radius: 8px;
}

textarea {
    width: 100%;
    max-width: 500px;
    padding: 13px;
    border: 1px solid #cadbd2;
    border-radius: 9px;
    font-family: Arial, sans-serif;
    font-size: 15px;
    resize: vertical;
}

textarea:focus {
    outline: 2px solid #82bba4;
    border-color: #176b55;
}

img {
    width: 100%;
    max-width: 500px;
    height: auto;
    border-radius: 12px;
    margin: 10px auto;
}

.message {
    color: #176b55;
    background: #e9f6ee;
    padding: 12px;
    border-radius: 8px;
}

#location, #reportStatus {
    overflow-wrap: anywhere;
}

a {
    color: #176b55;
}

form {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e2ebe6;
}

@media (max-width: 600px) {
    .box {
        margin: 15px auto;
        padding: 22px 16px;
    }

    h1 {
        font-size: 25px;
    }

    button {
        max-width: 100%;
    }
}
.navbar {
    background: #176b55;
    color: white;
    padding: 18px 6%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
    flex-wrap: wrap;
}

.brand {
    font-size: 20px;
    font-weight: bold;
}

.nav-links {
    display: flex;
    gap: 20px;
}

.nav-links a {
    color: white;
    text-decoration: none;
    font-weight: bold;
}

.nav-links a:hover {
    text-decoration: underline;
}

/* Professional page background */
body {
    background: linear-gradient(135deg, #e8f5ee, #f4f8fc, #dceee6);
    color: #20352d;
    font-family: Arial, sans-serif;
    min-height: 100vh;
}

/* Main content card */
.box {
    background: rgba(255, 255, 255, 0.96);
    max-width: 900px;
    width: calc(100% - 30px);
    margin: 35px auto;
    padding: 35px;
    border: 1px solid #dcebe2;
    border-radius: 22px;
    box-shadow: 0 12px 35px rgba(23, 107, 85, 0.12);
}

/* Headings */
h1 {
    color: #176b55;
    font-size: 32px;
    font-weight: 800;
}

h2 {
    color: #176b55;
}

/* Modern buttons */
button {
    background: linear-gradient(135deg, #176b55, #239875);
    color: white;
    padding: 13px 24px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-weight: bold;
    box-shadow: 0 5px 12px rgba(23, 107, 85, 0.18);
    transition: 0.2s ease;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(23, 107, 85, 0.25);
}

/* Image styling */
img {
    max-width: 100%;
    height: auto;
    border-radius: 14px;
    box-shadow: 0 5px 18px rgba(0, 0, 0, 0.08);
}

/* Mobile layout */
@media (max-width: 600px) {
    .box {
        margin: 18px auto;
        padding: 22px 16px;
    }

    h1 {
        font-size: 25px;
    }
}

    </style>
</head>
<body>
<nav class="navbar">
    <div class="brand">🛣️ Pothole Detection</div>
    <div class="nav-links">
        <a href="/">Home</a>
        <a href="/admin">Admin Dashboard</a>
    </div>
</nav>
    <div class="box">
        <h1>AI-Based Pothole Detection</h1>
        <p>Upload a road image to begin.</p>
        <button type="button" onclick="getLocation()">
    Get My Location
</button>

<p id="location">Location not captured yet.</p>
<h3>Report a Pothole</h3>
<label for="reportImage">Pothole Photo:</label><br>
<input type="file"
       id="reportImage"
       accept="image/*">
<br><br>
<label for="description">Road condition:</label><br>
<textarea id="description"
          placeholder="Describe the pothole..."
          rows="3"></textarea>
<br><br>

<button type="button" onclick="submitReport()">
    Submit Report
</button>

<p id="reportStatus"></p>
<script>
let currentLatitude = null;
let currentLongitude = null;

function getLocation() {
    const output = document.getElementById("location");

    if (!navigator.geolocation) {
        output.textContent = "GPS is not supported by this browser.";
        return;
    }

    output.textContent = "Getting location...";

    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            currentLatitude = lat;
            currentLongitude = lon;

            output.innerHTML =
                "Latitude: " + lat.toFixed(6) +
                "<br>Longitude: " + lon.toFixed(6) +
                '<br><a target="_blank" href="https://www.google.com/maps?q='
                + lat + ',' + lon + '">Open in Google Maps</a>';
        },
        function(error) {
            output.textContent =
                "Location unavailable. Please allow location permission.";
            console.error("Location error:", error);
        }
    );
}


async function submitReport() {
    const description =
        document.getElementById("description").value.trim();

    const status =
        document.getElementById("reportStatus");

    const photo =
        document.getElementById("reportImage").files[0];

    if (currentLatitude === null ||
        currentLongitude === null) {
        status.textContent = "Please get your location first.";
        return;
    }

    if (!description) {
        status.textContent = "Please enter a description.";
        return;
    }

    const formData = new FormData();
    formData.append("description", description);
    formData.append("latitude", currentLatitude);
    formData.append("longitude", currentLongitude);

    if (photo) {
        formData.append("report_image", photo);
    }

    status.textContent = "Submitting report...";

    try {
        const response = await fetch("/submit-report", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        

if (!response.ok) {
    status.textContent = data.message || "Report submission failed.";
    return;
}
window.location.href = "/report-success";
return;

    } catch (error) {
        status.textContent =
            "Could not submit report. Check the server.";
    }
}

</script>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="road_image"
                   accept="image/png,image/jpeg,image/webp" required>
            <br>
            <button type="submit">Detect Potholes</button>
        </form>
        {% if message %}
            <h3 class="message">{{ message }}</h3>
        {% endif %}
        {% if result_image %}
    <h2>AI Detection Result</h2>

    <h3>Original Image</h3>
    <img src="{{ original_image }}" alt="Original image">

    <h3>Detected Potholes</h3>
    <img src="{{ result_image }}" alt="Detection result">

    <h3>{{ pothole_count }} potholes detected</h3>
{% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""
    report_status=""
    result_image = None
    original_image = None
    pothole_count = 0

    if request.method == "POST":
        file = request.files.get("road_image")

        if not file or not file.filename:
            message = "Please select an image."
        elif not file.filename.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")
        ):
            message = "Please upload a JPG, PNG or WEBP image."
        else:
            filename = secure_filename(file.filename)

            if not filename:
                message = "Invalid filename."
            else:
                image_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], filename
                )
                file.save(image_path)

                try:
                    results = model.predict(
                        source=image_path,
                        conf=0.10,
                        save=False
                    )
                    pothole_count = len(results[0].boxes)
                    original_image = "/uploads/" + filename
                    result_img = results[0].plot()
                    result_filename = "result_" + filename
                    result_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], result_filename
                    )
                    cv2.imwrite(result_path, result_img)

                    message = "Pothole detection completed!"
                    result_image = "/uploads/" + result_filename
                except Exception as e:
                    message = "Detection failed. Please check the terminal."
                    print("Detection error:", e)

    return render_template_string(
    HTML,
    message=message,
    result_image=result_image,
    original_image=original_image,
    pothole_count=pothole_count
)


@app.route("/submit-report", methods=["POST"])
def submit_report():
    description = request.form.get("description", "").strip()
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    photo = request.files.get("report_image")

    if not description:
        return {"message": "Please enter a description"}, 400

    if latitude is None or longitude is None:
        return {"message": "Please capture your location first"}, 400

    photo_filename = None

    if photo and photo.filename:
        allowed = (".jpg", ".jpeg", ".png", ".webp")

        if not photo.filename.lower().endswith(allowed):
            return {"message": "Use JPG, PNG or WEBP image"}, 400

        photo_filename = secure_filename(photo.filename)

        if not photo_filename:
            return {"message": "Invalid photo filename"}, 400

        photo_path = os.path.join(
            app.config["UPLOAD_FOLDER"], photo_filename
        )
        photo.save(photo_path)

    report = {
        "description": description,
        "latitude": latitude,
        "longitude": longitude,
        "map_link": f"https://www.google.com/maps?q={latitude},{longitude}",
        "image": photo_filename,
        "created_at": datetime.now().isoformat()
    }

    reports = []

    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            try:
                reports = json.load(f)
            except json.JSONDecodeError:
                reports = []

    reports.append(report)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=4)

    return {"message": "Report saved successfully!"}


@app.route("/admin")
def admin():
    reports = []

    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            try:
                reports = json.load(f)
            except json.JSONDecodeError:
                reports = []

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pothole Admin Dashboard</title>
        <style>
            
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #e8f5ee, #f4f8fc);
    color: #243b32;
}

.header {
    background: linear-gradient(135deg, #104b3c, #239875);
    color: white;
    padding: 35px 20px;
    text-align: center;
}

.header h1 {
    margin: 0 0 10px;
    font-size: 30px;
    color: white;
}

.header p {
    margin: 0;
    color: #e0f4e9;
}

.container {
    width: calc(100% - 30px);
    max-width: 1000px;
    margin: 30px auto;
}

.summary {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 6px 22px rgba(23, 107, 85, 0.10);
    border-left: 5px solid #239875;
    margin-bottom: 25px;
}

.summary p {
    margin: 0 0 8px;
    color: #61756b;
}

.summary h2 {
    margin: 0;
    color: #176b55;
    font-size: 32px;
}

.report {
    background: white;
    padding: 25px;
    margin: 20px 0;
    border: 1px solid #dcebe2;
    border-radius: 18px;
    box-shadow: 0 7px 25px rgba(23, 107, 85, 0.08);
    overflow-wrap: anywhere;
    transition: transform 0.2s, box-shadow 0.2s;
}

.report:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 30px rgba(23, 107, 85, 0.13);
}

.report h3 {
    color: #176b55;
    margin-top: 0;
}

.report p {
    line-height: 1.7;
}

.report img {
    display: block;
    width: 100%;
    max-width: 450px;
    height: auto;
    margin: 12px 0;
    border-radius: 12px;
    border: 1px solid #e0eae4;
}

a {
    color: #176b55;
    font-weight: bold;
    text-decoration: none;
}

.report a {
    display: inline-block;
    margin-top: 8px;
    padding: 11px 15px;
    background: #e8f5ee;
    border-radius: 8px;
}

a:hover {
    text-decoration: underline;
}

.back-link {
    display: inline-block;
    background: #176b55;
    color: white;
    padding: 13px 20px;
    border-radius: 10px;
    margin: 10px 0 30px;
}

.empty-state {
    background: white;
    padding: 30px;
    border-radius: 16px;
    text-align: center;
}

@media (max-width: 600px) {
    .header {
        padding: 28px 15px;
    }

    .header h1 {
        font-size: 24px;
    }

    .container {
        width: calc(100% - 24px);
        margin: 20px auto;
    }

    .report {
        padding: 18px;
    }
}

        </style>
    </head>
    <body>
        <div class="header">
    <h1>🛣️ Pothole Admin Dashboard</h1>
    <p>Monitor and manage reported road potholes</p>
</div>

<div class="container">
    <div class="summary">
        <p>📊 TOTAL REPORTS</p>
        <h2>{{ reports|length }}</h2>
    </div>

        {% if reports %}
            {% for report in reports|reverse %}
                <div class="report">
                    <h3>Report #{{ loop.index }}</h3>
                    <p><b>Description:</b>
                        {{ report.description }}</p>
                         
{% if report.image %}
    <p><b>Pothole Photo:</b></p>
    <img src="/uploads/{{ report.image }}"
         alt="Reported pothole"
         style="width:100%; max-width:400px; border-radius:10px;">
{% endif %}
         
                    <p><b>Latitude:</b>
                        {{ report.latitude }}</p>
                    <p><b>Longitude:</b>
                        {{ report.longitude }}</p>
                    <p><b>Submitted:</b>
                        {{ report.created_at }}</p>
                    <a href="{{ report.map_link }}"
                       target="_blank">View Location on Google Maps</a>
                </div>
            {% endfor %}
        {% else %}
            <div class="empty-state">
    <h3>No Reports Yet</h3>
    <p>Submitted pothole reports will appear here.</p>
</div>
        {% endif %}

        <a class="back-link" href="/">← Back to Detection Page</a>
</div>
    </body>
    </html>
    """, reports=reports)



@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename
    )
@app.route("/report-success")
def report_success():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Report Submitted</title>
        <style>
            body {
                font-family: Arial;
                background: #e8f5ee;
                text-align: center;
                padding: 100px 20px;
            }
            .box {
                background: white;
                padding: 40px;
                border-radius: 15px;
                max-width: 500px;
                margin: auto;
            }
            .tick {
                color: green;
                font-size: 65px;
            }
            a {
                display: inline-block;
                background: #176b55;
                color: white;
                padding: 13px 25px;
                border-radius: 8px;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <div class="tick">✓</div>
            <h1>Report Submitted Successfully!</h1>
            <p>Your pothole report has been submitted.</p>
            <a href="/admin">View Report</a>
        </div>
    </body>
    </html>
    """)
if __name__ == "__main__":
    app.run(debug=True)
