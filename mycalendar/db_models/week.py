from . import db


class Week(db.Model):
    __tablename__ = "weeks"

    id = db.Column(db.Integer, primary_key=True)
    week_num = db.Column(db.Integer, nullable=False, unique=True)
    events = db.relationship("Event", backref="Week")

    def __repr__(self):
        return "<User(id=%d', week_num='%d', events='%s')>" % (
            self.id,
            self.week_num,
            self.events,
        )
