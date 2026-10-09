"""
Scrap Rates Views and Auto-Seed logic.
"""

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from common.permissions import IsAdminRole
from common.utils import api_success, api_failure
from rates.models import ScrapRateCategory, ScrapItem

DEFAULT_SEED_DATA = [
    {
        'categoryId': 'normal',
        'name': 'Paper & Cardboard',
        'icon': '📰',
        'description': 'Newspaper, books, corrugated boxes & packaging',
        'order': 1,
        'items': [
            {'itemId': 'newspaper', 'name': 'Newspaper (Raddi)', 'unit': 'kg', 'prices': {'delhi-ncr': 15, 'bengaluru': 14, 'mumbai': 15}, 'popular': True, 'description': 'Old newspapers, raddi', 'icon': '🗞️'},
            {'itemId': 'office-paper', 'name': 'Office Paper (A3/A4)', 'unit': 'kg', 'prices': {'delhi-ncr': 14, 'bengaluru': 14, 'mumbai': 13}, 'popular': False, 'description': 'White papers, documents, printouts', 'icon': '📄'},
            {'itemId': 'books', 'name': 'Books & Magazines', 'unit': 'kg', 'prices': {'delhi-ncr': 12, 'bengaluru': 12, 'mumbai': 12}, 'popular': True, 'description': 'School books, notebooks, novels, magazines', 'icon': '📚'},
            {'itemId': 'cardboard', 'name': 'Cardboard / Carton', 'unit': 'kg', 'prices': {'delhi-ncr': 8, 'bengaluru': 6, 'mumbai': 8}, 'popular': True, 'description': 'Corrugated shipping boxes, carton packaging', 'icon': '📦'},
        ],
    },
    {
        'categoryId': 'metals',
        'name': 'Metals & Utensils',
        'icon': '🔩',
        'description': 'Iron, Steel, Aluminium, Brass & Copper scrap',
        'order': 2,
        'items': [
            {'itemId': 'iron', 'name': 'Iron (Loha)', 'unit': 'kg', 'prices': {'delhi-ncr': 25, 'bengaluru': 23, 'mumbai': 26}, 'popular': True, 'description': 'Iron rods, grills, metal scraps, bed frames', 'icon': '🔩'},
            {'itemId': 'steel', 'name': 'Steel (Stainless)', 'unit': 'kg', 'prices': {'delhi-ncr': 42, 'bengaluru': 35, 'mumbai': 40}, 'popular': True, 'description': 'Steel utensils, sink parts, stainless steel scrap', 'icon': '🥄'},
            {'itemId': 'aluminium', 'name': 'Aluminium Scrap', 'unit': 'kg', 'prices': {'delhi-ncr': 112, 'bengaluru': 105, 'mumbai': 110}, 'popular': True, 'description': 'Aluminium utensils, door frames, sections', 'icon': '🥫'},
            {'itemId': 'brass', 'name': 'Brass (Peetal)', 'unit': 'kg', 'prices': {'delhi-ncr': 325, 'bengaluru': 325, 'mumbai': 330}, 'popular': True, 'description': 'Brass pooja items, taps, decorative items', 'icon': '🪔'},
            {'itemId': 'copper', 'name': 'Copper (Taamba)', 'unit': 'kg', 'prices': {'delhi-ncr': 505, 'bengaluru': 505, 'mumbai': 510}, 'popular': True, 'description': 'Copper wires, utensils, motor winding copper', 'icon': '🥉'},
        ],
    },
    {
        'categoryId': 'appliances',
        'name': 'Large Appliances',
        'icon': '❄️',
        'description': 'Air Conditioners, Refrigerators, Washing Machines',
        'order': 3,
        'items': [
            {'itemId': 'ac-15ton', 'name': 'Split / Window AC (1.5 Ton)', 'unit': 'unit', 'prices': {'delhi-ncr': 5150, 'bengaluru': 4150, 'mumbai': 5000}, 'popular': True, 'description': 'Indoor + Outdoor unit / Window AC with compressor', 'icon': '❄️'},
            {'itemId': 'fridge-double-door', 'name': 'Double Door Refrigerator', 'unit': 'unit', 'prices': {'delhi-ncr': 1350, 'bengaluru': 1200, 'mumbai': 1300}, 'popular': True, 'description': 'Frost-free double door fridge', 'icon': '🧊'},
            {'itemId': 'fridge-single-door', 'name': 'Single Door Refrigerator', 'unit': 'unit', 'prices': {'delhi-ncr': 1100, 'bengaluru': 1000, 'mumbai': 1050}, 'popular': True, 'description': 'Direct cool single door fridge', 'icon': '🧊'},
            {'itemId': 'wm-front-load', 'name': 'Automatic Washing Machine', 'unit': 'unit', 'prices': {'delhi-ncr': 1350, 'bengaluru': 1200, 'mumbai': 1300}, 'popular': True, 'description': 'Front / Top load automatic washing machine', 'icon': '🧺'},
            {'itemId': 'microwave', 'name': 'Microwave Oven', 'unit': 'unit', 'prices': {'delhi-ncr': 350, 'bengaluru': 250, 'mumbai': 300}, 'popular': False, 'description': 'Solo, grill or convection microwave', 'icon': '🍲'},
        ],
    },
    {
        'categoryId': 'electronics',
        'name': 'Small Appliances & E-Waste',
        'icon': '🔌',
        'description': 'Batteries, Inverters, Laptops, CPUs & Electronics',
        'order': 4,
        'items': [
            {'itemId': 'inverter-battery', 'name': 'Lead Acid Inverter Battery', 'unit': 'kg', 'prices': {'delhi-ncr': 81, 'bengaluru': 72, 'mumbai': 80}, 'popular': True, 'description': '100Ah - 220Ah tubular inverter battery', 'icon': '🔋'},
            {'itemId': 'laptops-cpus', 'name': 'Laptops & Desktop CPUs', 'unit': 'unit', 'prices': {'delhi-ncr': 350, 'bengaluru': 300, 'mumbai': 350}, 'popular': True, 'description': 'Old working or dead laptops, motherboards & CPUs', 'icon': '💻'},
            {'itemId': 'ceiling-fan', 'name': 'Ceiling Fan', 'unit': 'unit', 'prices': {'delhi-ncr': 200, 'bengaluru': 180, 'mumbai': 200}, 'popular': False, 'description': 'Copper winding ceiling fan with blades', 'icon': '🌀'},
        ],
    },
    {
        'categoryId': 'plastics',
        'name': 'Plastics & Bottles',
        'icon': '🧴',
        'description': 'PET bottles, HDPE containers, hard plastics & glass',
        'order': 5,
        'items': [
            {'itemId': 'plastic', 'name': 'Soft & Hard Plastic', 'unit': 'kg', 'prices': {'delhi-ncr': 12, 'bengaluru': 10, 'mumbai': 11}, 'popular': True, 'description': 'Plastic bottles, containers, jars, buckets', 'icon': '🧴'},
            {'itemId': 'glass', 'name': 'Glass Bottles', 'unit': 'kg', 'prices': {'delhi-ncr': 2, 'bengaluru': 2, 'mumbai': 2}, 'popular': False, 'description': 'Beer bottles, glass containers (unbroken)', 'icon': '🍾'},
        ],
    },
]

