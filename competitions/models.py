from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Competition(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
        ('finished', 'Завершён'),
    ]

    title = models.CharField('Название конкурса', max_length=255)
    description = models.TextField('Описание')
    category = models.CharField('Категория', max_length=255, blank=True)
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='draft')

    rules_file = models.FileField('Файл с правилами (PDF)', upload_to='rules/', blank=True, null=True)

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Конкурс'
        verbose_name_plural = 'Конкурсы'
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Подана'),
        ('under_review', 'На рассмотрении'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Пользователь',
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Конкурс',
    )

    full_name = models.CharField('ФИО участника', max_length=255)
    email = models.EmailField('E-mail')
    school = models.CharField('Школа / колледж / вуз', max_length=255, blank=True)
    grade = models.CharField('Класс / курс', max_length=50, blank=True)

    work_file = models.FileField('Файл работы', upload_to='works/', blank=True, null=True)
    work_link = models.URLField('Ссылка на работу', blank=True)

    status = models.CharField('Статус заявки', max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField('Дата подачи', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} — {self.competition.title}'


class Result(models.Model):
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='result',
        verbose_name='Заявка',
    )
    score = models.DecimalField('Баллы', max_digits=5, decimal_places=2, blank=True, null=True)
    place = models.PositiveIntegerField('Место', blank=True, null=True)
    comment = models.TextField('Комментарий жюри', blank=True)
    published = models.BooleanField('Опубликовано', default=False)

    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'
        ordering = ['place', '-score']

    def __str__(self):
        return f'Результат: {self.application}'
