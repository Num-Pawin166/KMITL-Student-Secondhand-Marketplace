from flask import Flask
from extensions import db, bcrypt, login_manager
from routes import api_bp
from flask_cors import CORS
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret-key'
CORS(app)
# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

# Register Blueprint
app.register_blueprint(api_bp)

if __name__ == "__main__":
    app.run(debug=True)
