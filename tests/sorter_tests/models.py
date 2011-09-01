from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User)

    def __unicode__(self):
        return (u"%s wrote on %s: %s" %
                (self.author.username, self.created, self.content))
