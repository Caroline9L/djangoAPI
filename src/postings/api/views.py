#generic - http://www.django-rest-framework.org/api-guide/generic-views/
from django.db.models import Q
from rest_framework import generics, mixins

from .permissions import IsOwnerOrReadOnly
from postings.models import BlogPost
from .serializers import BlogPostSerializer


class BlogPostAPIView(mixins.CreateModelMixin, generics.ListAPIView): 
	lookup_field 		= 'pk'
	serializer_class 	= BlogPostSerializer
	# permission_classes	= [] #settings permission override

	# def get_queryset(self): 
	# 	return BlogPost.objects.all()

	def get_queryset(self): 
		qs = BlogPost.objects.all()
		query = self.request.GET.get("q") #search function
		if query is not None:
			qs = qs.filter(Q(title__icontains=query)|Q(content__icontains=query)).distinct()
		return qs

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)

	def post(self, request, *args, **kwargs): #mixin to add post
		return self.create(request, *args, **kwargs)
	
	def get_serializer_context(self, *args, **kwargs): 
		return {"request": self.request}


	# def put(self, request, *args, **kwargs): #mixin to add put/update
	# 	return self.update(request, *args, **kwargs)

	# def patch(self, request, *args, **kwargs): #mixin to add patch/update
	# 	return self.update(request, *args, **kwargs)


class BlogPostRudView(generics.RetrieveUpdateDestroyAPIView): #detail view - this is an endpoint
	lookup_field 		= 'pk' #can be slug or id #(?P<pk>\d+)
	serializer_class 	= BlogPostSerializer
	permission_classes	= [IsOwnerOrReadOnly] #imported from the custom permissions

	# queryset 		= BlogPost.objects.all()

	def get_queryset(self): #overrides queryself above, which is from the model
		return BlogPost.objects.all()
		
	def get_serializer_context(self, *args, **kwargs): #get request to send to serializer for url view
		return {"request": self.request}

	# def get_object(self): #overrides lookupfield above
	# 	pk = self.kwargs.get("pk")
	# 	return BlogPost.objects.get(pk=pk)
