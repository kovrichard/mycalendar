from datetime import datetime


def calculate_days_of_week(year, week):
    day_of_week = []
    for i in range(1, 8):
        day_of_week.append(
            {
                "date": datetime.fromisocalendar(year, week, i)
                .date()
                .strftime("(%b. %-d)"),
                "name": datetime.fromisocalendar(year, week, i)
                .date()
                .strftime("%a"),
            }
        )

    return day_of_week


def calculate_different_year(year, week):
    if week < 1:
        year -= 1
        week = 53 if __has_53_weeks(year) else 52
    elif (week == 53 and not __has_53_weeks(year)) or (53 < week):
        year += 1
        week = 1

    return year, week


def __has_53_weeks(year):
    try:
        datetime.fromisocalendar(year, 53, 1)
        return True
    except:
        return False


def hour_number_to_24_hours_format(hour):
    tmp = ("0" + hour if len(hour) < 2 else hour) + ":00"
    return "00:00" if tmp == "24:00" else tmp
