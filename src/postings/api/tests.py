from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse as api_reverse
from rest_framework_jwt.settings import api_settings

from django.contrib.auth import get_user_model

from postings.models import BlogPost

payload_handler = api_settings.JWT_PAYLOAD_HANDLER
encode_handler = api_settings.JWT_ENCODE_HANDLER

User = get_user_model()

class BlogPostAPITestCase(APITestCase):
	def setUp(self):
		# user = User.objects.create(username='testuser', email='test@test.com')
		user_obj = User(username='testuser', email='test@test.com')
		user_obj.set_password("somepassword")
		user_obj.save()
		blog_post = BlogPost.objects.create(
				user=user_obj, 
				title="Title", 
				content="Some_content", 
				timestamp="2018-04-05T17:30:47Z"
				)

	def test_single_user(self):
		user_count = User.objects.count()
		self.assertEqual(user_count, 1)

	def test_single_post(self):
		post_count = BlogPost.objects.count()
		self.assertEqual(post_count, 1)

	def test_get_list(self):
		data = {}
		url = api_reverse("api-postings:post-create")
		response = self.client.get(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		# print(response.data)

	def test_post_item(self):
		data = {"title":"New Title", "content":"Some more content", "timestamp":"2018-03-05T17:30:47Z"}
		url = api_reverse("api-postings:post-create")
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
		# print(response.data)

	def test_get_item(self):
		blog_post = BlogPost.objects.first()
		data = {}
		url = blog_post.get_api_url()
		response = self.client.get(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		print(response.data)

	def test_update_item(self):
		blog_post = BlogPost.objects.first()
		url = blog_post.get_api_url()
		data = {"title":"New Title", "content":"Some more content", "timestamp":"2018-03-05T17:30:47Z"}
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
		response = self.client.put(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
		# print(response.data)

	def test_update_item_with_user(self):
		blog_post = BlogPost.objects.first()
		# print(blog_post.content)
		url = blog_post.get_api_url()
		data = {"title":"New Title", "content":"Some more content", "timestamp":"2018-03-05T17:30:47Z"}

# http://getblimp.github.io/django-rest-framework-jwt/#creating-a-new-token-manually
		user_obj = User.objects.first() #authenticate fake user - token header
		payload = payload_handler(user_obj)
		token_resp = encode_handler(payload)
		self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_resp)

		response = self.client.put(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		# print(response.data)

	def test_post_item_with_user(self):
		data = {"title":"New Title", "content":"Some more content", "timestamp":"2018-03-05T17:30:47Z"}
		url = api_reverse("api-postings:post-create")
		user_obj = User.objects.first() 
		payload = payload_handler(user_obj)
		token_resp = encode_handler(payload)
		self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_resp)
		response = self.client.post(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_user_ownership(self):
		owner = User.objects.create(username="Newtestuser")
		blog_post = BlogPost.objects.create(
				user=owner, 
				title="Title", 
				content="Some_content", 
				timestamp="2018-04-05T17:30:47Z"
				)

		user_obj = User.objects.first()
		self.assertNotEqual(user_obj.username, owner.username)

		payload = payload_handler(user_obj)
		token_resp = encode_handler(payload)
		self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_resp)

		url = blog_post.get_api_url()
		data = {"title":"New Title", "content":"Some more content", "timestamp":"2018-03-05T17:30:47Z"}
		response = self.client.put(url, data, format='json')
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_user_login_and_update(self):
		data = {
			"username":"testuser",
			"password":"somepassword"
		}
		url = api_reverse("api-login") #no namespace, just name
		response = self.client.post(url, data)
		print(response.data)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		token = response.data.get("token")
		if token is not None:
			blog_post = BlogPost.objects.first()
			url = blog_post.get_api_url()
			data = {"title":"New Title", "content":"Some more content", "timestamp":"2018-03-05T17:30:47Z"}
			self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
			response = self.client.put(url, data, format='json')
			self.assertEqual(response.status_code, status.HTTP_200_OK)

			

	#python manage.py test
	# http://getblimp.github.io/django-rest-framework-jwt/#creating-a-new-token-manually
	# request.post(url, data, headers={"Authorization": "JWT " + <token>})

