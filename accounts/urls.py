from django.urls import path
from .views import (
    create_user,
    update_user,
    logout_user,
    current_user,
    get_employees,
    get_employers,
    get_user_by_id,
    update_employee,
    update_employer,
    service_list,
    employee_search,
    obtain_auth_token
)

urlpatterns = [
    path('register/', create_user, name='register'),
    path('update/', update_user, name='update_user'),
    path('logout/', logout_user, name='logout_user'),
    path('me/', current_user, name='current_user'),
    path('employees/', get_employees, name='get_employees'),
    path('employee/profile/edit/', update_employee, name='employee-profile-edit'),
    path('employer/profile/edit/', update_employer, name='employer-profile-edit'),
    path('services/', service_list, name='service-list'),
    path('employee/search/', employee_search, name='employee-search'),
    path('user/<int:id>/', get_user_by_id, name='get_user_by_id'),
    path('login/', obtain_auth_token, name='login'),
]
