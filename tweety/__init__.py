from flask import Flask
from tweety.routes import main_routes, menu_routes
from tweety.models import db, migrate
from dotenv import load_dotenv
import os
load_dotenv()

# DATABASE_URI = os.getenv('DATABASE_URL')   
DATABASE_URI='postgres://wplgawvm:SIGuNevjiGyG5REvNeP22c8Rq7v3X3EL@satao.db.elephantsql.com:5432/wplgawvm'

# factory pattern
def create_app():
    app = Flask(__name__)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main_routes.main_routes)
    app.register_blueprint(menu_routes.menu_routes, url_prefix='/')
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
