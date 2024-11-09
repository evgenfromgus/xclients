from app.users.schemas import UserTable
from app.company.schemas import CompanyTable
from app.employee.schemas import EmployeeTable

metadata = (UserTable.metadata,
            CompanyTable.metadata,
            EmployeeTable.metadata)
