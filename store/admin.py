from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from .models import *
from accounts.models import TraderProfile


@admin.register(TraderProfile)
class TraderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'approved', 'commission_rate', 'total_parts')
    list_editable = ('approved', 'commission_rate')
    search_fields = ('user__username', 'user__company_name', 'user__email')
    list_filter = ('approved',)
    
    def total_parts(self, obj):
        count = Part.objects.filter(trader=obj.user).count()
        return count
    total_parts.short_description = 'Total Parts'


class CompatibilityInline(admin.TabularInline):
    model = Compatibility
    extra = 1
    autocomplete_fields = ['car_model']


class InventoryLogInline(admin.TabularInline):
    model = InventoryLog
    extra = 0
    readonly_fields = ('created_at', 'created_by', 'log_type', 'quantity', 'notes')
    classes = ['collapse']


class PartImageInline(admin.TabularInline):
    model = PartImage
    extra = 1
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="auto" />', obj.image.url)
        return "No Image"


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    search_fields = ('name', 'sku', 'description', 'oem_number')
    list_filter = ('approved', 'trader', 'category', 'is_active', 'is_featured')
    inlines = [CompatibilityInline, PartImageInline, InventoryLogInline]
    list_display = (
        'name',
        'trader',
        'category',
        'price',
        'quantity',
        'stock_status_colored',
        'is_active',
        'approved',
        'is_featured',
        'view_orders',
    )
    list_editable = ('is_active', 'approved', 'is_featured')
    actions = ['restock_action', 'toggle_active', 'approve_parts', 'unapprove_parts', 'mark_as_featured']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('trader', 'category', 'name', 'description', 'sku', 'oem_number')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'quantity', 'low_stock_threshold', 'reorder_quantity')
        }),
        ('Status', {
            'fields': ('is_active', 'approved', 'is_featured', 'warranty_months')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_trader and not request.user.is_superuser:
            return qs.filter(trader=request.user)
        return qs

    def formfield_for_foreign_key(self, db_field, request, **kwargs):
        if db_field.name == "trader" and not request.user.is_superuser:
            kwargs["queryset"] = User.objects.filter(id=request.user.id)
            kwargs["initial"] = request.user
        return super().formfield_for_foreign_key(db_field, request, **kwargs)

    @admin.action(description='Approve selected parts')
    def approve_parts(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f'{updated} parts have been approved.')

    @admin.action(description='Unapprove selected parts')
    def unapprove_parts(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(request, f'{updated} parts have been unapproved.')

    def stock_status_colored(self, obj):
        status = obj.stock_status
        if status == 'out_of_stock':
            return format_html('<span style="color: red; font-weight: bold;">Out of Stock</span>')
        elif status == 'low_stock':
            return format_html('<span style="color: orange; font-weight: bold;">Low Stock</span>')
        return format_html('<span style="color: green; font-weight: bold;">In Stock</span>')
    
    stock_status_colored.short_description = 'Stock Status'
    stock_status_colored.admin_order_field = 'quantity'

    @admin.action(description='Restock selected parts')
    def restock_action(self, request, queryset):
        for part in queryset:
            part.restock(part.reorder_quantity, request.user)
        self.message_user(request, f'{queryset.count()} parts have been restocked.')

    @admin.action(description='Toggle active status')
    def toggle_active(self, request, queryset):
        for part in queryset:
            part.is_active = not part.is_active
            part.save()
        self.message_user(request, f'Active status toggled for {queryset.count()} parts.')
    
    @admin.action(description='Mark as featured')
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} parts marked as featured.')
    
    def view_orders(self, obj):
        count = OrderItem.objects.filter(part=obj).count()
        if count:
            url = reverse('admin:store_orderitem_changelist') + f'?part__id__exact={obj.id}'
            return format_html('<a href="{}">{} orders</a>', url, count)
        return "0 orders"
    
    view_orders.short_description = 'Orders'


@admin.register(CategoryParent)
class CategoryParentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'child_categories_count', 'part_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    
    def child_categories_count(self, obj):
        return obj.children.count()
    child_categories_count.short_description = 'Child Categories'
    
    def part_count(self, obj):
        return obj.parts.count()
    part_count.short_description = 'Parts'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'part_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('parent',)
    
    def part_count(self, obj):
        return obj.parts.count()
    part_count.short_description = 'Parts'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'founded', 'headquarters', 'model_count')
    search_fields = ('name', 'headquarters')
    
    def model_count(self, obj):
        return obj.models.count()
    model_count.short_description = 'Models'


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'production_period', 'compatible_parts_count')
    list_filter = ('brand', 'production_start')
    search_fields = ('name', 'brand__name')
    autocomplete_fields = ['brand']
    
    def production_period(self, obj):
        end = obj.production_end or 'present'
        return f"{obj.production_start} - {end}"
    
    def compatible_parts_count(self, obj):
        return obj.compatibility_set.count()
    compatible_parts_count.short_description = 'Compatible Parts'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('part', 'quantity', 'price', 'supplier', 'line_total')
    
    def line_total(self, obj):
        return obj.price * obj.quantity
    line_total.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'item_count', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'tracking_number')
    readonly_fields = ('total', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    date_hierarchy = 'created_at'
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'
    
    @admin.action(description='Mark as processing')
    def mark_as_processing(self, request, queryset):
        queryset.update(status='PROCESSING')
        self.message_user(request, f'{queryset.count()} orders marked as processing.')
    
    @admin.action(description='Mark as shipped')
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='SHIPPED')
        self.message_user(request, f'{queryset.count()} orders marked as shipped.')
    
    @admin.action(description='Mark as delivered')
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='DELIVERED')
        self.message_user(request, f'{queryset.count()} orders marked as delivered.')
    
    @admin.action(description='Mark as cancelled')
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED')
        self.message_user(request, f'{queryset.count()} orders marked as cancelled.')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'part', 'quantity', 'price', 'total', 'supplier')
    list_filter = ('order__status', 'supplier')
    search_fields = ('order__id', 'part__name', 'supplier__username')
    
    def total(self, obj):
        return obj.price * obj.quantity
    total.short_description = 'Total'


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('part', 'quantity', 'log_type', 'created_at', 'created_by')
    list_filter = ('log_type', 'created_at')
    search_fields = ('part__name', 'notes', 'created_by__username')
    readonly_fields = ('part', 'quantity', 'log_type', 'notes', 'created_at', 'created_by')
    date_hierarchy = 'created_at'


@admin.register(StockReservation)
class StockReservationAdmin(admin.ModelAdmin):
    list_display = ('part', 'quantity', 'session_key', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('part__name', 'session_key')
    
    def is_expired(self, obj):
        from django.utils import timezone
        return obj.expires_at < timezone.now()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
