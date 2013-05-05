from django.http import HttpResponse
from django.template import Context, loader

from datetime import datetime, timedelta
from random import randrange
import pytz

from energymon_app.models import Usage

def index(request):
    latest_usage_list = Usage.objects.order_by('time_of_reading')
    template = loader.get_template('energymon/index.html')
    context = Context({ 'latest_usage_list': latest_usage_list })
    return HttpResponse(template.render(context))

def gen(request):
    response = ''
    start = datetime(year=2013, month=5, day=1, tzinfo=pytz.utc)
    end = datetime(year=2013, month=5, day=2, tzinfo=pytz.utc)
    response += "{} -> {}".format(start.ctime(), end.ctime())
    delta = timedelta(seconds=10)

    now = start
    usages = []
    while now < end:
        response += "Generating {}<br>".format(now.ctime())
        usage = Usage(time_of_reading=now,
                      watts=randrange(3000, 20000))
        usages.append(usage)
        now += delta

    Usage.objects.all().delete()
    Usage.objects.bulk_create(usages)

    return HttpResponse(response)
