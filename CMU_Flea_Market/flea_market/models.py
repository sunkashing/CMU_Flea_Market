from django.contrib.auth.models import User
from django.db import models
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=30)
    size = models.IntegerField(default=0)
    icon_name = models.CharField(max_length=30)

    def __str__(self):
        return '{Category: ' + self.name + ', ' + 'Size: ' + str(self.size) + '}'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    age = models.IntegerField()
    customer_log = models.CharField(blank=True, max_length=200)
    geo_location = models.CharField(max_length=100, default="")
    geo_lat_long = models.CharField(max_length=100, default="")
    preferences = models.ManyToManyField(to='Category', blank=True)
    follow_item = models.ManyToManyField(to='Item', blank=True)
    picture = models.FileField(blank=True)
    content_type = models.CharField(blank=True, max_length=100, default='DEFAULT VALUE')

    def __str__(self):
        return 'age=' + str(self.age) + ' ,customer_log="' + str(self.customer_log) + ' ,geo_location =' + str(
            self.geo_location) + ', preference =' + str(self.preferences) + ', picture = ' + str(self.picture)


class Item(models.Model):
    seller = models.ForeignKey(Customer, related_name='seller', on_delete=models.PROTECT, blank=True)
    buyer = models.ForeignKey(Customer, related_name='buyer', on_delete=models.PROTECT, blank=True, null=True)
    category = models.ManyToManyField(to='Category')
    name = models.CharField(max_length=100, default='')
    cat_str = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=300, default='')
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.DecimalField(max_digits=3, decimal_places=2, blank=True)
    geo_location = models.CharField(max_length=100, default="")
    geo_lat_long = models.CharField(max_length=100, default="")
    available_status = models.BooleanField()
    popularity = models.IntegerField(default=0)


class Transaction(models.Model):
    product = models.ForeignKey(Item, related_name='transaction_product', on_delete=models.PROTECT, blank=True)
    seller = models.ForeignKey(Customer, related_name='transaction_seller', on_delete=models.PROTECT, blank=True)
    buyer = models.ForeignKey(Customer, related_name='transaction_buyer', on_delete=models.PROTECT, blank=True,
                              null=True)
    startTime = models.DateTimeField(auto_now_add=True)
    endTime = models.DateTimeField(auto_now=True)
    finishStatus = models.BooleanField()

    def __str__(self):
        return 'product:' + self.product.name + ',seller:' + self.seller.User.name + ',buyer:' + self.buyer.User.name


# Image model for item photo list link to each Item
class Image(models.Model):
    file = models.FileField(blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

