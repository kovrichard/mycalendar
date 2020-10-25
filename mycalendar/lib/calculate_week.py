from datetime import datetime


def calculate_days_of_week(year, week):
    day_of_week = []
    for i in range(1, 8):
        day_of_week.append(
            {
                "date": datetime.fromisocalendar(year, week, i).date(),
                "name": datetime.fromisocalendar(year, week, i)
                .date()
                .strftime("%A"),
            }
        )

    return day_of_week
