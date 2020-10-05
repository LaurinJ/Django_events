from .cart import Cart

class CartMiddleware:

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.cart = Cart(request.session)

    def process_template_response(self, request, response):
        cart_update_views = [
            'CartDetailView',
        ]
        if 'view' in response.context_data:
            update = response.context_data['view'].__class__.__name__ in cart_update_views
            request.cart.prepare_to_render(update=update)
        response.context_data['cart'] = request.cart
        return response