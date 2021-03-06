from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from datetime import datetime

# Create your views here.
def index(request):
	request.session.set_test_cookie()
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list, 'pages': page_list}
	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']
	response =  render(request, 'rango/index.html', context=context_dict)
	return response

def about(request):
	context_dict = {'boldmessage': "Woah, wow! Django is cool."}
	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']
	return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
	context_dict = {}
	try:
		category = Category.objects.get(slug=category_name_slug)
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		context_dict['pages'] = None
		context_dict['category'] = None

	return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
	form = CategoryForm()
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print(form.errors)

	return render(request, 'rango/add_category.html', context={'form': form})

@login_required
def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None

	form = PageForm()
	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
		else:
			print(form.errors)

	context_dict = {'form': form, 'category': category}
	return render(request, 'rango/add_page.html', context_dict)

@login_required
def restricted(request):
	return render(request, 'rango/restricted.html', {})

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

def get_server_side_cookie(request, cookie, default_val=None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	return val

def visitor_cookie_handler(request):
	visits = int(get_server_side_cookie(request, 'visits', '1'))
	last_visit_cookie = get_server_side_cookie(request,
												'last_visit',
												str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], 
										'%Y-%m-%d %H:%M:%S')

	if (datetime.now() - last_visit_time).days > 0:
		visits = visits + 1
		request.session['last_visit'] = str(datetime.now())
	else:
		visits = 1
		request.session['last_visit'] = last_visit_cookie

	request.session['visits'] = visits



