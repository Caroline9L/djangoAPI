from rest_framework import serializers

from postings.models import BlogPost

#converts to JSON
#Validates passed data

class BlogPostSerializer(serializers.ModelSerializer):
	url 	= serializers.SerializerMethodField(read_only=True)
	class Meta: #what the api is going to return, in a pretty way
		model = BlogPost
		fields = [
			'url',
			'id',
			'user',
			'title',
			'content',
			'timestamp',
		]
		read_only_fields = ['id','user']

	def get_url(self, obj):
		request = self.context.get("request") #request from view
		return obj.get_api_url(request=request)

	def validate_title(self, value):
		qs = BlogPost.objects.filter(title__iexact=value) #we should not have a set -- just one!
		if self.instance: #exclude the self obj
			qs = qs.exclude(pk=self.instance.pk)
		if qs.exists():
			raise serializers.ValidationError("This title is already in use")
		return value
