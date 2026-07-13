from flask import Flask, render_template, request, redirect, session, flash, url_for
from db import engine, Base, SessionLocal
from ai import analyse_resume
from email_utils import send_otp

from werkzeug.security import generate_password_hash, check_password_hash

from dotenv import load_dotenv

import os
import random
import time
import json

import models
import PyPDF2
import docx


load_dotenv()


app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "temporary-secret-key"
)


Base.metadata.create_all(bind=engine)



# ================= HOME =================

@app.route("/")
def home():

    if "user" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))



@app.route("/signup", methods=["GET", "POST"])
def signup():

    db = SessionLocal()

    try:

        if request.method == "POST":

            email = request.form.get("email")
            password = request.form.get("password")

            existing_user = db.query(models.User).filter_by(
                email=email
            ).first()

            if existing_user:
                return render_template(
                    "signup.html",
                    error="User already exists."
                )

            hashed_password = generate_password_hash(password)

            new_user = models.User(
                email=email,
                password=hashed_password
            )

            db.add(new_user)
            db.commit()

            flash("Account created successfully!")

            return redirect(url_for("login"))

        return render_template("signup.html")

    except Exception as e:
        db.rollback()
        return f"Signup Error: {e}", 500

    finally:
        db.close()

# ================= LOGIN =================


@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()

    try:
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")

            if not email or not password:
                return render_template(
                    "login.html",
                    error="Please enter email and password."
                )

            user = db.query(models.User).filter(
                models.User.email == email
            ).first()

            if user and check_password_hash(user.password, password):
                session["user"] = user.email

                return redirect(url_for("dashboard"))

            return render_template(
                "login.html",
                error="Invalid Email or Password"
            )

        return render_template("login.html")

    finally:
        db.close()


# ================= DASHBOARD =================

# ================= DASHBOARD =================

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    result = None

    if request.method == "POST":

        user_goal = request.form.get(
            "role",
            ""
        ).strip()

        job_description = request.form.get(
            "job_description",
            ""
        ).strip()

        resume_text = ""

        file = request.files.get("file")

        if not file or not file.filename:

            result = {
                "error": "Please upload your resume in PDF or DOCX format."
            }

        else:

            filename = file.filename.lower()

            try:

                if filename.endswith(".pdf"):

                    pdf_reader = PyPDF2.PdfReader(file)

                    extracted_pages = []

                    for page in pdf_reader.pages:

                        page_text = page.extract_text()

                        if page_text:
                            extracted_pages.append(page_text)

                    resume_text = "\n".join(
                        extracted_pages
                    ).strip()

                elif filename.endswith(".docx"):

                    document = docx.Document(file)

                    resume_text = "\n".join(
                        paragraph.text
                        for paragraph in document.paragraphs
                        if paragraph.text.strip()
                    ).strip()

                else:

                    result = {
                        "error": "Only PDF and DOCX files are supported."
                    }

            except Exception as e:

                result = {
                    "error": f"Could not read the uploaded resume: {str(e)}"
                }

        if result is None:

            if not user_goal:

                result = {
                    "error": "Please enter a target role."
                }

            elif not resume_text:

                result = {
                    "error": (
                        "Resume text could not be extracted. "
                        "Please upload a text-based PDF or DOCX file."
                    )
                }

            else:

                try:

                    result = analyse_resume(
                        resume_text,
                        user_goal,
                        job_description
                    )

                    db = SessionLocal()

                    try:

                        user = db.query(models.User).filter_by(
                            email=session["user"]
                        ).first()

                        if user:

                            report = models.Report(
                                user_id=user.id,
                                resume_text=resume_text,
                                result=json.dumps(result)
                            )

                            db.add(report)
                            db.commit()

                    except Exception:

                        db.rollback()
                        raise

                    finally:

                        db.close()

                except Exception as e:

                    result = {
                        "error": str(e)
                    }

    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )




# ================= HISTORY =================


@app.route("/history")
def history():


    if "user" not in session:

        return redirect(url_for("login"))



    db = SessionLocal()



    user = db.query(models.User).filter_by(
        email=session["user"]
    ).first()



    reports = db.query(models.Report).filter_by(
        user_id=user.id
    ).all()



    parsed_reports = []



    for report in reports:


        parsed_reports.append({

            "resume": report.resume_text,

            "result": json.loads(
                report.result
            )

        })



    db.close()



    return render_template(

        "history.html",

        reports=parsed_reports

    )





# ================= FORGOT PASSWORD =================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email", "").strip()

        if not email:
            return render_template(
                "forgot_password.html",
                error="Please enter your email address."
            )

        db = SessionLocal()

        try:
            user = db.query(models.User).filter_by(
                email=email
            ).first()

            if not user:
                return render_template(
                    "forgot_password.html",
                    error="Email not registered."
                )

            otp = str(
                random.randint(100000, 999999)
            )

            session["otp"] = otp
            session["otp_time"] = time.time()
            session["reset_email"] = email

            email_sent = send_otp(
                email,
                otp
            )

            if not email_sent:
                session.pop("otp", None)
                session.pop("otp_time", None)
                session.pop("reset_email", None)

                return render_template(
                    "forgot_password.html",
                    error="OTP could not be sent. Please check email settings."
                )

            flash(
                "OTP sent successfully. Please check your inbox and spam folder."
            )

            return redirect(
                url_for("verify_otp")
            )

        except Exception as e:
            return render_template(
                "forgot_password.html",
                error=f"Something went wrong: {str(e)}"
            )

        finally:
            db.close()

    return render_template(
        "forgot_password.html"
    )




# ================= VERIFY OTP =================


@app.route("/verify-otp", methods=["GET","POST"])
def verify_otp():


    if request.method=="POST":


        entered_otp = request.form.get(
            "otp"
        )


        if time.time() - session.get(
            "otp_time",
            0
        ) > 300:


            return render_template(
                "verify_otp.html",
                error="OTP expired."
            )



        if entered_otp == session.get(
            "otp"
        ):


            session["otp_verified"] = True


            return redirect(
                "/reset-password"
            )



        return render_template(
            "verify_otp.html",
            error="Invalid OTP"
        )



    return render_template(
        "verify_otp.html"
    )





# ================= RESET PASSWORD =================


@app.route("/reset-password", methods=["GET","POST"])
def reset_password():


    if not session.get(
        "otp_verified"
    ):

        return redirect(
            "/forgot-password"
        )



    if request.method=="POST":


        new_password = request.form.get(
            "new_password"
        )


        confirm_password = request.form.get(
            "confirm_password"
        )



        if new_password != confirm_password:


            return render_template(
                "reset_password.html",
                error="Passwords do not match."
            )



        db = SessionLocal()



        user = db.query(models.User).filter_by(
            email=session["reset_email"]
        ).first()



        user.password = generate_password_hash(
            new_password
        )


        db.commit()

        db.close()



        session.clear()



        flash(
            "Password reset successful!"
        )


        return redirect(url_for("login"))



    return render_template(
        "reset_password.html"
    )





# ================= LOGOUT =================


@app.route("/logout")
def logout():


    session.clear()


    return redirect(url_for("login"))



if __name__=="__main__":


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )