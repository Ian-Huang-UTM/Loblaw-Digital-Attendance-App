from datetime import datetime
import pytz
from flask import Flask, redirect, render_template, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    LoginManager,
    logout_user,
    UserMixin,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash



app = Flask(__name__)

app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = (
    "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="craigreed",
        password="ianhuangloblaw",
        hostname="craigreed.mysql.pythonanywhere-services.com",
        databasename="craigreed$attendance_records",
    )
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.secret_key = "sdfsdfsdf"
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()


class Attendance_Records(db.Model):

    __tablename__ = "attendance_records"

    id = db.Column(db.Integer, primary_key=True)
    office = db.Column(db.String(4096))
    checkin_date = db.Column(
        db.DateTime, default=lambda: datetime.now(pytz.timezone("America/Toronto"))
    )
    employee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    employee = db.relationship("User", foreign_keys=employee_id)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template(
            "main_page.html", attendance_records=Attendance_Record.query.all()
        )

    if not current_user.is_authenticated:
        return redirect(url_for("index"))

    attendance = Attendance(office=request.form["offices"], employee=current_user)
    db.session.add(attendance_record)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for("index"))


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
