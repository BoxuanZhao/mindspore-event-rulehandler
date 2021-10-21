import os
import json
from flask import Flask, request
from rule_generator import rule_generator

app = Flask(__name__)


@app.route('/rulehandler', methods=['POST', 'GET'])
def rulehandler():
    issue = {}
    if request.method == 'POST':
        issue = request.get_json()
    else:
        pass

    # type(issue) = <class 'dict'>
    rules = rule_generator(issue)

    return json.dumps(rules)


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=int(os.environ.get('PORT', 8080)))
