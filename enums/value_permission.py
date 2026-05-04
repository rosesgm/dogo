from enum import Enum
class ValuePermission(Enum):
    CUSTOMER_EDIT = 1
    CUSTOMER_DELETE = 2
    ACCOUNT=3
    TRANSACTION_COMMIT=4
    USER_VIEW=5