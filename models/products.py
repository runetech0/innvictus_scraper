import enum


class InvictusProduct:
    def __init__(self):
        self.prod_name: str = None
        self.prod_link: str = None
        self.prod_code: str = None
        self.prod_img_link: str = None
        self.prod_price: str = None
        self.prod_gender: str = None
        self.prod_model: str = None
        self.prod_in_stock: bool = False
        self.out_of_stock_sizes: list = []
        self.in_stock_sizes: list = []


class TafProduct:
    def __init__(self):
        self.title = None
        self.link = None
        self.img_link = None
        self.price = None
        self.model = None
        self.in_stock_sizes: list(TafSize) = []
        self.out_of_stock_sizes: list(TafSize) = []
        self.sku = None


class TafSize:
    def __init__(self):
        self.size_number = None
        self.size_atc = None


class ProductStatus(enum.Enum):
    OUT_OF_STOCK = 'Out of Stock'
    IN_STOCK = 'In Stock'


class LiverPoolProduct:
    def __init__(self):
        self.name = None
        self.link = None
        self.img_link = None
        self.price = None
        self.in_stock_sizes = []
        self.out_of_stock_sizes = []
        self.color = None


class AliveMexProduct:
    def __init__(self):
        self.name = None
        self.link = None
        self.img_link = None
        self.price = None
