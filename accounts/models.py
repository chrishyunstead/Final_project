from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models


class SiggAreas(models.Model):
    sigg_no = models.PositiveSmallIntegerField(primary_key=True)
    adm_code = models.CharField(max_length=10)
    sido_name = models.CharField(max_length=10)
    sigg_name = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = "sigg_areas"

    def __str__(self):
        return f"{self.sido_name} {self.sigg_name}"


class UserManager(BaseUserManager):
    def create_user(self, user_id, username=None, password=None, **extra_fields):
        if not user_id:
            raise ValueError("The User ID field must be set")
        user = self.model(user_id=user_id, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(user_id, username, password, **extra_fields)


class User(AbstractUser):
    user_no = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20)
    user_id = models.CharField(max_length=12, unique=True)
    email = models.CharField(unique=True, max_length=45)
    birth_date = models.DateField(null=True, blank=True)
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, null=True, blank=True
    )
    cellphone = models.CharField(max_length=15, null=True, blank=True)

    sido_name = models.CharField(max_length=10)
    sigg_name = models.CharField(max_length=10)
    nickname = models.CharField(max_length=10)
    position_1 = models.CharField(max_length=10)
    ability_1 = models.CharField(max_length=10)
    level = models.IntegerField(null=True, blank=True)
    introduction = models.CharField(max_length=55, blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    image_url = models.ImageField(blank=True, null=True)
    team_no = models.ForeignKey(
        "team.Team",
        on_delete=models.SET_NULL,
        db_column="team_no",
        related_name="user_team_no",
        null=True,
        blank=True,
    )
    USERNAME_FIELD = "user_id"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        managed = True
        db_table = "authentication"

    def __str__(self):
        return self.user_id

    def add_perm(self, perm_name: str) -> None:
        user = self
        app_label, codename = perm_name.split(".", 1)
        permission = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )
        user.user_permissions.add(permission)


class SuperUserManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_superuser=True)


class SuperUser(User):
    objects = SuperUserManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.is_superuser = True
        super().save(*args, **kwargs)


class Group(models.Model):
    group_no = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = "group"

    def add_perm(self, perm_name: str) -> None:
        app_label, codename = perm_name.split(".", 1)
        permission = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )
        self.permissions.add(permission)


class Profile(models.Model):
    profile_no = models.AutoField(primary_key=True)
    user_no = models.OneToOneField(
        "User",
        models.DO_NOTHING,
        db_column="user_no",
        related_name="profile_user_no",
    )
    username = models.ForeignKey(
        "User",
        models.DO_NOTHING,
        db_column="username",
        related_name="profile_username",
    )
    nickname = models.ForeignKey(
        "User",
        models.DO_NOTHING,
        db_column="nickname",
        related_name="profile_nickname",
    )
    activity_area = models.ForeignKey(
        "User",
        models.DO_NOTHING,
        db_column="sigg_name",
        related_name="profile_activity_area",
    )

    ability_1 = models.ForeignKey(
        "User",
        models.DO_NOTHING,
        db_column="ability_1",
        related_name="profile_ability",
    )
    position_1 = models.ForeignKey(
        "User",
        models.DO_NOTHING,
        db_column="position_1",
        related_name="profile_position",
    )
    level = models.ForeignKey(
        "User",
        models.DO_NOTHING,
        db_column="level",
        related_name="profile_level",
    )
    image_url = models.ForeignKey(
        "User",
        models.DO_NOTHING,
        db_column="image_url",
        related_name="profile_image_url",
    )
    group_no = models.ForeignKey(
        "Group",
        models.DO_NOTHING,
        db_column="group_no",
        related_name="profile_group",
    )
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "profile"
