from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/?retryWrites=true&loadBalanced=false&serverSelectionTimeoutMS=5000&connectTimeoutMS=10000")
db = client.webhook_db
collection = db.github_events

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if not data or not event_type:
        return jsonify({"message": "Invalid data"}), 400

    if event_type == 'ping':
        print(f"Ping event received: {data.get('zen', 'No Zen message')}")
        return jsonify({'message': 'Ping received'}), 200
    
    elif event_type == 'push':
        if 'pusher' in data and 'ref' in data:
            author = data['pusher']['name']
            to_branch = data['ref'].split('/')[-1]
            timestamp = datetime.now()
        else:
            return jsonify({'message': 'Invalid data for push event'}), 400
    
    elif event_type == 'pull_request':
        if 'pull_request' in data:
            author = data['pull_request']['user']['login']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            timestamp = datetime.now()
        else:
            return jsonify({'message': 'Invalid data for pull request event'}), 400

    else:
        return jsonify({'message': 'Unhandled event type'}), 400

    # Store the event in MongoDB
    event = {
        "action": event_type,
        "author": author,
        "from_branch": from_branch if 'from_branch' in locals() else None,
        "to_branch": to_branch,
        "timestamp": timestamp
    }
    collection.insert_one(event)
    return jsonify({'message': f'{event_type} event received'}), 200

@app.route("/events", methods=["GET"])
def get_events():
    events = list(collection.find({}))
    for event in events:
        event["_id"] = str(event["_id"])  # Convert ObjectId to string for JSON serialization
    return jsonify(events), 200

if __name__ == "__main__":
    app.run(debug=True)
