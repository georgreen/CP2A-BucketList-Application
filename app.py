from flask import Flask

app = Flask(__name__)


@app.errorhandler(404)
def index(e):
    return "Not Implemented"


if __name__ == '__main__':
    app.run()
