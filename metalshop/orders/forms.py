from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']
        # опційно: можна визначити віджети
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # автозаповнення полів для залогіненого користувача
        if self.request and getattr(self.request, 'user', None) and self.request.user.is_authenticated:
            user = self.request.user
            self.initial.setdefault('first_name', user.first_name or '')
            self.initial.setdefault('last_name', user.last_name or '')
            self.initial.setdefault('email', user.email or '')

    def save(self, commit=True):
        order = super().save(commit=False)

        # прив’язуємо користувача, якщо він є
        if self.request and getattr(self.request, 'user', None) and self.request.user.is_authenticated:
            order.user = self.request.user
        else:
            # якщо в моделі user є null=True — це норм
            # інакше: або заборонити неавторизованих, або кидати ValidationError
            order.user = None

        if commit:
            order.save()
        return order
