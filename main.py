from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from views import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=False)
