from flask import Flask

api = Flask(__name__)


@api.route('/api1', methods=['GET', 'POST'])
@api.route('/api2', methods=['GET', 'POST'])
@api.route('/api3', methods=['GET', 'POST'])
@api.route('/api4', methods=['GET', 'POST'])
def endpoint():
    return {}


if __name__ == '__main__':
    api.run()
