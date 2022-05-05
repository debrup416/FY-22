from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

# Create your models here.


class UserProfile(models.Model):
    user=models.OneToOneField(User,primary_key=True,verbose_name='user',related_name='profile',on_delete=models.CASCADE)
    name=models.SlugField()
    bio=models.TextField(max_length=500,blank=True,null=True)
    birth_date=models.DateField(null=True,blank=True)
    location=models.CharField(max_length=100,blank=True,null=True)
    picture=models.ImageField(upload_to='uploads/profile_pictures',default='uploads/profile_pictures/default.jpg')
    followers=models.ManyToManyField(User,blank=True,related_name='followers')

    def get_absolute_url(self):
        return reverse('profile', args=[self.name])



@receiver(post_save,sender=User)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save,sender=User)
def save_user_profile(sender,instance,**kwargs):
    instance.profile.name=User.get_username(instance)
    instance.profile.save()




class ThreadModel(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
	receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')


class MessageModel(models.Model):
	thread = models.ForeignKey('ThreadModel', related_name='+', on_delete=models.CASCADE, blank=True, null=True)
	sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
	receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
	body = models.CharField(max_length=1000)
	image = models.ImageField(upload_to='uploads/message_photos', blank=True, null=True)
	date = models.DateTimeField(default=timezone.now)
	is_read = models.BooleanField(default=False)



