from pathlib import Path
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.http import HttpResponse, QueryDict
from django.utils.html import format_html, mark_safe
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib.auth.models import User
from .models import Visitation, ShowObjs, Showitem, Rejection, \
    ObjSuggestions, CallToClient, CallFromCard, \
    Bidding
from .forms import AddCallForm, CallFromCardForm, DateRangeForm, BiddingForm, \
    VisitationForm, NewClientForm
from .filters import CardFilter, ObjsFilter
from accounts.views import get_role
from ancrm.models import Objs, ObjectMeeting, Region
from ancrm.views import user_calendar
from card.models import CardToFind
from client.models import Clients, ClientPhone
import datetime
import os
import reversion
import weasyprint
from schedule.models import Calendar, Event, Rule
from userena.contrib.umessages.models import Message, MessageRecipient, MessageContact


# Create your views here.

def add_call(request, obj_id):
    if request.method == "POST":
        form = AddCallForm(request.POST)
        if form.is_valid():
            call = form.save(commit=False)
            call.obj = Objs.objects.get(pk=obj_id)
            call.manager = request.user
            call.save()
            return redirect('IndexList')
    else:
        form = AddCallForm()
    return render(request, 'obj_act/call_add.html', {'form': form})



class VisitationDetail(DetailView):
    model = Visitation

    def get_context_data(self, **kwargs):
        context = super(VisitationDetail, self).get_context_data(**kwargs)
        return context

    def get_object(self, queryset=None):
        obj = Visitation.objects.get(id=self.kwargs['pk'])
        return obj

    def post(self, request, *args, **kwargs):
        visit = self.get_object()
        for row in request.POST:
            print(row, request.POST[row])
            if 'result' in row:
                if request.POST[row] == 'deal':
                    pass
                if request.POST[row] == 'reject':
                    with reversion.create_revision():
                        reject = Rejection(obj=visit.obj, manager=visit.manager,
                                           date=datetime.datetime.now(), client=visit.client,
                                           reason='Отказ после посещения ID {}.'.format(visit.id))
                        reject.name = 'Отказ'
                        reject.save()
                        reversion.set_user(self.request.user)
                        reversion.set_comment("Отказ после посещения")
        return redirect('visit_list', pk=visit.obj.id)

class VisitationList(ListView):
    model = Visitation

    def get_object(self):
        obj = super(Visitation, self).get_object()
        return obj

    def get_queryset(self):
        obj_id = self.kwargs['pk']
        return Visitation.objects.filter(obj=obj_id)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VisitationList, self).get_context_data(**kwargs)
        obj_id = self.kwargs['pk']
        context['object'] = Objs.objects.get(pk=obj_id)
        return context



class SuggestionList(ListView):
    model = ObjSuggestions

    def get_context_data(self, **kwargs):
        context = super(SuggestionList, self).get_context_data(**kwargs)
        obj_id = self.kwargs['pk']
        role = get_role(self.request.user)
        usr = User.objects.get(username=self.request.user.username)
        obj = Objs.objects.get(pk=obj_id)
        if role['admin']:
            qs = ObjSuggestions.objects.filter(obj=obj).order_by('date')
        if role['of_man']:
            qs = ObjSuggestions.objects.filter(obj=obj, manager__in=role['users']).order_by('date')
        if role['manager']:
            qs = ObjSuggestions.objects.filter(obj=obj, manager=usr).order_by('date')
        context = {
            'object_list': qs,
            'obj_id': obj_id,
        }
        return context



def call_to_seller(request, obj_id):
    template = 'obj_act/call_to_seller_add.html'
    obj = Objs.objects.get(pk=obj_id)
    if request.method == 'POST':
        form = CallFromCardForm(request.POST)
        if form.is_valid():
            with reversion.create_revision():
                call = form.save(commit=False)
                call.manager = User.objects.get(username=request.user.username)
                call.date_call = datetime.datetime.now()
                call.obj = obj
                call.name = "Звонок продавцу"
                call.author = request.user
                call.save()
                reversion.set_user(request.user)
                reversion.set_comment("Звонок создан")
        return redirect('call_list', obj_id=obj_id)
    else:
        form = CallFromCardForm()
    context = {
        'form': form,
        'obj_id': obj_id,
    }
    return render(request, template, context)



def calendars(request):
    template = 'obj_act/calendars.html'
    role = get_role(request.user)
    agency = []
    if role['dobr']:
        agency.append('dobrodij')
    if role['br']:
        agency.append('broker')

    users = User.objects.filter(
        groups__name__in=agency
    ).exclude(
        Q(username='admin') | Q(username='admin1')
    ).order_by('username')
    events = []
    if role['admin'] or role['of_man']:
        for user in users:
            events.append([user, user_calendar(user, datetime.datetime.now())])
    if role['manager']:
        events.append([request.user, user_calendar(request.user, datetime.datetime.now())])
    print(events)
    context = {
        'events': events,
    }
    return render(request, template, context)


def oferta_print(request, bidding_id):
    template = 'obj_act/oferta_print.html'
    instance = Bidding.objects.get(id=bidding_id)
    context = {'obj': instance.obj, 'buyer_name': instance.buyer,
               'price': instance.price_usd_b, 'type': instance.obj.type_of_object,
               'valid_date': instance.date_valid}
    html = render_to_string(template, context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=oferta_{}.pdf'.format(instance.id)
    weasyprint.HTML(string=html).write_pdf(response,
                                           stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + '/ancrm/css/bootstrap.min.css')])

    return response
