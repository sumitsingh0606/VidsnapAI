import os
import uuid

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# ── Constants ──────────────────────────────────────────────────────────────────
UPLOAD_FOLDER = "user_uploads"
ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "png", "jpg", "jpeg"}

# ── App setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB max upload


# ── Helpers ────────────────────────────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_dirs():
    """Make sure upload and reel output directories exist at startup."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join("static", "reels"), exist_ok=True)


ensure_dirs()


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    # Generate a fresh UUID for each GET visit; reuse it on POST
    myid = str(uuid.uuid1())

    if request.method == "POST":
        rec_id = request.form.get("uuid", "").strip()
        desc = request.form.get("text", "").strip()

        if not rec_id:
            flash("Invalid form submission — missing ID.", "danger")
            return redirect(url_for("create"))

        # Build the upload directory for this submission
        upload_dir = os.path.join(app.config["UPLOAD_FOLDER"], rec_id)
        os.makedirs(upload_dir, exist_ok=True)

        # Save the voice-over text
        with open(os.path.join(upload_dir, "desc.txt"), "w") as f:
            f.write(desc)

        # Save uploaded files and build the ffmpeg concat list
        input_files = []
        for key in request.files:
            file = request.files[key]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_dir, filename))
                input_files.append(filename)

        if not input_files:
            flash("Please upload at least one valid file.", "warning")
            return redirect(url_for("create"))

        # Write ffmpeg concat input list
        with open(os.path.join(upload_dir, "input.txt"), "w") as f:
            for fl in input_files:
                f.write(f"file '{fl}'\nduration 1\n")

        flash("Your reel is being processed! Check the gallery in a minute.", "success")
        return redirect(url_for("gallery"))

    return render_template("create.html", myid=myid)


@app.route("/gallery")
def gallery():
    reels_dir = os.path.join("static", "reels")
    reels = [r for r in os.listdir(reels_dir) if r.endswith(".mp4")]
    return render_template("gallery.html", reels=reels)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Use debug=False in production; Railway uses gunicorn anyway
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
