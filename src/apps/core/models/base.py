from django.db import models


class BaseModel(models.Model):

    id = models.AutoField(primary_key=True)

    class Meta:
        abstract = True



class Nameable(models.Model):

    name = models.CharField(max_length=100)

    class Meta:
        abstract = True



class Creatable(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True



class Updatable(models.Model):

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True