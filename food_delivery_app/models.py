# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Cars(models.Model):
    license_plate_no = models.CharField(db_column='License_plate_no', primary_key=True, max_length=20)  # Field name made lowercase.
    brand = models.CharField(db_column='Brand', max_length=50, blank=True, null=True)  # Field name made lowercase.
    model = models.CharField(db_column='Model', max_length=50, blank=True, null=True)  # Field name made lowercase.
    color = models.CharField(db_column='Color', max_length=30, blank=True, null=True)  # Field name made lowercase.
    active_registration_status = models.IntegerField(db_column='Active_registration_status', blank=True, null=True)  # Field name made lowercase.
    driver = models.ForeignKey('Drivers', models.DO_NOTHING, db_column='Driver_ID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Cars'


class Customers(models.Model):
    customer_id = models.CharField(db_column='Customer_ID', primary_key=True, max_length=50, unique=True)  # 主键字段
    fname = models.CharField(db_column='Fname', max_length=50)
    lname = models.CharField(db_column='Lname', max_length=50)
    street = models.CharField(db_column='Street', max_length=100, blank=True, null=True)
    city = models.CharField(db_column='City', max_length=50, blank=True, null=True)
    state = models.CharField(db_column='State', max_length=50, blank=True, null=True)
    zipcode = models.CharField(db_column='Zipcode', max_length=20, blank=True, null=True)
    phone = models.CharField(db_column='Phone', max_length=20, blank=True, null=True)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)  # 新增字段
    email = models.EmailField(unique=True, blank=True, null=True)  # 新增字段
    password = models.CharField(max_length=255, blank=True, null=True)  # 新增字段

    class Meta:
        managed = True
        db_table = 'Customers'


class Drivers(models.Model):
    driver_id = models.CharField(db_column='Driver_ID', primary_key=True, max_length=50)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Drivers'


class EmergencyContacts(models.Model):
    driver = models.OneToOneField(Drivers, models.DO_NOTHING, db_column='Driver_ID', primary_key=True)  # Field name made lowercase.
    contact_name = models.CharField(db_column='Contact_Name', max_length=100)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Emergency_Contacts'
        unique_together = (('driver', 'contact_name'),)


class Members(models.Model):
    customer = models.OneToOneField(Customers, models.DO_NOTHING, db_column='Customer_ID', primary_key=True)  # Field name made lowercase.
    subscription_end_date = models.DateField()

    class Meta:
        # managed = False
        db_table = 'Members'


class MenuItems(models.Model):
    res = models.OneToOneField('Restaurants', models.DO_NOTHING, db_column='Res_ID', primary_key=True)  # Field name made lowercase.
    item_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        # managed = False
        db_table = 'Menu_items'
        unique_together = (('res', 'item_name'),)


class OrderItems(models.Model):
    order = models.OneToOneField('Orders', models.DO_NOTHING, db_column='Order_ID', primary_key=True)  # Field name made lowercase.
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()

    class Meta:
        # managed = False
        db_table = 'Order_items'
        unique_together = (('order', 'item_name'),)


class Orders(models.Model):
    order_id = models.CharField(db_column='Order_ID', primary_key=True, max_length=50)  # Field name made lowercase.
    customer = models.ForeignKey(Customers, models.DO_NOTHING, db_column='Customer_ID', blank=True, null=True)  # Field name made lowercase.
    restaurant = models.ForeignKey('Restaurants', models.DO_NOTHING, db_column='Restaurant_ID', blank=True, null=True)  # Field name made lowercase.
    driver = models.ForeignKey(Drivers, models.DO_NOTHING, db_column='Driver_ID', blank=True, null=True)  # Field name made lowercase.
    payment = models.ForeignKey('Payments', models.DO_NOTHING, db_column='Payment_ID', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20, blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp')  # Field name made lowercase.
    estimated_arrival = models.DateTimeField(db_column='Estimated_arrival', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Orders'


class Payments(models.Model):
    payment_id = models.CharField(db_column='Payment_ID', primary_key=True, max_length=50)  # Field name made lowercase.
    method = models.CharField(db_column='Method', max_length=50)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp')  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Payments'


class Restaurants(models.Model):
    res_id = models.CharField(db_column='Res_ID', primary_key=True, max_length=50)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100)  # Field name made lowercase.
    street = models.CharField(db_column='Street', max_length=100, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=50, blank=True, null=True)  # Field name made lowercase.
    zipcode = models.CharField(db_column='Zipcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=20, blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Restaurants'


class Reviews(models.Model):
    review_id = models.CharField(db_column='Review_ID', primary_key=True, max_length=50)  # Field name made lowercase.
    customer = models.ForeignKey(Customers, models.DO_NOTHING, db_column='Customer_ID', blank=True, null=True)  # Field name made lowercase.
    res = models.ForeignKey(Restaurants, models.DO_NOTHING, db_column='Res_ID', blank=True, null=True)  # Field name made lowercase.
    score = models.IntegerField(db_column='Score', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Reviews'
