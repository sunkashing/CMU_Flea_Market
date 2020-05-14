import math
from functools import reduce

import pytz
import decimal
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.forms import modelformset_factory
from django.http import Http404, HttpResponse, JsonResponse
from django.http import HttpResponse, Http404
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
# from django.db.models import
from haystack.forms import SearchForm
from haystack.generic_views import SearchView
from paypal.standard.forms import PayPalPaymentsForm

# Create your views here.
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from flea_market.forms import LoginForm, ItemForm, MySearchForm

from flea_market.forms import LoginForm, RegistrationForm, UserForm
from flea_market.models import Customer, Item, Category, Transaction
from webapps import settings
import googlemaps

from flea_market.models import Image

cols = 5


def login_action(request):
    init_db()
    context = {}
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request=request, template_name='flea_market/login.html', context=context)

    form = LoginForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request=request, template_name='flea_market/login.html', context=context)

    user = authenticate(username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'])
    login(request, user)
    return redirect(reverse('search'))


@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


@ensure_csrf_cookie
@login_required
def index_action(request, category):
    context = {}
    context['category'] = category
    context['items'] = Item.objects.filter(available_status=True)
    for cat in CAT:
        if cat[0] == category:
            context['items'] = Item.objects.filter(available_status=True, cat_str=category)
            break

    context['customer'] = Customer.objects.get(user=request.user)
    items = sort_by_preference(context['items'], context['customer'])
    context['items'] = items
    context['categories'] = Category.objects.all()
    context['form'] = MySearchForm()
    context['item_nums'] = reduce(lambda x, y: x + y, [i.size for i in context['categories']])
    context['page'] = 'search'
    return render(request=request, template_name='flea_market/index.html', context=context)


def sort_by_price_asc(request, category):
    context = {}
    context['category'] = category
    context['customer'] = Customer.objects.get(user=request.user)
    context['categories'] = Category.objects.all()
    items = sort_by(request, category, 'price+')
    context['items'] = items
    context['form'] = MySearchForm()
    context['item_nums'] = reduce(lambda x, y: x + y, [i.size for i in context['categories']])
    context['page'] = 'search'
    return render(request=request, template_name='flea_market/index.html', context=context)


def sort_by_price_desc(request, category):
    context = {}
    context['category'] = category
    context['customer'] = Customer.objects.get(user=request.user)
    context['categories'] = Category.objects.all()
    items = sort_by(request, category, 'price-')
    context['items'] = items
    context['form'] = MySearchForm()
    context['item_nums'] = reduce(lambda x, y: x + y, [i.size for i in context['categories']])
    context['page'] = 'search'
    return render(request=request, template_name='flea_market/index.html', context=context)


def sort_by_distance(request, category):
    context = {}
    context['category'] = category
    context['customer'] = Customer.objects.get(user=request.user)
    context['categories'] = Category.objects.all()
    items = sort_by(request, category, 'distance')
    context['items'] = items
    context['form'] = MySearchForm()
    context['item_nums'] = reduce(lambda x, y: x + y, [i.size for i in context['categories']])
    context['page'] = 'search'
    return render(request=request, template_name='flea_market/index.html', context=context)


def sort_by_popularity(request, category):
    context = {}
    context['category'] = category
    context['customer'] = Customer.objects.get(user=request.user)
    context['categories'] = Category.objects.all()
    items = sort_by(request, category, 'popularity')
    context['items'] = items
    context['form'] = MySearchForm()
    context['item_nums'] = reduce(lambda x, y: x + y, [i.size for i in context['categories']])
    context['page'] = 'search'
    return render(request=request, template_name='flea_market/index.html', context=context)


def sort_by_preference(items, customer):
    res_head = []
    res_tail = []
    if customer.preferences is None:
        return [item for item in items]
    preferences = set([category.name for category in customer.preferences.all()])
    for item in items:
        if item.category.last().name in preferences:
            res_head.append(item)
        else:
            res_tail.append(item)
    res_head.extend(res_tail)
    return row_to_column_order(res_head)


def sort_by(request, category, rank_name):
    cat = Item.objects.filter(available_status=True)
    for c in CAT:
        if c[0] == category:
            cat = Item.objects.filter(available_status=True, cat_str=category)
            break

    if rank_name == 'distance':
        # print(to_Latlng(Customer.objects.get(user=request.user).geo_location))
        cat = sorted(cat,
                     key=lambda a: haversine_distance(a.geo_lat_long,
                                                      Customer.objects.get(user=request.user).geo_lat_long))
    elif rank_name == 'price+':
        cat = cat.order_by('price')
    elif rank_name == 'price-':
        cat = cat.order_by('-price')
    elif rank_name == 'popularity':
        cat = cat.order_by('-popularity')
    return row_to_column_order(cat)


def haversine_distance(origin, destination):
    lat1, lon1 = [float(i) for i in origin.strip().split(',')]
    lat2, lon2 = [float(i) for i in destination.strip().split(',')]
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d


@login_required()
def author_action(request):
    context = {}
    if request.method == 'GET':
        curr_user = Customer.objects.get(user=request.user)
        context['customer'] = curr_user
        context['user_Geo'] = curr_user.geo_location
        context['customer_Name'] = curr_user.user.first_name + " " + curr_user.user.last_name
        context['Customer_form'] = UserForm(initial={'customer_log': curr_user.customer_log})
        preferences = set([category.name for category in curr_user.preferences.all()])
        context['customer_log_replaced'] = curr_user.customer_log.replace('\n', '<br>')

        res_head = []
        bought_items= Item.objects.filter(buyer=curr_user)
        on_sale_items = Item.objects.filter(available_status=True, seller=curr_user)
        sold_items = Item.objects.filter(available_status=False, seller=curr_user)
        items = Item.objects.filter(available_status=True).exclude(seller=curr_user)
        for item in items:
            if item.category.last().name in preferences:
                res_head.append(item)
        recommend_items = row_to_column_order(res_head)
        context["bought_items"] = bought_items
        context['on_sale_items'] = on_sale_items
        context['sold_items'] = sold_items
        context['recommend_items'] = recommend_items
        context['categories'] = Category.objects.all()
        context['transaction_seller_list'] = Transaction.objects.filter(seller=curr_user, finishStatus=True).all()
        context['transaction_buyer_list'] = Transaction.objects.filter(buyer=curr_user, finishStatus=True).all()
        context['page'] = 'author'
        context['customer_log_replaced'] = curr_user.customer_log.replace('\n', '<br>')
    return render(request=request, template_name='flea_market/author.html', context=context)


@login_required()
def update_cust_info(request):
    context = {}
    curr_user = Customer.objects.get(user=request.user)
    Customer_form = UserForm(request.POST, request.FILES)
    on_sale_items = Item.objects.filter(available_status=True, seller=curr_user)
    sold_items = Item.objects.filter(available_status=False, seller=curr_user)
    context['on_sale_items'] = on_sale_items
    context['sold_items'] = sold_items
    context['transaction_seller_list'] = Transaction.objects.filter(seller=curr_user, finishStatus=True).all()
    context['transaction_buyer_list'] = Transaction.objects.filter(buyer=curr_user, finishStatus=True).all()
    bought_items = Transaction.objects.filter(buyer=curr_user, finishStatus=True).all()
    context["bought_items"] = bought_items
    context['categories'] = Category.objects.all()
    preferences = set([category.name for category in curr_user.preferences.all()])
    res_head = []
    items = Item.objects.filter(available_status=True).exclude(seller=curr_user)
    for item in items:
        if item.category.last().name in preferences:
            res_head.append(item)
    recommend_items = row_to_column_order(res_head)
    context['recommend_items'] = recommend_items

    if not Customer_form.is_valid():
        context['Customer_form'] = Customer_form
        curr_user.customer_log = Customer_form.cleaned_data['customer_log']
        curr_user.save()
        curr_user = Customer.objects.get(user=request.user)
        context['customer_log_replaced'] = curr_user.customer_log.replace('\n', '<br>')
        context['customer'] = curr_user
        context['user_Geo'] = curr_user.geo_location
        context['customer_Name'] = curr_user.user.first_name + " " + curr_user.user.last_name
        context['Customer_form'] = UserForm(initial={'customer_log': curr_user.customer_log})
        return render(request=request, template_name='flea_market/author.html', context=context)
    if not request.FILES:
        curr_user.customer_log = Customer_form.cleaned_data['customer_log']
        curr_user.save()
        context['Customer_form'] = UserForm({'customer_log': curr_user.customer_log})
    else:
        pic = Customer_form.cleaned_data['picture']
        curr_user.picture = Customer_form.cleaned_data['picture']
        if Customer_form.cleaned_data['customer_log']:
            curr_user.customer_log = Customer_form.cleaned_data['customer_log']
        curr_user.content_type = Customer_form.cleaned_data['picture'].content_type
        curr_user.save()

    curr_user = Customer.objects.get(user=request.user)
    context['customer'] = curr_user
    context['customer_log_replaced'] = curr_user.customer_log.replace('\n', '<br>')
    context['user_Geo'] = curr_user.geo_location
    context['customer_Name'] = curr_user.user.first_name + " " + curr_user.user.last_name
    context['Customer_form'] = UserForm(initial={'customer_log': curr_user.customer_log})
    context['customer_log_replaced'] = curr_user.customer_log.replace('\n', '<br>')
    context['page'] = 'author'
    return render(request=request, template_name='flea_market/author.html', context=context)


@login_required()
def update_location(request):
    context = {}
    if request.method == 'POST':
        newPlaceId = (request.POST['new_geo_location'])
        curr_user = Customer.objects.get(user=request.user)
        curr_user.geo_location = newPlaceId
        curr_user.save()
        on_sale_items = Item.objects.filter(available_status=True, seller=curr_user)
        sold_items = Item.objects.filter(available_status=False, seller=curr_user)
        context['on_sale_items'] = on_sale_items
        context['sold_items'] = sold_items
        context['customer_Name'] = curr_user.user.first_name + " " + curr_user.user.last_name
        context['user_Geo'] = curr_user.geo_location
        context['Customer_form'] = UserForm(initial={'customer_log': curr_user.customer_log})
        context['customer'] = curr_user
        
        preferences = set([category.name for category in curr_user.preferences.all()])
        res_head = []
        items = Item.objects.filter(available_status=True).exclude(seller=curr_user)
        for item in items:
            if item.category.last().name in preferences:
                res_head.append(item)
        recommend_items = row_to_column_order(res_head)
        context['recommend_items'] = recommend_items
        context['transaction_seller_list'] = Transaction.objects.filter(finishStatus=True, seller=curr_user).all()
        context['transaction_buyer_list'] = Transaction.objects.filter(finishStatus=True, buyer=curr_user).all()
        bought_items = Transaction.objects.filter(buyer=curr_user, finishStatus=True).all()
        context["bought_items"] = bought_items
        context['categories'] = Category.objects.all()
        context['page'] = 'author'

    return render(request=request, template_name='flea_market/author.html', context=context)


@login_required
def contact_seller_action(request, item_id):
    context = {}
    if request.method == 'GET':
        this_item = Item.objects.get(id=item_id)
        curr_user = this_item.seller
        on_sale_items = Item.objects.filter(available_status=True, seller=curr_user)
        sold_items = Item.objects.filter(available_status=False, seller=curr_user)
        context['categories'] = Category.objects.all()
        context['on_sale_items'] = on_sale_items
        context['sold_items'] = sold_items
        context['page_owner'] = curr_user
        context['customer'] = Customer.objects.get(user=request.user)
        context['user_Geo'] = curr_user.geo_location
        context['customer_Name'] = curr_user.user.first_name + " " + curr_user.user.last_name
        context['page'] = '#'
        context['user_email'] = curr_user.user.email
        return render(request=request, template_name='flea_market/otherUser.html', context=context)


@login_required
def contact_buyer_action(request, item_id):
    context = {}
    if request.method == 'GET':
        this_item = Item.objects.get(id=item_id)
        curr_user = this_item.buyer
        on_sale_items = Item.objects.filter(available_status=True, seller=curr_user)
        sold_items = Item.objects.filter(available_status=False, seller=curr_user)
        context['categories'] = Category.objects.all()
        context['on_sale_items'] = on_sale_items
        context['sold_items'] = sold_items
        context['page_owner'] = curr_user
        context['customer'] = Customer.objects.get(user=request.user)
        context['user_Geo'] = curr_user.geo_location
        context['customer_Name'] = curr_user.user.first_name + " " + curr_user.user.last_name
        context['page'] = '#'
        return render(request=request, template_name='flea_market/otherUser.html', context=context)


@login_required
def product_action(request, item_id):
    context = {}
    context['customer'] = Customer.objects.get(user=request.user)
    # From post page.
    context["item_id"] = item_id
    context['categories'] = Category.objects.all()

    context['page'] = '#'
    if request.method == 'GET':
        new_item = Item.objects.get(id=item_id)
        picture_id_list = []
        if Image.objects.filter(item=new_item):
            for image in Image.objects.filter(item=new_item).all():
                picture_id_list.append(image.id)
            context['picture_id_list'] = picture_id_list
        if new_item.seller_id != context['customer'].id:
            new_item.popularity = new_item.popularity + 1
            new_item.save()

        if Item.objects.get(id=item_id).available_status:
            item_owner = Item.objects.get(id=item_id).seller
        else:
            item_owner = Item.objects.get(id=item_id).buyer
            context['transaction'] = Transaction.objects.filter(product=new_item, finishStatus=True).last()
        context['curr_item'] = new_item
        context['item_owner'] = item_owner
        context['item_owner_Name'] = item_owner.user.first_name + " " + item_owner.user.last_name
        context['item_geo'] = item_owner.geo_location
        context['description_replaced'] = new_item.description.replace('\n', '<br>')
        return render(request=request, template_name='flea_market/product.html', context=context)
    elif request.method == 'POST':
        new_item = Item.objects.filter(id=item_id).last()
        new_item.name = request.POST['product_name']
        new_item.price = request.POST['product_price']
        new_item.description = request.POST['product_descpt']
        new_item.status = request.POST['product_status']
        new_item.save()
        if Image.objects.filter(item=new_item):
            picture_id_list = []
            for image in Image.objects.filter(item=new_item):
                picture_id_list.append(image.id)
            context['picture_id_list'] = picture_id_list
            # print('picture_list:', picture_id_list)
        item_owner = Item.objects.get(id=item_id).seller
        context['curr_item'] = new_item
        context['item_geo'] = item_owner.geo_location
        context['description_replaced'] = new_item.description.replace('\n', '<br>')
        return render(request=request, template_name='flea_market/product.html', context=context)


def follow_action(request):
    curr_customer = Customer.objects.get(user=request.user)
    request_item_id = int(request.GET['item_id'])
    item_set = set([item.id for item in curr_customer.follow_item.all()])
    if request_item_id in item_set:
        curr_customer.follow_item.remove(Item.objects.get(id=request_item_id))
        follow_status = 'false'
    else:
        curr_customer.follow_item.add(Item.objects.get(id=request_item_id))
        follow_status = 'true'
    curr_customer.save()

    return JsonResponse({'follow_status': follow_status, 'item_id': request_item_id})


def favorite_action(request):
    context = {}
    context['category'] = '*'
    context['categories'] = Category.objects.all()
    context['customer'] = Customer.objects.get(user=request.user)
    context['item_nums'] = reduce(lambda x, y: x + y, [i.size for i in context['categories']])
    context['favorite_items'] = context['customer'].follow_item.all()

    context['form'] = MySearchForm()
    context['page'] = 'favorite'
    return render(request=request, template_name='flea_market/favorite.html', context=context)



@login_required
def post_action(request, id):
    context = {}
    curr_user = Customer.objects.filter(id=id).last()
    context['customer'] = Customer.objects.get(user=request.user)
    # Render to post page at the first time.
    if request.method == 'GET':
        form = ItemForm()
        context['post_form'] = form
        context['page'] = 'post'
        return render(request, 'flea_market/post.html', context)
    form = ItemForm(request.POST, request.FILES)
    context['post_form'] = form
    if not form.is_valid():
        context['post_form'] = form
        return render(request=request, template_name='flea_market/post.html', context=context)
    pic = request.FILES.getlist('itemPicture')[0]  # First Picture for display at index page.
    picture_list = request.FILES.getlist('itemPicture')  # All photos for item.
    category = Category.objects.get(name=form.cleaned_data.get('itemCategory'))
    new_product = Item(seller=curr_user,
                       name=form.cleaned_data.get('itemName'),
                       cat_str=form.cleaned_data.get('itemCategory'),
                       description=form.cleaned_data.get('itemDescription'),
                       picture=pic,
                       price=form.cleaned_data.get('itemPrice'),
                       available_status=True,
                       popularity=0,
                       status=decimal.Decimal(float(form.cleaned_data.get('itemStatus'))),
                       )
    # Save the new model and update the category.
    new_product.geo_location = Customer.objects.get(user=request.user).geo_location
    new_product.geo_lat_long = Customer.objects.get(user=request.user).geo_lat_long
    new_product.save()
    new_product.category.add(category)
    category.size += 1
    new_product.save()
    category.save()
    context['curr_item'] = new_product
    # add picture list model
    if len(picture_list) >= 2:
        picture_id_list = []
        for pic in picture_list:
            new_image = Image(item=new_product, file=pic)
            new_image.save()
            picture_id_list.append(new_image.id)
        context['picture_id_list'] = picture_id_list
    context['page'] = '#'

    return render(request=request, template_name='flea_market/product.html', context=context)


def register_action(request):
    context = {}
    context['categories'] = Category.objects.all()
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request=request, template_name='flea_market/register.html', context=context)

    form = RegistrationForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request=request, template_name='flea_market/register.html', context=context)

    new_user = User.objects.create_user(username=form.cleaned_data.get('username'),
                                        password=form.cleaned_data.get('password'),
                                        email=form.cleaned_data.get('email'),
                                        first_name=form.cleaned_data.get('first_name'),
                                        last_name=form.cleaned_data.get('last_name'))
    new_user.save()
    new_customer = Customer(user=new_user,
                            age=birthday_to_age(form.cleaned_data.get('birthday')),
                            geo_location=request.POST['hidden_geo_location'],
                            geo_lat_long=request.POST['hidden_geo_lat_long'])

    new_customer.save()
    add_preferences(form.cleaned_data.get('preferences'), new_customer)

    new_user = authenticate(username=form.cleaned_data.get('username'),
                            password=form.cleaned_data.get('password'))
    login(request, new_user)
    context['full_name'] = User.get_full_name(new_user)
    return redirect(reverse('index', args='*'))


