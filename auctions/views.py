from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import AuctionItem, Bid
from django.views import View
from django.utils.decorators import method_decorator
from .forms import LoginForm, ProductForm, BidsForm, SignupForm
from .models import Product
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import HttpResponse

class Home(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, "auctions/home.html")


class LoginView(View):

    def post(self, request, *args, **kwargs):
        # form = LoginForm(request.POST)
        username = request.POST["username"]
      
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
       
        if user is not None:
            if user.is_active:
                login(request, user)
                return render(request, "auctions/home1.html")
            else:
                return HttpResponse("Please! Verify your Email first")
        else:
            messages.error(request, "Username or Password is incorrect")
            return redirect("login")

    def get(self, request, *args, **kwagrs):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            form = LoginForm()
        return render(request, "auctions/login.html", {"form": form})


class SignUp(View):
    form_class = SignupForm
    def get(self, request, *args, **kwargs):
        # Handle GET request - show signup form
        
        form = self.form_class()
        return render(request, "auctions/signup.html", {"form": form})

    def post(self, request, *args, **kwargs):
        # Handle POST request - form submission
        if request.method == 'POST':
            form = self.form_class(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = True  # Deactivate account until email verification
                user.save()

            # Email verification setup
            # current_site = get_current_site(request)
            # subject = "Your Online-Auction Email Verification"
            # message = render_to_string(
            #     "auctions/acc_active_email.html",
            #     {
            #         "user": user,
            #         "domain": current_site.domain,
            #         "uid": urlsafe_base64_encode(force_bytes(user.pk)).decode("utf-8"),
            #         "token": account_activation_token.make_token(user),
            #     },
            # )
            # from_email = settings.EMAIL_HOST_USER
            # to_email = [user.email]

            # send_mail(subject, message, from_email, to_email, fail_silently=False)
            # Success message to the user
                messages.success(
                    request, "Please confirm your email to complete registration."
                )
                return redirect("home")  # Redirect to home or login page
            else:
                # form.errors.clear()  # Clear form errors
                print("Form validation failed with errors:", form.errors)
            # If form is invalid, re-render the signup page with errors
        else:        
            form = self.form_class(request.POST)
        return render(request, "auctions/signup.html", {"form": form})


def search(request):
    print("inside ajax")
    text = request.GET.get("value1", "")
    k = Product.objects.filter(category__iexact=text).values_list("name", "id")
    j = Product.objects.filter(name__iexact=text).values_list("name", "id")
    data = {}
    if j:

        data["products"] = list(j)
    else:

        data["products"] = list(k)

    return JsonResponse(data)


def options(request):
    if request.is_ajax:
        word = request.GET.get("value1", "")
        item = Product.objects.filter(category__istartswith=word)
        item1 = Product.objects.filter(name__istartswith=word)
        results = []
        for i in item:
            product = {}

            product["label"] = i.category

            product["value"] = i.category
            if product not in results:
                results.append(product)

        for j in item1:
            product = {}
            product["label"] = j.name
            product["value"] = j.name
            results.append(product)

        product_json = json.dumps(results)
    else:
        product_json = "fail"
    mimetype = "application/json"
    return HttpResponse(product_json, mimetype)


class RentView(View):
    template_name = 'auctions/rent_view.html'
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        product = Product.objects.get(id=kwargs['pk'])
        if product.current_bid==0:
            context = {
                'product': product,
                      }
            return render(request, self.template_name, context)

class RentProduct(View):

    template_name = "auctions/rent_products.html"
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        p = Product.objects.get(id=kwargs['pk'])
        if p.rent_status == 'False':
            context = {
                'name': p.name,
                'desp': p.desp,
                'category': p.category,
                'rent': p.rent_price,
                'owner': p.seller_id,
                }
            return render(request, self.template_name, context)
        else:
            context = {
                'name': p.name,
                'desp': p.desp,
                'category': p.category,
                'rent': p.rent_price,
                'owner': p.seller_id,
                'temp_onwer': p.rent_id
                      }
            return render(request, "auctions/product_sold.html", context)

class LogoutView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have been successfully Logged Out!!')
        return redirect('home')             


class Activate(View):

    def get(self, request, token, uidb64):

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, "EMAIL VERIFIED!!!! HURRAY....")
            return redirect("home")

        else:
            messages.error(
                request, "Activation Email Link is Invalid.Please try again!!"
            )
            return redirect("home")


