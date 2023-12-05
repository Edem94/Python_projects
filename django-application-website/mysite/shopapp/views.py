"""
There are different views in this module.

Different view for the online-shop: for products, orders etc.
"""
from timeit import default_timer
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.syndication.views import Feed
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Order, ProductImage
from .forms import ProductForm
from .serializers import ProductSerializer, OrderSerializer
from .common import save_csv_products
from drf_spectacular.utils import extend_schema, OpenApiResponse
from csv import DictWriter
import logging

log = logging.getLogger(__name__)


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Set of view for the actions with Product.

    Full CRUD for product entities
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, return 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field) for field in fields
            })

        return response

    @action(
        detail=False,
        methods=['post'],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES['file'].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


@extend_schema(description="Order views CRUD")
class OrderViewSet(ModelViewSet):
    """
    Set of view for the actions with Order.

    Full CRUD for order entities
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]
    search_fields = ["delivery_address", "promocode"]
    filterset_fields = [
        "delivery_address",
        "promocode",
        "user",
        "products",
    ]
    ordering_fields = [
        "delivery_address",
        "user",
        "created_at",
    ]

    @extend_schema(
        summary="Get one order by ID",
        description="Retrieves **order**, return 404 if not found",
        responses={
            200: OrderSerializer,
            404: OpenApiResponse(description="Empty response, order by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class ShopIndexView(View):
    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            'time_running': default_timer(),
            'products': products,
            'items': 5,
        }
        print('Shop index context', context)
        log.debug('Products for shop index: %s', products)
        log.info('Rendering shop index')
        return render(request, 'shopapp/shop-index.html', context=context)


class ProductDetailsView(DetailView):
    template_name = "shopapp/products-details.html"
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.is_authenticated

    model = Product
    success_url = reverse_lazy("shopapp:products_list")
    form_class = ProductForm

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        form.instance.created_by = self.request.user
        form.save()
        return response


class ProductUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_authenticated

    def get_queryset(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return super().get_queryset(*args, **kwargs).filter(
                created_by=self.request.user
            )
        return super().get_queryset(*args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
        .all()
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'shopapp.view_order'
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = 'products_data_export'
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by('pk').all()
            products_data = [
                {
                    'pk': product.pk,
                    'name': product.name,
                    'price': product.price,
                    'archived': product.archived
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        return JsonResponse({'products': products_data})


class OrdersDataExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by('pk').all()
        orders_data = [
            {
                'pk': order.pk,
                'address': order.delivery_address,
                'promocode': order.promocode,
                'user': order.user.pk,
                'products': list(order.products.all().values()),
            }
            for order in orders
        ]
        return JsonResponse({'orders': orders_data})


class LatestProductsFeed(Feed):
    title = 'Shop products (Latest)'
    link = reverse_lazy('shopapp:products')
    description = "Updates on changes and addition shop products"

    def items(self):
        return (
            Product.objects
            .filter(created_at__isnull=False)
            .order_by('-created_at')[:5]
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]


class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'shopapp/user_orders.html'
    context_object_name = 'orders'

    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        user_orders = Order.objects.filter(user=user)
        self.owner = user
        return user_orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.owner
        return context


class UserOrdersDataExportView(UserPassesTestMixin, ListView):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        cache_key = f'user_orders_data_export_{user_id}'
        orders_data = cache.get(cache_key)
        if orders_data is None:
            orders = Order.objects.order_by('pk').filter(user=user)
            orders_data = [
                {
                    'pk': order.pk,
                    'address': order.delivery_address,
                    'promocode': order.promocode,
                    'user': order.user.pk,
                    'products': list(order.products.all().values()),
                }
                for order in orders
            ]
            cache.set(cache_key, orders_data, 300)
        return JsonResponse({'orders': orders_data})
