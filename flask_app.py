from datetime import datetime
import pytz
from flask import Flask, redirect, render_template, request, url_for, Response
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
    ip_address = db.Column(db.String(45))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template(
            "main_page.html", attendance_records=Attendance_Records.query.all()
        )

    if not current_user.is_authenticated:
        return redirect(url_for("index"))
    ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    attendance_record = Attendance_Records(office=request.form["office"], employee=current_user, ip_address=ip_address)
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





@app.route("/export", methods=["GET"])
@login_required
def export_records():
    records = Attendance_Records.query.all()

    # Convert records to a CSV string
    csv_data = "username,office,checkin_date,ip_address\n"
    for record in records:
        csv_data += f"{record.employee.username},{record.office},{record.checkin_date},{record.ip_address}\n"

    # Create a response with the CSV data
    response = Response(csv_data, content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=attendance_records.csv"

    return response

