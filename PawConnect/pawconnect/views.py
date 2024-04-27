from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
import mimetypes
import json
from openai import OpenAI
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

from pawconnect.forms import LoginForm, RegisterForm, ProfileForm, MarketItemForm
from .models import CartItem, Order, OrderItem, Profile, Post
from pawconnect.models import (Post, Profile, Comment, RehomeQuizResult, AdoptQuizResult, ChatSession, Message,
                                MarketItem, Transaction, CartItem)

# This is the view function for the root URL
def root(request):
    if request.user.is_authenticated:
        # If the user is authenticated, redirect them to the home page
        return home_action(request)
    else:
        # If the user is not authenticated, redirect them to the login page
        return redirect('login')
    
@login_required
def home_action(request):
    if request.method == 'GET':
        return render(request, 'pawconnect/home_page.html')
@login_required
def community_action(request):
    if request.method == 'GET':
        return render(request, 'pawconnect/community.html')
@login_required
def map_action(request):
    if request.method == 'GET':
        return render(request, 'pawconnect/map.html')
@login_required
def marketplace_action(request):
    if request.method == 'GET':
        items = MarketItem.objects.filter(is_sold=False)
        user_profile = Profile.objects.get(user=request.user)
        virtual_currency = user_profile.virtual_currency
        items = MarketItem.objects.filter(is_sold=False)
        context = {'items': items, 'virtual_currency': virtual_currency}
        return render(request, 'pawconnect/marketplace.html', context)
    
@login_required
def quiz_action(request):
    user_has_rehome_quiz = RehomeQuizResult.objects.filter(user=request.user).exists()
    user_has_adopt_quiz = AdoptQuizResult.objects.filter(user=request.user).exists()

    context = {
        'user_has_submitted_quiz': user_has_rehome_quiz or user_has_adopt_quiz,
        'matches_exist': False,  # Default to False, update below if matches are found
        'quiz_type': '',
    }

    matches = False

    if user_has_rehome_quiz:
        rehome_quiz = RehomeQuizResult.objects.filter(user=request.user).first()
        matches = AdoptQuizResult.objects.filter(species=rehome_quiz.species, pet_size=rehome_quiz.size)
        context['quiz_type'] = 'rehome'
    
    elif user_has_adopt_quiz:
        adopt_quiz = AdoptQuizResult.objects.filter(user=request.user).first()
        matches = RehomeQuizResult.objects.filter(species=adopt_quiz.species, size=adopt_quiz.pet_size)
        context['quiz_type'] = 'adopt'

    if matches:
        context['matches_exist'] = True
        context['matches'] = matches
    else:
        messages.info(request, "No matches found. Please check back later as more pets are added.")

    return render(request, 'pawconnect/quiz.html', context)

def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        context['form'].fields['username'].widget.attrs.update({'id': 'id_username'})
        context['form'].fields['password'].widget.attrs.update({'id': 'id_password'})
        return render(request, 'pawconnect/login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'pawconnect/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    
    if new_user is not None:
    # The backend argument isn't always needed, but can be useful if using multiple backends.
        login(request, new_user, backend='django.contrib.auth.backends.ModelBackend') 
        return redirect(reverse('home'))


def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        context['form'].fields['username'].widget.attrs.update({'id': 'id_username'})
        context['form'].fields['password1'].widget.attrs.update({'id': 'id_password'})
        context['form'].fields['password2'].widget.attrs.update({'id': 'id_confirm_password'})
        context['form'].fields['email'].widget.attrs.update({'id': 'id_email'})
        context['form'].fields['first_name'].widget.attrs.update({'id': 'id_first_name'})
        context['form'].fields['last_name'].widget.attrs.update({'id': 'id_last_name'})
        return render(request, 'pawconnect/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'pawconnect/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    
    Profile.objects.create(user=new_user, bio='Share something about yourself!', city='Your city', virtual_currency=100.00)

    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])

    login(request, new_user)
    return redirect(reverse('global_stream'))

