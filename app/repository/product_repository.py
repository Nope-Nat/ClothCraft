from .product import (
    BaseRepository,
    CategoryRepository, 
    VariantRepository,
    ProductQueryRepository,
    ProductDetailRepository,
    ProductManagementRepository
)

class ProductRepository(
    BaseRepository,
    CategoryRepository,
    VariantRepository, 
    ProductQueryRepository,
    ProductDetailRepository,
    ProductManagementRepository
):
    """
    Main product repository that combines all specialized repositories.
    
    This class inherits from all specialized repository classes to provide
    a unified interface for product operations while maintaining backwards
    compatibility with existing code.
    """
    pass