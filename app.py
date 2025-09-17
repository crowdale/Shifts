import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import datetime
import pandas as pd

# Define shift types and times
shift_times = {
    "AM": "06:00–14:00",
    "Day": "07:30–15:30",
    "Flex": "07:30–15:30",
    "Dev day": "07:30–16:30",
    "PM": "13:30–21:30",
    "Night": "21:00–06:30",
    "Day Off": "—"
}

# All lunch breaks are 30 minutes
lunch_break = "30 minutes"

# Define Alan R Jones's 7-week rota
alan_rota = {
    1: ["PM", "Night", "Night", "Night", "Day Off", "Day Off", "Day Off"],
    2: ["Flex"] * 7,
    3: ["Day Off", "Day Off", "Day Off", "AM", "AM", "AM", "AM"],
    4: ["Day Off", "PM", "PM", "PM", "PM", "Day Off", "Day Off"],
    5: ["Day", "Day", "Dev day", "Day", "Day", "Day Off", "Day Off"],
    6: ["AM", "AM", "AM", "Day Off", "Night", "Night", "Night"],
    7: ["Night", "Day Off", "Day Off", "Day Off", "Day Off", "PM", "PM"]
}

# Other managers and their starting weeks
managers = {
    "Alan R Jones": 1,
    "Greg Hackett": 2,
    "Lea Meadows": 3,
    "Joe Grimes": 4,
    "Alex Elliott": 5,
    "Sam Tomlin": 6,
    "Andy Healy": 7
}

# Rota start date
rota_start = datetime.date(2025, 9, 15)

# Get shift for a given manager and date
def get_shift(manager, date):
    days_since_start = (date - rota_start).days
    week_number = (days_since_start // 7) % 7 + 1
    weekday = date.weekday()  # Monday=0, Sunday=6
    start_week = managers[manager]
    adjusted_week = (week_number - start_week + 7) % 7 + 1
    shift = alan_rota[adjusted_week][weekday]
    return shift, shift_times[shift]

# Create the Dash app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Shift Rota Dashboard"),
    html.Label("Select a date:"),
    dcc.DatePickerSingle(
        id='date-picker',
        min_date_allowed=rota_start,
        max_date_allowed=rota_start + datetime.timedelta(weeks=52),
        initial_visible_month=rota_start,
        date=rota_start
    ),
    html.Div(id='output')
])

@app.callback(
    Output('output', 'children'),
    Input('date-picker', 'date')
)
def update_output(date_str):
    if date_str is None:
        return ""
    date = datetime.date.fromisoformat(date_str)
    rows = []
    for manager in managers:
        shift, time = get_shift(manager, date)
        rows.append(html.Tr([
            html.Td(manager),
            html.Td(shift),
            html.Td(time),
            html.Td(lunch_break)
        ]))
    # Determine handover info for Alan
    alan_shift, _ = get_shift("Alan R Jones", date)
    handover_from = ""
    handover_to = ""
    if alan_shift == "Night":
        prev_day = date - datetime.timedelta(days=1)
        for mgr in managers:
            if get_shift(mgr, prev_day)[0] == "PM":
                handover_from = mgr
        for mgr in managers:
            if get_shift(mgr, date)[0] == "AM":
                handover_to = mgr
    elif alan_shift == "AM":
        for mgr in managers:
            if get_shift(mgr, date)[0] == "Night":
                handover_from = mgr
    elif alan_shift == "PM":
        for mgr in managers:
            if get_shift(mgr, date)[0] == "AM":
                handover_from = mgr
    elif alan_shift == "Day":
        for mgr in managers:
            if get_shift(mgr, date)[0] == "Night":
                handover_from = mgr

    return html.Div([
        html.H2(f"Shift Details for {date.strftime('%A %d %B %Y')}"),
        html.Table([
            html.Thead(html.Tr([html.Th("Manager"), html.Th("Shift"), html.Th("Time"), html.Th("Lunch Break")])),
            html.Tbody(rows)
        ]),
        html.Br(),
        html.Div([
            html.P(f"Handover from: {handover_from}" if handover_from else "No handover from previous shift"),
            html.P(f"Handover to: {handover_to}" if handover_to else "No handover to next shift")
        ])
    ])

if __name__ == '__main__':
    app.run_server(debug=True)

