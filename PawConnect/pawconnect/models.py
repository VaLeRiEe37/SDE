from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Post(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'id={self.id}, text="{self.text}"'
    
    class Meta:
        ordering = ['-creation_time']

class Profile(models.Model):
    bio = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    picture = models.FileField(blank=True)
    city = models.CharField(max_length=50, default='anywhere')
    content_type = models.CharField(max_length=50)
    following = models.ManyToManyField(User, related_name='followers')
    virtual_currency = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)  # add currency

    def __str__(self):
        return 'id=' + str(self.id) + ',bio="' + self.bio + '"' + ',city="' + self.city + '"'

class Comment(models.Model):
    text = models.CharField(max_length=200)
    creator = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, default=None, on_delete=models.PROTECT)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'id={self.id}, text="{self.text}, post_id={self.post.id}, creator_id={self.creator.id}"'
    
    class Meta:
        ordering = ['creation_time']

class RehomeQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    species = models.CharField(max_length=200)
    color = models.CharField(max_length=200)
    age = models.IntegerField()
    size = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    neutered_spayed = models.BooleanField()
    health_issues = models.TextField(blank=True, null=True)
    friendly_with_pets = models.BooleanField()
    vaccinations_up_to_date = models.BooleanField()
    rehoming_reason = models.TextField( null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Quiz Result - {self.created_at.strftime('%Y-%m-%d')}"

class AdoptQuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    species = models.CharField(max_length=200, null=False, default='Dog')
    living_situation = models.CharField(max_length=100, null=False, default='House with a yard')
    hours_away = models.CharField(max_length=100, null=False, default='4 hours')
    pet_size = models.CharField(max_length=50, null=False, default='Small')
    pet_experience = models.CharField(max_length=100, null=False, default='Yes')
    pet_energy_level = models.CharField(max_length=50, null=False, default='High energy')
    specific_training = models.CharField(max_length=100, null=False, default='Yes')
    medical_expenses_plan = models.CharField(max_length=100, null=False, default='Pet insurance')
    adoption_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Adoption Quiz Result - {self.created_at.strftime('%Y-%m-%d')}"

class ChatSession(models.Model):
    participants = models.ManyToManyField(User, related_name='chat_sessions')
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ChatSession {self.id}"

class Message(models.Model):
    chat_session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
class MarketItem(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='market_items')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.FileField(blank=True, null = True)
    #image = models.ImageField(upload_to='item_images/', blank=True, null=True)  # 新增图片字段
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Transaction(models.Model):
    buyer = models.ForeignKey(User, related_name='transactions_as_buyer', on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='transactions_as_seller', on_delete=models.CASCADE)
    item = models.ForeignKey(MarketItem, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transaction for {self.item.title} on {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}'


class CartItem(models.Model):
    user = models.ForeignKey(User, related_name='cart_items', on_delete=models.CASCADE)
    item = models.ForeignKey(MarketItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.item.title}'
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(MarketItem, on_delete=models.CASCADE)  # 假设您的商品模型名为 MarketItem
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.product.title}'

    def get_cost(self):
        return self.price * self.quantity
