from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name = 'index'),
    path('Query_results', views.Query_results, name = 'Query_results' ),
    path('Records_Management', views.Records_Management, name='Records_Management'),
    path('Record_Return', views.Record_Return, name='Records_Management'),
    path('Rankings', views.Rankings, name='Rankings')
]
