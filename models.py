import django.core.validators
from django.db import models
from ancrm.models import City, Region, TypeBuilding, TypeHouse, TypeHeating, TYPE_OBJ, \
    TypeUse, TypeUsing, Objs
from django.contrib.auth.models import User
from client.models import Clients
import reversion
import django_filters


class QuantFlat(models.Model):
    quant = models.IntegerField(default=1, blank=True, null=True, verbose_name='Количество комнат')

    class Meta:
        ordering = ['quant']
        verbose_name = 'Количество комнат'
        verbose_name_plural = 'Количество комнат'

    def __str__(self):
        return '{}'.format(self.quant)

@reversion.register()
class CardToFind(models.Model):
    manager_dobr = models.ForeignKey(User, blank=True, null=True, verbose_name='Менеджер АН Добродий',
                                     related_name='man_dobr')
    manager_br = models.ForeignKey(User, blank=True, null=True, verbose_name='Менеджер АН Брокер',
                                   related_name='man_br')
    created = models.DateField(auto_now=True, auto_now_add=False, verbose_name='Дата создания')
    name_client = models.CharField(max_length=50, default='', blank=True, null=True, verbose_name='Имя фамилия звонившего')
    phone = models.CharField(max_length=20, default='', blank=True, null=True, verbose_name='Телефон')
    client = models.ForeignKey(Clients, blank=True, null=True, verbose_name='Клиент')
    lpr = models.CharField(max_length=50, default='', blank=True, null=True, verbose_name='ЛПР')
    #cause = models.CharField(max_length=50, default='', blank=True, null=True, verbose_name='Причина звонка')
    cause = models.ForeignKey(Objs, default=None, blank=True, null=True, verbose_name='Объект')
    TYPE_STATUS = (
        ('А', 'Активный'),
        ('F', 'Срочный'),
        ('Z', 'Архивный'),
        ('D', 'Отложенный')
    )
    status_motiv = models.CharField(max_length=1, choices=TYPE_STATUS, default='F', blank=True, verbose_name='Статус мотивации')
    date_delay = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True, default=None, verbose_name='Отложено до')
    delay_comment = models.TextField(default='', null=True, blank=True, verbose_name='Комментарий к отложенной покупке')
    min_price = models.DecimalField(max_digits=8, decimal_places=0, default=0, blank=True,  null=True, verbose_name="Мин цена")
    max_price = models.DecimalField(max_digits=8, decimal_places=0, default=0, blank=True, null=True, verbose_name="Макс цена")
    city = models.CharField(max_length=30, default='', verbose_name='Город')
    regions = models.ManyToManyField(Region, blank=True, verbose_name='Желаемые районы')
    type_of_object = models.CharField(max_length=2, choices=TYPE_OBJ, default='кв',
                                      verbose_name='Тип')
    TYPE_WORK = (
        ('Пр', 'Продажа'),
        ('Ас', 'Сдача в аренду'),
    )
    type_of_work = models.CharField(max_length=2, choices=TYPE_WORK, default='Пр',
                                    verbose_name='Что делаем')
    min_floor = models.IntegerField(null=True, blank=True, verbose_name='Мин этаж')
    max_floor = models.IntegerField(null=True, blank=True, verbose_name='Макс этаж')
    min_floor_build = models.IntegerField(null=True, blank=True, verbose_name='Мин этажность')
    max_floor_build = models.IntegerField(null=True, blank=True, verbose_name='Макс этажность')
    can_be_first = models.NullBooleanField(default=False, verbose_name='Первый этаж допустим')
    can_be_last = models.NullBooleanField(default=False, verbose_name='Верхний этаж допустим')
    type_of_build = models.ManyToManyField(TypeBuilding, blank=True, verbose_name='Стены', related_name='type_build_apart')
    room_list = models.ManyToManyField(QuantFlat, blank=True, verbose_name='Количество комнат')
    # -
    quant_room = models.IntegerField(default=0, blank=True, null=True, verbose_name='Количество комнат от')
    # -
    quant_room_max = models.IntegerField(default=0, blank=True, null=True, verbose_name='Количество комнат до')
    # -
    square_all_min = models.FloatField(default=0, blank=True, null=True, verbose_name='Общая площадь')
    # -
    square_all_max = models.FloatField(default=0, blank=True, null=True, verbose_name='Общая площадь')
    # -
    heating = models.ManyToManyField(TypeHeating, blank=True, verbose_name='Отопление')
    repairs = models.NullBooleanField(default=False, blank=True, verbose_name='Ремонт')
    furniture = models.NullBooleanField(default=False, blank=True, verbose_name='Мебель')
    # house
    type_of_build_h = models.ManyToManyField(TypeBuilding, blank=True, verbose_name='Стены дома', related_name='type_build_h_card')
    type_of_house = models.ManyToManyField(TypeHouse, blank=True, verbose_name='Тип', related_name='type_house_card')
    year_build_min = models.DecimalField(max_digits=4, decimal_places=0, default=2000, blank=True, null=True,
                                         verbose_name="Год постройки")
    # room (помещения)
    type_of_build_r = models.ManyToManyField(TypeBuilding, blank=True, verbose_name='Стены дома')

    type_of_use = models.ForeignKey(TypeUse, default='', blank=True, null=True, verbose_name='Тип')
    floor_r_min = models.IntegerField(default=0, blank=True, null=True, verbose_name='Этаж min')
    floor_r_max = models.IntegerField(default=0, blank=True, null=True, verbose_name='Этаж max')
    square_r_min = models.FloatField(default=0, blank=True, null=True, verbose_name='Общая площадь помещения')
    square_r_max = models.FloatField(default=0, blank=True, null=True, verbose_name='Общая площадь помещения')
    # lands
    type_of_use1 = models.ManyToManyField(TypeUsing, blank=True, verbose_name='Назначение')
    land_area_l_min = models.DecimalField(max_digits=6, decimal_places=2, default=0, blank=True, null=True,
                                      verbose_name="Площадь участка")
    land_area_l_max = models.DecimalField(max_digits=6, decimal_places=2, default=0, blank=True, null=True,
                                      verbose_name="Площадь участка")
    mark_for_delete = models.BooleanField(default=False, blank=True, verbose_name='Запрос на архивацию')
    comment_for_mark = models.CharField(max_length=100, default='', blank=True, null=True,
                                        verbose_name='Комментарий к пометке об удалении')
    is_archive = models.BooleanField(default=False, blank=True, verbose_name='Архивный')
    comments = models.TextField(default='', blank=True, null=True, verbose_name='Комментарий')

    class Meta:
        ordering = ['created']
        verbose_name = 'Карточка покупателя'
        verbose_name_plural = 'Карточки покупателя'

    def card_string(self):

        if self.type_of_object == 'кв':
            is_all_region = False
            quant_regions = Region.objects.all().count()
            if quant_regions == len(self.regions.all()):
                regs = 'Все районы'
            else:
                regs = ''
                for item in self.regions.all():
                    regs += '{}; '.format(item)
            r = ""
            for item in self.room_list.all():
                r += "{}, ".format(item.quant)

            res = "{}; район - {}; комн - {}".format(self.city, regs, r)
        elif self.type_of_object == 'д':
            regs = ''
            for item in self.regions.all():
                regs += '{}; '.format(item)
            type_h = ''
            for item in self.type_of_house.all():
                type_h += '{}; '.format(item)
            type_b = ''
            for item in self.type_of_build_h.all():
                type_b += '{}; '.format(item)
            res = "{}; район - {}; тип -{}; год > {}; стены {}".format(self.city, regs, type_h,
                    self.year_build_min, type_b)
        elif self.type_of_object == 'п':
            res = "{}: {} ({}-{}) ".format(self.city, self.type_of_use, self.square_r_min, self.square_r_max)
        else:
            type_of_use1 = ''
            for item in self.type_of_use1.all():
                type_of_use1 += '{}; '.format(item)
            res = "{} {} ({}-{})".format(self.city, type_of_use1,
                                         self.land_area_l_min if self.land_area_l_min else 0,
                                         self.land_area_l_max if self.land_area_l_min else 'max')
        return res

    def __str__(self):
        return self.card_string()

