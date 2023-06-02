from django.db import models

# Create your models here.
from datetime import date
from django.urls import reverse 
from django.contrib.auth.models import User 

class Author(models.Model):

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(max_length=400, help_text="Enter your bio details here.")
    date_joined = models.DateField(default=date.today)
    class Meta:
        ordering = ["user","date_joined"]

    def get_absolute_url(self):
        
        return reverse('blogs-by-author', args=[str(self.id)])

    def __str__(self):
       
        return self.user.username


class Blog(models.Model):
    
    name = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    description = models.TextField(max_length=2000, help_text="Enter you blog text here.")
    post_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    class Meta:
        ordering = ["-post_date"]
        permissions = (("can_create_post", "Create blog post"),)
        permissions = (("can_accept_request", "Approve request"),)
    def get_absolute_url(self):
        
        return reverse('blog-detail', args=[str(self.id)])

    def __str__(self):
       
        return self.name
        
        
class BlogComment(models.Model):
    
    description = models.TextField(max_length=1000, help_text="Enter comment about blog here.")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
      # Foreign Key used because BlogComment can only have one author/User, but users can have multiple comments
    post_date = models.DateTimeField(auto_now_add=True)
    blog= models.ForeignKey(Blog, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    class Meta:
        ordering = ["post_date"]

    def __str__(self):
       
        len_title=75
        if len(self.description)>len_title:
            titlestring=self.description[:len_title] + '...'
        else:
            titlestring=self.description
        return titlestring
    
class AuthorRequest(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(max_length=400, help_text="Enter your bio details here.")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Author Request by {self.user.username}"