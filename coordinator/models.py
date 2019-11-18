from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from coordinator.api.models.study import Study


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        user = self.model(
            username=username,
            auth_groups=[],
            auth_roles=[],
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username=username,
            email=self.normalize_email(email),
        )
        user.is_superuser = True
        user.auth_groups = []
        user.auth_roles = ['ADMIN']
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """
    Stores only basic information about the user, namely their primary id
    that may be used to fetch their full profile.
    """
    USERNAME_FIELD = "sub"
    # This overrides the AbstractUser username which has a unique contraint
    # on it in preference of the sub being the unique field.
    username = models.CharField(_("username"), max_length=150, unique=False)

    sub = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        help_text="The subject of the JWT and primary user identifier",
    )
    auth_groups = ArrayField(models.CharField(max_length=100, blank=True))
    auth_roles = ArrayField(models.CharField(max_length=100, blank=True))
    picture = models.CharField(max_length=500, blank=True)
    slack_notify = models.BooleanField(
        default=False,
        help_text="Whether the user has enabled slack notifications",
    )
    slack_member_id = models.CharField(
        default="",
        blank=True,
        max_length=10,
        help_text="The user's slack member id",
    )

    objects = MyUserManager()

    @property
    def is_admin(self):
        return 'ADMIN' in self.auth_roles
