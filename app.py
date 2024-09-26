from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['github_events']
collection = db['events']

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Parse the webhook data
    event_type = request.headers.get('X-GitHub-Event')
    payload = data['payload']
    
    if event_type == 'push':
        author = payload['pusher']['name']
        branch = payload['ref'].split('/')[-1]
        timestamp = datetime.utcnow().strftime('%d %B %Y - %I:%M %p UTC')
        message = f"{author} pushed to {branch} on {timestamp}"
    elif event_type == 'pull_request':
        author = payload['pull_request']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = datetime.utcnow().strftime('%d %B %Y - %I:%M %p UTC')
        message = f"{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
    elif event_type == 'pull_request_review' and payload['review']['state'] == 'approved':
        author = payload['review']['user']['login']
        from_branch = payload['pull_request']['head']['ref']
        to_branch = payload['pull_request']['base']['ref']
        timestamp = datetime.utcnow().strftime('%d %B %Y - %I:%M %p UTC')
        message = f"{author} merged branch {from_branch} to {to_branch} on {timestamp}"
    else:
        return jsonify(success=False, message="Unsupported event type"), 400

    # Store in MongoDB
    collection.insert_one({
        'event_type': event_type,
        'message': message,
        'timestamp': datetime.utcnow()
    })

    return jsonify(success=True), 200

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(10))
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)