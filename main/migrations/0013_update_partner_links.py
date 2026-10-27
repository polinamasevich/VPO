from django.db import migrations


def update_partners(apps, schema_editor):
    Partner = apps.get_model('main', 'Partner')
    Partner.objects.filter(name='Белорусские сыры').update(name='Пицца Темпо', website='https://www.pizzatempo.by/')
    Partner.objects.filter(name='Мука Беларуси').update(name='Белпочта', website='https://www.belpost.by/')
    Partner.objects.filter(name='Доставка Минск').update(name='Беларусбанк', website='https://belarusbank.by/')


class Migration(migrations.Migration):
    dependencies = [('main', '0012_review_user')]
    operations = [migrations.RunPython(update_partners, migrations.RunPython.noop)]
