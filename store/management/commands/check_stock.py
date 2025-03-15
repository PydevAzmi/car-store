from django.core.management.base import BaseCommand
from django.db.models import Q

from ...models import Part


class Command(BaseCommand):
    help = 'Check stock levels and generate reorder recommendations'

    def handle(self, *args, **options):
        low_stock = Part.objects.filter(
            Q(quantity__lte=F('low_stock_threshold')) & Q(is_active=True)
        )

        for part in low_stock:
            self.stdout.write(
                f"Low stock: {part.name} (Current: {part.quantity}, "
                f"Threshold: {part.low_stock_threshold})"
            )
