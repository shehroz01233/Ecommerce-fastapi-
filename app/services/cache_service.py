from ..core.redis import redis_manager
from typing import Optional


class CacheService:
    @staticmethod
    def get_products(search: str = None, category: str = None):
        key = f"cache:products:{search or 'all'}:{category or 'all'}"
        return redis_manager.cache_get(key)

    @staticmethod
    def set_products(products: list, search: str = None, category: str = None):
        key = f"cache:products:{search or 'all'}:{category or 'all'}"
        redis_manager.cache_set(key, products, expire=300)

    @staticmethod
    def invalidate_products():
        redis_manager.cache_delete_pattern("cache:products:*")

    @staticmethod
    def get_product(product_id: int):
        key = f"cache:product:{product_id}"
        return redis_manager.cache_get(key)

    @staticmethod
    def set_product(product_id: int, product: dict):
        key = f"cache:product:{product_id}"
        redis_manager.cache_set(key, product, expire=600)

    @staticmethod
    def invalidate_product(product_id: int):
        redis_manager.cache_delete(f"cache:product:{product_id}")
        CacheService.invalidate_products()

    @staticmethod
    def get_categories():
        key = "cache:categories"
        return redis_manager.cache_get(key)

    @staticmethod
    def set_categories(categories: list):
        key = "cache:categories"
        redis_manager.cache_set(key, categories, expire=600)

    @staticmethod
    def invalidate_categories():
        redis_manager.cache_delete("cache:categories")

    @staticmethod
    def get_user_cart(user_id: int):
        key = f"cache:cart:{user_id}"
        return redis_manager.cache_get(key)

    @staticmethod
    def set_user_cart(user_id: int, cart: list):
        key = f"cache:cart:{user_id}"
        redis_manager.cache_set(key, cart, expire=120)

    @staticmethod
    def invalidate_user_cart(user_id: int):
        redis_manager.cache_delete(f"cache:cart:{user_id}")

    @staticmethod
    def get_product_rating(product_id: int):
        key = f"cache:rating:{product_id}"
        return redis_manager.cache_get(key)

    @staticmethod
    def set_product_rating(product_id: int, rating: dict):
        key = f"cache:rating:{product_id}"
        redis_manager.cache_set(key, rating, expire=300)

    @staticmethod
    def invalidate_product_rating(product_id: int):
        redis_manager.cache_delete(f"cache:rating:{product_id}")


cache_service = CacheService()
