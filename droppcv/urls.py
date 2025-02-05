from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
# schema_view = get_schema_view(
#     openapi.Info(
#         title="My API",
#         default_version='v1',
#         description="My API description",
#         terms_of_service="https://www.example.com/terms/",
#         contact=openapi.Contact(email="contact@example.com"),
#         license=openapi.License(name="Awesome License"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

urlpatterns = [
    path('', admin.site.urls),
    path('api/', include('accounts.urls')),
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)