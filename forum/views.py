from multiprocessing import context
from django.shortcuts import render,HttpResponse,get_object_or_404,redirect
from django.http import JsonResponse,HttpResponseRedirect
from .models import Question,Answer,Comment
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import AnswerForm,QuestionForm
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


# Home Page
def home(request):
    page='home'
    if 'q' in request.GET:
        q=request.GET['q']
        quests=Question.objects.annotate(total_comments=Count('answer__comment')).filter(title__icontains=q).order_by('-id')
    else:
        quests=Question.objects.annotate(total_comments=Count('answer__comment')).all().order_by('-id')
    paginator=Paginator(quests,10)
    page_num=request.GET.get('page',1)
    quests=paginator.page(page_num)
    context={
        'quests':quests,
        'page':page,
    }
    return render(request,'forum/home.html',context)

def give_answer(request):
    if 'q' in request.GET:
        q=request.GET['q']
        unanswered_question=Question.objects.filter(answer__isnull=True).filter(title__icontains=q)
    else:
        unanswered_question=Question.objects.filter(answer__isnull=True)
    count=unanswered_question.count()
    
    paginator=Paginator(unanswered_question,17)
    page_num=request.GET.get('page',1)
    unanswered_question=paginator.page(page_num)
    
    context={
        'unanswered_question':unanswered_question,
        'count':count,
    }
    return render(request,'forum/unanswered.html',context)

# Detail
@login_required
def detail(request,slug):
    quest=get_object_or_404(Question,slug=slug)
    tags=quest.tags.split(',')
    answers=Answer.objects.filter(question=quest)
    answerform=AnswerForm
    if request.method=='POST':
        answerData=AnswerForm(request.POST)
        if answerData.is_valid():
            answer=answerData.save(commit=False)
            answer.question=quest
            answer.user=request.user
            answer.save()
            messages.success(request,'Answer has been submitted.')
    context={
        'quest':quest,
        'tags':tags,
        'answers':answers,
        'answerform':answerform
    }
    return render(request,'forum/detail.html',context)

# Save Comment
@login_required
def save_comment(request):
    if request.method=='POST':
        comment=request.POST['comment']
        answerid=request.POST['answerid']
        answer=Answer.objects.get(pk=answerid)
        user=request.user
        Comment.objects.create(
            answer=answer,
            comment=comment,
            user=user
        )
        return JsonResponse({'bool':True})

 
@login_required
def save_upvote(request,id,pk):
    p=get_object_or_404(Answer,id=id)

    if p.downvote.filter(id=request.user.id).exists():
        p.downvote.remove(request.user)

    if p.upvote.filter(id=request.user.id).exists():
        p.upvote.remove(request.user)
    else:
        p.upvote.add(request.user)

    p.total_upvote=p.upvote.count()
    p.total_downvote=p.downvote.count()
    p.save()

    q=get_object_or_404(Question,id=pk)

    return redirect(q.get_absolute_url())  

@login_required
def save_downvote(request,id,pk):
    p=get_object_or_404(Answer,id=id)

    if p.upvote.filter(id=request.user.id).exists():
        p.upvote.remove(request.user)

    if p.downvote.filter(id=request.user.id).exists():
        p.downvote.remove(request.user)
    else:
        p.downvote.add(request.user)

    p.total_upvote=p.upvote.count()
    p.total_downvote=p.downvote.count()
    p.save()

    q=get_object_or_404(Question,id=pk)  
    return redirect(q.get_absolute_url()) 


# Ask Form
@login_required
def ask_form(request):
    form=QuestionForm
    if request.method=='POST':
        questForm=QuestionForm(request.POST)
        if questForm.is_valid():
            questForm=questForm.save(commit=False)
            questForm.user=request.user
            questForm.save()
            messages.success(request,'Question has been added.')
            return redirect(questForm.get_absolute_url())
    return render(request,'forum/ask-question.html',{'form':form})



@login_required
def answer_edit(request, pk):
    pg = 'answer-post'
    p = get_object_or_404(Answer,id=pk)
    if p.user.id != request.user.id:
        raise PermissionDenied
    ans_form = AnswerForm(instance=p)

    if request.method == 'POST':
        ans_form =AnswerForm(request.POST,
                        request.FILES,
                        instance=p)
        if ans_form.is_valid():
            ans_form.save()
            messages.success(request, f'Answer Updated')
            return redirect(p.question.get_absolute_url())
    else:
        ans_form = AnswerForm(instance=p)
    print("OK")
    print(ans_form)

    context = {
        'ans_form': ans_form,
        'pg': pg,
        'post': p,
    }
    return render(request, 'forum/ansedit.html', context)


@login_required
def deleteAns(request, pk):
    p = get_object_or_404(Answer,id=pk)
    if p.user.id != request.user.id:
        raise PermissionDenied

    if request.method == 'POST':
        p.delete()
        return redirect(p.question.get_absolute_url())

    context = {'object': p}
    return render(request, 'forum/ansdelete.html', context)



@login_required
def post_edit(request, slug):

    page = 'post-edit'
    p = get_object_or_404(Question, slug=slug)
    if p.user.id != request.user.id:
        raise PermissionDenied
    form = QuestionForm(instance=p)

    if request.method == 'POST':
        form = QuestionForm(request.POST,
                        request.FILES,
                        instance=p)
        if form.is_valid():
            form.save()
            messages.success(request, f'Question Updated')
            return redirect(p.get_absolute_url())

    else:
        form = QuestionForm(instance=p)

    context = {
        'form': form,
        'page': page,
        'post': p,
    }

    return render(request, 'forum/detail.html', context)


@login_required
def deletePost(request, slug):
    # p=Post.objects.get(slug=slug)

    p = get_object_or_404(Question, slug=slug)
    if p.user.id != request.user.id:
        raise PermissionDenied

    if request.method == 'POST':
        p.delete()
        return redirect('forum:home')

    context = {'object': p}
    return render(request, 'forum/quesdelete.html', context)




# Questions according to tag
def tag(request,tag):
    quests=Question.objects.annotate(total_comments=Count('answer__comment')).filter(tags__icontains=tag).order_by('-id')
    paginator=Paginator(quests,10)
    page_num=request.GET.get('page',1)
    quests=paginator.page(page_num)
    return render(request,'forum/tag.html',{'quests':quests,'tag':tag})



# Tags Page
def tags(request):
    quests=Question.objects.all()
    tags=[]
    for quest in quests:
        qtags=[tag.strip() for tag in quest.tags.split(',')]
        for tag in qtags:
            if tag not in tags:
                tags.append(tag)
    # Fetch Questions
    tag_with_count=[]
    for tag in tags:
        tag_data={
            'name':tag,
            'count':Question.objects.filter(tags__icontains=tag).count()
        }
        tag_with_count.append(tag_data)
    print(tag_with_count)
    return render(request,'forum/tags.html',{'tags':tag_with_count})
        
        