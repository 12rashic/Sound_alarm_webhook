from flask import Flask, request, render_template
from flask_socketio import SocketIO
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

current_alarm = None
stop_event = threading.Event()
alarm_thread = None  # ✅ NEW: Track the running alarm thread

def _alarm_loop():
    while not stop_event.is_set() and current_alarm:
        print(f"Emitting alarm: {current_alarm}")
        socketio.emit("alert_received", {"msg": current_alarm})
        time.sleep(2)

@app.route("/webhook-tango", methods=["POST"])
def webhook_tango():
    global current_alarm, alarm_thread
    data = request.json
    print("TANGO ALERT:", data)

    # ✅ Stop any existing alarm thread
    stop_event.set()
    if alarm_thread and alarm_thread.is_alive():
        alarm_thread.join()

    # ✅ Start new alarm
    current_alarm = "tango_alarm"
    stop_event.clear()

    alarm_thread = threading.Thread(target=_alarm_loop)
    alarm_thread.daemon = True
    alarm_thread.start()

    return "", 204

@app.route("/webhook-ipa", methods=["POST"])
def webhook_ipa():
    global current_alarm, alarm_thread
    data = request.json
    print("IPA ALERT:", data)

    # ✅ Stop any existing alarm thread
    stop_event.set()
    if alarm_thread and alarm_thread.is_alive():
        alarm_thread.join()

    # ✅ Start new alarm
    current_alarm = "ipa_alarm"
    stop_event.clear()

    alarm_thread = threading.Thread(target=_alarm_loop)
    alarm_thread.daemon = True
    alarm_thread.start()

    return "", 204

@app.route("/acknowledge", methods=["POST"])
def acknowledge():
    global current_alarm, alarm_thread
    print("Alarm acknowledged by external system.")

    # ✅ Stop and join current alarm thread
    stop_event.set()
    if alarm_thread and alarm_thread.is_alive():
        alarm_thread.join()

    current_alarm = None
    socketio.emit("alarm_stopped")  # ✅ Notify all connected clients

    return "", 204

@app.route("/tango")
def tango():
    return render_template("indextango.html")

@app.route("/ipa")
def ipa():
    return render_template("indexipaalarm.html")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5002, debug=True)
