from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from littleutils import setattrs


class CrispyForm(forms.Form):
    helper_attrs = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        setattrs(self.helper, **self.helper_attrs)


class PlaceHolderForm(CrispyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = self.helper.layout = Layout()
        for field_name, field in self.fields.items():
            layout.append(Field(field_name, placeholder=field.label))
        self.helper.form_show_labels = False