@login_required
def profile_action(request):

    if request.method == 'GET':
        context = { 'form': ProfileForm(initial={'bio': request.user.profile.bio, 'city': request.user.profile.city}) }
        return render(request, 'pawconnect/profile.html', context)

    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        context = {'form': form }
        return render(request, 'pawconnect/profile.html', context)

    profile = request.user.profile  # Access the user's profile
    profile.bio = form.cleaned_data['bio']  # Update bio
    profile.city = form.cleaned_data['city'] # Update city
    if form.cleaned_data['picture']:  # Check if a picture was uploaded
        profile.picture = form.cleaned_data['picture']  # Update picture

    profile.save()  # Save the profile with the updated data

    # Redirect to the profile page or another success page
    return redirect('profile')

@login_required
def user_photo(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)

    if not profile.picture:
        raise Http404('No picture found for this profile.')

    # Dynamically determine the content type of the image
    content_type, _ = mimetypes.guess_type(profile.picture.path)
    if not content_type:
        content_type = 'image/jpeg'  # Default to JPEG if content type cannot be guessed

    # Open the file and return it as a response
    try:
        with profile.picture.open('rb') as image:
            return HttpResponse(image.read(), content_type=content_type)
    except FileNotFoundError:
        raise Http404('Image file not found.')

@login_required
def follower_stream(request):
    following_users = request.user.profile.following.all()
    followed_posts = Post.objects.filter(user__in=following_users).order_by('-creation_time')
    context = {'posts': followed_posts}
    return render(request, 'pawconnect/follower_stream.html', context)

# Action for the /pawconnect/new-post route.
@login_required
def post_action(request):

    # Set context with current list of items so we can easily return if we discover errors.
    context = { 'posts': Post.objects.all() }

    # Adds the new item to the database if the request parameter is present
    if 'post' not in request.POST or not request.POST['post']:
        context['error'] = 'You must enter something to post.'
        return render(request, 'pawconnect/global_stream.html', context)

    new_post = Post(text=request.POST['post'], user=request.user)
    new_post.save()
    return redirect('global_stream')

