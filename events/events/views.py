from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'events/index.html')

def events(request, name):
    events = {'swiming':'456 Euro',
              'programing':'686 Euro',
              'sleeping':'6466 Euro',
              'chill':'4526 Euro',}
    if name in events:
        return HttpResponse(events[name])
    return HttpResponse('Neexistujci udalost')

def event_listing(request):
    html = '''
    <ul>
        <li><a href="chill/">Chill on the beach</a></li>
        <li>Camping in the woods</li>
        <li>Flying into the space</li>
    </ul>
    '''
    return HttpResponse(html)