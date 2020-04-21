from django.db import models


class Users(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=10)
    password = models.CharField(max_length=20)
    image = models.TextField()
    is_committee_member = models.IntegerField(default=0)
    is_approved = models.IntegerField(default=0)

    class Meta:
        db_table = 'users'


class MaintenanceTxns(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField()

    class Meta:
        db_table = 'maintenance_txns'
