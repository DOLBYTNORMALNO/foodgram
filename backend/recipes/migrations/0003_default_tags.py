from django.db import migrations


DEFAULT_TAGS = (
    ('Завтрак', '#E26C2D', 'breakfast'),
    ('Обед', '#49B64E', 'lunch'),
    ('Ужин', '#8775D2', 'dinner'),
)


def create_default_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    Tag.objects.bulk_create(
        [Tag(name=name, color=color, slug=slug)
         for name, color, slug in DEFAULT_TAGS],
        ignore_conflicts=True,
    )


def remove_default_tags(apps, schema_editor):
    Tag = apps.get_model('recipes', 'Tag')
    Tag.objects.filter(
        slug__in=[slug for _, _, slug in DEFAULT_TAGS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_tags, remove_default_tags),
    ]
