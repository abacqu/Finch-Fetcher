from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Finch, Hat
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import FeedingForm

# Create your views here.
def home(request):
    # this is where we return a response
    # in most cases we would render a template
    # and we'll need some data for that template
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def finches_index(request):
  finches = Finch.objects.filter(user=request.user)
  # You could also retrieve the logged in user's cats like this
  # cats = request.user.cat_set.all()
  return render(request, 'finches/index.html', { 'finches': finches })

@login_required
def finches_detail(request, finch_id):
  finch = Finch.objects.get(id=finch_id)
  # instantiate FeedingForm to be rendered in the template
  hats_finch_doesnt_have = Hat.objects.exclude(id__in = finch.hats.all().values_list('id'))
  feeding_form = FeedingForm()
  return render(request, 'finches/detail.html', {
    # include the cat and feeding_form in the context
    'finch': finch, 'feeding_form': feeding_form,
    'hats': hats_finch_doesnt_have
  })

@login_required
def add_feeding(request, finch_id):
  form = FeedingForm(request.POST)
  # validate the form
  if form.is_valid():
    new_feeding = form.save(commit=False)
    new_feeding.finch_id = finch_id
    new_feeding.save()
  return redirect('detail', finch_id=finch_id)

@login_required
def assoc_hat(request, finch_id, hat_id):
  # Note that you can pass a toy's id instead of the whole object
  Finch.objects.get(id=finch_id).hats.add(hat_id)
  return redirect('detail', finch_id=finch_id)

@login_required
def assoc_hat_delete(request, finch_id, hat_id):
  Finch.objects.get(id=finch_id).hats.remove(hat_id)
  return redirect('detail', finch_id=finch_id)

def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)

# the CUDs in CRUD we will use class-based views
class FinchCreate(LoginRequiredMixin, CreateView):
  model = Finch
  fields = ['name', 'breed', 'description', 'age']

  def form_valid(self, form):
    # Assign the logged in user (self.request.user)
    form.instance.user = self.request.user  # form.instance is the cat
    # Let the CreateView do its job as usual
    return super().form_valid(form)
  

class FinchUpdate(LoginRequiredMixin, UpdateView):
  model = Finch
  # Let's disallow the renaming of a cat by excluding the name field!
  fields = ['breed', 'description', 'age']

class FinchDelete(LoginRequiredMixin, DeleteView):
  model = Finch
  success_url = '/finches/'


class HatList(LoginRequiredMixin, ListView):
  model = Hat
  template_name = 'hats/index.html'

class HatDetail(LoginRequiredMixin, DetailView):
  model = Hat
  template_name = 'hats/detail.html'

class HatCreate(LoginRequiredMixin, CreateView):
    model = Hat
    fields = ['name', 'color']


class HatUpdate(LoginRequiredMixin, UpdateView):
    model = Hat
    fields = ['name', 'color']


class HatDelete(LoginRequiredMixin, DeleteView):
    model = Hat
    success_url = '/hats/'