@login_required
def delete_action(request, id):
    item = Item.objects.filter(id=id).last()
    if item:
        try:
            transactions = Transaction.objects.get(product=item, finishStatus=False).all()
            for transaction in transactions:
                transaction.delete()
        except:
            pass
        category = Category.objects.get(name=item.cat_str)
        category.size -= 1
        category.save()
        item.delete()
    return redirect(reverse('index', args='*'))


@login_required
def get_customer_photo(request, id):
    customer = get_object_or_404(Customer, user_id=id)

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not customer.picture:
        raise Http404

    return HttpResponse(customer.picture, content_type=customer.content_type)


@login_required
def get_item_photo(request, id):
    item = get_object_or_404(Item, id=id)
    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not item.picture:
        raise Http404

    return HttpResponse(item.picture, content_type=item.content_type)


@login_required
def get_item_photo_list(request, id):
    image = Image.objects.filter(id=id).last()

    # Maybe we don't need this check as form validation requires a picture be uploaded.
    # But someone could have delete the picture leaving the DB with a bad references.
    if not image.file:
        raise Http404

    return HttpResponse(image.file)


def birthday_to_age(birthday):
    today = timezone.now()
    duration = today - birthday
    duration_in_s = duration.total_seconds()
    age = divmod(duration_in_s, 31536000)[0]
    return int(age)


