from django.shortcuts import render

# Create your views here.
from django.views import generic
from .models import Blog, Author, BlogComment
from django.contrib.auth.models import User #Blog author or commenter
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AuthorRequestForm
from .models import AuthorRequest, Author
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.http import HttpResponseRedirect
from django.views import View
from .models import AuthorRequest
from django.contrib.auth.models import Permission, Group
from django.db.models import Count
from django.conf import settings
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import SignupForm
from django.views.generic import UpdateView
from django.core.exceptions import PermissionDenied
from .forms import BlogForm
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

def index(request):
    num_blogs = Blog.objects.all().count()
    
    context = {
        'num_blogs': num_blogs,
    }


    return render(request, 'index.html', context=context)

class BlogListView(generic.ListView):
    model = Blog
    paginate_by = 5

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class BlogListbyAuthorView(LoginRequiredMixin, generic.DetailView):
    model = Author
    template_name = 'blog/blog_list_by_author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_object()
        context['blogs'] = author.blog_set.filter(is_deleted=False)
        return context



# class BlogsbyAuthorView(generic.ListView):
#     model = Blog
#     paginate_by = 5
#     template_name ='blog/blogs_by_author.html'
    
#     def get_queryset(self):
#         id = self.kwargs['pk']
#         target_author = get_object_or_404(Author, pk=id)
#         return Blog.objects.filter(author=target_author)
        
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['blogger'] = get_object_or_404(Author, pk=self.kwargs['pk'])
#         return context

class BlogsbyAuthorView(generic.ListView):
    model = Blog
    paginate_by = 5
    template_name ='blog/blogs_by_author.html'
    
    def get_queryset(self):
        id = self.kwargs['pk']
        target_author = get_object_or_404(Author, pk=id)
        return Blog.objects.filter(author=target_author, is_deleted=False)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blogger'] = get_object_or_404(Author, pk=self.kwargs['pk'])
        return context






# class BlogDetailView(generic.DetailView):
#     model = Blog
    
class BlogDetailView(LoginRequiredMixin, generic.DetailView):
    model = Blog

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.get_object()
        context['comments'] = blog.blogcomment_set.filter(deleted=False)
        return context


class BloggerListView(LoginRequiredMixin, generic.ListView):
    model = Author
    paginate_by = 5
    template_name = 'blog/author_list.html'

    def get_queryset(self):
        queryset = Author.objects.annotate(num_blogs=Count('blog', filter=Q(blog__is_deleted=False))).order_by('id')
        return queryset




class BlogCommentCreate(LoginRequiredMixin, CreateView):
    model = BlogComment
    fields = ['description',]

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BlogCommentCreate, self).get_context_data(**kwargs)
        # Get the blog from id and add it to the context
        context['blog'] = get_object_or_404(Blog, pk = self.kwargs['pk'])
        return context
        
    def form_valid(self, form):
        """
        Add author and associated blog to form data before setting it as valid (so it is saved to model)
        """
        #Add logged-in user as author of comment
        form.instance.author = self.request.user
        #Associate comment with blog based on passed id
        form.instance.blog=get_object_or_404(Blog, pk = self.kwargs['pk'])
        # Call super-class form validation behaviour
        return super(BlogCommentCreate, self).form_valid(form)

    def get_success_url(self): 
        """
        After posting comment return to associated blog.
        """
        return reverse('blog-detail', kwargs={'pk': self.kwargs['pk'],})
    


class SignupViews(CreateView):
    form_class = SignupForm
    template_name = 'blog/signup.html'
    success_url = reverse_lazy('login')

class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'blog/signup.html'
    success_url = reverse_lazy('login')

class AuthorRequestView(LoginRequiredMixin, View):
    form_class = AuthorRequestForm
    template_name = 'blog/author_request.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            if AuthorRequest.objects.filter(user=request.user).exists():
                author_request = AuthorRequest.objects.get(user=request.user)
                status = author_request.status
                if status == 'rejected':
                    message = 'Your author request has been rejected.'
                else:
                    message = 'Your author request already exists and is pending.'
                return render(request, self.template_name, {'form': form, 'message': message})

            author_request = form.save(commit=False)
            author_request.user = request.user
            author_request.save()
            editors_group = Group.objects.get(name='Editors')
            editors = editors_group.user_set.all()
            for editor in editors:
                editor_email = editor.email
                send_mail(
                    "New Author Request",
                    f"{request.user} has requested to become an Author",
                    settings.EMAIL_HOST_USER,
                    [editor_email]
                )
            return redirect('request_success') 

        return render(request, self.template_name, {'form': form})




def request_success_view(request):
    return render(request, 'blog/request_success.html')

def approve_author_request(request, pk):
    author_request = get_object_or_404(AuthorRequest, pk=pk)
    author_request.status = 'A'
    author_request.save()
    send_mail(
        "Author Request Acceted",
        f"CONGRATULATIONS {author_request.first_name}, Your Request to become an author has been approved",
        settings.EMAIL_HOST_USER,
        [author_request.user.email]
    )
    if author_request.status == 'A':
        Author.objects.create(
            user=author_request.user,
            first_name=author_request.first_name,
            last_name=author_request.last_name,
            bio=author_request.bio
        )

    return redirect('author_request_list')


def author_request_list(request):
    author_requests = AuthorRequest.objects.filter(status='P')  # Get pending requests
    return render(request, 'blog/author_request_list.html', {'author_requests': author_requests})



class CreateBlogView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blog/create_blog.html'
    success_url = '/blog/blogs/'

    def form_valid(self, form):
        form.instance.author = self.request.user.author
        return super().form_valid(form)



class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ['name', 'description']
    template_name = 'blog/blog_edit.html'
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj.author == request.user.author:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)



class BlogUpdateStatusView(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ['is_deleted']
    success_url = reverse_lazy('blogs')
    template_name = 'blog/post_confirm_delete.html'

    def form_valid(self, form):
        blog = self.get_object()
        blog.is_deleted = True
        blog.save()
        return HttpResponseRedirect(self.get_success_url())


# class CommentDeleteView(UserPassesTestMixin, DeleteView):
#     model = BlogComment
#     template_name = 'blog/comment_confirm_delete.html'
#     success_url = reverse_lazy('blogs')

#     def test_func(self):
#         comment = self.get_object()
#         return comment.author == self.request.user or comment.blog.author == self.request.user

#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         self.object.deleted = True
#         self.object.save()
#         return super().delete(request, *args, **kwargs)

class CommentUpdateStatusView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model = BlogComment
    fields = ['deleted']
    success_url = reverse_lazy('blogs')
    template_name = 'blog/comment_confirm_delete.html'
    
    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user or comment.blog.author == self.request.user

    def form_valid(self, form):
        comment = self.get_object()
        comment.deleted = True
        comment.save()
        return HttpResponseRedirect(self.get_success_url())
    
from django.utils import timezone
from datetime import timedelta

class CommentUpdateView(UpdateView):
    model = BlogComment
    fields = ['description']
    template_name = 'blog/comment_update.html'
    context_object_name = 'comment'
    success_url = reverse_lazy('blogs')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        # Check if the comment is editable
        if (self.request.user == obj.author and
                obj.post_date >= timezone.now() - timedelta(minutes=5)):
            return obj

        # If the comment is not editable, raise a permission denied error
        raise PermissionDenied

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


def permission_denied_view(request, exception):
    return render(request, 'blog/403.html', status=403)