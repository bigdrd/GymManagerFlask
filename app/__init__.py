from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db,render_as_batch=True)

#app.redis = Redis.from_url(app.config['REDIS_URL'])
#app.task_queue = rq.Queue('tornello', connection=app.redis)
#app.job = app.task_queue.enqueue("app.tornello.openOrCloseDoorListener")
login = LoginManager(app)
login.login_view = 'login'
from app import routes,forms





    