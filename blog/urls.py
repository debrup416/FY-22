from unicodedata import name
from django.urls import path
from . import views


app_name = 'blog'
urlpatterns = [
    # post views  
    path('', views.post_list, name='post_list'),
    path('q/', views.search_post, name='search_post'),
    path('new/', views.post_create, name='post_create'),
    path('<slug:post>/edit/', views.post_edit, name='post_edit'),
    path('<slug:post>/',views.post_detail, name='post_detail'),
    path('<slug:post>/del/',views.deletePost, name='post_del'),
    path('<int:post_id>/share/',views.post_share, name='post_share'),
    path('tag/<slug:tag_slug>/',views.post_list, name='post_list_by_tag'),
    path('<slug:post>/like',views.like_view,name='like_post'),
    

]

