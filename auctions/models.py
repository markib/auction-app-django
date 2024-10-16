from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator
from django.utils import timezone
import datetime

class AuctionItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="auction_images/", blank=True, null=True)
    end_date = models.DateTimeField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")


class Bid(models.Model):
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)


class MyProfile(models.Model):

    CHOICE_SET1 = (("Male", "Male"), ("Female", "Female"), ("Others", "Others"))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(max_length=10, null=True, blank=True)
    avatar = models.ImageField(upload_to="profile_pic", default="profile.png")
    gender = models.CharField(max_length=10, choices=CHOICE_SET1, default="Male")

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def create_MyProfile(sender, instance, created, **kwargs):
        if created:
            MyProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_MyProfile(sender, instance, **kwargs):
        instance.myprofile.save()


class Product(models.Model):
    CHOICE = (
        ("Grocery", "Grocery"),
        ("Mobiles", "Mobiles"),
        ("Clothes", "Clothes"),
        ("Electronics", "Electronics"),
        ("Home Appliances", "Home appliances"),
        ("Beauty", "Beauty"),
        ("Toys", "Toys"),
        ("Sports", "Sports"),
        ("Footwear", "Footwear"),
        ("Others", "Others"),
    )
    option = (("Sell", "Sell"), ("Rent", "Rent"))
    seller_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="%(class)s_seller",
    )
    name = models.CharField(max_length=50, blank=False, unique=True)
    desp = models.TextField(max_length=500, blank=False, null=True)
    category = models.CharField(max_length=50, blank=True, null=True, choices=CHOICE)
    minimum_price = models.IntegerField(
        blank=True, validators=[MinValueValidator(1)], default=1
    )
    start = models.DateTimeField(default=timezone.now, null=True)
    end = models.DateTimeField(default=timezone.now() + timezone.timedelta(hours=10))
    current_bid = models.IntegerField(default=0)
    product_sold = models.BooleanField(default=False)
    choose = models.CharField(max_length=50, blank=True, null=True, choices=option)
    bidder_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(class)s_bidder",
    )
    rent_status = models.BooleanField(default=False)
    rent_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(class)s_rent",
    )
    rent_price = models.IntegerField(default=0)
    rent_time_start = models.DateTimeField(null=True)
    rent_time_end = models.DateTimeField(null=True)
    rent_fine = models.IntegerField(default=0)
    # bid_only = models.BooleanField(default=False)
    # rent_only = models.BooleanField(default=False)
    # rent_and_bid = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)
