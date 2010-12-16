from django.contrib.auth.models import User, AnonymousUser
from django.core.cache import cache
from django.http import HttpRequest, Http404
from django.test import TestCase

from gargoyle.models import gargoyle, Switch

class GargoyleTest(TestCase):
    urls = 'gargoyle.urls'
    
    def setUp(self):
        self.user = User.objects.create(username='foo', email='foo@example.com')

    def test_isolations(self):
        gargoyle['isolation'] = {'users': [[0, 50]], 'forums': [[0, 5]], 'admins': True}

        user = User(pk=5)
        self.assertTrue(gargoyle.is_active('isolation', user))

        user = User(pk=8771)
        self.assertFalse(gargoyle.is_active('isolation', user))

    def test_decorator_for_user(self):
        @gargoyle.is_active('switched_for_user')
        def test(request):
            return True

        request = HttpRequest()
        request.user = self.user

        self.assertRaises(Http404, test, request)

        gargoyle['switched_for_user'] = {}

        self.assertTrue(test(request))

        gargoyle['switched_for_user'] = {'users': [self.admin_username]}

        self.assertTrue(test(request))

    def test_decorator_for_ip_address(self):
        @gargoyle.is_active('switched_for_ipaddress')
        def test(request):
            return True

        request = HttpRequest()
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        self.assertRaises(Http404, test, request)

        gargoyle['switched_for_ipaddress'] = {'ipaddress': ['192.168.1.1']}

        self.assertTrue(test(request))

        gargoyle['switched_for_ipaddress'] = {'ipaddress': ['127.0.1.1']}

        self.assertRaises(Http404, test, request)

        gargoyle['switched_for_ipaddress'] = {}

        self.assertTrue(test(request))

        gargoyle['switched_for_ipaddress'] = {'ipaddress': [[50, 100]]}

        self.assertTrue(test(request))

        gargoyle['switched_for_ipaddress'] = {'ipaddress': [[0, 50]]}

        self.assertRaises(Http404, test, request)

    def test_global(self):
        gargoyle['test_for_all'] = {}

        self.assertTrue(gargoyle.is_active('test_for_all'))

        gargoyle['test_for_all'] = {'users': ['dcramer']}

        self.assertFalse(gargoyle.is_active('test_for_all'))

    def test_disable(self):
        user = User(pk=5, username=self.admin_username)

        gargoyle['test_disable'] = {'disable': True}

        self.assertFalse(gargoyle.is_active('test_disable'))

        self.assertFalse(gargoyle.is_active('test_disable', user))

    def test_expiration(self):
        gargoyle['test_expiration'] = {'disable': True}

        self.assertFalse(gargoyle.is_active('test_expiration'))

        Switch.objects.filter(key='test_expiration').update(value="{}")

        # cache shouldn't have expired
        self.assertFalse(gargoyle.is_active('test_expiration'))

        # in memory cache shouldnt have expired
        cache.delete(gargoyle.cache_key)
        self.assertFalse(gargoyle.is_active('test_expiration'))

        # any request should expire the in memory cache
        self.client.get('/')

        self.assertTrue(gargoyle.is_active('test_expiration'))

    def test_anonymous_user(self):
        gargoyle['test_anonymous_user'] = {'disable': True}

        user = AnonymousUser()

        self.assertFalse(gargoyle.is_active('test_anonymous_user', user))

        gargoyle['test_anonymous_user'] = {'users': [1, 10]}

        self.assertFalse(gargoyle.is_active('test_anonymous_user', user))

        gargoyle['test_anonymous_user'] = {}

        self.assertTrue(gargoyle.is_active('test_anonymous_user', user))

        gargoyle['test_anonymous_user'] = {'anon': True}

        self.assertTrue(gargoyle.is_active('test_anonymous_user', user))

        gargoyle['test_anonymous_user'] = {'users': [1, 10], 'anon': True}

        self.assertTrue(gargoyle.is_active('test_anonymous_user', user))