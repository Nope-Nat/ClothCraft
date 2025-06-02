from fastapi.templating import Jinja2Templates
from utils.auth_utils import get_current_user

# Custom template response class that adds global context
class CustomTemplates:
    def __init__(self, directory: str):
        self.templates = Jinja2Templates(directory=directory)
    
    async def TemplateResponse(self, name: str, context: dict, **kwargs):
        # Add global data to every template context
        request = context.get('request')
        if request:
            context['current_user'] = await get_current_user(request)
            context['current_path'] = str(request.url.path)
            context['current_url'] = str(request.url)
            # Add cart count here if you have a cart repository
            # context['cart_count'] = await get_cart_count(context['current_user'])
        
        return self.templates.TemplateResponse(name, context, **kwargs)

# Use custom template class
templates = CustomTemplates(directory="templates")