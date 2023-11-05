from collections.abc import Iterable
from django.db import models
from decimal import Decimal
from django.db.models.signals import post_save, post_delete, pre_delete, pre_save
from django.dispatch import receiver
from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify
import datetime


# TODO:
# !Add revenue details
# !Multiple Medications 
# !Calf Medication and events


# list of breeds
dairy_cow_breeds = [
    ("HF", "Holstein Friesian (HF)"),
    ("HF Jersey (cross)", "HF Jersey (cross)"),
    ("Jersey", "Jersey"),
    ("Guernsey", "Guernsey"),
    ("Ayrshire", "Ayrshire"),
    ("Brown Swiss", "Brown Swiss"),
    ("Milking Shorthorn", "Milking Shorthorn"),
    ("Dutch Belted", "Dutch Belted"),
    ("Red and White Holstein", "Red and White Holstein"),
    ("Friesian", "Friesian"),
    ("Montbéliarde", "Montbéliarde"),
    ("Normande", "Normande"),
    ("Swedish Red", "Swedish Red"),
    ("Danish Red", "Danish Red"),
    ("Ayshire", "Ayshire"),
    ("Canadienne", "Canadienne"),
    ("Shorthorn", "Shorthorn"),
    ("Simmental", "Simmental"),
    ("Gelbvieh", "Gelbvieh"),
    ("Fleckvieh", "Fleckvieh"),
    ("Norwegian Red", "Norwegian Red"),
    ("Finnish Ayrshire", "Finnish Ayrshire"),
    ("South Devon", "South Devon"),
    ("Holstein-Sahiwal", "Holstein-Sahiwal"),
    ("Meuse-Rhine-Issel", "Meuse-Rhine-Issel"),
    ("British Friesian", "British Friesian"),
    ("Kostroma", "Kostroma"),
    ("Kholmogory", "Kholmogory"),
    ("Red Poll", "Red Poll"),
    ("Murray Grey", "Murray Grey"),
    ("Chianina", "Chianina"),
    ("Charolais", "Charolais"),
    ("Simbrah", "Simbrah"),
]

payment_type = [
    ("Advanced","Advanced"),
    ("After delivery", "After delivery"),
    ("Not paid", "Not paid")
]

class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone_no = models.IntegerField()

    # Custom property to define the username based on name and phone_no
    @property
    def username(self):
        return f"{self.name}{self.phone_no}"
    qty = models.DecimalField(max_digits=10, decimal_places=3)
    rate = models.DecimalField(max_digits=10, decimal_places=3)
    start_date = models.DateField(null=True, blank=True)  # Optional start date
    end_date = models.DateField(null=True, blank=True)    # Optional end date
    def __str__(self):
        return f"{self.name}'s Account"


class HandleCustomer(models.Model):
    account = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    qty = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    rate = models.DecimalField(
        max_digits=100, decimal_places=3, blank=True, null=True)
    paid = models.DecimalField(
        max_digits=100, decimal_places=3, default=0, blank=True, null=True)
    balance = models.DecimalField(
        max_digits=100, decimal_places=3, blank=True, null=True)
    remarks = models.TextField(blank=True)
    date = models.DateField()

    def save(self, *args, **kwargs):
        if not self.qty or self.qty == 0:
            self.qty = self.account.qty
        if not self.rate or self.rate == 0:
            self.rate = self.account.rate
        if not self.amount:
            self.amount = self.qty * Decimal(str(self.rate))
            # Get the cumulative balance for the same account
            previous_balance = (
                HandleCustomer.objects
                .filter(account=self.account)
                # Exclude the current instance from the calculation
                .exclude(pk=self.pk)
                .aggregate(total_balance=models.Sum('amount') - models.Sum('paid'))
            )
            previous_balance = previous_balance['total_balance'] or Decimal(
                '0')
            balance_before_payment = previous_balance + self.amount
            balance_after_payment = balance_before_payment - \
                Decimal(str(self.paid))
            self.balance = balance_after_payment

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account.username} + {self.date}"


class Cow(models.Model):
    tag_id = models.CharField(max_length=255)
    nickname = models.CharField(blank=True, null=True, max_length=255)
    date_of_arrival = models.DateField()
    offspring = models.ManyToManyField(
        'Calf', related_name='parents', blank=True)
    breed = models.CharField(choices=list(dairy_cow_breeds), max_length=30)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nickname or 'Cow'} ({self.tag_id})"


class MilkProduction(models.Model):
    cow = models.ForeignKey(Cow, on_delete=models.CASCADE)
    date = models.DateField()
    morning_milk_quantity = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    evening_milk_quantity = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    morning_time = models.TimeField(null=True, blank=True)
    evening_time = models.TimeField(null=True, blank=True)
    total_milk = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate the total milk before saving the instance
        if self.morning_milk_quantity is not None and self.evening_milk_quantity is not None:
            self.total_milk = self.morning_milk_quantity + self.evening_milk_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cow} - Milk Production"


