from django.urls import path
from rest_framework import permissions
from .views import (OrderListCreateView, OrderDetailView, AdminOrderUpdateView,
                    OrderListView, AdminStatisticsView, UserStatisticsView,
                    TimeRangeStatisticsView)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Market System API",
        default_version="v1",
        description="Market System API hujjatlari",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your_email@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/all', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update-status',
         AdminOrderUpdateView.as_view(), name='admin-order-update'),
    path('admin/statistics/',
         AdminStatisticsView.as_view(), name='admin-statistics'),
    path('user/statistics/',
         UserStatisticsView.as_view(), name='user-statistics'),
    path('statistics/time-range',
         TimeRangeStatisticsView.as_view(), name='time-range-statistics')
]
