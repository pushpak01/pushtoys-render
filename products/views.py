from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Product
from .forms import ProductSearchForm, NewsletterForm
from django.contrib import messages


def newsletter_subscribe(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for subscribing!")
            return redirect("home")  # change 'home' to your homepage name
        else:
            messages.error(request, "This email is already subscribed or invalid.")



def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True).order_by('-created_at')

    # Initialize search form with GET parameters
    search_form = ProductSearchForm(request.GET or None)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Apply search filters if form is valid
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        selected_category = search_form.cleaned_data.get('category')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        in_stock = search_form.cleaned_data.get('in_stock')

        if query:
            products = products.filter(
                Q(name__icontains=query)
            )
        if selected_category:
            products = products.filter(category=selected_category)
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        if in_stock:
            products = products.filter(stock__gt=0)

    # Moved pagination outside of search_form.is_valid() block
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'categories': categories,
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, pk, slug=None):
    product = get_object_or_404(
        Product,
        pk=pk,
        available=True,
    )
    # Optional: Add related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(pk=pk)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

def home(request):
    featured_products = Product.objects.filter(is_featured=True, available=True)[:8]
    return render(request, "home.html", {
        "featured_products": featured_products,
    })





