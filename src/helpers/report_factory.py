"""Primitive implementation of a report generation factory that generates different types of reports based on the report type provided.

The implementation itself can be a lot smarter than the one provided below.
This simply serves as a means to demonstrate the complete concept of this project.
"""

import operator
from os import environ

import sqlalchemy as sa
from sqlalchemy.sql.expression import Select, and_, select


_DSN = environ.get("PGHOST", "")

metadata = sa.MetaData()

stores_table = sa.Table('stores', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('city', sa.String(255)),
    sa.Column('country', sa.String(255)),
)

employees_table = sa.Table('employees', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('email', sa.String(255)),
    sa.Column('password', sa.String(255)),
    sa.Column('role', sa.String(255)),
    sa.Column('name', sa.String(255)),
    sa.Column('store_id', sa.Integer, sa.ForeignKey('stores.id')),
)

products_table = sa.Table('products', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('category', sa.String(255)),
    sa.Column('price', sa.Float),
)

inventory_table = sa.Table('inventory', metadata,
    sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id')),
    sa.Column('store_id', sa.Integer, sa.ForeignKey('stores.id')),
    sa.Column('quantity', sa.Integer),
)

sales_table = sa.Table('sales', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('store_id', sa.Integer, sa.ForeignKey('stores.id')),
    sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id')),
    sa.Column('order_quantity', sa.Integer),
    sa.Column('employee_id', sa.Integer, sa.ForeignKey('employees.id')),
    sa.Column('date', sa.Date, default=sa.func.current_date()),
)


class BaseReport:
    NAME_MAPPING = {}

    JOIN = None

    OPERATOR_MAPPING = {
        "=": operator.eq,
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
        "!=": operator.ne,
        "IN": lambda field, value: field.in_(value),
        "NOT IN": lambda field, value: field.not_in(value),
    }

    def __init__(self, report_config) -> None:
        self.report_config = report_config

    def build_query(self):
        query = self.select()
        query = self.apply_filters(query)
        query = self.apply_group_by(query).select_from(self.JOIN)
        return query

    @property
    def metrics(self):
        return self.report_config.get("metrics", [])

    @property
    def dimensions(self):
        return self.report_config.get("dimensions", [])
    
    @property
    def filters(self):
        return self.report_config.get("filters", [])

    def _consume_filter(self, filter):
        field = filter.get("field")
        value = filter.get("value")
        operator = filter.get("operator")

        mapped_field = self.NAME_MAPPING.get(field)
        op_func = self.OPERATOR_MAPPING.get(operator)
        if op_func is None or mapped_field is None:
            raise ValueError("Invalid operator or field provided")
        
        return op_func(mapped_field, value)
    
    def select(self):
        dimensions = [self.NAME_MAPPING.get(dim) for dim in self.dimensions]
        metrics = [self.NAME_MAPPING.get(metric) for metric in self.metrics]
        selectable = dimensions + metrics
        return select(*selectable)

    def apply_filters(self, query: Select) -> Select:
        filters = [self._consume_filter(filter) for filter in self.filters]
        return query.where(and_(*filters) if filters else sa.true())
    
    def apply_group_by(self, query: Select) -> Select:
        return query.group_by(*[self.NAME_MAPPING.get(dim) for dim in self.dimensions])


class StorePerformanceReport(BaseReport):

    NAME_MAPPING = {
        "store_city": stores_table.c.city.label("store_city"),
        "store_country": stores_table.c.country.label("store_country"),
        "date": sales_table.c.date.label("date"),
        "total_sales": sa.func.sum(products_table.c.price).label("total_sales"),
        "number_of_transactions": sa.func.count(sales_table.c.product_id).label("number_of_transactions"),
        "average_sale_value": sa.func.avg(products_table.c.price)/sa.func.count(sales_table.c.product_id).label("average_sale_value"),
        "store_id": sales_table.c.store_id.label("store_id"),
        "start_date": sales_table.c.date.label("start_date"),
        "end_date": sales_table.c.date.label("end_date"),
    }

    JOIN = (
        sales_table.join(products_table, sales_table.c.product_id == products_table.c.id)
        .join(stores_table, sales_table.c.store_id == stores_table.c.id)
    )


