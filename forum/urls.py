from django.urls import path
from . import views

app_name = 'forum'
urlpatterns=[
    path('',views.home,name='home'),
    path('tags',views.tags,name='tags'),
    path('tag/<str:tag>/',views.tag,name='tag'),
    path('ask-question',views.ask_form,name='ask-question'),
    path('unanswered',views.give_answer,name='unanswered'),
    path('save-comment',views.save_comment,name='save-comment'),
    path('<slug:slug>',views.detail,name='detail'),
    path('<slug:slug>/edit/', views.post_edit, name='ques_edit'),
    path('<slug:slug>/del/',views.deletePost, name='ques_del'),
    path('<int:id>/<int:pk>/save-upvote',views.save_upvote,name='save-upvote'),
    path('<int:id>/<int:pk>/save-downvote',views.save_downvote,name='save-downvote'),
    
    
    
]
