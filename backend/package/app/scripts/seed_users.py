import asyncio
from app.database import AsyncSessionLocal
from app.models import User, UserRole
from app.security import hash_password

async def seed_users()->None:
    async with AsyncSessionLocal() as session:
        session.add_all([
            User(username="admin", hashed_password=hash_password("adminpass123!"), first_name="John", last_name="Smith", role=UserRole.OPERATIONS_ADMIN),
            User(username="technician", hashed_password=hash_password("technicianpass123!"), first_name="Angie", last_name="Paltrow", role=UserRole.FIELD_TECHNICIAN),
            User(username="auditor", hashed_password=hash_password("auditorpass123!"), first_name="Winston", last_name="Church", role=UserRole.AUDITOR),
            User(username="admin_carrie", hashed_password=hash_password("adminpass123!"), first_name="Carrie", last_name="Brown", role=UserRole.OPERATIONS_ADMIN),
            User(username="technician_carrie", hashed_password=hash_password("technicianpass123!"), first_name="Carrie", last_name="McGill", role=UserRole.FIELD_TECHNICIAN),
            User(username="auditor_mike", hashed_password=hash_password("auditorpass123!"), first_name="Mike", last_name="Church", role=UserRole.AUDITOR),
            User(username="admin_john", hashed_password=hash_password("adminpass123!"), first_name="John", last_name="Mikakis", role=UserRole.OPERATIONS_ADMIN),
            User(username="technician_james", hashed_password=hash_password("technicianpass123!"), first_name="James", last_name="McGill", role=UserRole.FIELD_TECHNICIAN),
            User(username="auditor_jamie", hashed_password=hash_password("auditorpass123!"), first_name="Jamie", last_name="Weerasethankul", role=UserRole.AUDITOR),
            User(username="admin_parmy", hashed_password=hash_password("adminpass123!"), first_name="Parmjeet", last_name="Larson", role=UserRole.OPERATIONS_ADMIN),
            User(username="technician_paul", hashed_password=hash_password("technicianpass123!"), first_name="Paul", last_name="McHogeoan", role=UserRole.FIELD_TECHNICIAN),
            User(username="auditor_paul", hashed_password=hash_password("auditorpass123!"), first_name="Paul", last_name="Atreides", role=UserRole.AUDITOR),
        ])
        await session.commit()
if __name__ == "__main__":
    asyncio.run(seed_users())