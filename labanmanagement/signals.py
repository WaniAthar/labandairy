from .models import *

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
    id = instance.id
    print(date)
    DailyTotalMilk.update_daily_total(date, id)


@receiver(post_save, sender=HandleCustomer)
@receiver(post_delete, sender=HandleCustomer)
def handle_customer_payment(sender, instance, **kwargs):
    update_revenue_record(instance)


@receiver(post_save, sender=PayAsYouGoCustomer)
@receiver(post_delete, sender=PayAsYouGoCustomer)
def pay_as_you_go_customer_payment(sender, instance, **kwargs):
    # this small code to update the balance of the customer account 

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


@receiver(post_save, sender=HandleCustomer)
def update_customer_balance_on_create(sender, instance, created, **kwargs):
        customer = instance.account
        customer.balance = instance.balance
        customer.save()
    

@receiver(post_delete, sender=HandleCustomer)
def update_customer_balance_on_delete(sender, instance, **kwargs):
    handle_customer = HandleCustomer.objects.filter(account=instance.account).order_by('id').values('id', 'balance')
    instance.account.balance = handle_customer.last()['balance']
    instance.account.save()