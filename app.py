import sqlite3
import pandas as pd
import gradio as gr
import plotly.graph_objects as go   

connection = sqlite3.connect("data/covid_19.db")
daily_report = pd.read_sql("SELECT * FROM daily_report;",con=connection)
time_series = pd.read_sql("SELECT * FROM time_series;",con=connection)
connection.close()

total_cases = daily_report["confirmed"].sum()
total_deaths = daily_report["deaths"].sum()
lastest_time_series = time_series[time_series["reported_on"] == "2023-03-09"]
total_vaccinated = lastest_time_series["doses_administered"].sum()
sum_confirmed_by_country = daily_report.groupby("country")["confirmed"].sum().sort_values(ascending=False)
top_confirmed = sum_confirmed_by_country.index[:30].to_list()
time_series["reported_on"] = pd.to_datetime(time_series["reported_on"],format="%Y-%m-%d")

def filter_global_map(country_names:list):
    filter_daily_report = daily_report[daily_report["country"].isin(country_names)]
    countries = filter_daily_report["country"].values
    provinces = filter_daily_report["province"].values
    counties = filter_daily_report["county"].values
    confirmed = filter_daily_report["confirmed"].values
    deaths = filter_daily_report["deaths"].values
    information_when_hovered = []

    for country,province,county,c,d in zip(countries,provinces,counties,confirmed,deaths):
        if county is not None:
            marker_information = [(country,province,county),c,d]
        elif province is not None:
            marker_information = [(country,province),c,d]
        else:
            marker_information = [country,c,d]
        information_when_hovered.append(marker_information)

    fig = go.Figure(
        go.Scattermap(
            lat = filter_daily_report["latitude"],
            lon = filter_daily_report["longitude"],
            mode = "markers", #點圖模式
            customdata = information_when_hovered,
            hoverinfo = "text",
            hovertemplate = "Location: %{customdata[0]}<br>Confirmed: %{customdata[1]}<br>Deaths: %{customdata[2]}",
            marker = {
                "size": filter_daily_report["confirmed"],
                "color": filter_daily_report["confirmed"],
                "sizemin": 2, #min size of marker
                "sizeref": filter_daily_report["confirmed"].max() / 2500, #標準化校正
                "sizemode": "area",
                "showscale":True  # 顯示顏色比例尺
            }
        )
    )

    fig.update_layout(
        map_style = "open-street-map",
        map_zoom=2, #縮放比例
        map_center={"lat": 0, "lon": 0} #中心點
    )
    return fig

with gr.Blocks() as global_map_tab:
    gr.Markdown("""# Covid 19 Global Map""") #title

    with gr.Row():
        gr.Label(f"{total_cases:,}",label="Total cases")
        gr.Label(f"{total_deaths:,}",label="Total deaths")
        gr.Label(f"{total_vaccinated:,}",label="Total doses administered")

    #篩選UI
    with gr.Column():
        countries = gr.Dropdown(choices=daily_report["country"].unique().tolist(),
                                label="Select countries:",
                                multiselect=True,
                                value=top_confirmed #default
                                )
        btn = gr.Button(value="Update")
        global_map = gr.Plot()

    global_map_tab.load(fn=filter_global_map,
              inputs=countries,
              outputs=global_map)    

    btn.click(fn=filter_global_map,
              inputs=countries,
              outputs=global_map)

with gr.Blocks() as country_time_serise_tab:
    gr.Markdown("""# Covid 19 Country Time Series""")

    with gr.Row():
        country = gr.Dropdown(
            choices=time_series["country"].unique().tolist(),
            label="Select a country:",
            multiselect=False,
            value="Taiwan*"
        )

    plt_confirmed = gr.LinePlot(time_series.head(),x="reported_on",y="confirmed")
    plt_deaths = gr.LinePlot(time_series.head(),x="reported_on",y="deaths")
    plt_doses = gr.LinePlot(time_series.head(),x="reported_on",y="doses_administered")

    @gr.on(inputs=country,outputs=plt_confirmed)
    @gr.on(inputs=country,outputs=plt_deaths)
    @gr.on(inputs=country,outputs=plt_doses)

    def filter_time_series(country):
        filtered_df = time_series[time_series["country"]==country]
        return filtered_df
    
    country_time_serise_tab.load(fn=filter_time_series,
              inputs=country,
              outputs=plt_confirmed)
    
    country_time_serise_tab.load(fn=filter_time_series,
              inputs=country,
              outputs=plt_deaths)
    
    country_time_serise_tab.load(fn=filter_time_series,
              inputs=country,
              outputs=plt_doses)


demo = gr.TabbedInterface([global_map_tab,country_time_serise_tab],["Global Map","Country Time Series"])
demo.launch()
