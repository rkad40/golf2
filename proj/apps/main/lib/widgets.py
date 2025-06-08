from django.forms.widgets import Input, DateTimeInput

class ReadOnlyInput(Input):
    input_type = 'text'
    template_name = 'main/widgets/read_only_input.html'

class DateTimeReadOnlyInput(DateTimeInput):
    # input_type = 'text'
    template_name = 'main/widgets/datetime_read_only_input.html'

