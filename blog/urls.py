from django.urls import path
from .views import (
    PostListView, PostDetailView, PostCreateView,
    PostUpdateView, PostDeleteView, UserPostListView,
    buy_post, payment_success, my_purchases,
    inbox, user_profile, add_comment, send_negotiation # ← NEW VIEWS
)
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('user/<str:username>/', user_profile, name='user-profile'), 
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('post/<int:pk>/buy/', buy_post, name='buy-post'),  
    path('payment-success/<int:order_id>/', payment_success, name='payment-success'),  
    path('my-purchases/', my_purchases, name='my-purchases'),  
    path('cart/', views.cart_detail, name='cart-detail'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add-to-cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove-from-cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('inbox/', inbox, name='inbox'),
    path('post/<int:pk>/comment/', add_comment, name='add-comment'),
    path('negotiate/<int:receiver_id>/', send_negotiation, name='send-negotiation'),
    path('user/<str:username>/', user_profile, name='user-posts'),
    path('chat/<int:post_id>/<int:user_id>/', views.chat_view, name='chat-view'),
]