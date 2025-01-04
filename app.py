from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, redirect, url_for, request
from flask_migrate import Migrate, migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    original_due_date = db.Column(
        db.Date, default=date.today(), nullable=False)
    due_date = db.Column(db.Date, default=date.today(), nullable=False)
    repeat_interval = db.Column(db.Integer, default=1, nullable=False)
    repeat_often = db.Column(db.Integer, default=1, nullable=False)
    times_completed = db.Column(db.Integer, default=0, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship("User", backref=db.backref("events", lazy=True))


@app.template_filter("next_event_date")
def next_event_date_filter(
    original_due_date, repeat_interval, repeat_often, times_completed
):
    if repeat_often == 1:
        return original_due_date + relativedelta(days=repeat_interval * times_completed)
    elif repeat_often == 2:
        return original_due_date + relativedelta(
            weeks=repeat_interval * times_completed
        )
    elif repeat_often == 3:
        return original_due_date + relativedelta(
            months=repeat_interval * times_completed
        )
    elif repeat_often == 4:
        return original_due_date + relativedelta(
            years=repeat_interval * times_completed
        )


def init_db():
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            user = User(username="Player")
            db.session.add(user)
            db.session.commit()


@app.route("/")
def index():
    events = Event.query.all()
    user = User.query.first()
    return render_template("index.html", events=events, user=user)


@app.route("/add_event", methods=["POST"])
def add_event():
    name = request.form.get("name")
    original_due_date = request.form.get("start_date")
    repeat_interval = int(request.form.get("repeat_interval"))
    repeat_often = int(request.form.get("repeat_often"))
    new_event = Event(
        name=name,
        original_due_date=datetime.strptime(
            original_due_date, "%Y-%m-%d").date(),
        due_date=datetime.strptime(original_due_date, "%Y-%m-%d").date(),
        repeat_interval=repeat_interval,
        repeat_often=repeat_often,
        times_completed=0,
    )
    db.session.add(new_event)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/complete_event/<int:event_id>")
def complete_event(event_id):
    event = Event.query.get(event_id)
    event.times_completed += 1
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/delete_event/<int:event_id>")
def delete_event(event_id):
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8081)
