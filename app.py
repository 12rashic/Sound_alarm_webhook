from flask import Flask, request, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Routes for UI
@app.route("/tango")
def tango():
    return render_template("indextango.html")

@app.route("/ipa")
def ipa():
    return render_template("indexipaalarm.html")

# Webhook endpoints
@app.route("/webhook-tango", methods=["POST"])
def webhook_tango():
    data = request.json
    print("TANGO ALERT:", data)
    socketio.emit("alert_received", {"msg": "tango_alarm"})
    return "", 204

@app.route("/webhook-ipa", methods=["POST"])
def webhook_ipa():
    data = request.json
    print("IPA ALERT:", data)
    socketio.emit("alert_received", {"msg": "ipa_alarm"})
    return "", 204

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5002, debug=True)
