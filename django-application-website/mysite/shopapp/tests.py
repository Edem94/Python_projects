from json import dumps
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from string import ascii_letters
from random import choices
from .models import Product, Order
from .utils import add_two_numbers
from django.conf import settings


class ProductCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        permission_create_product = Permission.objects.get(
            codename='add_product',
        )
        cls.user = User.objects.create_user(username='Masha', password='Masha1994!')
        cls.user.user_permissions.add(permission_create_product)

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "123.45",
                "description": "A good table",
                "discount": "10",
            }
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        permission_update_product = Permission.objects.get(
            codename='change_product',
        )
        cls.user = User.objects.create_user(username='Anton', password='qwerty1234')
        cls.user.user_permissions.add(permission_update_product)
        cls.product = Product.objects.create(name='Best Product', created_by=cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={'pk': self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'product-fixture.json',
        'user-fixture.json',
    ]

    def test_product(self):
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context['products']),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/products-list.html')


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Bob123', password='qwerty')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Orders')

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'product-fixture.json',
        'user-fixture.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(
            reverse('shopapp:products-export'),
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': str(product.price),
                'archived': product.archived
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data['products'],
            expected_data
        )


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        permission_view_order = Permission.objects.get(
            codename='view_order',
        )
        cls.user = User.objects.create_user(username='Antony', password='qwerty123')
        cls.user.user_permissions.add(permission_view_order)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.order = Order.objects.create(delivery_address='Moscow, Garden circle, 32', promocode='123', user=self.user)
        self.client.force_login(self.user)

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_details", kwargs={'pk': self.order.pk})
        )
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promocode)
        self.assertContains(response, self.order.pk)
        self.assertEqual(response.status_code, 200)


class OrdersExportViewTestCase(TestCase):
    fixtures = [
        'orders-fixture.json',
        'user-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='Shaun', password='qwerty123', is_staff=True)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_get_order_view(self):
        response = self.client.get(
            reverse('shopapp:orders-export'),
        )
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': order.pk,
                'address': order.delivery_address,
                'promocode': order.promocode,
                'user': order.user.pk,
                'products': list(order.products.all().values()),
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(
            orders_data['orders'],
            expected_data
        )
