import json
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


merged_df = 0
dataCsv = 0
diseasesCsv = 0
year = 2019
diseasesRaw = pd.read_csv(
    "/Users/aliyildiz/Documents/development/django/Django-AQI-Diseases-Map/django_project/static/diseases.csv",
    header=6,
    on_bad_lines="skip",
    sep=";",
)


def home(request):
    global merged_df
    global dataCsv
    global diseasesCsv
    global year

    year = int(request.GET.get("year", 2019))

    dataRaw = pd.read_csv(
        "/Users/aliyildiz/Documents/development/django/Django-AQI-Diseases-Map/django_project/static/data.csv",
        header=0,
        sep=",",
    )

    dataCsv = dataRaw.drop(
        columns=[
            "IndicatorCode",
            "Indicator",
            "ValueType",
            "ParentLocationCode",
            "Location type",
            "Period type",
            "IsLatestYear",
            "Dim1 type",
            "Dim1ValueCode",
            "Dim2 type",
            "Dim2",
            "Dim2ValueCode",
            "Dim3 type",
            "Dim3",
            "Dim3ValueCode",
            "DataSourceDimValueCode",
            "DataSource",
            "FactValueNumericPrefix",
            "FactValueUoM",
            "FactValueNumericLowPrefix",
            "FactValueNumericLow",
            "FactValueNumericHighPrefix",
            "FactValueNumericHigh",
            "Value",
            "FactValueTranslationID",
            "FactComments",
            "Language",
            "DateModified",
        ]
    )

    countryRegionMapping = dict(
        zip(diseasesRaw["Country Name"], diseasesRaw["Region Name"])
    )
    dataCsvCountries = set(dataCsv["Location"])
    diseasesCountries = set(countryRegionMapping.keys())
    commonCountries = dataCsvCountries.intersection(diseasesCountries)
    dataCsv.loc[dataCsv["Location"].isin(commonCountries), "ParentLocation"] = (
        dataCsv.loc[dataCsv["Location"].isin(commonCountries), "Location"].map(
            countryRegionMapping
        )
    )

    dataCsv.loc[
        dataCsv["Location"] == "The former Yugoslav Republic of Macedonia", "Location"
    ] = "Macedonia"
    dataCsv.loc[dataCsv["Location"] == "Republic of Moldova", "Location"] = "Moldova"
    dataCsv.loc[dataCsv["Location"] == "Sao Tome and Principe", "Location"] = "Sao Tome"
    dataCsv.loc[
        dataCsv["Location"] == "Lao People's Democratic Republic", "Location"
    ] = "Laos"
    dataCsv.loc[
        dataCsv["Location"] == "Micronesia (Federated States of)", "Location"
    ] = "Micronesia"
    dataCsv.loc[dataCsv["Location"] == "Republic of Korea", "Location"] = "South Korea"
    dataCsv.loc[
        dataCsv["Location"] == "Democratic People's Republic of Korea", "Location"
    ] = "North Korea"
    dataCsv.loc[
        dataCsv["Location"] == "Venezuela (Bolivarian Republic of)", "Location"
    ] = "Venezuela"
    dataCsv.loc[
        dataCsv["Location"] == "Bolivia (Plurinational State of)", "Location"
    ] = "Bolivia"
    dataCsv.loc[dataCsv["Location"] == "Syrian Arab Republic", "Location"] = "Syria"
    dataCsv.loc[dataCsv["Location"] == "Iran (Islamic Republic of)", "Location"] = (
        "Iran"
    )
    dataCsv.loc[dataCsv["Location"] == "Russian Federation", "Location"] = "Russia"
    dataCsv.loc[dataCsv["Location"] == "Central African Republic", "Location"] = (
        "Central African"
    )
    dataCsv.loc[
        dataCsv["Location"] == "United Kingdom of Great Britain and Northern Ireland",
        "Location",
    ] = "United Kingdom"

    diseasesCsv = diseasesRaw.drop(
        columns=[
            "Region Code",
            "Age group code",
            "Age-standardized death rate per 100 000 standard population",
        ]
    )

    diseasesCsv = diseasesCsv.dropna(subset=["Number"])
    diseasesCsv["Number"] = diseasesCsv["Number"].astype(int)
    diseasesCsv["Population"] = diseasesCsv["Number"]
    diseasesCsv["Population"] = diseasesCsv["Population"] * 100000
    diseasesCsv["Population"] = (
        diseasesCsv["Population"] / diseasesCsv["Death rate per 100 000 population"]
    )
    diseasesCsv = diseasesCsv.dropna(subset=["Population"])
    diseasesCsv["Population"] = diseasesCsv["Population"].astype(int)

    dataCsvYear = dataCsv[(dataRaw["Period"] == year) & (dataRaw["Dim1"] == "Total")]
    groupedAqi = dataCsvYear.groupby("SpatialDimValueCode")["FactValueNumeric"].first()
    country_data = groupedAqi.to_dict()

    def calc_aqi_pm25(concentration):
        c_low = [0, 12.1, 35.5, 55.5, 150.5, 250.5, 350.5, 500.5]
        c_high = [12, 35.4, 55.4, 150.4, 250.4, 350.4, 500.4, 999.9]
        i_low = [0, 51, 101, 151, 201, 301, 401, 501]
        i_high = [50, 100, 150, 200, 300, 400, 500, 999]

        c = float(concentration)

        for i, item in enumerate(c_low):
            if item <= c <= c_high[i]:
                aqi = ((i_high[i] - i_low[i]) / (c_high[i] - item)) * (
                    c - item
                ) + i_low[i]
                return round(aqi, 1)

        if c > c_high[-1]:
            aqi = ((i_high[-1] - i_low[-1]) / (c_high[-1] - c_low[-1])) * (
                c - c_low[-1]
            ) + i_low[-1]
            return round(aqi, 1)
        else:
            return "Input concentration is below AQI scale"

    def calc_pm25(country_data):
        updated_country_data = {}
        for country, concentration in country_data.items():
            try:
                tam_kisim, ondalik_kisim = str(concentration).split(".")
                ondalik_kisim = int(ondalik_kisim)
                yuvarlanmis_ondalik = (ondalik_kisim + 5) // 10 * 10
                float(tam_kisim + "." + str(yuvarlanmis_ondalik).zfill(2))
                pm25_concentration = float(
                    tam_kisim + "." + str(yuvarlanmis_ondalik).zfill(2)
                )
                aqi = calc_aqi_pm25(pm25_concentration)
                updated_country_data[country] = aqi
            except ValueError:
                print("Invalid concentration value for {}. Skipping...".format(country))
        return updated_country_data

    country_data = calc_pm25(country_data)

    dataCsv["AQI"] = calc_pm25(dataCsv["FactValueNumeric"])
    dataCsv["AQI"] = dataCsv["AQI"].apply(lambda x: int(round(x)))

    return render(
        request,
        "/Users/aliyildiz/Documents/development/django/Django-AQI-Diseases-Map/django_project/templates/index.html",
        {"country_data": country_data},
    )


def treeMap():
    global dataCsv
    global year

    treemapData = dataCsv.copy()
    treemapData = treemapData[
        (treemapData["Dim1"] == "Total") & (treemapData["Period"] == year)
    ]

    fig = px.treemap(
        treemapData,
        path=[px.Constant("World"), "ParentLocation", "Location"],
        values="AQI",
        color="AQI",
        color_continuous_scale="RdYlGn_r",
    )
    fig.data[0].textinfo = "label+text+value"

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        width=1250,
        height=800,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font=dict(color="white", family="Arial"),
        coloraxis_colorbar=dict(
            title_font=dict(color="white"), tickfont=dict(color="white")
        ),
    )

    graph = fig.to_html(full_html=False)
    return graph


@csrf_exempt
def get_sunburts_chart(request):
    if request.method == "POST":
        try:
            global diseasesCsv
            global year

            sunDiseasesCsv = diseasesCsv.copy()
            lastSunDiseasesCsv = diseasesCsv.copy()

            data = json.loads(request.body)
            selected_country = data.get("country", "TUR")

            selected_country_regions = sunDiseasesCsv[
                sunDiseasesCsv["Country Code"] == selected_country
            ]["Region Name"].unique()

            lastSunDiseasesCsv = lastSunDiseasesCsv[
                lastSunDiseasesCsv["Region Name"].isin(selected_country_regions)
            ]

            selected_country_data = sunDiseasesCsv[
                sunDiseasesCsv["Country Code"] == selected_country
            ]

            lastSunDiseasesCsv = lastSunDiseasesCsv[
                lastSunDiseasesCsv["Sex"].isin(["Male", "Female"])
            ]
            lastSunDiseasesCsv = lastSunDiseasesCsv[
                lastSunDiseasesCsv["Age Group"].isin(["[All]"])
            ]

            average_percentage = (
                lastSunDiseasesCsv.groupby(["Year", "Sex"])[
                    "Percentage of cause-specific deaths out of total deaths"
                ]
                .mean()
                .reset_index()
            )

            selected_country_data = selected_country_data[
                [
                    "Region Name",
                    "Country Name",
                    "Year",
                    "Sex",
                    "Age Group",
                    "Number",
                    "Percentage of cause-specific deaths out of total deaths",
                ]
            ]

            selected_country_data = selected_country_data[
                selected_country_data["Sex"].isin(["Male", "Female"])
            ]

            selected_country_data = selected_country_data[
                selected_country_data["Age Group"] == "[All]"
            ]

            years = selected_country_data["Year"].unique()
            years.sort()

            top_10_years = years[-10:]

            selected_country_data = selected_country_data[
                selected_country_data["Year"].isin(top_10_years)
            ]

            selected_country_data["Number"] = selected_country_data["Number"].astype(
                int
            )

            selected_country_data = selected_country_data[
                selected_country_data["Number"] != 0
            ]

            selected_country_data = (
                selected_country_data.groupby(["Year", "Sex"]).sum().reset_index()
            )

            selected_country_data["Country Name"] = selected_country

            selected_country_data = selected_country_data.dropna(
                subset=["Percentage of cause-specific deaths out of total deaths"]
            )
            selected_country_data[
                "Percentage of cause-specific deaths out of total deaths"
            ] = selected_country_data[
                "Percentage of cause-specific deaths out of total deaths"
            ].apply(
                lambda x: round(x, 2)
            )

            merged_data = selected_country_data.merge(
                average_percentage,
                on=["Year", "Sex"],
                how="left",
                suffixes=("", "_average"),
            )

            merged_data[
                "Percentage of cause-specific deaths out of total deaths_average"
            ] = merged_data[
                "Percentage of cause-specific deaths out of total deaths_average"
            ].apply(
                lambda x: round(x, 2)
            )

            merged_data["color"] = merged_data.apply(
                lambda row: (
                    "red"
                    if row["Percentage of cause-specific deaths out of total deaths"]
                    > row[
                        "Percentage of cause-specific deaths out of total deaths_average"
                    ]
                    else "blue"
                ),
                axis=1,
            )

            merged_data["Sex"] = merged_data["Sex"].replace(
                {"Male": "M", "Female": "F"}
            )

            df = pd.DataFrame(merged_data)
            df

            fig = px.sunburst(
                df,
                path=[
                    "Country Name",
                    "Year",
                    "Sex",
                    "Percentage of cause-specific deaths out of total deaths",
                    "Percentage of cause-specific deaths out of total deaths_average",
                ],
                values="Percentage of cause-specific deaths out of total deaths",
                color="Percentage of cause-specific deaths out of total deaths",
                color_continuous_scale="Spectral_r",
                hover_data={
                    "Percentage of cause-specific deaths out of total deaths": True,
                    "Percentage of cause-specific deaths out of total deaths_average": True,
                    "Year": True,
                    "Sex": True,
                },
            )
            fig.update_coloraxes(
                colorbar_title="Percentage",
                colorbar_title_font_color="white",
                colorbar_tickfont=dict(color="white"),
            )
            fig.update_layout(
                width=1250,
                height=800,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=20, b=0),  # Optional: Adjust margins as needed
            )

            graph = fig.to_html(full_html=False)
            return JsonResponse({"graph_data": graph})
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def get_bar_chart(request):
    if request.method == "POST":
        try:

            global dataCsv
            global year

            data = json.loads(request.body)
            selected_country = data.get("country", "TUR")

            original_pieDataCsv = dataCsv.copy()

            filtered_pieDataCsv = original_pieDataCsv[
                (original_pieDataCsv["SpatialDimValueCode"] == selected_country)
                & (original_pieDataCsv["Period"] == year)
            ]

            filtered_pieDataCsv["Dim1"] = filtered_pieDataCsv["Dim1"].str.capitalize()

            fig = make_subplots(
                specs=[[{"secondary_y": False}, {"secondary_y": True}]],
                horizontal_spacing=0,
                shared_yaxes=True,
                rows=1,
                cols=2,
            )

            x1 = filtered_pieDataCsv["AQI"]
            text1 = [f"{t}" for t in x1]
            y = filtered_pieDataCsv["Dim1"]
            fig.add_trace(
                go.Bar(
                    orientation="h",
                    x=x1,
                    y=y,
                    name="tr-name 1",
                    text=text1,
                    textposition="inside",
                    marker_color="rgb(186, 44, 58)",
                ),
                1,
                1,
            )

            fig.update_layout(
                height=400,
                yaxis=dict(
                    tickfont=dict(color="white", size=12, family="Arial", weight="bold")
                ),
                yaxis3_showticklabels=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, visible=False),
                bargap=0.2,
            )

            graph = fig.to_html(full_html=False)
            return JsonResponse({"graph_data": graph})
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def get_pie_chart(request):
    if request.method == "POST":
        try:
            global diseasesCsv
            global year

            pieDiseasesCsv = diseasesCsv.copy()

            data = json.loads(request.body)
            selected_country = data.get("country", "TUR")

            pieDiseasesCsv = pieDiseasesCsv[
                (pieDiseasesCsv["Year"] == year)
                & (pieDiseasesCsv["Age Group"] == "[All]")
                & (pieDiseasesCsv["Sex"] == "All")
            ]

            if selected_country in diseasesRaw["Country Code"].values:
                region_name = diseasesRaw[
                    diseasesRaw["Country Code"] == selected_country
                ]["Region Name"].values[0]
                pieDiseasesCsv = pieDiseasesCsv[
                    pieDiseasesCsv["Region Name"] == region_name
                ]

                pieDiseasesCsv["Death rate per all population"] = (
                    pieDiseasesCsv["Number"] / pieDiseasesCsv["Population"]
                )

            else:
                pieDiseasesCsv = pd.DataFrame()

            df = pd.DataFrame(pieDiseasesCsv)
            df.loc[df["Death rate per all population"] < 0.0003, "Country Name"] = (
                "Others"
            )
            fig = px.pie(
                df,
                values="Death rate per all population",
                names="Country Name",
                hover_data=["Population"],
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.RdBu,
                labels={"Number": "Number"},
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")

            fig.update_layout(
                height=500,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=350, r=0, t=50, b=0),
            )

            graph = fig.to_html(full_html=False)
            return JsonResponse({"graph_data": graph})
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def get_line_chart(request):
    if request.method == "POST":
        try:
            global diseasesCsv
            global dataCsv
            average_death_ratesC = []
            average_death_rates = []
            average_death_ratesW = []
            lineDiseasesCsv = diseasesCsv.copy()

            data = json.loads(request.body)
            selected_country = data.get("country", "TUR")

            if selected_country in diseasesRaw["Country Code"].values:
                selected_country_name = lineDiseasesCsv.loc[
                    lineDiseasesCsv["Country Code"] == selected_country, "Country Name"
                ].iloc[0]
            else:
                selected_country_name = ""

            lineDiseasesCsv = lineDiseasesCsv[
                (lineDiseasesCsv["Sex"] == "All")
                & (lineDiseasesCsv["Age Group"] == "[All]")
            ]

            countryLineDiseasesCsv = lineDiseasesCsv.copy()

            countryLineDiseasesCsv = lineDiseasesCsv[
                lineDiseasesCsv["Country Code"] == selected_country
            ]

            yearsC = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
            average_death_ratesC = []
            for year in yearsC:
                average_death_rate = countryLineDiseasesCsv[
                    countryLineDiseasesCsv["Year"] == year
                ]["Death rate per 100 000 population"].mean()
                average_death_ratesC.append(average_death_rate)

            regionLineDiseasesCsv = lineDiseasesCsv.copy()

            if selected_country in lineDiseasesCsv["Country Code"].values:
                selected_region_name = regionLineDiseasesCsv.loc[
                    regionLineDiseasesCsv["Country Code"] == selected_country,
                    "Region Name",
                ].iloc[0]
                regionLineDiseasesCsv = regionLineDiseasesCsv[
                    regionLineDiseasesCsv["Region Name"] == selected_region_name
                ]
            else:
                selected_region_name = ""

            years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
            average_death_rates = []
            for year in years:
                average_death_rate = regionLineDiseasesCsv[
                    regionLineDiseasesCsv["Year"] == year
                ]["Death rate per 100 000 population"].mean()
                average_death_rates.append(average_death_rate)

            worldLineDiseasesCsv = lineDiseasesCsv.copy()

            yearsW = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
            average_death_ratesW = []
            for year in yearsW:
                average_death_rate = worldLineDiseasesCsv[
                    worldLineDiseasesCsv["Year"] == year
                ]["Death rate per 100 000 population"].mean()
                average_death_ratesW.append(average_death_rate)

            dataCsv = dataCsv[dataCsv["Dim1"] == "Total"]

            cDataCsv = dataCsv.copy()
            rDataCsv = dataCsv.copy()
            wDataCsv = dataCsv.copy()

            selected_country_data = cDataCsv[
                cDataCsv["SpatialDimValueCode"] == selected_country
            ]

            selected_country_aqi = selected_country_data["AQI"].tolist()

            selected_country_parent_location = rDataCsv.loc[
                rDataCsv["SpatialDimValueCode"] == selected_country, "ParentLocation"
            ].iloc[0]

            selected_country_parent_location_data = rDataCsv[
                rDataCsv["ParentLocation"] == selected_country_parent_location
            ]

            selected_country_parent_location_aqi = (
                selected_country_parent_location_data.groupby("Period")["AQI"].mean()
            )
            selected_country_parent_location_aqi = (
                selected_country_parent_location_aqi.round(2)
            )

            aqiMeanValue = selected_country_parent_location_aqi.tolist()

            selected_country_parent_location_aqiW = wDataCsv.groupby("Period")[
                "AQI"
            ].mean()
            selected_country_parent_location_aqiW = (
                selected_country_parent_location_aqiW.round(2)
            )

            aqiMeanValueW = selected_country_parent_location_aqiW.tolist()

            colors = [
                "rgb(203, 16, 52)",
                "rgb(255, 255, 255)",
                "rgb(115,115,115)",
                "rgb(203, 16, 52)",
                "rgb(255, 255, 255)",
                "rgb(115,115,115)",
            ]

            labels = [
                str(selected_country_name) + " AQI",
                str(selected_region_name) + " AQI",
                "World AQI",
            ]
            mode_size = [15, 10, 10]
            line_size = [8, 3, 3]

            x_data = np.vstack((np.arange(2010, 2020),) * 3)

            y_data = np.array(
                [
                    selected_country_aqi,
                    aqiMeanValue,
                    aqiMeanValueW,
                ]
            )

            fig = go.Figure()

            for i in range(0, 3):
                fig.add_trace(
                    go.Scatter(
                        x=x_data[i],
                        y=y_data[i],
                        mode="lines",
                        name=labels[i],
                        line=dict(color=colors[i], width=line_size[i]),
                        connectgaps=True,
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=[x_data[i][0], x_data[i][-1]],
                        y=[y_data[i][0], y_data[i][-1]],
                        mode="markers",
                        marker=dict(color=colors[i], size=mode_size[i]),
                    )
                )

            fig.update_layout(
                xaxis=dict(
                    showline=True,
                    showgrid=False,
                    showticklabels=True,
                    linecolor="rgb(204, 204, 204)",
                    linewidth=2,
                    ticks="outside",
                    tickfont=dict(
                        family="Arial",
                        size=12,
                        color="rgb(82, 82, 82)",
                    ),
                ),
                yaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showline=False,
                    showticklabels=False,
                ),
                autosize=False,
                margin=dict(
                    autoexpand=False,
                    l=100,
                    r=20,
                    t=110,
                ),
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                width=1200,
                height=450,
            )

            annotations = []

            for i, (y_trace, label, color) in enumerate(zip(y_data, labels, colors)):
                if i == 0 or i == 3:
                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.3,
                            y=y_trace[0],
                            yref="y",
                            yanchor="middle",
                            text=label.format(y_trace[0]),
                            font=dict(family="Arial", size=20, color=colors[i]),
                            showarrow=False,
                        )
                    )
                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.1,
                            y=y_trace[0],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_trace[0]),
                            font=dict(family="Arial", size=20, color=colors[i]),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=1.07,
                            y=y_trace[-1],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_trace[-1]),
                            font=dict(family="Arial", size=20, color=colors[i]),
                            showarrow=False,
                        )
                    )
                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.3,
                            y=y_trace[0],
                            yref="y",
                            yanchor="middle",
                            text=label.format(y_trace[0]),
                            font=dict(family="Arial", size=20, color=colors[i]),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=1.07,
                            y=y_trace[-1],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_trace[-1]),
                            font=dict(family="Arial", size=20, color=colors[i]),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=1.07,
                            y=y_data[1][-1],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_data[1][-1]),
                            font=dict(
                                family="Arial", size=20, color="rgb(255, 255, 255)"
                            ),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.3,
                            y=y_data[1][0],
                            yref="y",
                            yanchor="middle",
                            text=selected_region_name.format(y_data[1][0]),
                            font=dict(
                                family="Arial", size=20, color="rgb(255, 255, 255)"
                            ),
                            showarrow=False,
                        )
                    )
                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.1,
                            y=y_data[1][0],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_data[1][0]),
                            font=dict(
                                family="Arial", size=20, color="rgb(255, 255, 255)"
                            ),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.3,
                            y=y_data[2][0],
                            yref="y",
                            yanchor="middle",
                            text="World".format(y_data[2][0]),
                            font=dict(
                                family="Arial", size=20, color="rgb(115, 115, 115)"
                            ),
                            showarrow=False,
                        )
                    )
                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.1,
                            y=y_data[2][0],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_data[2][0]),
                            font=dict(
                                family="Arial", size=20, color="rgb(115, 115, 115)"
                            ),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=1.07,
                            y=y_data[2][-1],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_data[2][-1]),
                            font=dict(
                                family="Arial", size=20, color="rgb(115,115,115)"
                            ),
                            showarrow=False,
                        )
                    )

            fig.update_layout(
                title="For AQI Average Values",
                title_font=dict(family="Arial", size=20, color="rgb(255, 255, 255)"),
                title_x=0,
                title_y=0.9,
                yaxis=dict(
                    zeroline=True,
                    showline=True,
                    showticklabels=True,
                    tickfont=dict(
                        family="Arial",
                        size=12,
                        color="rgb(255, 255, 255)",
                    ),
                ),
                xaxis=dict(
                    tickfont=dict(
                        family="Arial",
                        size=12,
                        color="rgb(255, 255, 255)",
                    ),
                ),
                annotations=annotations,
                autosize=True,
                margin=dict(
                    l=300,
                    r=70,
                ),
            )

            graph = fig.to_html(full_html=False)
            return JsonResponse({"graph_data": graph})
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def get_line2_chart(request):
    if request.method == "POST":
        try:
            global diseasesCsv
            global dataCsv
            average_death_ratesC = []
            average_death_rates = []
            average_death_ratesW = []
            lineDiseasesCsv = diseasesCsv.copy()

            data = json.loads(request.body)
            selected_country = data.get("country", "TUR")

            if selected_country in diseasesRaw["Country Code"].values:
                selected_country_name = lineDiseasesCsv.loc[
                    lineDiseasesCsv["Country Code"] == selected_country, "Country Name"
                ].iloc[0]
            else:
                selected_country_name = ""

            lineDiseasesCsv = lineDiseasesCsv[
                (lineDiseasesCsv["Sex"] == "All")
                & (lineDiseasesCsv["Age Group"] == "[All]")
            ]

            countryLineDiseasesCsv = lineDiseasesCsv.copy()

            countryLineDiseasesCsv = lineDiseasesCsv[
                lineDiseasesCsv["Country Code"] == selected_country
            ]

            yearsC = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
            average_death_ratesC = []
            for year in yearsC:
                average_death_rate = countryLineDiseasesCsv[
                    countryLineDiseasesCsv["Year"] == year
                ]["Death rate per 100 000 population"].mean()
                average_death_ratesC.append(average_death_rate)

            regionLineDiseasesCsv = lineDiseasesCsv.copy()

            if selected_country in lineDiseasesCsv["Country Code"].values:
                selected_region_name = regionLineDiseasesCsv.loc[
                    regionLineDiseasesCsv["Country Code"] == selected_country,
                    "Region Name",
                ].iloc[0]
                regionLineDiseasesCsv = regionLineDiseasesCsv[
                    regionLineDiseasesCsv["Region Name"] == selected_region_name
                ]
            else:
                selected_region_name = ""

            years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
            average_death_rates = []
            for year in years:
                average_death_rate = regionLineDiseasesCsv[
                    regionLineDiseasesCsv["Year"] == year
                ]["Death rate per 100 000 population"].mean()
                average_death_rates.append(average_death_rate)

            worldLineDiseasesCsv = lineDiseasesCsv.copy()

            yearsW = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
            average_death_ratesW = []
            for year in yearsW:
                average_death_rate = worldLineDiseasesCsv[
                    worldLineDiseasesCsv["Year"] == year
                ]["Death rate per 100 000 population"].mean()
                average_death_ratesW.append(average_death_rate)

            dataCsv = dataCsv[dataCsv["Dim1"] == "Total"]

            cDataCsv = dataCsv.copy()
            rDataCsv = dataCsv.copy()
            wDataCsv = dataCsv.copy()

            selected_country_data = cDataCsv[
                cDataCsv["SpatialDimValueCode"] == selected_country
            ]

            selected_country_aqi = selected_country_data["AQI"].tolist()

            selected_country_parent_location = rDataCsv.loc[
                rDataCsv["SpatialDimValueCode"] == selected_country, "ParentLocation"
            ].iloc[0]

            selected_country_parent_location_data = rDataCsv[
                rDataCsv["ParentLocation"] == selected_country_parent_location
            ]

            selected_country_parent_location_aqi = (
                selected_country_parent_location_data.groupby("Period")["AQI"].mean()
            )
            selected_country_parent_location_aqi = (
                selected_country_parent_location_aqi.round(2)
            )

            aqiMeanValue = selected_country_parent_location_aqi.tolist()

            selected_country_parent_location_aqiW = wDataCsv.groupby("Period")[
                "AQI"
            ].mean()
            selected_country_parent_location_aqiW = (
                selected_country_parent_location_aqiW.round(2)
            )

            aqiMeanValueW = selected_country_parent_location_aqiW.tolist()

            colors = [
                "rgb(203, 16, 52)",
                "rgb(255, 255, 255)",
                "rgb(115,115,115)",
                "rgb(203, 16, 52)",
                "rgb(255, 255, 255)",
                "rgb(115,115,115)",
            ]

            labels = [
                selected_country_name,
                selected_region_name,
                "World",
            ]
            mode_size = [15, 10, 10]
            line_size = [8, 3, 3]

            x_data = np.vstack((np.arange(2010, 2020),) * 3)

            y_data = np.array(
                [
                    average_death_ratesC,
                    average_death_rates,
                    average_death_ratesW,
                ]
            )

            fig = go.Figure()

            for i in range(0, 3):
                fig.add_trace(
                    go.Scatter(
                        x=x_data[i],
                        y=y_data[i],
                        mode="lines",
                        name=labels[i],
                        line=dict(color=colors[i], width=line_size[i]),
                        connectgaps=True,
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=[x_data[i][0], x_data[i][-1]],
                        y=[y_data[i][0], y_data[i][-1]],
                        mode="markers",
                        marker=dict(color=colors[i], size=mode_size[i]),
                    )
                )

            fig.update_layout(
                xaxis=dict(
                    showline=True,
                    showgrid=False,
                    showticklabels=True,
                    linecolor="rgb(204, 204, 204)",
                    linewidth=2,
                    ticks="outside",
                    tickfont=dict(
                        family="Arial",
                        size=12,
                        color="rgb(82, 82, 82)",
                    ),
                ),
                yaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showline=False,
                    showticklabels=False,
                ),
                autosize=False,
                margin=dict(
                    autoexpand=False,
                    l=100,
                    r=20,
                    t=110,
                ),
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                width=1200,
                height=450,
            )

            annotations = []

            for i, (y_trace, label, color) in enumerate(zip(y_data, labels, colors)):
                if i == 0 or i == 3:

                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.3,
                            y=y_trace[0],
                            yref="y",
                            yanchor="middle",
                            text=label.format(y_trace[0]),
                            font=dict(family="Arial", size=20, color=colors[i]),
                            showarrow=False,
                        )
                    )
                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.1,
                            y=y_trace[0],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_trace[0]),
                            font=dict(family="Arial", size=20, color=colors[i]),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=1.07,
                            y=y_trace[-1],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_trace[-1]),
                            font=dict(family="Arial", size=20, color=colors[i]),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=1.07,
                            y=y_data[1][-1],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_data[1][-1]),
                            font=dict(
                                family="Arial", size=20, color="rgb(255, 255, 255)"
                            ),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.3,
                            y=y_data[1][0],
                            yref="y",
                            yanchor="middle",
                            text=selected_region_name.format(y_data[1][0]),
                            font=dict(
                                family="Arial", size=20, color="rgb(255, 255, 255)"
                            ),
                            showarrow=False,
                        )
                    )
                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.1,
                            y=y_data[1][0],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_data[1][0]),
                            font=dict(
                                family="Arial", size=20, color="rgb(255, 255, 255)"
                            ),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.3,
                            y=y_data[2][0],
                            yref="y",
                            yanchor="middle",
                            text="World ".format(y_data[2][0]),
                            font=dict(
                                family="Arial", size=20, color="rgb(115, 115, 115)"
                            ),
                            showarrow=False,
                        )
                    )
                    annotations.append(
                        dict(
                            xref="paper",
                            x=-0.1,
                            y=y_data[2][0],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_data[2][0]),
                            font=dict(
                                family="Arial", size=20, color="rgb(115, 115, 115)"
                            ),
                            showarrow=False,
                        )
                    )

                    annotations.append(
                        dict(
                            xref="paper",
                            x=1.07,
                            y=y_data[2][-1],
                            yref="y",
                            yanchor="middle",
                            text="{:.2f}".format(y_data[2][-1]),
                            font=dict(
                                family="Arial", size=20, color="rgb(115,115,115)"
                            ),
                            showarrow=False,
                        )
                    )

            fig.update_layout(
                title="For Death Rate per 100,000 Population",
                title_font=dict(family="Arial", size=20, color="rgb(255, 255, 255)"),
                title_x=0,
                title_y=0.9,
                yaxis=dict(
                    zeroline=True,
                    showline=True,
                    showticklabels=True,
                    tickfont=dict(
                        family="Arial",
                        size=12,
                        color="rgb(255, 255, 255)",
                    ),
                ),
                xaxis=dict(
                    tickfont=dict(
                        family="Arial",
                        size=12,
                        color="rgb(255, 255, 255)",
                    ),
                ),
                annotations=annotations,
                autosize=True,
                margin=dict(
                    l=300,
                    r=70,
                ),
            )

            graph = fig.to_html(full_html=False)
            return JsonResponse({"graph_data": graph})
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


def get_selected_country_years(request, selected_country):
    global diseasesRaw

    selected_country = request.GET.get("country", "TUR")
    years = diseasesRaw[diseasesRaw["Country Code"] == selected_country][
        "Year"
    ].unique()

    return JsonResponse({"years": years.tolist()})


@csrf_exempt
def get_graph_data(request):
    if request.method == "POST":
        try:
            treeMapGraph = treeMap()
            return JsonResponse({"graph_data": treeMapGraph})
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)
