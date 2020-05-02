from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


class Objetivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tarefa = db.Column(db.String(50), nullable=False)
    competidor = db.Column(db.String(20), nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<Objetivo {self.id}>'


class ObjetivoSchema(Schema):
    class Meta:
        fields = ('id', 'tarefa', 'competidor', 'status')


objetivo_schema = ObjetivoSchema()
objetivos_schema = ObjetivoSchema(many=True)


class ObjetivosResource(Resource):
    def get(self):
        objetivos = Objetivo.query.all()
        return objetivos_schema.dump(objetivos)

    def post(self):
        objetivo_json = request.get_json()
        new_objetivo = Objetivo(
            tarefa=objetivo_json['tarefa'],
            competidor=objetivo_json['competidor'],
            status=False
        )
        db.session.add(new_objetivo)
        db.session.commit()
        return objetivo_schema.dump(new_objetivo)


class ObjetivoResource(Resource):
    def patch(self, objetivo_id):
        objetivo = Objetivo.query.get_or_404(objetivo_id)
        objetivo.status = request.json['status']
        db.session.commit()
        return objetivo_schema.dump(objetivo)

    def delete(self, objetivo_id):
        objetivo = Objetivo.query.get_or_404(objetivo_id)
        db.session.delete(objetivo)
        db.session.commit()
        return '', 204


api.add_resource(ObjetivosResource, '/')
api.add_resource(ObjetivoResource, '/<int:objetivo_id>')

if __name__ == '__main__':
    app.run(debug=True)
