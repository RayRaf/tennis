from django.shortcuts import render

# Create your views here.
def main(request):
    return render(request, 'home_index.html')

def play(request):
    return render(request, 'play.html')

def my_tournaments(request):
    return render(request, 'my_tournaments.html')

def rules(request):
    return render(request, 'rules.html')

