"""Primitive implementation of a report generation factory that generates different types of reports based on the report type provided.

The implementation itself can be a lot smarter than the one provided below.
This simply serves as a means to demonstrate the complete concept of this project.
"""

class StorePerformanceReport:
    """Aggregates the data using the stores table, products table and the sales table."""
    @classmethod
    def generate(cls, report_config: dict):
        query = cls._build_query(report_config)

    @classmethod
    def _build_filters():
        start = report_config.get("start_date")
        end = report_config.get("end_date")
        params = [start, end]
        filters = [
            "s.date >= %s",
            "s.date < %s",
        ]
        if city := report_config.get("city"):
            filters.append("s.city = %s")
            params.append(city)

        query = f"WHERE {" AND ".join(filters) if filters else "1=1"}"
        # mogrify and return the query
        
    @classmethod
    def _build_query(cls, report_config: dict):
        where = cls._build_filters(report_config)
        query = f"""
            SELECT
                s.city,
                s.country,
                s.date,
                SUM(p.price) as total_sales,
                COUNT(s.product_id) as total_products_sold,
                AVG(p.price)/COUNT(s.product_id) as avg_order_quantity
            FROM sales AS s
            INNER JOIN stores AS st
                ON s.store_id = st.id
            INNER JOIN products AS p
                ON s.product_id = p.id
            {where}
            GROUP BY s.city, s.country, s.date
        """


class StoreInventoryReport:
    """Aggregates and displays the current inventory of all stores using the stores, inventory and product tables."""

    @classmethod
    def generate(cls, report_config: dict):
        query = cls._build_query(report_config)


    @classmethod
    def _build_filters():
        filters = []
        params = []
        if product_id := report_config.get("product_id"):
            filters.append("i.product_id = %s")
            params.append(product_id)
        query = f"WHERE {" AND ".join(filters) if filters else "1=1"}"
        # mogrify and return the query

    @classmethod
    def _build_query(cls, report_config: dict):
        where = cls._build_filters(report_config)
        query = f"""
            SELECT
                st.city,
                st.country,
                i.quantity,
                p.name
            FROM inventory AS i
            INNER JOIN stores AS st
                ON i.store_id = st.id
            INNER JOIN products AS p
                ON i.product_id = p.id
            {where}
            GROUP BY st.city, st.country, p.name
        """
    

class ProductPerformanceReport:

    dimension_mapping = {
        "city": "s.city",
        "country": "s.country",
    }


    @classmethod
    def _build_filters(cls, report_config):
        filters = []
        params = []
        if product_id := report_config.get("product_id"):
            filters.append("s.product_id = %s")
            params.append(product_id)
        query = f"WHERE {" AND ".join(filters) if filters else "1=1"}"
        # mogrify and return the query

    @classmethod
    def _build_query(cls, report_config: dict):
        where = cls._build_filters(report_config)
        dimensions = report_config.get("dimensions", [])
        dimensions = [cls.dimension_mapping.get(dim) for dim in dimensions]
        if not all(dimensions):
            raise ValueError("Invalid dimension provided")
        query = f"""
            SELECT
                p.name,
                {", ".join(dimensions)},
                SUM(p.price) as total_sales,
                COUNT(s.product_id) as total_products_sold,
                AVG(p.price)/COUNT(s.product_id) as avg_order_quantity
            FROM sales AS s
            INNER JOIN products AS p
                ON s.product_id = p.id
            {where}
            GROUP BY {", ".join(dimensions)}
        """

    @classmethod
    def generate(cls, report_config: dict):
        query = cls._build_query(report_config)


class EmployeePerformanceReport:

    @classmethod
    def generate(cls, report_config: dict):
        pass


class ReportFactory:
    REPORT_MAPPING = {
        "store_performance": StorePerformanceReport,
        "store_inventory": StoreInventoryReport,
        "product_performance": ProductPerformanceReport,
        "employee_performance": EmployeePerformanceReport
    }
    
    @classmethod
    def _get_report_class(self, report_type):
        return self.REPORT_MAPPING.get(report_type)

    @classmethod
    def generate(cls, report_config: dict):
        report_type = report_config.get("report_type")
        klass = cls._get_report_class(report_type)
        if klass:
            klass.generate(report_config)
        else:
            raise ValueError(f"Invalid report type: {self.report_type}")

