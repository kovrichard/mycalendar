from . import db


class Week(db.Model):
    __tablename__ = "weeks"
    __table_args__ = (
        db.UniqueConstraint("year", "week_num", name="unique_year_week"),
    )

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    week_num = db.Column(db.Integer, nullable=False)
    events = db.relationship("Event", backref="Week")

    def __repr__(self):
        return "<User(id=%d', year='%d', week_num='%d', events='%s')>" % (
            self.id,
            self.year,
            self.week_num,
            self.events,
        )