def add_preferences(preferences, customer):
    lst = preferences.strip().split(', ')
    for p in lst:
        try:
            cat = Category.objects.get(name=p)
        except ObjectDoesNotExist:
            print("Category doesn't exist.")
        customer.preferences.add(cat)


def row_to_column_order(items):
    res = []
    items_list = [i for i in items]
    if len(items_list) % cols != 0:
        for i in range(cols - len(items_list) % cols):
            items_list.append('null')

    for x in range(cols):
        for i, item in enumerate(items_list):
            if i % cols == x:
                res.append(item)
    return res


def get_category_photo(request):
    return None


@login_required
def order_action(request, item_id):
    context = {}
    curr_product = get_object_or_404(Item, id=item_id)
    if not curr_product.available_status:
        return render(request, 'payment/canceled.html', {})
    owner = curr_product.seller
    customer = get_object_or_404(Customer, id=request.user.id)
    new_transaction = Transaction(product=curr_product, seller=owner, buyer=customer, finishStatus=False)
    new_transaction.save()
    paypal_dict = {'business': settings.PAYPAL_RECEIVER_EMAIL,
                   'amount': '%.2f' % curr_product.price.quantize(decimal.Decimal('.01')),
                   'item_name': 'Order {}'.format(curr_product.name), 'invoice': str(new_transaction.id),
                   'currency_code': 'USD',
                   'notify_url': 'https://cmufleamarkets.com{}'.format(reverse('paypal-ipn')),
                   'return_url': 'https://cmufleamarkets.com/flea_market/payment/payment_done/{}'.format(str(new_transaction.id)),
                   'cancel_return': 'https://cmufleamarkets.com/{}'.format(reverse('payment_cancel')), }

    form = PayPalPaymentsForm(initial=paypal_dict)
    context['page'] = '#'
    return render(request, 'payment/process.html',
                  {'order': curr_product, 'form': form, 'customer': customer})


