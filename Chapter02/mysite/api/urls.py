from django.urls import path, include
import api.views as views

app_name = "api"

urlpatterns = [
    path('comments/', views.CommentList.as_view(), name='comments'),
    path('comments/<int:pk>/', views.CommentDetail.as_view(), name='comment'),
    path('posts/', views.PostList.as_view(), name='posts'),
    path('posts/<int:pk>/', views.PostDetail.as_view(), name='post'),
    path('files/', views.BackUP.as_view(), name='files'),
    path('files/download/<uuid:uuid>', views.Download.as_view(), name='download'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
