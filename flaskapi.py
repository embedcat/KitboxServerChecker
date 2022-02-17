from flask import Flask

api = Flask(__name__)


@api.route('/api', methods=['GET', 'POST'])
def endpoint():
    return {}


if __name__ == '__main__':
    api.run()
