from enum import Enum

# ATM Status
class ATMStatus(str, Enum):
    OPERATIONAL = "Operational"
    LOW_CASH = "Low-Cash" 
    MAINTENANCE = "Maintenance"
    OFFLINE = "Offline"

# Service Call Priority 
class ServicePriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    CRITICAL = "Critical"

# Service Call Status
class ServiceStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In-Progress" 
    COMPLETED = "Completed"
    FAILED = "Failed"

# User Role
class UserRole(str, Enum):
    OPERATIONS_ADMIN = "Operations Admin"
    TECHNICIAN = "Technician"
    AUDITOR = "Auditor"