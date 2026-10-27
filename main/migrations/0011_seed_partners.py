from django.db import migrations


def add_partners(apps, schema_editor):
    Partner = apps.get_model('main', 'Partner')
    for name, website in [
        ('Белорусские сыры', 'https://www.belaruskie-syry.by/'),
        ('Мука Беларуси', 'https://www.belmuka.by/'),
        ('Доставка Минск', 'https://minsk.gov.by/'),
    ]:
        Partner.objects.get_or_create(name=name, defaults={'website': website})


def remove_partners(apps, schema_editor):
    apps.get_model('main', 'Partner').objects.filter(name__in=['Белорусские сыры', 'Мука Беларуси', 'Доставка Минск']).delete()


class Migration(migrations.Migration):
    dependencies = [('main', '0010_partner_companyinfo_certificate_text_and_more')]
    operations = [migrations.RunPython(add_partners, remove_partners)]
