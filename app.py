import os, redis, json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/mydb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Хост 'redis-master' — стандартное имя для Redis из Helm
cache = redis.Redis(host=os.environ.get('REDIS_HOST', 'redis-master'), port=6379, db=0)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/items', methods=['GET'])
def get_items():
    cached = cache.get('items_list')
    if cached: return json.loads(cached), 200
    items = Item.query.all()
    res = [{"id": i.id, "name": i.name} for i in items]
    cache.setex('items_list', 30, json.dumps(res))
    return jsonify(res), 200

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    new_item = Item(name=data['name'])
    db.session.add(new_item)
    db.session.commit()
    cache.delete('items_list')
    return jsonify({"status": "created", "id": new_item.id}), 201
