from django.test import TestCase

from django import template
from django.conf import settings
from django.core.exceptions import FieldError
from django.test.client import RequestFactory
from django.template import Template, Context, TemplateSyntaxError
from django.http import HttpResponse

from django.contrib.auth.models import User

from milkman.dairy import milkman

from sorter.models import SorterConf
from sorter.utils import cycle_pairs

from .models import Post

template.add_to_builtins('sorter.templatetags.sorter_tags')
template.add_to_builtins('sorter_tests.templatetags.sorter_test_tags')


class SorterTestCase(TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    def create_user(self, username='testuser', email='test@test.de', password='12345'):
        try:
            return User.objects.create_user(username, email, password)
        except:
            pass

    def create_posts(self, count, **kwargs):
        posts = [milkman.deliver(Post, **kwargs) for i in range(count)]
        return Post.objects.filter(pk__in=[post.pk for post in posts])

    def create_response(self, request, template, context=None):
        return HttpResponse(Template(template).render(Context(context)))

    def create_context(self, **kwargs):
        context = {}
        context.update(kwargs)
        return context

    def assertViewRenders(self, template, result, query=None, **kwargs):
        # Create an instance of a GET request.
        request = self.rf.get('/', data=query or {})
        context = self.create_context(request=request, **kwargs)
        response = self.create_response(request, template, context)
        self.assertContains(response, result,
                            msg_prefix="Got: '%s'" % response.content.strip())

    def assertViewRaises(self, exception, template, query=None, with_request=True, **kwargs):
        request = self.rf.get('/', data=query or {})
        context = self.create_context(**kwargs)
        if with_request:
            context['request'] = request
        self.assertRaises(exception, self.create_response, request, template, context)


class SortTests(SorterTestCase):

    def setUp(self):
        super(SortTests, self).setUp()
        self.post1, self.post2, self.post3 = self.create_posts(3)

    def tearDown(self):
        Post.objects.all().delete()

    def test_simple(self):
        self.assertViewRenders(
            "{% sort objects as objects %}{{ objects|pks }}",
            "1.2.3", {'sort': 'id'}, objects=Post.objects.all())
        self.assertViewRenders(
            "{% sort objects as objects %}{{ objects|pks }}",
            "3.2.1", {'sort': '-id'}, objects=Post.objects.all())

    def test_custom_name(self):
        query = {'sort_objects': '-id'}
        kwargs = dict(objects=Post.objects.all())
        self.assertViewRenders(
            """{% sort objects with "objects" as objects %}{{ objects|pks }}""",
            "3.2.1", query=query, **kwargs)
        self.assertViewRenders(
            """{% sort objects with "sort_objects" as objects %}{{ objects|pks }}""",
            "3.2.1", query=query, **kwargs)
        self.assertViewRenders(
            """{% sort objects with "sort_a_completely_different_objects" as objects %}{{ objects|pks }}""",
            "1.2.3", query=query, **kwargs)

    def test_request_not_in_context(self):
        self.assertViewRaises(TemplateSyntaxError,
            """{% sort objects with "objects" as objects %}{{ objects|pks }}""",
            {'sort': 'id'}, with_request=False, objects=Post.objects.all())

    def test_multiple_sorting(self):

        testuser = self.create_user()
        self.create_posts(3, author=testuser)
        self.assertEqual(Post.objects.count(), 6)
        self.assertViewRenders("""
                {% sort objects with "objects" as objects %}
                {% sort others with "others" as others %}
                {{ objects|pks }}.{{ others|pks }}
            """, "3.2.1.6.5.4", {"sort_objects": "-id", "sort_others": "-id"},
            objects=Post.objects.exclude(author=testuser),
            others=Post.objects.filter(author=testuser))

    def test_name_is_not_basestring(self):
        """
        Validates that the given query name is a string and not
        accidently another object.
        """
        self.assertViewRaises(TemplateSyntaxError,
            "{% sort objects with another_var as sorted %}{{ sorted|pks }}",
            {'sort': 'id'}, objects=Post.objects.all(), another_var=123)

    def test_ALLOWED_CRITERIA(self):
        old_setting = settings.SORTER_ALLOWED_CRITERIA
        try:
            settings.SORTER_ALLOWED_CRITERIA = {
                'sort': ['non-existing'],
                'sort_objects': ['created', 'author__*'],
            }
            self.assertViewRenders(
                "{% sort objects as sorted %}{{ sorted|pks }}",
                "1.2.3", {'sort': '-id'}, objects=Post.objects.all())
            self.assertViewRenders(
                "{% sort objects with 'objects' as sorted %}{{ sorted|pks }}",
                "1.2.3", {'sort_objects': '-id,created'},
                objects=Post.objects.all())
        finally:
            settings.SORTER_ALLOWED_CRITERIA = old_setting


class SortlinkTests(SorterTestCase):

    def test_cycle_pairs(self):
        self.assertEqual(list(cycle_pairs([1, 2, 3])), [(1, 2), (2, 3), (3, 1)])

    def test_simple(self):
        self.assertViewRenders(
            """{% sortlink by "creation_date" %}Creation date{% endsortlink %}""",
            """<a href="/?sort=creation_date" title="Sort by: &#39;creation_date&#39; (asc)">Creation date</a>""")

        self.assertViewRenders(
            """{% sortlink with "objects" by "creation_date,-title" %}Creation and title{% endsortlink %}""",
            """<a href="/?sort_objects=creation_date%2C-title" title="Sort by: &#39;creation_date&#39; (asc) and &#39;title&#39; (desc)">Creation and title</a>""")

    def test_attributes(self):
        self.assertViewRenders(
            """{% sortlink by "creation_date" rel "nofollow" class "sortlink" %}Creation date{% endsortlink %}""",
            """<a href="/?sort=creation_date" title="Sort by: &#39;creation_date&#39; (asc)" class="sortlink" rel="nofollow">Creation date</a>""")

    def test_cycling(self):
        self.assertViewRenders(
            """{% sortlink by "creation_date" "-creation_date" %}Creation date{% endsortlink %}""",
            """<a href="/?sort=-creation_date" title="Sort by: &#39;creation_date&#39; (desc)">Creation date</a>""",
            {'sort': 'creation_date'})

    def test_errors(self):
        self.assertViewRaises(TemplateSyntaxError,
            """{% sortlink with "objects" by "creation_date,-title" %}"""
            """{% endsortlink %}""")


class SortFormTests(SorterTestCase):

    def test_simple(self):
        self.assertViewRenders(
            """{% sortform by "creation_date" %}Creation date{% endsortform %}""",
            """\
<form action="" method="get">
    <input type="hidden" name="sort" value="creation_date" />
    <input type="submit" value="Creation date" title="Sort by: &#39;creation_date&#39; (asc)" />
</form>""")

    def test_post(self):
        """
        The csrf token isn't shown in the follow example since it's really
        not included in the context.
        """
        self.assertViewRenders(
            """{% sortform by "creation_date" method "post" %}Creation date{% endsortform %}""",
            """\
<form action="" method="post">
    <input type="hidden" name="sort" value="creation_date" />
    <input type="submit" value="Creation date" title="Sort by: &#39;creation_date&#39; (asc)" />
</form>""")