@login_required
@csrf_exempt
def payment_done(request, tran_id):
    curr_tran = Transaction.objects.filter(id=tran_id).last()
    if not curr_tran:
        # No such transaction
        return payment_canceled()
    if curr_tran.finishStatus:
        # Has been sold out
        return payment_canceled()
    curr_tran.finishStatus = True
    curr_tran.save()
    curr_product = curr_tran.product
    curr_product.available_status = False
    cat = Category.objects.get(name=curr_product.cat_str)
    cat.size = cat.size - 1
    cat.save()
    curr_product.buyer = curr_tran.buyer
    curr_product.save()
    context = {}
    context['page'] = '#'
    context['customer'] = curr_tran.buyer
    return render(request, 'payment/done.html', context)


@login_required
@csrf_exempt
def payment_canceled(request):
    context = {}
    context['page'] = '#'
    context['customer'] = Customer.objects.filter(user=request.user).last()
    return render(request, 'payment/canceled.html', context)


def to_Latlng(place_id):
    gmaps = googlemaps.Client(key=settings.API_KEY)
    # Geocoding an address
    geocode_result = gmaps.reverse_geocode(place_id)
    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']
    latlng = [lat, lng]
    return latlng


CAT = [('Clothes', 'person'),
       ('Electronic Devices', 'power'),
       ('Cars', 'drive_eta'),
       ('House Leasing', 'house'),
       ('Books', 'menu_book')]

