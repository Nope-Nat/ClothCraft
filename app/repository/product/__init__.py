"""
Product repository package.

This package contains specialized repositories for different aspects of product management:
- BaseRepository: Basic data fetching (categories, countries, etc.)
- CategoryRepository: Category hierarchy and navigation
- VariantRepository: Product variants, sizes, and formatting
- ProductQueryRepository: Product searches and filtering
- ProductDetailRepository: Product details, materials, tags, discounts
- ProductManagementRepository: Product creation and management operations
"""

from .base_repository import BaseRepository
from .category_repository import CategoryRepository
from .variant_repository import VariantRepository
from .product_query_repository import ProductQueryRepository
from .product_detail_repository import ProductDetailRepository
from .product_management_repository import ProductManagementRepository

__all__ = [
    'BaseRepository',
    'CategoryRepository', 
    'VariantRepository',
    'ProductQueryRepository',
    'ProductDetailRepository',
    'ProductManagementRepository'
]