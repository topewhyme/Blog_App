from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogListView.as_view(), name='blogs'),
    path('blogger/<int:pk>', views.BlogListbyAuthorView.as_view(), name='blogs-by-author'),
    path('blog/<int:pk>', views.BlogDetailView.as_view(), name='blog-detail'),
    path('bloggers/', views.BloggerListView.as_view(), name='bloggers'),
    path('blog/<int:pk>/comment/', views.BlogCommentCreate.as_view(), name='blog_comment'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('author/request/', views.AuthorRequestView.as_view(), name='author_request'),
    path('author/requests/', views.author_request_list, name='author_request_list'),
    path('author/request/success/', views.request_success_view, name='request_success'),
    path('author/requests/approve/<int:pk>/', views.approve_author_request, name='approve_author_request'),
    path('blog/create/', views.CreateBlogView.as_view(), name='create_blog'),
    path('blog/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('blog/<int:pk>/delete/', views.BlogUpdateStatusView.as_view(), name='post_delete'),
    path('author/<int:pk>', views.BlogsbyAuthorView.as_view(), name='blog_list_by_author'),
    path('comment/<int:pk>/delete/', views.CommentUpdateStatusView.as_view(), name='comment_delete'),
    path('comment/<int:pk>/edit/', views.CommentUpdateView.as_view(), name='comment_update'),
]