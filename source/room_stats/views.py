from datetime import datetime, timedelta
from django.shortcuts import render
from django.http.response import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from room_stats.models import Room, DailyMembers, Tag, ServerStats


def render_rooms_paginated(request, queryset, context={}, page_size=20):
    page = request.GET.get('page', 1)
    paginator = Paginator(queryset, page_size)
    try:
        rooms = paginator.page(page)
    except EmptyPage:
        rooms = paginator.page(paginator.num_pages)
    context['rooms'] = rooms
    return render(request, 'room_stats/rooms_list.html', context)


def get_daily_members_stats(request, room_id, days=30):
    from_date = datetime.now() - timedelta(days=int(days)-1)
    dm = DailyMembers.objects.filter(
        room_id=room_id,
        date__gte=from_date,
    )
    result = []
    for day in dm:
        result.append({
            'date': day.date,
            'members_count': day.members_count
        })
    return JsonResponse({'result':result})

def room_stats_view(request, room_id):
    days = 30
    from_date = datetime.now() - timedelta(days=int(days)-1)
    room = Room.objects.get(id=room_id)
    dm = DailyMembers.objects.filter(
        room_id=room_id,
        date__gte=from_date,
    ).order_by('date')
    points = []
    for day in dm:
        points.append({
            'x': day.date.strftime("%d-%m-%Y"),
            'y': day.members_count
        })
    labels = str([ point['x'] for point in points ])
    context = {
        'room': room,
        'points': points,
        'labels': labels,
    }
    return render(request, 'room_stats/room_stats.html', context)

def list_rooms(request):
    return render(request, 'room_stats/rooms.html')

# FIXME optimize query and add daily/weekly/monthly stats
def list_server_stats(request, server):
    server_stats = ServerStats.objects.filter(server=server).order_by('id')[0:180]
    points = []

    LATENCY_GROUP_SIZE = 6;
    latency_group = []
    for stat in server_stats:
        latency_group.append(stat.latency)
        if len(latency_group) == LATENCY_GROUP_SIZE:
            points.append({
                'x': stat.date.strftime("%H:%M %d-%m-%Y"),
                'y': sum(latency_group) / LATENCY_GROUP_SIZE
            })
            latency_group = []
        # points.append({
        #     'x': stat.date.strftime("%H:%M %d-%m-%Y"),
        #     'y': stat.latency
        # })
    labels = str([ point['x'] for point in points ])
    context = {
        'points': points,
        'labels': labels,
        'server': server
    }
    return render(request, 'room_stats/server_stats.html', context)

def list_rooms_by_random(request):
    rooms = Room.objects.filter(members_count__gt=5).order_by('?')[:20]
    context = {'rooms': rooms}
    return render(request, 'room_stats/rooms_list.html', context)

def list_rooms_by_members_count(request):
    # rooms = Room.objects.filter(
    #     members_count__gt=5).order_by('-members_count')[:20]
    # context = {'rooms': rooms}
    # return render(request, 'room_stats/rooms_list.html', context)
    rooms = Room.objects.filter(
        members_count__gt=5).order_by('-members_count')
    return render_rooms_paginated(request,rooms)

def list_rooms_with_tag(request, tag):
    rooms = Room.objects.filter(topic__iregex='#%s' % tag)
    return render_rooms_paginated(request, rooms)

def list_tags(request):
    tags = Tag.objects.all()
    context = {'tags': tags}
    return render(request, 'room_stats/tag_list.html', context)


def all_rooms_view(request):
    rooms = Room.objects.filter(members_count__gt=5).order_by('?')[:20] # order_by('-members_count')[:20]
    context = {'rooms': rooms}
    return render(request, 'room_stats/rooms_list.html', context)

def list_rooms_by_lang_ru(request):
    rooms = Room.objects.filter(topic__iregex=r'[а-яА-ЯёЁ]+') #.order_by('?')[:20]
    return render_rooms_paginated(request, rooms)

from django.contrib.postgres.search import SearchVector
def list_rooms_by_search_term(request, term):
    rooms = Room.objects.annotate(
        search=SearchVector('name', 'aliases', 'topic'),
    ).filter(search=term)
    return render_rooms_paginated(request, rooms)

from .rawsql import MOST_INCOMERS_PER_PERIOD_QUERY
def list_most_joinable_rooms(request, delta, rating='absolute', limit=100):
    rating_to_order_mapper = {
        'absolute': 'delta',
        'relative': 'percentage'
    }
    # supported order_by values: ('delta', 'percentage')
    from_date = datetime.now() - timedelta(days=delta)
    to_date = datetime.now()
    rooms = Room.objects.raw(
        MOST_INCOMERS_PER_PERIOD_QUERY % {
            'from_date': from_date,
            'to_date': to_date,
            'order_by': rating_to_order_mapper[rating]
        }
    )[:limit]
    context = {
        'rating': rating
    }
    return render_rooms_paginated(request, rooms, context=context)

from .rawsql import NEW_ROOMS_FOR_LAST_N_DAYS_QUERY
def list_new_rooms(request, delta=3):
    rooms = Room.objects.raw(
        NEW_ROOMS_FOR_LAST_N_DAYS_QUERY % delta
    )[::]
    return render_rooms_paginated(request, rooms)