class ProfileView(View):

    @method_decorator(login_required)
    def get(self, request, user_id, *args, **kwargs):
        user_object = User.objects.get(id=user_id)
        context = {"user": user_object}
        return render(request, "auctions/profile.html", context)


class ProfileEdit(View):

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        user_obj = request.user.id
        form = EditProfileForm(
            request.POST, request.FILES, instance=request.user.myprofile
        )
        if form.is_valid():
            form.save()
            return redirect("profile", user_obj)

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = EditProfileForm(instance=request.user.myprofile)
        context = {
            "form": form,
        }
        return render(request, "auctions/edit_profile.html", context)


class AddProduct(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = ProductForm()
        context = {"form": form}
        return render(request, "auctions/product_form.html", context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):

        form = ProductForm(request.POST)
        if form.is_valid():
            print(10)
            product_item = form.save(commit=False)
            print(11)
            product_item.seller_id = request.user
            product_item.save()
            print(12)

        return redirect("products_listed")


class BuyerView(View):

    template_name = "auctions/buyer.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {
            "product_list": Product.objects.order_by("id"),
        }
        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):

        sort_by = request.POST["sort"]
        if sort_by == "new_to_old":
            context = {
                "product_list": Product.objects.order_by("-start"),
            }

        elif sort_by == "old_to_new":
            context = {
                "product_list": Product.objects.order_by("start"),
            }

        elif sort_by == "high_to_low":
            context = {
                "product_list": Product.objects.order_by("-current_bid"),
            }

        elif sort_by == "low_to_high":
            context = {
                "product_list": Product.objects.order_by("current_bid"),
            }

        elif sort_by == "unsold":
            context = {
                "product_list": Product.objects.filter(product_sold="False").order_by(
                    "?"
                ),
            }

        return render(request, self.template_name, context)


# --------------------------USER CAN SEE DETAILS OF A PARTICULAR PRODUCT AND CAN BID------------------------------------


class ProductView(View):

    template_name = "auctions/product.html"

    @method_decorator(login_required)
    def get(self, request, p_id, *args, **kwargs):
        time_now = timezone.now()
        p = Product.objects.get(pk=p_id)
        if time_now < p.end:
            form = BidsForm()
            context = {
                "name": p.name,
                "desp": p.desp,
                "start": p.start,
                "minbid": p.minimum_price,
                "end": p.end,
                "category": p.category,
                "currentbid": p.current_bid,
                "form": form,
                "id": p.id,
            }
            return render(request, self.template_name, context, p_id)
        else:
            p.product_sold = "True"
            p.save()
            context = {
                "name": p.name,
                "desp": p.desp,
                "start": p.start,
                "minbid": p.minimum_price,
                "end": p.end,
                "category": p.category,
                "currentbid": p.current_bid,
                "buyer": p.bidder_id,
            }

            return render(request, "auctions/product_sold.html", context, p_id)

    @method_decorator(login_required)
    def post(self, request, p_id, *args, **kwargs):
        product = Product.objects.get(pk=p_id)
        form = BidsForm(request.POST)
        if form.is_valid():
            product.bidder_id = request.user

            if product.bidder_id == product.seller_id:
                redirect("home")

            else:

                if product.minimum_price < int(
                    (request.POST["bidder_amount"])
                ) and product.current_bid < int((request.POST["bidder_amount"])):
                    product.current_bid = int((request.POST["bidder_amount"]))
                    product.save()

        context = {
            "name": product.name,
            "desp": product.desp,
            "start": product.start,
            "minbid": product.minimum_price,
            "end": product.end,
            "category": product.category,
            "currentbid": product.current_bid,
            "form": form,
        }
        return render(request, self.template_name, context, p_id)


# ------------------USER CAN SEE WHAT ALL PRODUCTS HAVE BEEN LISTED FOR SALE-------------------------------------------


