from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, redirect, url_for, request
from flask_migrate import Migrate as MigrateClass
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate_instance = MigrateClass(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   unique=True, nullable=False)  # user id
    username = db.Column(db.String(80), unique=True,
                         nullable=False)  # username


class Event(db.Model):
    id = db.Column(
        db.Integer, primary_key=True, unique=True, nullable=False
    )  # event id
    name = db.Column(db.String(80), nullable=False)  # event name
    original_due_date = db.Column(
        db.Date, default=date.today(), nullable=False
    )  # event original due date
    due_date = db.Column(
        db.Date, default=date.today(), nullable=False
    )  # event due date
    repeat_interval = db.Column(
        db.Integer, default=1, nullable=False
    )  # event repeat interval
    repeat_often = db.Column(
        db.Integer, default=1, nullable=False
    )  # event repeat often
    times_completed = db.Column(
        db.Integer, default=0, nullable=False
    )  # number of times event has completed
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))  # user id
    user = db.relationship(
        "User", backref=db.backref("events", lazy=True))  # user


@app.template_filter("next_event_date")  # next event date filter
def next_event_date_filter(
    original_due_date, repeat_interval, repeat_often, times_completed
):  # calculate next recurring event date
    if repeat_often == 1:  # if repeat interval is daily
        return original_due_date + relativedelta(
            days=repeat_interval * times_completed
        )  # add days to original date
    elif repeat_often == 2:  # if repeat interval is weekly
        return original_due_date + relativedelta(
            weeks=repeat_interval * times_completed
        )  # add weeks to original date
    elif repeat_often == 3:  # if repeat interval is monthly
        return original_due_date + relativedelta(
            months=repeat_interval * times_completed
        )  # add months to original date
    elif repeat_often == 4:  # if repeat interval is yearly
        return original_due_date + relativedelta(
            years=repeat_interval * times_completed
        )  # add years to original date


def init_db():  # initialize database
    with app.app_context():
        db.create_all()  # create tables if they don't exist
        if User.query.count() == 0:  # if there are no users
            user = User(username="Player")  # create new user
            db.session.add(user)  # add user to database
            db.session.commit()  # commit database changes


@app.route("/")
def index():  # get index page template
    events = Event.query.order_by(
        Event.due_date
    ).all()  # get list of all events sorted by due date
    user = User.query.first()  # get first user in database
    return render_template(
        "index.html", events=events, user=user
    )  # return index page template


@app.route("/add_event", methods=["POST"])
def add_event():  # add event to database
    name = request.form.get("name")  # get name from add event form
    original_due_date = request.form.get("start_date")  # get original due date
    repeat_interval = int(request.form.get(
        "repeat_interval"))  # get repeat interval
    repeat_often = int(request.form.get("repeat_often"))  # get repeat often
    new_event = Event(
        name=name,
        original_due_date=datetime.strptime(
            original_due_date, "%Y-%m-%d").date(),
        due_date=datetime.strptime(original_due_date, "%Y-%m-%d").date(),
        repeat_interval=repeat_interval,
        repeat_often=repeat_often,
        times_completed=0,
    )  # create new event with input parameters
    db.session.add(new_event)  # add new event to database
    db.session.commit()  # commit database changes
    return redirect(url_for("index"))  # redirect to index page template


@app.route("/complete_event/<int:event_id>")
def complete_event(event_id):  # complete event from event id
    event = Event.query.get(event_id)  # find event by event id
    event.times_completed += 1  # increase event times completed by 1
    event.due_date = next_event_date_filter(
        event.original_due_date,
        event.repeat_interval,
        event.repeat_often,
        event.times_completed,
    )  # calculate event due date
    db.session.commit()  # commit database changes
    return redirect(url_for("index"))  # redirect to index page template


@app.route("/delete_event/<int:event_id>")
def delete_event(event_id):  # delete event from event id
    event = Event.query.get(event_id)  # find event by event id
    if event:
        db.session.delete(event)  # delete event from database
        db.session.commit()  # commit database changes
    return redirect(url_for("index"))  # redirect to index page template


if __name__ == "__main__":
    init_db()  # initialize database
    app.run(debug=True, port=8081)  # run the server at port 8081
