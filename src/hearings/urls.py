from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import apis, views

app_name = "hearings"

router = DefaultRouter()
router.register(r'', apis.CourtHearingViewSet, basename='hearing-api')

urlpatterns = [
    # HTML resource routes
    path('',                      views.HearingListView.as_view(),   name='hearing-list'),
    path('new/',                  views.HearingCreateView.as_view(), name='hearing-create'),
    path('<int:pk>/edit/',        views.HearingUpdateView.as_view(), name='hearing-update'),
    path('<int:pk>/delete/',      views.HearingDeleteView.as_view(), name='hearing-delete'),

    # DRF API routes
    path('api/', include(router.urls)),
]