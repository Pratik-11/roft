import ast
import json
import random
from collections import defaultdict
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from core.models import Prompt, Tag, EvaluationText, Annotation, Group
from markdown2 import markdown


BATCH_SIZE = 10


def play(request):
    if not request.user.is_authenticated:
        return redirect('/')
        
    groups = Group.objects.all()
    total_available = sum(len(g.evaluation_texts.all()) for g in groups)

    for group in groups:
        group.description = markdown(group.description)

    return render(request, 'play.html', {
        'groups': groups,
        'total': total_available
    })


def leaderboard(request):
    points = defaultdict(int)
    for annotation in Annotation.objects.filter():
        points[annotation.annotator.username] += annotation.points
    sorted_usernames = sorted(points.items(), key=lambda x: x[1], reverse=True)
    return render(request, 'leaderboard.html', {
        'sorted_usernames': tuple(sorted_usernames)
    })


def profile(request, username):
    if not request.user.is_authenticated:
        return redirect('/')

    profile = User.objects.get(username=username)
    counts = defaultdict(int)
    distances = []
    for annotation in Annotation.objects.filter(annotator=profile):
        counts['points'] += annotation.points
        counts['total'] += 1
        distances.append(abs(annotation.boundary - annotation.text.boundary))
        if annotation.boundary == annotation.text.boundary:
            counts['correct'] += 1

    distance = sum(distances) / len(distances) if distances else "N/A"

    return render(request, 'profile.html', {
        'profile': profile, 
        'counts': counts, 
        'distance': distance
    })


def onboard(request):
    if not request.user.is_authenticated:
        return redirect('/')
        
    return render(request, "onboard.html", {})


def splash(request):
    if request.user.is_authenticated:
        return redirect('/play')
    return render(request, "splash.html", {})


def annotate(request):
    if not request.user.is_authenticated:
        return redirect('/')

    seen_set = Annotation.objects.filter(annotator=request.user).values('text')
  
    annotation = -1  # If this one hasn't been annotated yet.
    if 'qid' in request.GET:
        qid = int(request.GET['qid']) 
        text = EvaluationText.objects.get(pk=qid)
        annotation = Annotation.objects.get(
                annotator=request.user, text_id=qid).boundary
    elif 'group' in request.GET:
        group = Group.objects.get(id=int(request.GET['group']))
        text = random.choice(group.evaluation_texts.exclude(id__in=seen_set))
    else:
        text = random.choice(EvaluationText.objects.exclude(id__in=seen_set))
    sentences = ast.literal_eval(text.body)[:10]

    remaining = request.session.get('remaining', BATCH_SIZE)
    
    return render(request, "annotate.html", {
        "remaining": remaining,
        "prompt": text.prompt, 
        "text_id": text.pk, 
        "sentences": json.dumps(sentences), 
        "name": request.user.username, 
        "max_sentences": len(sentences),
        "boundary": text.boundary,
        "TAXONOMY": False,
        "annotation": annotation,  # Previous annotation given by user, else -1. 
    })


@csrf_exempt
def save(request):  
    text = int(request.POST['text'])
    name = request.POST['name']
    boundary = int(request.POST['boundary'])
    revision = request.POST['revision']
    points = request.POST['points']

    grammar = request.POST['grammar'] == 'true'
    repetition = request.POST['repetition'] == 'true'
    entailment = request.POST['entailment'] == 'true'
    sense = request.POST['sense'] == 'true'

    annotation = Annotation.objects.create(
        annotator=request.user,
        text=EvaluationText.objects.get(pk=text),
        boundary=boundary,
        revision=revision,
        points=points
    )
    
    remaining = request.session.get('remaining', BATCH_SIZE)
    request.session['remaining'] = remaining - 1

    if grammar: annotation.tags.add(Tag.objects.get(name="grammar"))
    if repetition: annotation.tags.add(Tag.objects.get(name="repetition"))
    if entailment: annotation.tags.add(Tag.objects.get(name="entailment"))
    if sense: annotation.tags.add(Tag.objects.get(name="sense"))
    annotation.save()

    return JsonResponse({'status': 200})


def log_in(request):
    if request.method == 'GET': return render(request, 'signin.html', {})
    username, password = request.POST['username'], request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/')
    else:
        return redirect('/?login_error=True')


def sign_up(request):
    username, password = request.POST['username'], request.POST['password']
    if User.objects.filter(username=username).exists():
        return redirect('/?signup_error=True') 
    user = User.objects.create_user(username=username, email=None, password=password)
    login(request, user)
    return redirect('/onboard')


def log_out(request):
    logout(request)
    return redirect('/')
