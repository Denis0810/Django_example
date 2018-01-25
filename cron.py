from django.shortcuts import render
import requests
import reversion
import datetime
from bs4 import BeautifulSoup
from decimal import Decimal
from ancrm.models import CursUSD


# Create your views here.
def get_currency():
    r = requests.get('http://minfin.com.ua/')
    soup = BeautifulSoup(r.text)
    res = soup.findAll("span", {"class": "mf-currency-ask"})
    with reversion.create_revision():
        curs = CursUSD.objects.get(id=1)
        curs.valueUS = Decimal(res[0].contents[0].strip().replace(',', '.'))
        curs.save()
        #reversion.set_user()
        reversion.set_comment("Изменены значения курсов на дату: {}".format(datetime.datetime.date()))

    return
