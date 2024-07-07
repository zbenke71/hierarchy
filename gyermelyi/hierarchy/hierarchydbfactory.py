from .hierarchydb import HierarchyDBOracle


class HierarchyDBFactory:
    @staticmethod
    def create(db_type, **kwargs):
        if db_type == 'oracle':
            return HierarchyDBOracle(**kwargs)
        # Add more database handlers here (e.g., Postgres, MySQL)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
