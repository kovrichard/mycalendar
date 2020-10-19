from . import db


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.Integer, nullable=False, server_default="0")
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    location = db.Column(db.String(255))
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    week_id = db.Column(db.Integer, db.ForeignKey("weeks.id"))

    def __repr__(self):
        return "<Event(id=%d', event_type='%d', title='%s', description='%s', location='%s', start='%s', end='%s', week_id='%d')>" % (
            self.id,
            self.event_type,
            self.title,
            self.description,
            self.location,
            self.start,
            self.end,
            self.week_id,
        )
