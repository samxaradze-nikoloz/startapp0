from django.shortcuts import render
from django.http import HttpResponse
from .models import Post



posts = [
    {
        'author': 'Samxaridze',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2024'
    },
    {
        'author': 'John Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2024'
    }
    ]

def home(request ):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)
def about(request):
    return render(
        request,
        'blog/about.html',
        {
            'title': 'About'
        }
    )
    

# Create your views here.