users = [
    # CMU
    {'username': 'Nishino_Nanase', 'password': 'a', 'email': 'a@a', 'first_name': 'Nanase', 'last_name': 'Nishino',
     'birthday': '1994-5-25', 'geo_location': 'ChIJkZqj4iPyNIgRkRiPR6mXTt4', 'geo_lat_long': '40.442723,-79.942955',
     'preferences': 'Clothes, Electronic Devices',
     'picture': 'Nishino_Nanase.jpg'},
    # Panda
    {'username': 'Shiraishi_Mai', 'password': 'a', 'email': 'a@a', 'first_name': 'Mai', 'last_name': 'Shiraishi',
     'birthday': '1992-8-20', 'geo_location': 'ChIJMWsnJADyNIgRw4CWZZRWuTY', 'geo_lat_long': '40.437879,-79.921096',
     'preferences': 'Clothes, House Leasing, Electronic Devices, Cars, Books',
     'picture': 'Shiraishi_Mai.jpg'},
    # Point State Park Fountain
    {'username': 'Yoda_Yuki', 'password': 'a', 'email': 'a@a', 'first_name': 'Yuki', 'last_name': 'Yoda',
     'birthday': '1998-8-10', 'geo_location': 'ChIJXzT5vqv2NIgRfqEmldPesjc', 'geo_lat_long': '40.441790,-80.012732',
     'preferences': 'House Leasing, Electronic Devices, Clothes',
     'picture': 'Yoda_Yuki.jpg'},
    # UPMC Children Hospital
    {'username': 'Saito_Asuka', 'password': 'a', 'email': 'a@a', 'first_name': 'Asuka', 'last_name': 'Saito',
     'birthday': '2000-5-25', 'geo_location': 'ChIJi5Ly2wFiNIgRP9zMK-dVM5E',  'geo_lat_long': '40.467097,-79.953053',
     'preferences': 'Cars',
     'picture': 'Saito_Asuka.jpg'}]