@login_required
def unfollow(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    request.user.profile.following.remove(user_to_unfollow)
    request.user.profile.save()
    return other_profile(request, user_id)

@login_required
def follow(request,user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    request.user.profile.following.add(user_to_follow)
    request.user.profile.save()
    return other_profile(request, user_id)

@login_required
def other_profile(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(user=user).order_by('-creation_time')  # Ensure the posts are ordered by creation time

    context = {
        'profile': profile,
        'posts': posts
    }
    return render(request, 'pawconnect/other_user.html', context)

# Ajax implementation

def _my_json_error_response(message, status=200):
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)

def get_global(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    response_data = []
    for model_item in Post.objects.all():
        my_item = {
            'id': model_item.id,
            'text': model_item.text,
            'creation_time': model_item.creation_time.isoformat(),
            'user_id': model_item.user.id,
            'fname': model_item.user.first_name,
            'lname': model_item.user.last_name,
        }
        response_data.append(my_item)
    
    comment_data = []
    for model_item in Comment.objects.all():
        my_item = {
            'id': model_item.id,
            'text': model_item.text,
            'creation_time': model_item.creation_time.isoformat(),
            'user_id': model_item.creator.id,
            'post_id': model_item.post.id,
            'fname': model_item.creator.first_name,
            'lname': model_item.creator.last_name,
        }
        comment_data.append(my_item)
    
    # make a dictionary to convert to JSON
    response_data = {
        'posts': response_data,
        'comments': comment_data
    }

    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

def add_comment(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)
    
    comment_text = request.POST.get('comment_text')
    post_id = request.POST.get('post_id')
        # Ensure 'post_id' is provided and is a valid integer
    try:
        if post_id is None or post_id == '':
            raise ValueError("Post ID is required.")
        post_id = int(post_id)  # Convert to integer to validate
    except ValueError as e:
        # Return 400 Bad Request if post_id is missing or not a valid integer
        return _my_json_error_response(str(e), status=400)
    
    if not 'comment_text' in request.POST or not comment_text:
        return _my_json_error_response("You must type something to add.", status=400)
    
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=400)
    
    new_comment = Comment(text=comment_text, creator=request.user, post=post)
    new_comment.save()
    
    comment_data = {
        'id': new_comment.id,
        'text': new_comment.text,
        'creation_time': new_comment.creation_time.isoformat(),
        'user_id': new_comment.creator.id,
        'post_id': new_comment.post.id,
        'fname': new_comment.creator.first_name,
        'lname': new_comment.creator.last_name,
    }

    # Return only the new comment info as JSON
    return JsonResponse({'comment': comment_data})

def get_follower(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=403)

    # Get the current user's profile
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return _my_json_error_response("User profile does not exist.", status=400)

    # Get the list of users the current user is following
    following_users = user_profile.following.all()

    # Filter posts created by users that the current user is following
    posts = Post.objects.filter(user__in=following_users)

    # Prepare the posts data
    posts_data = [{
        'id': post.id,
        'text': post.text,
        'creation_time': post.creation_time.isoformat(),
        'user_id': post.user.id,
        'fname': post.user.first_name,
        'lname': post.user.last_name,
    } for post in posts]

    # Filter comments associated with the filtered posts
    comments = Comment.objects.filter(post__in=posts)

    # Prepare the comments data
    comments_data = [{
        'id': comment.id,
        'text': comment.text,
        'creation_time': comment.creation_time.isoformat(),
        'user_id': comment.creator.id,
        'post_id': comment.post.id,
        'fname': comment.creator.first_name,
        'lname': comment.creator.last_name,
    } for comment in comments]

    # Make a dictionary to convert to JSON
    response_data = {
        'posts': posts_data,
        'comments': comments_data
    }

    response_json = json.dumps(response_data)

    return HttpResponse(response_json, content_type='application/json')

## for quiz
@login_required
def rehome_quiz_action(request):
    return render(request, 'pawconnect/rehome_quiz.html')

@login_required
def adopt_quiz_action(request):
    return render(request, 'pawconnect/adopt_quiz.html')

@login_required
def rehome_quiz_submit(request):
    if request.method == 'POST':
        species = request.POST.get('species')
        color = request.POST.get('color')
        age = request.POST.get('age')
        size = request.POST.get('size')
        gender = request.POST.get('gender')
        neutered_spayed = request.POST.get('neutered') == 'Yes'
        health_issues = request.POST.get('health_issues')
        friendly_with_pets = request.POST.get('friendly') == 'Yes'
        vaccinations_up_to_date = request.POST.get('vaccine') == 'Yes'
        rehoming_reason = request.POST.get('reason')

        new_result = RehomeQuizResult(
            user=request.user,
            species=species,
            color=color,
            age=int(age) if age.isdigit() else 0,
            size=size,
            gender=gender,
            neutered_spayed=neutered_spayed,
            health_issues=health_issues,
            friendly_with_pets=friendly_with_pets,
            vaccinations_up_to_date=vaccinations_up_to_date,
            rehoming_reason=rehoming_reason
        )
        
        new_result.save()

        messages.add_message(request, messages.SUCCESS, 'Thank you for submitting the adoption quiz!')

        # Fetch the user's location from UserProfile
        # user_profile = UserProfile.objects.get(user=request.user)
        # user_location = user_profile.location

        # Fetch matching adopt quiz results
        matches = AdoptQuizResult.objects.filter(
            species=new_result.species,
            pet_size=new_result.size,
            # user__userprofile__location=user_location  # Assuming a backward relation from User to UserProfile
        )

        # Redirect back to the quiz page, or to a success page
        # return redirect('quiz')

        # Render the results page, passing the matches
        return render(request, 'pawconnect/matching_result.html', {
            'matches': matches, 
            'quiz_type': 'rehome',
            'rehome_result': new_result
        })
    else:
        # Redirect to home if not a POST request
         return render(request, 'pawconnect/rehome_quiz.html')

@login_required
def adopt_quiz_submit(request):
    if request.method == 'POST':

        new_result = AdoptQuizResult(
            user=request.user,
            species = request.POST.get('species'),
            living_situation=request.POST.get('living_situation'),
            hours_away=request.POST.get('hours_away'),
            pet_size=request.POST.get('pet_size'),
            pet_experience=request.POST.get('experience'),
            pet_energy_level=request.POST.get('energy_level'),
            specific_training=request.POST.get('specific_training'),
            medical_expenses_plan=request.POST.get('medical_expenses'),
            adoption_reason=request.POST.get('adoption_reason'),
        )
        new_result.save()

        messages.success(request, messages.SUCCESS, 'Thank you for submitting the adoption quiz!')

        # Fetch matching adopt quiz results
        matches = RehomeQuizResult.objects.filter(
            species=new_result.species,
            size=new_result.pet_size,
            # user__userprofile__location=user_location  # Assuming a backward relation from User to UserProfile
        )

        return render(request, 'pawconnect/matching_result.html', {
            'matches': matches,
            'quiz_type': 'adopt',
            'adopt_result': new_result
        })

    else:
        return render(request, 'pawconnect/adopt_quiz.html')

@login_required
def matching_result_view(request):
    try:
        # Attempt to retrieve the user's latest AdoptQuizResult
        latest_quiz = AdoptQuizResult.objects.filter(user=request.user).latest('created_at')
    except AdoptQuizResult.DoesNotExist:
        latest_quiz = None
    
    matches = []
    if latest_quiz:
        matches = RehomeQuizResult.objects.filter(
            species=latest_quiz.species,
            size=latest_quiz.pet_size
            # Add any other criteria
        )
    
    return render(request, 'pawconnect/matching_result.html', {
        'matches': matches,
        'quiz_type': 'adopt' if latest_quiz else '',
        'adopt_result': latest_quiz
    })

# For private chat
@login_required
def my_chats_view(request):
    chat_sessions = ChatSession.objects.filter(participants=request.user).distinct()
    chat_sessions_info = []

    for session in chat_sessions:
        # Identify the other user in the chat session
        other_user = session.participants.exclude(id=request.user.id).first()

        # Count unread messages directed to the current user in this session
        unread_count = session.messages.filter(receiver=request.user, is_read=False).count()

        # Add session info including other user details and unread message count
        chat_sessions_info.append({
            'session_id': session.id,
            'chat_url': reverse('chat_with_user', args=[session.id]),
            'other_user_full_name': f"{other_user.first_name} {other_user.last_name}",
            'unread_count': unread_count,
            'last_activity': session.last_activity
        })

    return render(request, 'pawconnect/my_chats.html', {'chat_sessions': chat_sessions_info})

@login_required
def fetch_new_chats(request):
    chat_sessions = ChatSession.objects.filter(participants=request.user).distinct()
    chat_sessions_info = []

    for session in chat_sessions:
        other_user = session.participants.exclude(id=request.user.id).first()
        unread_count = session.messages.filter(receiver=request.user, is_read=False).count()

        chat_sessions_info.append({
            'session_id': session.id,
            'other_user_full_name': f"{other_user.first_name} {other_user.last_name}",
            'unread_count': unread_count,
            'last_activity': session.last_activity.strftime('%Y-%m-%d %H:%M:%S') if session.last_activity else None
        })

    return JsonResponse({'chat_sessions': chat_sessions_info})

@login_required
def initiate_chat_session(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    chat_sessions = ChatSession.objects.filter(participants=request.user).filter(participants=other_user)

    if chat_sessions.exists():
        chat_session = chat_sessions.first()
    else:
        # No session exists, let's create a new one
        chat_session = ChatSession.objects.create()
        chat_session.participants.add(request.user, other_user)
        chat_session.save()

    return redirect('chat_with_user', session_id=chat_session.id)

@login_required
def chat_with_user(request, session_id):
    chat_session = get_object_or_404(ChatSession, id=session_id)
    other_user = chat_session.participants.exclude(id=request.user.id).first()
    
    # Check if the user is a participant of the chat session
    if request.user not in chat_session.participants.all():
        return redirect('some_error_page')  # Redirect to an error page or the homepage

    # once enter the chat interface, mark all message as read
    chat_session.messages.filter(receiver=request.user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            Message.objects.create(
                chat_session=session,
                sender=request.user,
                receiver=other_user,
                message=message_text,
            )
            return redirect('chat_with_user', session_id=session.id)
    
    messages = chat_session.messages.all().order_by('-created_at')

    return render(request, 'pawconnect/chat_interface.html', {
        'chat_session': chat_session, 
        'other_user':other_user, 
        'messages': messages
    })

@login_required
def send_message(request, session_id):
    if request.method == 'POST':
        chat_session = get_object_or_404(ChatSession, id=session_id)
        message_text = request.POST.get('message', '').strip()

        if message_text:
            participants = chat_session.participants.exclude(id=request.user.id)
            if participants.exists():
                receiver = participants.first()
                Message.objects.create(
                    chat_session=chat_session,
                    sender=request.user,
                    receiver=receiver,
                    message=message_text
                )
                # Redirect back to the chat session view
                return redirect('chat_with_user', session_id=session_id)
            else:
                pass
    return HttpResponseRedirect(reverse('chat_with_user', args=[session_id]))

@login_required
def fetch_new_messages(request, session_id):
    chat_session = get_object_or_404(ChatSession, id=session_id)
    messages = chat_session.messages.order_by('-created_at')
    messages_data = [
        {
            "sender": message.sender.username,
            "message": message.message,
            "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "is_sender": message.sender == request.user
        } for message in messages
    ]
    
    return JsonResponse({"messages": messages_data})

# Chatbot view
# Function to get user input and return chatbot response
def chatbot(request):
    try:
        messages = request.session['chat_history']
    except KeyError:
        messages = []

    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            response = chat(user_message)
            now = timezone.now()
            messages.append({'type': 'you', 'text': "🧑‍🎓 " + user_message, 'timestamp': now.isoformat()})
            messages.append({'type': 'chatbot', 'text': "️🤖️ " + response, 'timestamp': now.isoformat()})
            request.session['chat_history'] = messages

    context = {'messages': messages}
    return render(request, 'pawconnect/chatbot.html', context)

client = OpenAI(
    api_key="replace with the API key",
)

# Function for calling the model and the prompt
def chat(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0, 
    )
    return(response.choices[0].message.content)

# End of chatbot view


@login_required
def purchase_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(MarketItem, id=item_id)

        # ensure unsold
        if item.is_sold:
            messages.error(request, "This item has already been sold.")
            return redirect('market_item_detail', item_id=item_id)

        # update the item
        item.is_sold = True
        item.buyer = request.user
        item.sold_at = timezone.now()
        item.save()

        transaction = Transaction(
            buyer=request.user,
            seller=item.seller,
            item=item,
            amount=item.price
        )
        transaction.save()

        messages.success(request, "Congratulations! You've successfully purchased the item.")
        return redirect('marketplace')
    else:
        return HttpResponse("Method not allowed", status=405)

@login_required
def view_transactions(request):
    transactions_as_buyer = request.user.transactions_as_buyer.all()
    transactions_as_seller = request.user.transactions_as_seller.all()

    return render(request, 'your_template.html', {
        'transactions_as_buyer': transactions_as_buyer,
        'transactions_as_seller': transactions_as_seller,
    })

# def market_item_list(request):
#     items = MarketItem.objects.filter(is_sold=False)
#     return render(request, 'pawconnect/marketplace.html', {'items': items})

def item_detail(request, item_id):
    item = get_object_or_404(MarketItem, id=item_id)
    return render(request, 'pawconnect/item_detail.html', {'item': item})


# add to cart
@login_required
def add_item_view(request):
    if request.method == 'POST':
        form = MarketItemForm(request.POST, request.FILES)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.seller = request.user # seller?
            new_item.save()
            # redirect
            return redirect('my_items')
    else:
        form = MarketItemForm() #instance = item?
    return render(request, 'pawconnect/add_item.html', {'form': form})

# shopping cart
@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MarketItem, id=item_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, item=item)
    if not created:
        cart_item.quantity += 1  # If the item is already in the cart, increase the amount
        if cart_item.quantity > cart_item.item.quantity:
            messages.error(request, f'The quantity for {cart_item.item.title} exceeds the available stock.', extra_tags=item_id)
        else:
            cart_item.save()
    return redirect('confirm_purchase')

#update the cart （quantity）
@require_POST
@login_required
def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    quantity = request.POST.get('quantity')
    if quantity:
        new_quantity = int(quantity)
        if new_quantity > cart_item.item.quantity: 
            messages.error(request, f'The quantity for {cart_item.item.title} exceeds the available stock.', extra_tags=cart_item_id)
        else:
            cart_item.quantity = int(quantity)
            cart_item.save()
    return redirect('confirm_purchase')

# delete item from cart
@require_POST
@login_required
def delete_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('confirm_purchase')

# confirm purchase  have a reivew of cart
from django.db.models import Sum, F
@login_required
def confirm_purchase(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = cart_items.aggregate(total=Sum(F('item__price') * F('quantity')))['total']
    return render(request, 'pawconnect/confirm_purchase.html', {'cart_items': cart_items, 'total': total})

# end of shopping cart


# check out

@login_required
def checkout(request):
    with transaction.atomic():
        user = request.user
        cart_items = CartItem.objects.filter(user=user)
        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect('confirm_purchase')
        
        total_cost = sum(item.item.price * item.quantity for item in cart_items)
        
        profile = Profile.objects.get(user=user)
        if profile.virtual_currency < total_cost:
            messages.error(request, "Insufficient 🪙 in your account", extra_tags='insufficient-funds')
            return redirect('confirm_purchase')
        
        profile.virtual_currency -= total_cost
        profile.save()
        order = Order(user=user)
        order.save()
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.item,
                price=item.item.price,
                quantity=item.quantity
            )
            item.delete()
        messages.success(request, "Your order has been placed successfully.")
    return redirect('order_summary', order_id=order.id)

@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'pawconnect/order_summary.html', {'order': order})

@login_required
def view_purchase_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'pawconnect/purchase_history.html', {'orders': orders})

from .forms import AddBalanceForm
# add balance
@login_required
def add_balance(request):
    if request.method == 'POST':
        form = AddBalanceForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_profile = request.user.profile
            user_profile.virtual_currency += amount
            user_profile.save()
            
            messages.success(request, f"Successfully added ${amount} to your balance.")
            return redirect('marketplace')
    else:
        form = AddBalanceForm()
    
    return render(request, 'pawconnect/add_balance.html', {'form': form})


# about my items

@login_required
def my_items(request):
    items = MarketItem.objects.filter(seller=request.user)
    print(items)
    return render(request, 'pawconnect/my_items.html', {'items': items})

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(MarketItem, id=item_id, seller=request.user)
    if request.method == 'POST':
        form = MarketItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            print(form)
            return redirect('my_items')
    else:
        form = MarketItemForm(instance=item)

    context = {'form': form, 'item': item}
    return render(request, 'pawconnect/edit_item.html', context)

@login_required
@require_POST 
def delete_item(request, item_id):
    item = get_object_or_404(MarketItem, id=item_id, seller=request.user)
    item.delete()
    messages.success(request, "Item deleted successfully.")
    return redirect('my_items')

@login_required
def item_photo(request, item_id):
    item = get_object_or_404(MarketItem, id=item_id)
    if not item.image:
        raise Http404('No image found for this item.')

    content_type, _ = mimetypes.guess_type(item.image.path)
    if not content_type:
        content_type = 'image/jpeg'

    try:
        with item.image.open('rb') as image:
            return HttpResponse(image.read(), content_type=content_type)
    except FileNotFoundError:
        raise Http404('Image file not found.')
