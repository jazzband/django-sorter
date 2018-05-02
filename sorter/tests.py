from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.http import HttpResponse
from django.template import Library, Template, Context, TemplateSyntaxError
from django.test import TestCase
from django.test.client import RequestFactory

from model_mommy import mommy

from sorter.conf import settings
from sorter.utils import cycle_pairs

register = Library()


@register.filter
def sorter_tests_pks(value):
    pk_list = []
    for obj in value:
        pk_list.append(str(obj.pk))
    if pk_list:
        return u'.'.join(pk_list)
    return ''


class SorterTestCase(TestCase):

    def setUp(self):
        self.rf = RequestFactory()
        self.old_sorter_allowed_criteria = settings.SORTER_ALLOWED_CRITERIA
        settings.SORTER_ALLOWED_CRITERIA = {
            'sort': ['*'],
            'sort_objects': ['*'],
            'sort1': ['*'],
            'sort2': ['*'],
            'sort_others': ['*'],
        }

    def tearDown(self):
        settings.SORTER_ALLOWED_CRITERIA = self.old_sorter_allowed_criteria

    def create_entries(self, count, **kwargs):
        entries = [mommy.make(LogEntry, **kwargs) for i in range(count)]
        return LogEntry.objects.filter(pk__in=[entry.pk for entry in entries])

    def create_response(self, request, template, context=None):
        return HttpResponse(Template(template).render(Context(context)))

    def create_context(self, **kwargs):
        context = {}
        context.update(kwargs)
        return context

    def assertViewRenders(self, template, result, query=None, func=None, **kwargs):
        # Create an instance of a GET request.
        request = self.rf.get('/', data=query or {})
        context = self.create_context(request=request, **kwargs)
        response = self.create_response(request, template, context)
        if func is None:
            func = self.assertContains
        func(response, result, msg_prefix="Got: '%s'" % response.content.strip())

    def assertViewNotRenders(self, template, result, query=None, **kwargs):
        self.assertViewRenders(template, result, query=None,
                               func=self.assertNotContains, **kwargs)

    def assertViewRaises(self, exception, template, query=None, with_request=True, **kwargs):
        request = self.rf.get('/', data=query or {})
        context = self.create_context(**kwargs)
        if with_request:
            context['request'] = request
        self.assertRaises(exception, self.create_response, request, template, context)


class SortTests(SorterTestCase):

    def setUp(self):
        super(SortTests, self).setUp()
        self.entry1, self.entry2, self.entry3 = self.create_entries(3)

    def tearDown(self):
        self.entry1.delete()
        self.entry2.delete()
        self.entry3.delete()

    def test_simple(self):
        self.assertViewRenders(
            "{% sort objects as objects %}{{ objects|sorter_tests_pks }}",
            "1.2.3", {'sort': 'id'}, objects=LogEntry.objects.all())
        self.assertViewRenders(
            "{% sort objects as objects %}{{ objects|sorter_tests_pks }}",
            "3.2.1", {'sort': '-id'}, objects=LogEntry.objects.all())
        self.assertViewNotRenders(
            "{% sort objects as objects %}{{ objects|sorter_tests_pks }}",
            "3.2.1", {}, objects=LogEntry.objects.order_by('?'))

    def test_custom_name(self):
        query = {'sort_objects': '-id'}
        kwargs = dict(objects=LogEntry.objects.all())
        self.assertViewRenders(
            """{% sort objects with "objects" as objects %}{{ objects|sorter_tests_pks }}""",
            "3.2.1", query=query, **kwargs)
        self.assertViewRenders(
            """{% sort objects with "sort_objects" as objects %}{{ objects|sorter_tests_pks }}""",
            "3.2.1", query=query, **kwargs)
        self.assertViewRenders(
            """{% sort objects with "sort_a_completely_different_objects" as objects %}{{ objects|sorter_tests_pks }}""",
            "3.2.1", query=query, **kwargs)

    def test_request_not_in_context(self):
        self.assertViewRaises(TemplateSyntaxError,
            """{% sort objects with "objects" as objects %}{{ objects|sorter_tests_pks }}""",
            {'sort': 'id'}, with_request=False, objects=LogEntry.objects.all())

    def test_multiple_sorting(self):

        testuser = mommy.make(User)
        testuser.set_password("letmein")
        testuser.save()

        self.create_entries(3, user=testuser)
        self.assertEqual(LogEntry.objects.count(), 6)
        self.assertViewRenders("""
                {% sort objects with "objects" as objects %}
                {% sort others with "others" as others %}
                {{ objects|sorter_tests_pks }}.{{ others|sorter_tests_pks }}
            """, "3.2.1.6.5.4", {"sort_objects": "-id", "sort_others": "-id"},
            objects=LogEntry.objects.exclude(user=testuser),
            others=LogEntry.objects.filter(user=testuser))

    def test_name_is_not_basestring(self):
        """
        Validates that the given query name is a string and not
        accidently another object.
        """
        self.assertViewRaises(TemplateSyntaxError,
            "{% sort objects with another_var as sorted %}{{ sorted|sorter_tests_pks }}",
            {'sort': 'id'}, objects=LogEntry.objects.all(), another_var=123)

    def test_ALLOWED_CRITERIA(self):
        old_setting = settings.SORTER_ALLOWED_CRITERIA
        try:
            settings.SORTER_ALLOWED_CRITERIA = {
                'sort': ['non-existing'],
                'sort_objects': ['action_time', 'user__*'],
            }
            # This will follow the default order of the LogEntry class, -action_time
            self.assertViewRenders(
                "{% sort objects as sorted %}{{ sorted|sorter_tests_pks }}",
                "3.2.1", {'sort': 'id'}, objects=LogEntry.objects.all())
            self.assertViewRenders(
                "{% sort objects with 'objects' as sorted %}{{ sorted|sorter_tests_pks }}",
                "1.2.3", {'sort_objects': '-id,action_time'},
                objects=LogEntry.objects.all())
        finally:
            settings.SORTER_ALLOWED_CRITERIA = old_setting


class SortURLTests(SorterTestCase):

    def test_cycle_pairs(self):
        self.assertEqual(list(cycle_pairs([1, 2, 3])), [(1, 2), (2, 3), (3, 1)])

    def test_simple(self):
        self.assertViewRenders(
            """{% sorturl by "creation_date" %}""",
            """/?sort=creation_date""")


class SortlinkTests(SorterTestCase):

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
