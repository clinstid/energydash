from django.http import HttpResponse
from django.template import Context, loader
from django.core import serializers
from django.utils.safestring import mark_safe

from datetime import datetime, timedelta
from random import randrange
import pytz
import json

from energymon_app.models import Usage

def index(request):
    template = loader.get_template('energymon/index.html')
    usage_data = mark_safe(serializers.serialize("json", Usage.objects.order_by('time_of_reading')))
    context = Context({ 'usage_data': usage_data })
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
