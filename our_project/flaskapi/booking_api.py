from flask import Flask
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app)

# SQLite Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'




app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Booking model
class BookingModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    hotel = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    nights = db.Column(db.Integer, nullable=False)

# Create DB tables
with app.app_context():
    db.create_all()

# Request parser
booking_parser = reqparse.RequestParser()
booking_parser.add_argument('user', type=str, required=True, help='User name is required')
booking_parser.add_argument('hotel', type=str, required=True, help='Hotel name is required')
booking_parser.add_argument('date', type=str, required=True, help='Booking date is required')
booking_parser.add_argument('nights', type=int, required=True, help='Number of nights is required')

# Output fields
booking_fields = {
    'id': fields.Integer,
    'user': fields.String,
    'hotel': fields.String,
    'date': fields.String,
    'nights': fields.Integer
}

class BookingList(Resource):
    @marshal_with(booking_fields)
    def get(self):
        bookings = BookingModel.query.all()
        return bookings, 200

    @marshal_with(booking_fields)
    def post(self):
        args = booking_parser.parse_args()
        new_booking = BookingModel(
            user=args['user'],
            hotel=args['hotel'],
            date=args['date'],
            nights=args['nights']
        )
        db.session.add(new_booking)
        db.session.commit()
        return new_booking, 201

class Booking(Resource):
    @marshal_with(booking_fields)
    def get(self, booking_id):
        booking = BookingModel.query.get_or_404(booking_id)
        return booking

    @marshal_with(booking_fields)
    def put(self, booking_id):
        args = booking_parser.parse_args()
        booking = BookingModel.query.get_or_404(booking_id)
        booking.user = args['user']
        booking.hotel = args['hotel']
        booking.date = args['date']
        booking.nights = args['nights']
        db.session.commit()
        return booking, 200

    def delete(self, booking_id):
        booking = BookingModel.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        return {'message': f'Booking {booking_id} deleted'}, 200

# Routes
api.add_resource(BookingList, '/bookings')
api.add_resource(Booking, '/bookings/<int:booking_id>')

if __name__ == '__main__':
    app.run(debug=True)
