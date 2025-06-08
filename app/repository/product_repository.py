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
    
    @staticmethod
    async def get_product_variants(product_id: int, include_inactive: bool = False):
        """Get variants for a product, excluding inactive variants by default."""
        return await VariantRepository.get_product_variants(product_id, include_inactive)