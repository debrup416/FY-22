from email import message
from importlib.resources import contents
from re import search
from turtle import pos, title
from django.contrib import messages
from multiprocessing import context
from urllib import request
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EmailPostForm, CommentForm, PostForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
import os
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q

# Create your views here.

def search_post(request):
    query=request.GET.get("q")
    result=None
    lookups=Q(title__icontains=query) | Q(body__icontains=query)
    result=Post.objects.filter(lookups)
    content={
        "searched":query,
        "result":result
    }
    return render(request,'blog/post/search.html',content)
    


@login_required
def like_view(request,post):
    p=get_object_or_404(Post,slug=post,status='published')
    liked=False
    if p.likes.filter(id=request.user.id).exists():
        p.likes.remove(request.user)
        liked=False
    else:
        p.likes.add(request.user)
        liked=True

    return redirect(p.get_absolute_url())

@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        form.save_m2m()
      
        messages.success(request, "Successfully Created")
        return redirect(instance.get_absolute_url())
    context = {
        "form": form,
        'page': 'new-post',
      
    }
    return render(request, "blog/post/post_form.html", context)


@login_required
def post_edit(request, post):

    page = 'post-edit'
    p = get_object_or_404(Post, slug=post, status='published')
    if p.author.id != request.user.id:
        raise PermissionDenied
    form = PostForm(instance=p)

    if request.method == 'POST':
        form = PostForm(request.POST,
                        request.FILES,
                        instance=p)
        if form.is_valid():
            form.save()
            print(p.tags.all())
            messages.success(request, f'Post Updated')
            return redirect(p.get_absolute_url())

    else:
        form = PostForm(instance=p)

    context = {
        'form': form,
        'page': page,
        'post': p,
    }

    return render(request, 'blog/post/detail.html', context)


@login_required
def deletePost(request, post):
    # p=Post.objects.get(slug=slug)

    p = get_object_or_404(Post, slug=post, status='published')
    if p.author.id != request.user.id:
        raise PermissionDenied

    if request.method == 'POST':
        p.delete()
        return redirect('blog:post_list')

    context = {'object': p}
    return render(request, 'blog/post/postdelete.html', context)


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # 3 posts in each page
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    # posts = Post.published.all()
    context = {
        'posts': posts,
        'page': page,
        'tag': tag
    }
    return render(request, 'blog/post/list.html', context)

@login_required
def post_detail(request,  post):
    post = get_object_or_404(Post, slug=post,
                             status='published',
                             )
    # List of active comments for this post
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.name=request.user
           
        # # Create Comment object but don't save to database yet
            new_comment.post = post
        # Assign the current post to the comment
            new_comment.save()
        # Save the comment to the database

    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
        .order_by('-same_tags', '-publish')[:4]

    total_likes=post.total_likes()
    
    liked=False
    if post.likes.filter(id=request.user.id).exists():
        liked=True
   
    
    

    context = { 
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts,
        'total_likes':total_likes,
        'liked':liked
    }

    return render(request, 'blog/post/detail.html', context)


@login_required
def post_share(request, post_id):
    # Retrive post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form feilds passsed validation.
            cd = form.cleaned_data
            # send mail
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{ request.user } recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{request.user}\'s comments: {cd['comments']}"
            send_mail(subject, message, os.environ.get(
                'EMAIL_USER'), [cd['to']])
            sent = True

    else:
        form = EmailPostForm()
    context = {
        'post': post,
        'form': form,
        'sent': sent
    }

    return render(request, 'blog/post/share.html', context)

