from django.urls import path
from .views import (
    show,
    ProfileView,
    ProfileEditView,
    AddFollwer,
    RemoveFollwer,
    UserSearch,
    ListFollowers,
    ListThreads,
    CreateThread,
    ThreadView,
    CreateMessage,
)
urlpatterns =[
    path('',show,name='index'),
    path('profile/<int:pk>',ProfileView.as_view(),name='profile'),
    path('profile/edit/<int:pk>/',ProfileEditView.as_view(),name='profile-edit'),
    path('profile/<int:pk>/followers/',ListFollowers.as_view(),name='list-followers'),
    path('profile/<int:pk>/followers/add',AddFollwer.as_view(),name='add-follower'),
    path('profile/<int:pk>/followers/remove',RemoveFollwer.as_view(),name='remove-follower'),
    path('search/',UserSearch.as_view(),name='profile-search'),

    path('inbox/', ListThreads.as_view(), name='inbox'),
    path('inbox/create-thread/', CreateThread.as_view(), name='create-thread'),
    path('inbox/<int:pk>/', ThreadView.as_view(), name='thread'),
    path('inbox/<int:pk>/create-message/', CreateMessage.as_view(), name='create-message'),
    
]