class ProductListed(View):

    template_name = "auctions/products_listed.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_id = request.user
        product = Product.objects.filter(seller_id=user_id)
        context = {"product": product}

        return render(request, self.template_name, context)


# ---------------------USER CAN SEE THE BIDS(LIVE) IN WHICH HE/SHE IS CURRENTLY WINNING---------------------------------


class BidsCurrentlyWinning(View):

    template_name = "auctions/bids_currently_winning.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_id = request.user
        product = Product.objects.filter(bidder_id=user_id, product_sold=False)
        context = {"product": product}

        return render(request, self.template_name, context)


# -------------------USER CAN VIEW ALL THE BIDS HE/SHE HAS WON TILL NOW------------------------------------------------


class BidsWon(View):
    template_name = "auctions/bids_won.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_id = request.user
        product = Product.objects.filter(bidder_id=user_id, product_sold=True)
        context = {"product": product}
        return render(request, self.template_name, context)


# ----------------------PRODUCTS AVAILABLE FOR RENT---------------------------------------------------------------------


class RentView(View):
    template_name = "auctions/rent_view.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        rent_product_list = Product.objects.filter(current_bid=0)

        context = {
            "rent_product_list": rent_product_list,
        }

        return render(request, self.template_name, context)


# ----------------------------RENT PRODUCT HERE--------------------------------------------------------------------------


class RentProductView(View):
    template_name = "auctions/rent_products.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        rent_product = Product.objects.get(id=kwargs["pk"])
        if rent_product.rent_status == False:
            context = {
                "name": rent_product.name,
                "desp": rent_product.desp,
                "category": rent_product.category,
                "rent": rent_product.rent_price,
                "owner": rent_product.seller_id,
            }
            return render(request, self.template_name, context)

        else:

            context = {
                "name": rent_product.name,
                "desp": rent_product.desp,
                "category": rent_product.category,
                "rent": rent_product.rent_price,
                "owner": rent_product.seller_id,
                "temp_onwer": rent_product.rent_id,
            }

            return render(request, "auctions/product_already_rented.html", context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):

        rent_product = Product.objects.get(id=kwargs["pk"])
        user_id = request.user
        rent = request.POST["rented"]

        if rent == "product_rented":

            if rent_product.seller_id == user_id:
                redirect("home")

            else:
                time_now = timezone.now()
                return_time = timezone.now() + timezone.timedelta(days=1)
                rent_product.save(commit=False)
                rent_product.rent_id = user_id
                rent_product.rent_status = True
                rent_product.rent_time_start = time_now
                rent_product.rent_time_end = return_time
                rent_product.save()

        return redirect("products_rented")


# ------------------------------------PRODUCTS RENTED-------------------------------------------------------------------


class ProductsRented(View):
    template_name = "auctions/products_rented.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_id = request.user
        product = Product.objects.filter(rent_id=user_id)
        # time_now = timezone.now()
        # time_end = product.rent_time_end
        #
        # if time_now > time_end :
        #     product.save(commit=False)
        #     product.rent_fine = 10
        #     product.save()
        context = {"product": product}

        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return_product = Product.objects.get(id=kwargs["pk"])
        user_id = request.user
        return_pro = request.POST["return"]
        if return_pro == "return_product":
            return_product.rent_id = NULL
            return_product.rent_status = False
            return_product.save()

        return redirect("home")


def item_list(request):
    items = AuctionItem.objects.all()
    return render(request, "auctions/item_list.html", {"items": items})


def item_detail(request, item_id):
    item = get_object_or_404(AuctionItem, pk=item_id)
    return render(request, "auctions/item_detail.html", {"item": item})


@login_required
def place_bid(request, item_id):
    item = get_object_or_404(AuctionItem, pk=item_id)
    if request.method == "POST":
        amount = request.POST.get("amount")
        if float(amount) > item.current_bid:
            bid = Bid(item=item, bidder=request.user, amount=amount)
            bid.save()
            item.current_bid = amount
            item.save()
    return redirect("item_detail", item_id=item.id)
