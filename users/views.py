from django.http.response import JsonResponse
from django.shortcuts import render


def user_register(request):
    print("register called")
    if request.method == 'POST':
        print(request.POST)
    return JsonResponse({"code": 200})


def user_login(request):
    print("login called")
    if request.method == 'POST':
        print(request.POST)
    return JsonResponse({"code": 200})
