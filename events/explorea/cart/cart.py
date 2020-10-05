from django.conf import settings

from explorea.events.models import EventRun
from .forms import CartAddForm

class Cart:

    def __init__(self, session):
        self.session = session
        self.cart = session.get(settings.CART_SESSION_ID)
        if not self.cart:
            self.cart = self.session[settings.CART_SESSION_ID] = {}

    def __getitem__(self, item):
        return self.cart[str(item)]

    def __contains__(self, item):
        return item in self.cart

    def __eq__(self, other):
        return self.cart == other
    
    def __iter__(self):
        runs = EventRun.objects.filter(id__in=self.cart.keys())

        for run in runs:
            self.cart[str(run.id)]['object'] = run

        for item_id, data in self.cart.items():
            data['total_price'] = data['quantity'] * data['object'].price
            yield data    
    
    def __len__(self):
        return len(self.cart)

    def is_empty(self):
        return len(self.cart) == 0

    def add(self, product_id, quantity=1, update=False, **kwargs):
        product_id = str(product_id)
        if product_id in self.cart and not update:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart.update({str(product_id): {'quantity':quantity}})
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            self.cart.pop(product_id)
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def get(self, product_id):
        try:
            return self.cart[str(product_id)]['quantity']
        except KeyError:
            return 0

    def prepare_to_render(self, update):
        # import pdb; pdb.set_trace()
        for item in self:
            form_initial = {
                'quantity':item['quantity'],
                'update': update
            }
            item['cartadd_form'] = CartAddForm(initial=form_initial)