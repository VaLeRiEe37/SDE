from django.urls import path
from pawconnect import views

urlpatterns = [
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),  
    path('photo/<int:user_id>', views.user_photo, name='photo'),
    path('follower_stream', views.follower_stream, name='follower_stream'),
    path('profile', views.profile_action, name='my_profile'), # remember to add the id later
    # path('profile/<int:user_id>/', views.profile_action, name='user_profile'),
    path('other_user/<int:user_id>', views.other_profile, name='other_user'),
    path('follow/<int:user_id>', views.follow, name='follow'),
    path('unfollow/<int:user_id>', views.unfollow, name='unfollow'),
    path('get-global', views.get_global, name='get-global-stream'),
    path('add-comment', views.add_comment, name='add-comment'),
    path('get-follower', views.get_follower, name='get-follower-stream'),

    path('home', views.home_action, name='home'), 
    path('global_stream', views.post_action, name='global_stream'),
    # path('message', views.message_action, name='message'),
    path('marketplace', views.marketplace_action, name='marketplace'),
    path('quiz', views.quiz_action, name='quiz'),

    path('rehome_quiz', views.rehome_quiz_action, name='rehome_quiz'),
    path('adopt_quiz', views.adopt_quiz_action, name='adopt_quiz'),
    path('rehome_quiz_submit', views.rehome_quiz_submit, name='rehome_quiz_submit'),
    path('adopt_quiz_submit', views.adopt_quiz_submit, name='adopt_quiz_submit'),
    path('matching_result', views.matching_result_view, name='matching_result'),

    path('my_chats/', views.my_chats_view, name='my_chats'),
    path('fetch_new_chats/', views.fetch_new_chats, name='fetch_new_chats'),
    path('initiate_chat_session/<int:user_id>/', views.initiate_chat_session, name='initiate_chat_session'),
    path('chat_with_user/<int:session_id>/', views.chat_with_user, name='chat_with_user'),
    path('send_message/<int:session_id>/', views.send_message, name='send_message'),
    path('fetch_new_messages/<int:session_id>/', views.fetch_new_messages, name='fetch_new_messages'),
    
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),  
    path('photo/<int:user_id>', views.user_photo, name='photo'),
    path('follower_stream', views.follower_stream, name='follower_stream'),
    path('profile', views.profile_action, name='profile'), # remember to add the id later
    path('other_user/<int:user_id>', views.other_profile, name='other_user'),
    path('follow/<int:user_id>', views.follow, name='follow'),
    path('unfollow/<int:user_id>', views.unfollow, name='unfollow'),
    path('get-global', views.get_global, name='get-global-stream'),
    path('add-comment', views.add_comment, name='add-comment'),
    path('get-follower', views.get_follower, name='get-follower-stream'),

    path('home', views.home_action, name='home'), 
    path('global_stream', views.post_action, name='global_stream'),
    path('map', views.map_action, name='map'),
    path('quiz', views.quiz_action, name='quiz'),

    path('rehome_quiz', views.rehome_quiz_action, name='rehome_quiz'),
    path('adopt_quiz', views.adopt_quiz_action, name='adopt_quiz'),
    path('rehome_quiz_submit', views.rehome_quiz_submit, name='rehome_quiz_submit'),
    path('adopt_quiz_submit', views.adopt_quiz_submit, name='adopt_quiz_submit'),
    path('matching_result', views.matching_result_view, name='matching_result'),

    path('chatbot', views.chatbot, name='chatbot'),

    path('marketplace', views.marketplace_action, name='marketplace'),
    # add balance
    path('add_balance/', views.add_balance, name='add_balance'),

    # items
    path('my_items/', views.my_items, name='my_items'),
    path('add_item/', views.add_item_view, name='add_item'),
    path('edit_item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),
    path('items/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item_photo/<int:item_id>/', views.item_photo, name='item_photo'),
    path('purchase-item/<int:item_id>/', views.purchase_item, name='purchase_item'),
    # cart
    path('add_to_cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart_item/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('delete_cart_item/<int:cart_item_id>/', views.delete_cart_item, name='delete_cart_item'),
    # end of cart
    path('checkout/', views.checkout, name='checkout'),
    
    path('transactions/', views.view_transactions, name='view_transactions'),
    path('confirm_purchase/', views.confirm_purchase, name='confirm_purchase'),
    path('order_summary/<int:order_id>/', views.order_summary, name='order_summary'),
    path('purchase-history/', views.view_purchase_history, name='purchase_history'),

]