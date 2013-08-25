from django.dispatch import receiver
from django.db.models.signals import pre_save
from schedule.models import ScheduleSet

@receiver(pre_save, sender=ScheduleSet)
def remove_replacement_demand_when_replacement_occurs(sender, instance, **kwargs):
    if instance.replacement_demand:
        schedule = ScheduleSet.objects.get(pk=instance.pk)
        if not schedule.teacher == instance.teacher:
            instance.replacement_demand = False
