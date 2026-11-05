from django.db import migrations

GENRES = [
    '소설/시/희곡', '경제/경영', '자기계발', '인문/교양',
    '취미/실용', '어린이/청소년', '과학',
]


def add_categories(apps, schema_editor):
    Category = apps.get_model('accounts', 'Category')
    for name in GENRES:
        Category.objects.get_or_create(name=name)


def remove_categories(apps, schema_editor):
    Category = apps.get_model('accounts', 'Category')
    Category.objects.filter(name__in=GENRES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_category_user_preferred_categories'),  # 실제 이름 유지
    ]

    operations = [
        migrations.RunPython(add_categories, remove_categories),
    ]