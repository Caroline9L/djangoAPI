from django.conf import settings
from django.db import models
from django.urls import reverse

from rest_framework.reverse import reverse as api_reverse
#django hosts -- for reverse with subdomains

# Create your models here.

class BlogPost(models.Model):
	user		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	title 		= models.CharField(max_length=120, null=True, blank=True)
	content 	= models.TextField(max_length=120, null=True, blank=True)
	timestamp 	= models.DateTimeField()#auto_add_now=True
	
	def __str__(self):
		return str(self.user.username)

	@property
	def owner(self): #assigns user to owner needed in permissions, like let owner = user
		return self.user

	def get_api_url(self, request=None): #detail view of the single api post - returns full addy not relative
		return api_reverse("api-postings:post-rud", kwargs={'pk': self.pk}, request=request) # url namespace: url name, search term (in the regex)

		
