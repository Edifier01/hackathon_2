from django import forms
from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['full_name', 'email', 'school', 'grade', 'work_file', 'work_link']
        labels = {
            'full_name': 'ФИО участника',
            'email': 'E-mail',
            'school': 'Школа / колледж / вуз',
            'grade': 'Класс / курс',
            'work_file': 'Файл работы',
            'work_link': 'Ссылка на работу',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
