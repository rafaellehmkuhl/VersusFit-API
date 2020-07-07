from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)
api = Api(app)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    g_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    creation_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    goals = db.relationship('Goal', backref='user', lazy='dynamic')
    challenges = db.relationship('Challenge', secondary='linkuserchallenge')

    def __repr__(self):
        return f'<User {self.name}>'


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    creation_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    users = db.relationship('User', secondary='linkuserchallenge')
    goals = db.relationship('Goal', backref='challenge', lazy='dynamic')

    def __repr__(self):
        return f'<Challenge {self.name}>'


class LinkUserChallenge(db.Model):
    __tablename__ = 'linkuserchallenge'
    challenge_id = db.Column(db.Integer, db.ForeignKey(
        'challenge.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), primary_key=True)


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    repetitions = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey(
        'challenge.id'), nullable=False)
    dom_status = db.Column(db.Boolean(), nullable=False, default=False)
    seg_status = db.Column(db.Boolean(), nullable=False, default=False)
    ter_status = db.Column(db.Boolean(), nullable=False, default=False)
    qua_status = db.Column(db.Boolean(), nullable=False, default=False)
    qui_status = db.Column(db.Boolean(), nullable=False, default=False)
    sex_status = db.Column(db.Boolean(), nullable=False, default=False)
    sab_status = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return f'<Goal {self.name}>'


class GoalSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    name = fields.String()
    repetitions = fields.Int()
    dom_status = fields.Boolean()
    seg_status = fields.Boolean()
    ter_status = fields.Boolean()
    qua_status = fields.Boolean()
    qui_status = fields.Boolean()
    sex_status = fields.Boolean()
    sab_status = fields.Boolean()


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    # g_id = fields.Int()
    name = fields.String()
    creation_date = fields.DateTime()
    # goals = fields.Nested(GoalSchema, many=True)


class ChallengeSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()
    creation_date = fields.DateTime()
    users = fields.Nested(UserSchema, many=True)
    goals = fields.Nested(GoalSchema, many=True)


goal_schema = GoalSchema()
goals_schema = GoalSchema(many=True)

challenge_schema = ChallengeSchema()
challenges_schema = ChallengeSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class GoalResource(Resource):
    def get(self, goal_id):
        goal = Goal.query.get_or_404(goal_id)
        return goal_schema.dump(goal)

    def delete(self, goal_id):
        goal = Goal.query.get_or_404(goal_id)
        db.session.delete(goal)
        db.session.commit()
        return '', 204

    def patch(self, goal_id):
        goal = Goal.query.get_or_404(goal_id)

        try:
            weekday = request.get_json()['weekday']
        except KeyError as e:
            return 'Weekday key does not exist in json package', 404

        if (weekday == 'dom'):
            day_status = goal.dom_status = not goal.dom_status
        elif (weekday == 'seg'):
            day_status = goal.seg_status = not goal.seg_status
        elif (weekday == 'ter'):
            day_status = goal.ter_status = not goal.ter_status
        elif (weekday == 'qua'):
            day_status = goal.qua_status = not goal.qua_status
        elif (weekday == 'qui'):
            day_status = goal.qui_status = not goal.qui_status
        elif (weekday == 'sex'):
            day_status = goal.sex_status = not goal.sex_status
        elif (weekday == 'sab'):
            day_status = goal.sab_status = not goal.sab_status
        else:
            return 'Try one of the following values for weekday: dom, seg, ter, qua, qui, sex, sab', 404

        db.session.commit()

        return goal_schema.dump(goal)


class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return user_schema.dump(user)


class UsersResource(Resource):
    def get(self):
        users = User.query.all()
        return users_schema.dump(users)

    def post(self):
        new_user_json = request.get_json()
        registered_user = User.query.filter_by(
            g_id=new_user_json['g_id']).first()
        if registered_user:
            return user_schema.dump(registered_user)
        else:
            new_user = User(
                name=new_user_json['name'],
                g_id=new_user_json['g_id']
            )
            db.session.add(new_user)
            db.session.commit()
            return user_schema.dump(new_user)


class UserGoalsResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        goals = user.goals.all()
        return goals_schema.dump(goals)

    def post(self, user_id):
        user = User.query.get_or_404(user_id)
        goal_json = request.get_json()
        new_goal = Goal(
            name=goal_json['name'],
            repetitions=goal_json['repetitions'],
            user=user
        )
        db.session.add(new_goal)
        db.session.commit()
        return goal_schema.dump(new_goal)


class IndexResource(Resource):
    def get(self):
        return 'Welcome to the VersusFit API'


# api.add_resource(GoalsResource, '/')
api.add_resource(IndexResource, '/')
api.add_resource(UsersResource, '/users')
api.add_resource(UserResource, '/user/<string:user_id>')
api.add_resource(GoalResource, '/goal/<int:goal_id>')
api.add_resource(UserGoalsResource, '/user_goals/<string:user_id>')

if __name__ == '__main__':
    app.run(debug=True)
