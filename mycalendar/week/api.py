from flask import Blueprint, render_template, request
from flask_user import current_user, login_required

from mycalendar.db_models import db
from mycalendar.db_models.event import Event
from mycalendar.db_models.week import Week

week_bp = Blueprint("week", __name__, template_folder="templates")


@week_bp.route("/<int:year>/<int:week>", methods=["GET", "POST"])
@login_required
def get_week(year, week):
    year, week = calculate_different_year(year, week)

    if request.method == "GET":
        return handle_get(year, week)
    else:
        return handle_post(year, week)


def handle_get(year, week):
    tmp = Week.query.filter_by(year=year, week_num=week).first()

    if tmp is None:
        new_week = Week(year=year, week_num=week)
        db.session.add(new_week)
        db.session.commit()

    return render_template("week.html", year_number=year, week_number=week)


def handle_post(year, week):
    event_type = 1 if "business_hour" in request.form else 0

    if current_week := Week.query.filter_by(year=year, week_num=week).first():
        if event := Event.query.filter_by(
            start=f"{request.form['start_date']} {request.form['start_time']}",
            end=f"{request.form['end_date']} {request.form['end_time']}",
        ).first():
            event.title = request.form["title"]
            event.description = request.form["description"]
            event.location = request.form["location"]
            event.event_type = event_type
        else:
            event = Event(
                title=request.form["title"],
                description=request.form["description"],
                location=request.form["location"],
                start=f"{request.form['start_date']} {request.form['start_time']}",
                end=f"{request.form['end_date']} {request.form['end_time']}",
                event_type=event_type,
            )
            db.session.add(event)

            current_week.events.append(event)
            current_user.events.append(event)

        db.session.commit()

    return render_template("week.html", year_number=year, week_number=week)


def calculate_different_year(year, week):
    if week < 1:
        year -= 1
        week = 53
    elif 53 < week:
        year += 1
        week = 1

    return year, week