class Medication(models.Model):
    date = models.DateField()
    Diagnosis = models.TextField()
    doctor = models.CharField(max_length=255, default="Dr. ")
    Medication = models.CharField(max_length=255)
    cows = models.ManyToManyField(Cow, related_name='medications')
    remarks = models.TextField(null=True, blank=True)


def validate_dam(value):
    try:
        cow = Cow.objects.get(tag_id=value)
        return cow
    except Cow.DoesNotExist:
        pass
    raise ValidationError(
        f"{value} is not a valid Cow tag_id. Please make sure the Cow exists in the database.")


class BirthEvent(models.Model):
    date = models.DateField()
    calf_name = models.CharField(max_length=100, blank=True)
    dam = models.ForeignKey(
        Cow, on_delete=models.CASCADE, related_name='calves')
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.calf_name} {self.dam} - {self.date}"


class DryPeriod(models.Model):
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    cow = models.ForeignKey(Cow, on_delete=models.CASCADE,
                            related_name='dry_periods')
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.cow} - Dry Period: {self.start_date} to {self.end_date}"


class HeatPeriod(models.Model):
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    cow = models.ForeignKey(Cow, on_delete=models.CASCADE,
                            related_name='heat_periods')
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.cow} - Heat Period: {self.start_date} to {self.end_date}"


class Calf(models.Model):
    tag_id = models.CharField(max_length=255)
    nickname = models.CharField(blank=True, null=True, max_length=255)
    gender = models.CharField(max_length=10, choices=[("M", "Male"),("F","Female")])
    dob = models.DateField()
    dam = models.ForeignKey(Cow, on_delete=models.CASCADE,
                               related_name='calves_as_dam', null=True, blank=True)
    father = models.CharField(max_length=255, blank=True)
    breed = models.CharField(max_length=100, choices=dairy_cow_breeds)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nickname or 'Calf'} ({self.tag_id})"


class DailyTotalMilk(models.Model):
    date = models.DateField(unique=True)
    total_milk = models.DecimalField(
        max_digits=10, decimal_places=3, default=0)
    sold_milk = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    remaining_milk = models.DecimalField(
        max_digits=10, decimal_places=3, default=0)

    @classmethod
    def update_daily_total(cls, date):
        '''Signal to update daily total milk after each MilkProduction save or delete'''
        
        # Calculate and update the total milk for the given date
        total_milk = MilkProduction.objects.filter(
            date=date).aggregate(total_milk=models.Sum('total_milk'))
        total_milk = total_milk['total_milk'] or 0

        # Calculate the total sold milk for the given date
        sold_milk_pay_as_you_go = PayAsYouGoCustomer.objects.filter(
            date=date).aggregate(total_qty=models.Sum('qty'))['total_qty'] or 0

        sold_milk_handle_customer = HandleCustomer.objects.filter(
            date=date).aggregate(total_qty=models.Sum('qty'))['total_qty']  or 0
        
        # Check for BulkOrder records with delivered unchecked for the given date
        bulk_order_delivered = BulkOrder.objects.filter(date_of_delivery=date).values()
        print(bulk_order_delivered)
        if bulk_order_delivered[0]['delivered']:
                # Calculate the total sold milk when there are no records with delivered=False
            sold_milk_bulk_order = BulkOrder.objects.filter(
                date_of_delivery=date).aggregate(total_sold=models.Sum('quantity'))['total_sold'] or 0
        else:
            sold_milk_bulk_order = 0

        print("sold milk handle customer: ", sold_milk_handle_customer)
        print("sold milk pay as you go: ",sold_milk_pay_as_you_go)
        print("sold milk bulk: ", sold_milk_bulk_order)
        total_sold = sold_milk_pay_as_you_go + sold_milk_handle_customer + sold_milk_bulk_order
        print("Total sold: ",total_sold)

        # Create or get the DailyTotalMilk instance for the date
        daily_total, created = cls.objects.get_or_create(date=date)

        # Update the total milk and total sold fields
        daily_total.total_milk = total_milk
        daily_total.sold_milk = total_sold
        daily_total.remaining_milk = total_milk - total_sold
        print(daily_total.remaining_milk)

        daily_total.save()



class PayAsYouGoCustomer(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(blank=True, null=True, decimal_places=3, max_digits=100)
    qty = models.DecimalField(
        max_digits=100, decimal_places=3)
    rate = models.DecimalField(
        max_digits=100, decimal_places=3)
    paid = models.DecimalField(
        max_digits=100, decimal_places=3, default=0, blank=True, null=True)
    balance = models.DecimalField(
        max_digits=100, decimal_places=3, blank=True, null=True)
    payment_date = models.DateField(default=None, blank=True, null= True)
    remarks = models.TextField(blank=True)
    date = models.DateField()

    def save(self, *args, **kwargs):
        self.amount = self.rate * self.qty if self.rate and self.qty else None
        if not self.paid:
            self.paid = Decimal('0')
        if self.amount is not None:
            self.balance = self.amount - self.paid
        else:
            self.balance = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} + {self.qty} + {self.date}"


