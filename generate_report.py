import requests
import pandas as pd
from fpdf import FPDF
from datetime import datetime, timedelta
import argparse
import json

# ----------------------------
# Configuration
# ----------------------------
API_URL = "http://localhost:1880/api/v1/alert_groups/"
API_KEY = "d38faf14c8585b897476d4316316e840a7f01c053724dcff297dedcfa6b44ee3"

HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

# ----------------------------
# Argument Parsing
# ----------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Generate Grafana OnCall Alert Report")
    parser.add_argument("--days", type=int, default=3, help="Look back this many days (default: 3)")
    return parser.parse_args()

def load_json_from_file(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


# ----------------------------
# Fetch Alert Group Data
# ----------------------------
def fetch_alert_groups():
    response = requests.get(API_URL, headers=HEADERS, verify=False)
    if response.status_code != 200:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")
    return response.json()

# ----------------------------
# Filter Alerts by Date Range
# ----------------------------
def filter_alerts_by_days(alert_groups, days):
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days)
    
    filtered = []
    for group in alert_groups:
        created_at_str = group.get('created_at')
        if not created_at_str:
            continue
        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", ""))
            if created_at >= cutoff:
                filtered.append(group)
        except ValueError:
            continue
    return filtered

# ----------------------------
# Generate CSV Report
# ----------------------------
def generate_csv(alert_groups, filename='grafana_oncall_report.csv'):
    #report_data = []
    nanobsc_data = []
    smsc_data = []

    for group in alert_groups:
        last_alert = group.get('last_alert', {})
        payload = last_alert.get('payload', {})
        first_alert = payload.get('alerts', [{}])[0]
        labels = first_alert.get('labels', {})
        annotations = first_alert.get('annotations', {})

        #if not isinstance(group, dict):
        # continue
#
        #last_alert = group.get('last_alert') or {}
        #if not isinstance(last_alert, dict):
        #    continue
        ##payload = last_alert.get('payload', {}) 
        #alerts = payload.get('alerts', [])
        #first_alert = alerts[0] if alerts and isinstance(alerts[0], dict) else {}
#
        #labels = first_alert.get('labels', {}) if isinstance(first_alert, dict) else {}
        #annotations = first_alert.get('annotations', {}) if isinstance(first_alert, dict) else {}
#
        #alertname = labels.get('alertname', '')
        
        report_data=({
            'Alert ID': group.get('id'),
            'Created At': group.get('created_at'),
            'State': group.get('state'),
            'Title': group.get('title', '').strip(),
            'Hostname': labels.get('hostname', ''),
            'Service Name': labels.get('service_name', ''),
            'Alert Name': labels.get('alertname', ''),
            'Severity': labels.get('severity', ''),
            'Description': annotations.get('description', ''),
            'Summary': annotations.get('summary', ''),
            'Generator URL': first_alert.get('generatorURL', ''),
        })
        alertname = labels.get('alertname', '').strip()
        if alertname == "NanoBSC Alarm":
            nanobsc_data.append(report_data)
        elif alertname == "SMSC Alarm":
            smsc_data.append(report_data)
    #df = pd.DataFrame(report_data)
    #df.to_csv(filename, index=False)
    #print(f"[✔] CSV report saved to {filename}")

    

    if nanobsc_data:
        pd.DataFrame(nanobsc_data).to_csv("NanoBSC_Alarm_Report.csv", index=False)
        print("[✔] Saved: NanoBSC_Alarm_Report.csv")
    else:
        print("[!] No NanoBSC Alarm alerts found.")
       

    if smsc_data:
        pd.DataFrame(smsc_data).to_csv("SMSC_Alarm_Report.csv", index=False)
        print("[✔] Saved: SMSC_Alarm_Report.csv")
    else:
        print("[!] No SMSC Alarm alerts found.")
       

# ----------------------------
# Generate PDF Report
# ----------------------------
#def generate_pdf(alert_groups, filename='grafana_oncall_report.pdf'):
#    pdf = FPDF()
#    pdf.add_page()
#    pdf.set_font("Arial", 'B', 14)
#    pdf.cell(200, 10, txt="Grafana OnCall Alert Report", ln=True, align='C')
#    pdf.set_font("Arial", size=10)
#
#    for group in alert_groups:
#        pdf.ln(5)
#        pdf.cell(200, 10, txt=f"Alert ID: {group.get('id')}", ln=True)
#        pdf.cell(200, 10, txt=f"Title: {group.get('title')}", ln=True)
#        pdf.cell(200, 10, txt=f"Status: {group.get('status')}", ln=True)
#        pdf.cell(200, 10, txt=f"Created At: {group.get('created_at')}", ln=True)
#        pdf.cell(200, 10, txt=f"Service: {group.get('service', {}).get('name', '')}", ln=True)
#        pdf.cell(200, 10, txt=f"Labels: {group.get('labels')}", ln=True)
#        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
#
#    pdf.output(filename)
#    print(f"[✔] PDF report saved to {filename}")
#
# ----------------------------
# Main Execution
# ----------------------------
def main():
    args = parse_args()

    try:
        print(f"[...] Fetching alert groups from Grafana OnCall API (last {args.days} days)")
        #data = fetch_alert_groups()
        data = load_json_from_file("report.json")
        alert_groups = data.get('results', [])  # Adjust key if needed

        if not alert_groups:
            print("[!] No alert groups found.")
            return

        filtered_alerts = filter_alerts_by_days(alert_groups, args.days)

        if not filtered_alerts:
            print(f"[!] No alerts found in the last {args.days} days.")
            return

        generate_csv(filtered_alerts)
        generate_pdf(filtered_alerts)

    except Exception as e:
        print(f"[✖] Error: {e}")

if __name__ == "__main__":
    main()