items = [
    # Books
    {'name': 'Watashi no Koto', 'seller': 'Nishino_Nanase', 'category': 'Books',
     'description': "Nishino Nanase's 2nd album.", 'price': '16.23',
     'picture': 'Nishino_Nanase_WatashiNoKoto.jpg', 'status': '4.7'},
    {'name': 'Passport', 'seller': 'Shiraishi_Mai', 'category': 'Books',
     'description': "Shiraishi Mai's 2nd album.",
     'price': '18.25',
     'picture': 'Shiraishi_Mai_Passport.jpg', 'status': '4.5'},
    {'name': 'Muguchi no Jikan', 'seller': 'Yoda_Yuki', 'category': 'Books',
     'description': "Yoda Yuki's 1st album.", 'price': '18.76',
     'picture': 'Yoda_Yukii_MuguchiNoJikan.jpg', 'status': '5.0'},
    # Clothes
    {'name': 'Nogizaka 6th Seifuku', 'seller': 'Shiraishi_Mai', 'category': 'Clothes',
     'description': "Nogizaka's 6th single's uniform", 'price': '99.97',
     'picture': 'Nogizaka_6th_Seifuku.jpg', 'status': '4.5'},
    {'name': 'Nogizaka 8th Seifuku', 'seller': 'Nishino_Nanase', 'category': 'Clothes',
     'description': "Nogizaka's 8th single's uniform", 'price': '99.98',
     'picture': 'Nogizaka_8th_Seifuku.jpg', 'status': '4.5'},
    {'name': 'Nogizaka 9th Seifuku', 'seller': 'Nishino_Nanase', 'category': 'Clothes',
     'description': "Nogizaka's 9th single's uniform", 'price': '99.98',
     'picture': 'Nogizaka_9th_Seifuku.jpg', 'status': '4.5'},
    {'name': 'Nogizaka 11th Seifuku', 'seller': 'Nishino_Nanase', 'category': 'Clothes',
     'description': "Nogizaka's 11th single's uniform", 'price': '99.98',
     'picture': 'Nogizaka_11th_Seifuku.jpg', 'status': '4.5'},
    {'name': 'Nogizaka 13rd Seifuku', 'seller': 'Nishino_Nanase', 'category': 'Clothes',
     'description': "Nogizaka's 13rd single's uniform", 'price': '99.99',
     'picture': 'Nogizaka_13rd_Seifuku.jpg', 'status': '4.7'},
    {'name': 'Nogizaka 15th Seifuku', 'seller': 'Saito_Asuka', 'category': 'Clothes',
     'description': "Nogizaka's 15th single's uniform", 'price': '99.98',
     'picture': 'Nogizaka_15th_Seifuku.jpg', 'status': '4.5'},
    {'name': 'Nogizaka 20th Seifuku', 'seller': 'Shiraishi_Mai', 'category': 'Clothes',
     'description': "Nogizaka's 20th single's uniform", 'price': '99.98',
     'picture': 'Nogizaka_20th_Seifuku.jpg', 'status': '4.5'},
    {'name': 'Nogizaka 21st Seifuku', 'seller': 'Saito_Asuka', 'category': 'Clothes',
     'description': "Nogizaka's 21st single's uniform", 'price': '99.98',
     'picture': 'Nogizaka_21st_Seifuku.jpg', 'status': '4.5'},
    {'name': 'Nogizaka 22nd Seifuku', 'seller': 'Nishino_Nanase', 'category': 'Clothes',
     'description': "Nogizaka's 22nd single's uniform", 'price': '99.98',
     'picture': 'Nogizaka_22nd_Seifuku.jpg', 'status': '4.9'},
    {'name': 'Nogizaka 23rd Seifuku', 'seller': 'Saito_Asuka', 'category': 'Clothes',
     'description': "Nogizaka's 23rd single's uniform", 'price': '99.98',
     'picture': 'Nogizaka_23rd_Seifuku.jpg', 'status': '4.5'},
    # Electronic Devices
    {'name': 'iPhone7 32GB Gold', 'seller': 'Yoda_Yuki', 'category': 'Electronic Devices',
     'description': 'iPhone 7 32GB Gold', 'price': '599.99',
     'picture': 'iPhone7_32GB_Gold.jpg', 'status': '5.0'},
    {'name': 'iPhone11 Pro Max 64GB Midnight Green', 'seller': 'Yoda_Yuki', 'category': 'Electronic Devices',
     'description': 'iPhone 11 Pro Max 64GB Midnight Green', 'price': '1050',
     'picture': 'iPhone11_Pro_Max_64GB_Midnight_Green.jpg', 'status': '4.6'},
    {'name': 'iPhoneXR 64GB Red', 'seller': 'Nishino_Nanase', 'category': 'Electronic Devices',
     'description': 'iPhone XR 64GB Red', 'price': '599',
     'picture': 'iPhoneXR_64GB_Red.jpg', 'status': '5.0'},
]