class Revenue(models.Model):
    date = models.DateField()
    revenue = models.DecimalField(max_digits=100, decimal_places=3, default=0)
    

    def __str__(self) -> str:
        return f"{self.date} {self.revenue}"


class Expenditure(models.Model):
    date = models.DateField()
    time = models.TimeField(auto_now=False)
    particulars = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    remarks = models.TextField(max_length=150)

    def __str__(self) -> str:
        return f"{self.date} {self.particulars} {self.amount}"
    
class BulkOrder(models.Model):
    date_of_delivery = models.DateField()
    order_time = models.TimeField()
    name_of_client = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    occasion = models.CharField(max_length=100)
    rate = models.DecimalField(default=60, max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=100, decimal_places=3, blank=True, null=True, default=0)
    payment = models.CharField(choices=payment_type, max_length=30)
    paid = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True)
    balance = models.DecimalField(max_digits=100, decimal_places=3, default=0, blank=True, null=True)
    delivered = models.BooleanField(default=False)
    delivery_time = models.CharField(choices=[("Morning", "M"), ("Evening", "E")], max_length=30, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    date = models.DateField()
    remarks = models.TextField(max_length=300)

    def save(self, *args, **kwargs):
        self.amount = self.rate * self.quantity if self.rate and self.quantity else None
        if self.payment in ["Advanced", "After delivery"] and self.amount is not None:
            self.balance = self.amount - self.paid
            if self.balance == Decimal('0'):
                self.is_paid = True
        else:
            self.is_paid = False
            self.paid = Decimal('0')
            self.balance = self.amount - self.paid
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name_of_client}"


#?###########################################################################
#?###########################################################################
#!########################### Django Signals ################################
#!############################# Start Here ##################################
#?###########################################################################
#?###########################################################################
@receiver(post_save, sender=MilkProduction)
@receiver(post_delete, sender=MilkProduction)
@receiver(post_save, sender=PayAsYouGoCustomer)
@receiver(post_save, sender=HandleCustomer)
@receiver(post_delete, sender=HandleCustomer)
@receiver(post_delete, sender=PayAsYouGoCustomer)
def update_daily_total_milk(sender, instance, **kwargs):
    date = instance.date
    DailyTotalMilk.update_daily_total(date)


@receiver(post_delete, sender=BulkOrder)
@receiver(post_save, sender=BulkOrder)
def update_bulk_milk(sender, instance, **kwargs):
    date = instance.date_of_delivery
    print(date)
    DailyTotalMilk.update_daily_total(date)


@receiver(post_save, sender=HandleCustomer)
@receiver(post_delete, sender=HandleCustomer)
def handle_customer_payment(sender, instance, **kwargs):
    update_revenue_record(instance)


@receiver(post_save, sender=PayAsYouGoCustomer)
@receiver(post_delete, sender=PayAsYouGoCustomer)
def pay_as_you_go_customer_payment(sender, instance, **kwargs):
    update_revenue_record(instance)

@receiver(post_save, sender=BulkOrder)
@receiver(post_delete, sender=BulkOrder)
def bulk_order_payment(sender, instance,**kwargs):
    update_revenue_record(instance)

def update_revenue_record(instance):
    if hasattr(instance, 'date'):
        revenue_record, _ = Revenue.objects.get_or_create(date=instance.date)
        total_revenue = HandleCustomer.objects.filter(date=instance.date).aggregate(
            total_revenue=models.Sum('paid'))['total_revenue']
        total_revenue_pay_as_you_go = PayAsYouGoCustomer.objects.filter(
            date=instance.date).aggregate(total_revenue=models.Sum('paid'))['total_revenue']
        
        total_revenue_bulk = BulkOrder.objects.filter(date=instance.date).aggregate(total_revenue=models.Sum('paid'))['total_revenue']

        revenue_record.revenue = (total_revenue or 0) + \
            (total_revenue_pay_as_you_go or 0) + (total_revenue_bulk or 0)
        revenue_record.save()

# signal to update the birthevent and Cow objects whenever a calf is added to the records
@receiver(post_save, sender=Calf)
def create_calf(sender, instance, created, **kwargs):
    if created:
        try:
            birth_event = BirthEvent(date=instance.dob, calf_name=instance.nickname or "", dam=instance.dam, remarks=instance.remarks)
            birth_event.save()
        except birth_event.DoesNotExist:
            pass

        instance.dam.offspring.add(instance)
    
# signal to delete calf from the dam relation 
@receiver(post_delete, sender=Calf)
def delete_calf(sender, instance, **kwargs):
    if instance.dam:
        instance.dam.offspring.remove(instance)