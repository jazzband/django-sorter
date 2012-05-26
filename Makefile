test:
	coverage run --branch --source=sorter `which django-admin.py` test --settings=sorter.test_settings sorter
	coverage report --omit=sorter/test*
