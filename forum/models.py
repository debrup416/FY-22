from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField
# Create your models here.

class Question(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    detail=RichTextField()
    tags=models.TextField(default='')
    add_time=models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('forum:detail', args=[self.slug])

    def __str__(self):
        return self.title

    
class Answer(models.Model):
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    detail=RichTextField()
    add_time=models.DateTimeField(auto_now_add=True)
    upvote=models.ManyToManyField(User,related_name='upvote_ans')
    downvote=models.ManyToManyField(User,related_name='downvote_ans')
    total_upvote=models.IntegerField(default=0)
    total_downvote=models.IntegerField(default=0)

    def __str__(self):
        return self.detail

class Comment(models.Model):
    answer=models.ForeignKey(Answer,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='comment_user')
    comment=models.TextField(default='')
    add_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment






from blog.utils import unique_slug_generator

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        # instance.slug = create_slug(instance)
        instance.slug = unique_slug_generator(instance)



pre_save.connect(pre_save_post_receiver, sender=Question)

