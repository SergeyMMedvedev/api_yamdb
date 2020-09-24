from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=False,
                          is_admin=False,
                          is_superuser=False,
                          username=username
                          )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)

        user = self.model(email=email,
                          is_staff=True,
                          is_admin=True,
                          is_superuser=True,
                          username=username,
                          role='admin')
        user.set_password(password)
        user.save(using=self._db)
        return user
