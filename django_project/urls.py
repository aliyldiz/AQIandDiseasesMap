from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home),
    path("get_graph_data/", views.get_graph_data, name="get_graph_data"),
    path("get_line_chart", views.get_line_chart, name="get_line_chart"),
    path("get_line2_chart", views.get_line2_chart, name="get_line2_chart"),
    path("get_pie_chart", views.get_pie_chart, name="get_pie_chart"),
    path("get_bar_chart", views.get_bar_chart, name="get_bar_chart"),
    path("get_sunburts_chart", views.get_sunburts_chart, name="get_sunburts_chart"),
    path(
        "get_selected_country_years/",
        views.get_selected_country_years,
        name="get_selected_country_years",
    ),
]