def init_db():
    if not Category.objects.exists():
        for category in CAT:
            cat = Category()
            cat.name = category[0]
            cat.size = 0
            cat.icon_name = category[1]
            cat.save()

    if not User.objects.exists() and not Customer.objects.exists():
        for user in users:
            new_user = User.objects.create_user(username=user['username'],
                                                password=user['password'],
                                                email=user['email'],
                                                first_name=user['first_name'],
                                                last_name=user['last_name'])
            new_user.save()
            new_customer = Customer(user=new_user,
                                    age=birthday_to_age(
                                        datetime.strptime(user['birthday'], '%Y-%m-%d').replace(tzinfo=pytz.UTC)),
                                    geo_location=user['geo_location'],
                                    geo_lat_long=user['geo_lat_long'])
            new_customer.picture.name = settings.MEDIA_ROOT + user['picture']
            new_customer.save()
            add_preferences(user['preferences'], new_customer)

    if not Item.objects.exists():
        for item in items:
            user = User.objects.get(username=item['seller'])
            customer = Customer.objects.get(user=user)
            category = Category.objects.get(name=item['category'])
            new_product = Item(seller=customer,
                               buyer=None,
                               name=item['name'],
                               cat_str=item['category'],
                               description=item['description'],
                               price=decimal.Decimal(float(item['price'])),
                               status=decimal.Decimal(float(item['status'])),
                               geo_location=customer.geo_location,
                               geo_lat_long=customer.geo_lat_long,
                               available_status=True,
                               popularity=0)
            new_product.picture.name = settings.MEDIA_ROOT + item['picture']
            new_product.save()
            new_product.category.add(category)
            category.size += 1
            category.save()


class MySearchIndex(SearchView):
    template_name = 'flea_market/index.html'
    form_class = MySearchForm
    user = None
    items = None
    search_text = None

    def get_context_data(self, *args, **kwargs):
        context = super(MySearchIndex, self).get_context_data(*args, **kwargs)
        # do something
        context['category'] = '*'
        context['categories'] = Category.objects.all()
        context['customer'] = self.user
        context['item_nums'] = reduce(lambda x, y: x + y, [i.size for i in context['categories']])
        context['page'] = 'search'
        if self.search_text != '':
            context['items'] = sort_by_preference([q.object for q in self.get_queryset().load_all()], context['customer'])
            self.search_text = None
        else:
            context['items'] = sort_by_preference(self.items, context['customer'])
        return context

    def get(self, request, *args, **kwargs):
        self.user = Customer.objects.get(user=request.user)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            self.search_text = form.cleaned_data.get(self.search_field)
            if self.search_text == '':
                self.items = Item.objects.filter(available_status=True)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


