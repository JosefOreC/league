from django.db import models

class UserModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    email = models.EmailField(unique=True, max_length=255)
    password_hash = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    rol = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    birth_date = models.DateField()
    attempts = models.IntegerField(default=0)
    blocked_until = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "authentication_user"

    def __str__(self):
        return f"User({self.id} - {self.email})"
