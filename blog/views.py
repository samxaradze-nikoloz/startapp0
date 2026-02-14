from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post, Order, CartItem
from users.models import Message, Comment 
from django.contrib import messages
from django.db.models import Q

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'image', 'price']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'image', 'price']

    def form_valid(self, form):
        
        if not form.cleaned_data.get('image'):
            form.instance.image = self.get_object().image
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})




@login_required
def buy_post(request, pk):
    """Handle purchase of a post"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if not payment_method:
            return redirect('post-detail', pk=pk)
        
        order = Order.objects.create(
            buyer=request.user,
            post=post,
            amount=post.price,
            payment_method=payment_method,
            status='pending'
        )
        
        
        return redirect('payment-success', order_id=order.id)
    
    return redirect('post-detail', pk=pk)


def payment_success(request, order_id):
    """Display payment success page"""
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'payment_method': order.get_payment_method_display()
    }
    return render(request, 'blog/payment_success.html', context)


def my_purchases(request):
    """View user's purchase history"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    orders = Order.objects.filter(buyer=request.user)
    context = {
        'orders': orders
    }
    return render(request, 'blog/my_purchases.html', context)



#CART
from .models import Post, Order, CartItem 

@login_required
def add_to_cart(request, pk):
    post = get_object_or_404(Post, pk=pk)
   
    cart_item, created = CartItem.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart-detail')

@login_required
def cart_detail(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in items)
    return render(request, 'blog/cart_detail.html', {'items': items, 'total': total})

@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    item.delete()
    return redirect('cart-detail')

@login_required
def checkout(request):
    """Converts CartItems into permanent Orders"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    if request.method == 'POST' and cart_items.exists():
        payment_method = request.POST.get('payment_method')
        
    
        for item in cart_items:
            Order.objects.create(
                buyer=request.user,
                post=item.post,
                amount=item.get_total_price(),
                payment_method=payment_method,
                status='pending'
            )
        
        
        cart_items.delete()
        return redirect('my-purchases')
        
    return render(request, 'blog/checkout.html', {'items': cart_items})






def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-date_posted')
 
    return render(request, 'blog/user_posts.html', {'seller': user, 'posts': posts})


@login_required
def inbox(request):
    received_messages = Message.objects.filter(receiver=request.user)
    return render(request, 'blog/inbox.html', {'messages': received_messages})

@login_required
def send_negotiation(request, receiver_id):
    if request.method == 'POST':
        receiver = User.objects.get(id=receiver_id)
        post_id = request.POST.get('post_id')
        post = Post.objects.get(id=post_id)
        content = request.POST.get('content')
        
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            post=post,
            content=content
        )
        messages.success(request, f'Negotiation request sent to {receiver.username}!')
        return redirect('post-detail', pk=post_id)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        Comment.objects.create(post=post, author=request.user, content=content)
        messages.success(request, 'Comment added!')
    return redirect('post-detail', pk=pk)


class PostDetailView(DetailView):
    model = Post
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.get_object()).order_by('-date_posted')
        return context
    


@login_required
def chat_view(request, post_id, user_id):
    other_user = get_object_or_404(User, id=user_id)
    post = get_object_or_404(Post, id=post_id)
    
    # Retrieve the conversation between these two users for this post
    chat_messages = Message.objects.filter(
        post=post
    ).filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                post=post,
                content=content
            )
        return redirect('chat-view', post_id=post.id, user_id=other_user.id)

    return render(request, 'blog/chat.html', {
        'chat_messages': chat_messages,
        'other_user': other_user,
        'post': post
    })



@login_required
def inbox(request):

    user_messages = Message.objects.filter(
        Q(receiver=request.user) | Q(sender=request.user)
    ).select_related('sender', 'receiver', 'post').order_by('-timestamp')

    received_requests = Message.objects.filter(receiver=request.user).order_by('-timestamp')

    return render(request, 'blog/inbox.html', {'messages': received_requests})

# Create your views here.