class StoreInventoryReport(BaseReport):
    """Aggregates and displays the current inventory of all stores using the stores, inventory and product tables."""

    NAME_MAPPING = {
        "store_city": stores_table.c.city.label("store_city"),
        "store_country": stores_table.c.country.label("store_country"),
        "quantity": inventory_table.c.quantity.label("quantity"),
        "product_name": products_table.c.name.label("product_name"),
        "store_id": stores_table.c.id.label("store_id"),
    }

    JOIN = (
        stores_table.join(inventory_table, stores_table.c.id == inventory_table.c.store_id)
        .join(products_table, inventory_table.c.product_id == products_table.c.id)
    )


class ProductPerformanceReport(BaseReport):

    NAME_MAPPING = {
        "product_name": products_table.c.name.label("product_name"),
        "store_country": stores_table.c.country.label("store_country"),
        "store_city": stores_table.c.city.label("store_city"),
        "total_sales": sa.func.sum(products_table.c.price).label("total_sales"),
        "average_sale_value": sa.func.avg(products_table.c.price).label("average_sale_value"),
        "total_products_sold": sa.func.sum(sales_table.c.order_quantity).label("total_products_sold"),
        "store_id": stores_table.c.id.label("store_id"),
        "start_date": sales_table.c.date.label("start_date"),
        "end_date": sales_table.c.date.label("end_date"),
    }

    JOIN = (
        products_table.join(sales_table, products_table.c.id == sales_table.c.product_id)
        .join(stores_table, sales_table.c.store_id == stores_table.c.id)
    )


class EmployeePerformanceReport(BaseReport):

    NAME_MAPPING = {
        "employee_name": employees_table.c.name.label("employee_name"),
        "store_city": stores_table.c.city.label("store_city"),
        "store_country": stores_table.c.country.label("store_country"),
        "employee_total_sales": sa.func.sum(products_table.c.price).label("employee_total_sales"),
        "employee_average_sale_value": sa.func.avg(products_table.c.price).label("employee_average_sale_value"),
        "number_of_transactions": sa.func.count(sales_table.c.product_id).label("number_of_transactions"),
        "store_id": stores_table.c.id.label("store_id"),
        "start_date": sales_table.c.date.label("start_date"),
        "end_date": sales_table.c.date.label("end_date"),
    }

    JOIN = (
        employees_table.join(sales_table, employees_table.c.id == sales_table.c.employee_id)
        .join(products_table, sales_table.c.product_id == products_table.c.id)
        .join(stores_table, sales_table.c.store_id == stores_table.c.id)
    )


class ReportGeneratorAPI:
    REPORT_MAPPING = {
        "store_performance": StorePerformanceReport,
        "store_inventory": StoreInventoryReport,
        "product_performance": ProductPerformanceReport,
        "employee_performance": EmployeePerformanceReport
    }

    def __init__(self) -> None:
        self.engine = None

    def _init_engine(self):
        if self.engine:
            return
        self.engine = sa.create_engine(_DSN)
    
    def _conn(self):
        self._init_engine()
        return self.engine.connect()

    def _get_report_class(self, report_type):
        return self.REPORT_MAPPING.get(report_type)

    def generate(self, report_config: dict):
        report_type = report_config.get("report_name", {})
        klass = self._get_report_class(report_type)
        if klass:
            instance = klass(report_config)
            query = instance.build_query()
            compiled = query.compile(bind=self.engine, compile_kwargs={"literal_binds": True})
            return str(compiled)
        else:
            raise ValueError("InvalidReportType")

    def run_query(self, query: Select):
        with self._conn() as conn:
            result = conn.execute(query)
            return [dict(row) for row in result.fetchall()]


ReportGenerator = ReportGeneratorAPI()
