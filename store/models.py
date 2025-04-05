import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify

from accounts.models import Location, TraderProfile

User = get_user_model()
NEW = 'NEW'
RESTOCK = 'RESTOCK'
ADJUSTMENT = 'ADJUSTMENT'
TYPE_CHOICES = [
    (NEW, 'New Stock'),
    (RESTOCK, 'Restock'),
    (ADJUSTMENT, 'Adjustment'),
]

STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('PROCESSING', 'Processing'),
    ('SHIPPED', 'Shipped'),
    ('DELIVERED', 'Delivered'),
    ('CANCELLED', 'Cancelled'),
]

SHIPPING_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('IN_PROGRESS', 'In Progress'),
    ('DELIVERED', 'Delivered'),
    ('RETURNED', 'Returned'),
]

PAYMENT_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('COMPLETED', 'Completed'),
    ('FAILED', 'Failed'),
]


class CategoryParent(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories Parents"
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        CategoryParent,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
    )
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return f"{self.parent} - {self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.parent} {self.name}")
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    founded = models.PositiveIntegerField(null=True, blank=True)
    headquarters = models.CharField(max_length=255, blank=True)
    icon = models.ImageField(upload_to='brand_icons/', blank=True, null=True)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=255)
    production_start = models.PositiveIntegerField()
    production_end = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.brand.name} {self.name} ({self.production_start}-{self.production_end or 'present'})"


class Part(models.Model):
    trader = models.ForeignKey(
        TraderProfile, on_delete=models.CASCADE, related_name='parts'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='parts'
    )
    category_parent = models.ForeignKey(
        CategoryParent, on_delete=models.CASCADE, related_name='parts'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    compatible_models = models.ManyToManyField(CarModel, through='Compatibility')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    reorder_quantity = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)  # Admin approval
    oem_number = models.CharField(max_length=255, blank=True)
    warranty_months = models.PositiveIntegerField(default=12)
    is_featured = models.BooleanField(default=False)

    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'out_of_stock'
        if self.quantity <= self.low_stock_threshold:
            return 'low_stock'
        return 'in_stock'

    def restock(self, quantity, user):
        self.quantity += quantity
        self.save()
        InventoryLog.objects.create(
            part=self,
            quantity=quantity,
            log_type=RESTOCK,
            created_by=user,
            notes=f"Restocked {quantity} units",
        )

    def __str__(self):
        return self.name


class Compatibility(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    car_model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('part', 'car_model')

    def __str__(self):
        return f"{self.part.name} compatible with {self.car_model}"


class PartImage(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='part_images/')
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.part.name}"


class InventoryLog(models.Model):
    part = models.ForeignKey(
        Part, on_delete=models.CASCADE, related_name='inventory_logs'
    )
    quantity = models.IntegerField()
    log_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_number = models.UUIDField(
        default=uuid.uuid4().hex[:20].upper(), editable=False
    )
    notes = models.TextField(blank=True)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.tracking_number

    def save(self, *args, **kwargs):
        total_commission = 0
        for item in self.items.all():
            commission = (
                item.quantity * item.price * item.part.trader.commission_rate / 100
            )
            total_commission += commission
        self.commission = total_commission  # Add a commission field to the Order model
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.part.quantity -= self.quantity
            self.part.save()
            InventoryLog.objects.create(
                part=self.part,
                quantity=-self.quantity,
                log_type=ADJUSTMENT,
                notes=f"Order {self.order.id} deduction",
                created_by=self.order.user,
            )
        super().save(*args, **kwargs)


class StockReservation(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Reservation for {self.part.name} ({self.quantity})"


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name='payment'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"Payment for Order {self.order.id}"

    def clean(self):
        if self.amount != self.order.total:
            raise ValidationError("Payment amount must match order total")


class Shipping(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="shipping"
    )
    carrier = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=SHIPPING_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_number = models.UUIDField(
        default=uuid.uuid4().hex[:20].upper(), editable=False
    )
    estimated_delivery = models.DateField(null=True, blank=True)
    shipping_address = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='shipments',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Shipping for Order {self.order.id}"

    def save(self, *args, **kwargs):
        if not self.shipping_address:
            if not self.order.user.location:
                raise ValidationError("Shipping address is required")
            self.shipping_address = self.order.user.location
        super().save(*args, **kwargs)
