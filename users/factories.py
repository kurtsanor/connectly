from.models import User
from django.contrib.auth.hashers import make_password

class UserFactory:
    @staticmethod
    def create_user(username, password, email, first_name, last_name, role):
        if role not in dict(User.ROLES):
            raise ValueError(f"Invalid role. Valid roles are {User.ROLES}")
        
        hashed_password = make_password(password)
        
        return User.objects.create(
            username=username,
            password=hashed_password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )


