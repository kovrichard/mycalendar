import unittest
from datetime import datetime

from ddt import data, ddt, unpack
from truth.truth import AssertThat

from mycalendar.lib.datetime_calculator import (
    calculate_days_of_week,
    calculate_different_year,
    hour_number_to_24_hours_format,
)


@ddt
class DateTimeCalculatorTest(unittest.TestCase):
    def test_calculate_days_of_week_calculates_weekdays_correctly(self):
        now = datetime.now().isocalendar()

        days_of_week = calculate_days_of_week(now[0], now[1])

        for i in range(1, 8):
            AssertThat(days_of_week[i - 1]["date"]).IsEqualTo(
                datetime.fromisocalendar(now[0], now[1], i).date()
            )
            AssertThat(days_of_week[i - 1]["name"]).IsEqualTo(
                datetime.fromisocalendar(now[0], now[1], i)
                .date()
                .strftime("%A")
            )

    @data(
        (2020, -1, 2019, 52),
        (2020, 0, 2019, 52),
        (2020, 52, 2020, 52),
        (2020, 53, 2020, 53),
        (2020, 54, 2021, 1),
        (2021, -1, 2020, 53),
        (2021, 0, 2020, 53),
        (2021, 52, 2021, 52),
        (2021, 53, 2022, 1),
        (2021, 54, 2022, 1),
        (
            datetime.now().isocalendar()[0],
            datetime.now().isocalendar()[1],
            datetime.now().isocalendar()[0],
            datetime.now().isocalendar()[1],
        ),
    )
    @unpack
    def test_calculate_different_year_handles_anniversaries_correctly(
        self, year, week, expected_year, expected_week
    ):
        calculated_year, calculated_week = calculate_different_year(year, week)

        AssertThat(calculated_year).IsEqualTo(expected_year)
        AssertThat(calculated_week).IsEqualTo(expected_week)

    @data(
        ("0", "00:00"),
        ("1", "01:00"),
        ("2", "02:00"),
        ("3", "03:00"),
        ("4", "04:00"),
        ("5", "05:00"),
        ("6", "06:00"),
        ("7", "07:00"),
        ("8", "08:00"),
        ("9", "09:00"),
        ("10", "10:00"),
        ("11", "11:00"),
        ("12", "12:00"),
        ("13", "13:00"),
        ("14", "14:00"),
        ("15", "15:00"),
        ("16", "16:00"),
        ("17", "17:00"),
        ("18", "18:00"),
        ("19", "19:00"),
        ("20", "20:00"),
        ("21", "21:00"),
        ("22", "22:00"),
        ("23", "23:00"),
        ("24", "00:00"),
    )
    @unpack
    def test_hour_number_to_24_hours_format_transforms_correctly(
        self, hour, expected_hour
    ):
        calculated_hour = hour_number_to_24_hours_format(hour)

        AssertThat(calculated_hour).IsEqualTo(expected_hour)
