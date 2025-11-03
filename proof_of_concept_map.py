import sqlite3
import pandas as pd
import gradio as gr
import plotly.graph_objects as go   

connection = sqlite3.connect("data/covid_19.db")
daily_report = pd.read_sql("SELECT * FROM daily_report;",con=connection)
connection.close()

fig = go.Figure(
    go.Scattermapbox(
        lat = daily_report["latitude"],
        lon = daily_report["longitude"],
        mode = "markers", #dot form
        marker={
            "size": daily_report["confirmed"],
            "color": daily_report["confirmed"],
            "sizemin": 2, #min size of marker
            "sizeref": daily_report["confirmed"].max() / 2500, #標準化校正
            "sizemode": "area"
        }
    )
)

fig.update_layout(
    mapbox_style = "open-street-map",
    mapbox = dict(
        zoom = 2,#縮放比例
        center = go.layout.mapbox.Center(
            lat=0,lon=0),#中心點
    )
)

with gr.Blocks() as demo:
    gr.Markdown("""# Covid 19 Global Map""") #title
    gr.Plot(fig)

demo.launch()