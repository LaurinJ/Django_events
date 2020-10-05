from django import forms

from explorea.events.models import EventRun

class PositiveIntegerField(forms.IntegerField):

    def validate(self, value):
        super().validate(value)
        if value < 1:
            raise forms.ValidationError('Only positive integer allowed')

class CartAddForm(forms.ModelForm):
    quantity = PositiveIntegerField(initial=0)
    product_id = forms.CharField(max_length=10, widget=forms.HiddenInput())
    update = forms.BooleanField(required=False, initial=False, 
                                    widget=forms.HiddenInput)
    current_quantity = forms.IntegerField(required=False, initial=0, 
                                   widget=forms.HiddenInput)

    class Meta:
        model = EventRun
        fields = [
            'quantity', 
            'product_id', 
            'update', 
            'current_quantity',
        ]

    def clean(self):
        super().clean()
        product_id = self.cleaned_data.get('product_id')
        quantity = self.cleaned_data.get('quantity')
        update = self.cleaned_data.get('update')
        current_quantity = 0 if update else  self.cleaned_data.get('current_quantity')
        
        if all([product_id, quantity]) and current_quantity >= 0:
            
            try:
                run = self._meta.model.objects.get(pk=int(product_id))

                if run.seats_available < int(quantity) + int(current_quantity):
                    self.add_error('quantity', 'Not enough items available')
            except self._meta.model.DoesNotExist:
                self.add_error('product_id', 'Requested item does not exist')
