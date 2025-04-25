from django.shortcuts import render
from rest_framework import generics
from .models import MenuItem, Category
from .serializers import MenuItemSerializer, CategorySerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.paginator import Paginator,EmptyPage
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes,throttle_classes
from rest_framework.throttling import UserRateThrottle
# from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle
from .throttles import TenCallsPerMinute

# Create your views here.
# class MenuItemsView(generics.ListCreateAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
    
# class SingleMenuIView(generics.RetrieveUpdateDestroyAPIView,generics.DestroyAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer    


@api_view(['GET','POST'])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage',default=2)
        page = request.query_params.get('page',default=1)
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__startswith=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items,per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
            
        serialized_item = MenuItemSerializer(items,many=True)
        return Response(serialized_item.data)
    elif request.method == 'POST':
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data,status.HTTP_201_CREATED)
 
@api_view()
def single_item(request,id):
    item = get_object_or_404(MenuItem,pk=id)
    serializer_item = MenuItemSerializer(item)
    return Response(serializer_item)    
    

@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category,pk=pk)
    serialized_category = CategorySerializer(category)
    return Response(serialized_category.data)     
##########

@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message":"Some secret message"})

api_view()
# @permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def roles(request):
    isdelivery = request.user.groups.filter(name='Delivery').exists()
    return Response(isdelivery)

api_view()
# @permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name='Manager').exists():
        return Response({"message": "Only Manager Should See This"})
    else:        
        return Response({"message": "You are not authorized"},403)


@api_view(['GET'])
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "Successful"})


@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def throttle_check_auth(request):
    return Response({"message":"message for the logged in users only"})

@api_view()
@permission_classes([IsAuthenticated])
def me(request):
    return Response(request.user.email)

# @api_view()
# @permission_classes([IsAuthenticated])
# @throttle_check_auth([TenCallsPerMinute])
# def manager_view(request):
#     return Response({"message":"message for the logged in users only"})