"""
Scrap Rates Relational Models.
Models categories and item rate catalog with JSON city prices and relational integrity.
"""

from django.db import models

class ScrapRateCategory(models.Model):
    category_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='📦')
    description = models.TextField(blank=True, default='')
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scrap_rate_categories'
        ordering = ['order']

    def to_dict(self):
        return {
            '_id': str(self.id),
            'id': self.category_id,
            'categoryId': self.category_id,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'order': self.order,
            'active': self.active,
        }

class ScrapItem(models.Model):
    category = models.ForeignKey(
        ScrapRateCategory, on_delete=models.CASCADE, related_name='items'
    )
    item_id = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=120)
    unit = models.CharField(max_length=30, default='kg')
    prices = models.JSONField(default=dict)  # {"delhi-ncr": 15, "bengaluru": 14}
    popular = models.BooleanField(default=False)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, default='📦')
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'scrap_rate_items'
        unique_together = ('category', 'item_id')

    def to_dict(self, city='delhi-ncr'):
        normalized_city = city.lower()
        price_map = self.prices or {}
        effective_price = (
            price_map.get(normalized_city)
            or price_map.get('delhi-ncr')
            or (list(price_map.values())[0] if price_map else 0)
        )
        return {
            '_id': str(self.id),
            'id': self.item_id,
            'itemId': self.item_id,
            'name': self.name,
            'unit': self.unit,
            'prices': price_map,
            'price': effective_price,
            'effectivePrice': effective_price,
            'popular': self.popular,
            'description': self.description,
            'icon': self.icon,
            'active': self.active,
        }
