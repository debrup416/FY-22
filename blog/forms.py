from django import forms
from .models import Comment, Post
from taggit.forms import TagWidget
# from pagedown.widgets import PagedownWidget

class PostForm(forms.ModelForm):
    # body = forms.CharField(widget=PagedownWidget())
    class Meta:
        model=Post
        fields=['title','body','image','tags']
        widgets = {
            'tags': TagWidget(),
             
        }
        labels={
            'body':'',
        }


class EmailPostForm(forms.Form):
    # name = forms.CharField(max_length=25)
    # email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
    

    

