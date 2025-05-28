from flask import Flask, request, render_template
from flask_socketio import SocketIO
import threading
from collections import deque
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

alarm_queue = deque()
is_processing_queue = False
alarm_duration_server_side = 5  # seconds, matches client-side animation duration

# Routes for UI
@app.route("/tango")
def tango():
    return render_template("indextango.html")

@app.route("/ipa")
def ipa():
    return render_template("indexipaalarm.html")

def _process_alarm_queue():
    global is_processing_queue
    while True:
        if alarm_queue:
            alarm_type = alarm_queue.popleft()
            print(f"Server processing queued alarm: {alarm_type}")
            socketio.emit("alert_received", {"msg": alarm_type})
            time.sleep(alarm_duration_server_side)
        else:
            is_processing_queue = False
            break

def start_queue_processing():
    global is_processing_queue
    if not is_processing_queue:
        is_processing_queue = True
        thread = threading.Thread(target=_process_alarm_queue)
        thread.daemon = True
        thread.start()

# Webhook endpoints
@app.route("/webhook-tango", methods=["POST"])
def webhook_tango():
    data = request.json
    print("TANGO ALERT:", data)
    alarm_queue.append("tango_alarm")
    start_queue_processing()
    return "", 204

@app.route("/webhook-ipa", methods=["POST"])
def webhook_ipa():
    data = request.json
    print("IPA ALERT:", data)
    alarm_queue.append("ipa_alarm")
    start_queue_processing()
    return "", 204

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5002, debug=True)