from django import forms

class ManuallyScheduleForm(forms.ModelForm):
    schedule = forms.ModelChoiceField(
        queryset=Schedule.objects.all('shortName'),
        to_field_name='schedule',
        required=True,
        initial=0)
    

    def __init__(self, *args, **kwargs):
        super(ManuallyScheduleForm, self).__init__(*args, **kwargs)
        

    class Meta:
        model = Schedule
        fields = [
            'schedule'
        ]

    def save(self, user):
        manually_scheduled_record = super(ManuallyScheduleForm, self).save(commit=False)
       
        manually_scheduled_record.save()
        return manually_scheduled_record