def ensure_rates_seeded():
    """Seeds scrap rates if database is empty."""
    if not ScrapRateCategory.objects.exists():
        for cat_data in DEFAULT_SEED_DATA:
            cat = ScrapRateCategory.objects.create(
                category_id=cat_data['categoryId'],
                name=cat_data['name'],
                icon=cat_data['icon'],
                description=cat_data['description'],
                order=cat_data['order'],
                active=True,
            )
            for item in cat_data['items']:
                ScrapItem.objects.create(
                    category=cat,
                    item_id=item['itemId'],
                    name=item['name'],
                    unit=item['unit'],
                    prices=item['prices'],
                    popular=item['popular'],
                    description=item['description'],
                    icon=item['icon'],
                    active=True,
                )

class RatesListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ensure_rates_seeded()
        city = request.query_params.get('city', 'delhi-ncr').lower().strip()

        categories = ScrapRateCategory.objects.filter(active=True).order_by('order').prefetch_related('items')
        formatted_cats = []

        for cat in categories:
            cat_dict = cat.to_dict()
            item_list = [item.to_dict(city=city) for item in cat.items.filter(active=True)]
            cat_dict['items'] = item_list
            formatted_cats.append(cat_dict)

        data = {
            'city': city,
            'updatedAt': timezone.now().isoformat(),
            'categories': formatted_cats,
        }
        return api_success(data=data, message='Scrap rates retrieved successfully')

class RateItemUpdateView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request):
        item_id = request.data.get('itemId')
        if not item_id:
            return api_failure(message='itemId is required', status_code=400)

        item = ScrapItem.objects.filter(item_id=item_id).first()
        if not item:
            return api_failure(message='Item not found', status_code=404)

        if 'name' in request.data:
            item.name = request.data['name']
        if 'unit' in request.data:
            item.unit = request.data['unit']
        if 'prices' in request.data and isinstance(request.data['prices'], dict):
            current = item.prices or {}
            for c, p in request.data['prices'].items():
                current[c.lower()] = float(p)
            item.prices = current

        item.save()
        return api_success(
            data={'item': item.to_dict()},
            message=f'Scrap rate for {item.name} updated successfully',
        )

class RateItemCreateView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request):
        category_id = request.data.get('categoryId')
        name = request.data.get('name')
        if not category_id or not name:
            return api_failure(message='categoryId and name are required', status_code=400)

        cat = ScrapRateCategory.objects.filter(category_id=category_id).first()
        if not cat:
            return api_failure(message='Category not found', status_code=404)

        import re
        item_id = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

        item = ScrapItem.objects.create(
            category=cat,
            item_id=item_id,
            name=name,
            unit=request.data.get('unit', 'kg'),
            prices=request.data.get('prices', {'delhi-ncr': 20, 'bengaluru': 18}),
            description=request.data.get('description', ''),
            icon=request.data.get('icon', '📦'),
            popular=bool(request.data.get('popular', False)),
        )

        return api_success(
            data={'item': item.to_dict()},
            message=f'Scrap item {item.name} added successfully',
            status_code=201,
        )

class RateItemDeleteView(APIView):
    permission_classes = [IsAdminRole]

    def delete(self, request, item_id):
        item = ScrapItem.objects.filter(item_id=item_id).first()
        if not item:
            return api_failure(message='Item not found', status_code=404)

        item.delete()
        return api_success(message='Scrap item removed successfully')
