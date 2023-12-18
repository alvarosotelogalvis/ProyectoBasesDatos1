from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'Home.html')

def signup(request):
    if request.method == 'GET':
        #print("Enviando formulario")
        return render(request, 'signup.html', {'form':UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                #register user
                #print(request.POST)
                #print("Obteniendo datos")
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save() #guarda en la db
                login(request, user) # crea la sesion de user en las cookies del browser
                #return HttpResponse('user created successfully')
                #return render(request, 'signup.html', {'form':UserCreationForm, "error":'user created successfully'})
                return redirect('tasks')
            #except:
            except IntegrityError:
                #return HttpResponse('username already exists')
                return render(request, 'signup.html', {'form':UserCreationForm, "error":'user already exists'})
        #return HttpResponse('password do not match')
        return render(request, 'signup.html', {'form':UserCreationForm, "error":'password do not match'})

@login_required #Protege las rutas para que se requiera un usuario logueado
def tasks(request):
    #tasks = Task.objects.all()
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks':tasks})

@login_required #Protege las rutas para que se requiera un usuario logueado
def tasks_completed(request):
    #tasks = Task.objects.all()
    #tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False)
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks':tasks})

@login_required #Protege las rutas para que se requiera un usuario logueado
def create_task(request):
    if request.method=='GET':
        return render(request, 'create_task.html', {'form':TaskForm})
    else:
        try:
            #print(request.POST)
            form = TaskForm(request.POST)
            #print(form)
            new_task = form.save(commit = False)
            new_task.user = request.user
            #print(new_task)
            new_task.save()
            #return render(request, 'create_task.html', {'form':TaskForm})
            return redirect('tasks')
        #except:
        except ValueError:
            return render(request, 'create_task.html', {'form':TaskForm, 'error':'please provide valid data...'})

@login_required #Protege las rutas para que se requiera un usuario logueado
def task_detail(request, task_id):
    if request.method == 'GET':
        #task = Task.objects.get(pk=task_id) #puede dar error al no encontrar la tarea y cae el servidor
        task = get_object_or_404(Task, pk=task_id, user=request.user) #Se obitienen las tareas del user.
        form = TaskForm(instance = task)
        return render(request, 'task_detail.html', {'task':task, 'form':form})
    else:
        try:
            #task = Task.objects.get(pk=task_id) #puede dar error al no encontrar la tarea y cae el servidor
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance = task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task':task, 'form':form, 'error':"Error updating task."})

@login_required #Protege las rutas para que se requiera un usuario logueado
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required #Protege las rutas para que se requiera un usuario logueado
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == "POST":
        task.delete()
        return redirect('tasks')

@login_required #Protege las rutas para que se requiera un usuario logueado
def signout(request):
    logout(request)#cierra la sesion de user de las cookies
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form':AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {'form':AuthenticationForm, 'error':'username or password incorrect'})
        else:
            login(request, user) # crea la sesion de user en las cookies del browser
            return redirect('tasks')
    #return render(request, 'signin.html', {'form':AuthenticationForm})
