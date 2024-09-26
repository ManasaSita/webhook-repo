from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/?retryWrites=true&loadBalanced=false&serverSelectionTimeoutMS=5000&connectTimeoutMS=10000")
db = client.webhook_db
collection = db.github_events

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data and "action" in data:
        event = {
            "author": data["sender"]["login"],
            "action": data["action"],
            "repo": data["repository"]["name"],
            "timestamp": datetime.utcnow(),
        }
        # Insert event into MongoDB
        collection.insert_one(event)
        return jsonify({"message": "Event received"}), 200
    return jsonify({"message": "Invalid data"}), 400

@app.route("/events", methods=["GET"])
def get_events():
    events = list(collection.find({}))
    for event in events:
        event["_id"] = str(event["_id"])  # Convert ObjectId to string for JSON serialization
    return jsonify(events), 200

if __name__ == "__main__":
    app.run(debug=True)
