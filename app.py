from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    creation_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    goals = db.relationship('Goal', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.name}>'


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dom_status = db.Column(db.Boolean, nullable=False, default=False)
    seg_status = db.Column(db.Boolean, nullable=False, default=False)
    ter_status = db.Column(db.Boolean, nullable=False, default=False)
    qua_status = db.Column(db.Boolean, nullable=False, default=False)
    qui_status = db.Column(db.Boolean, nullable=False, default=False)
    sex_status = db.Column(db.Boolean, nullable=False, default=False)
    sab_status = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Goal {self.name}>'


class GoalSchema(Schema):
    class Meta:
        fields = ('id', 'tarefa', 'competidor', 'status')


goal_schema = GoalSchema()
goals_schema = GoalSchema(many=True)


class GoalResource(Resource):
    def get(self, goal_id):
        goal = Goal.query.get_or_404(goal_id)
        return goal_schema.dump(goal)

    def patch(self, goal_id):
        goal = Goal.query.get_or_404(goal_id)
        goal.status = request.json['status']
        db.session.commit()
        return goal_schema.dump(goal)

    def delete(self, goal_id):
        goal = Goal.query.get_or_404(goal_id)
        db.session.delete(goal)
        db.session.commit()
        return '', 204


class GoalsResource(Resource):
    def get(self):
        goals = Goal.query.all()
        return goals_schema.dump(goals)

    def post(self):
        goal_json = request.get_json()
        new_goal = Goal(
            tarefa=goal_json['tarefa'],
            competidor=goal_json['competidor'],
            status=False
        )
        db.session.add(new_goal)
        db.session.commit()
        return goal_schema.dump(new_goal)


class CompetidorResource(Resource):
    def get(self, competidor_name):
        goals = Goal.query.filter_by(competidor=competidor_name)
        return goals_schema.dump(goals)


api.add_resource(GoalsResource, '/')
api.add_resource(GoalResource, '/<int:goal_id>')
api.add_resource(CompetidorResource, '/<string:competidor_name>')

if __name__ == '__main__':
    app.run(debug=True)
