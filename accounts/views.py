from email.mime import image
from urllib.request import Request
from django.shortcuts import render,redirect
from django.views import View
from .models import UserProfile,ThreadModel,MessageModel
from .forms import *
from django.views.generic.edit import UpdateView,DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin
from django.http import HttpResponseRedirect,HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from blog.models import *
from forum.models import *
# Create your views here.

def show(request):
    return render(request,'index.html')




class ProfileView(LoginRequiredMixin,View):
    def get(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        user=profile.user
       
        posts = Post.objects.filter(author=user)
        quests=Question.objects.filter(user=user).order_by('-id')
        answers=Answer.objects.filter(user=user).order_by('-id')

        followers=profile.followers.all()

        is_following=False
        for follower in followers:
            if follower==request.user:
                is_following=True
                break

        number_of_followers=len(followers)



        context={
            'user':user,
            'profile':profile,
            'posts':posts,
            'number_of_followers':number_of_followers,
            'is_following':is_following,
            'quests':quests,
            'answers':answers,
        }

        return render(request,'accounts/profile.html',context)

        

class ProfileEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=UserProfile
    fields=['bio','birth_date','location','picture']
    template_name='accounts/profile_edit.html'

    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('profile',kwargs={'pk':pk})

    def test_func(self):
        profile=self.get_object()
        return self.request.user == profile.user 




class AddFollwer(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)


        return redirect('profile',pk=profile.pk)



class RemoveFollwer(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect('profile',pk=profile.pk)
 
class UserSearch(View):
    def get(self,request,*args,**kwargs):
        query=self.request.GET.get('query')
        profile_list=UserProfile.objects.filter(
            Q(user__username__icontains=query)
        )
        context={
            'profile_list':profile_list,
        }
        return render(request,'accounts/search.html',context)


        


class ListFollowers(View):
    def get(self,request,pk,*args,**kwargs):
        profile=UserProfile.objects.get(pk=pk)
        followers=profile.followers.all()

        context={
            'profile':profile,
            'followers':followers,
        }

        return render(request,'accounts/followers_list.html',context)



class ListThreads(View):
    def get(self, request, *args, **kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))

        context = {
            'threads': threads
        }

        return render(request, 'accounts/inbox.html', context)


class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()

        context = {
            'form': form
        }

        return render(request, 'accounts/create_thread.html', context)

    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)

        username = request.POST.get('username')

        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists():
                thread = ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)
            elif ThreadModel.objects.filter(user=receiver, receiver=request.user).exists():
                thread = ThreadModel.objects.filter(user=receiver, receiver=request.user)[0]
                return redirect('thread', pk=thread.pk)

            if form.is_valid():
                thread = ThreadModel(
                    user=request.user,
                    receiver=receiver
                )
                thread.save()

                return redirect('thread', pk=thread.pk)
        except:
            messages.error(request,'User not exist')
            return redirect('create-thread')



class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        context = {
            'thread': thread,
            'form': form,
            'message_list': message_list
        }

        return render(request, 'accounts/thread.html', context)



class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        form=MessageForm(request.POST,request.FILES)
        thread = ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver

        if form.is_valid():
            message=form.save(commit=False)
            message.thread=thread
            message.sender_user=request.user
            message.receiver_user=receiver
            message.save()
 

        return redirect('thread', pk=pk)




