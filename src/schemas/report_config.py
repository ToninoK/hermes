import hashlib
import json
from typing import List, Union, Literal

from fastapi.exceptions import HTTPException
from pydantic import BaseModel, NaiveDatetime, EmailStr

from src.helpers.auth import get_current_user
from src.helpers.acl import has_permission


class StoreIdFilter(BaseModel):
    field: str = "store_id"
    operator: Literal["=", "IN", "!=", "NOT IN"]
    value: Union[int, List[int]]


class ProductNameFilter(BaseModel):
    field: str = "product_name"
    operator: Literal["=", "IN", "!=", "NOT IN"]
    value: Union[str, List[str]]


class EmployeeNameFilter(BaseModel):
    field: str = "employee_name"
    operator: Literal["=", "IN", "!=", "NOT IN"]
    value: Union[str, List[str]]


class StartDateFilter(BaseModel):
    field: str = "start_date"
    operator: Literal["=", "!=", ">", "<", ">=", "<="]
    value: NaiveDatetime


class EndDateFilter(BaseModel):
    field: str = "end_date"
    operator: Literal["=", "!=", ">", "<", ">=", "<="]
    value: NaiveDatetime


class StorePerformanceReportConfig(BaseModel):
    report_name: str = "store_performance"
    metrics: List[str]
    dimensions: List[str]
    filters: List[Union[StoreIdFilter, StartDateFilter, EndDateFilter]]


class EmployeePerformanceReportConfig(BaseModel):
    report_name: str = "employee_performance"
    metrics: List[str]
    dimensions: List[str]
    filters: List[Union[EmployeeNameFilter, StoreIdFilter, StartDateFilter, EndDateFilter]]


class ProductPerformanceReportConfig(BaseModel):
    report_name: str = "product_performance"
    metrics: List[str]
    dimensions: List[str]
    filters: List[Union[ProductNameFilter, StoreIdFilter, StartDateFilter, EndDateFilter]]


class StoreInventoryReportConfig(BaseModel):
    report_name: str = "store_inventory"
    metrics: List[str]
    dimensions: List[str]
    filters: List[Union[ProductNameFilter, StoreIdFilter]]


class ReportConfig(BaseModel):
    config: Union[
        StorePerformanceReportConfig,
        EmployeePerformanceReportConfig,
        ProductPerformanceReportConfig,
        StoreInventoryReportConfig
    ]
    emails: List[EmailStr]

    async def verify_acl(self, token):
        user = await get_current_user(token)
        if not has_permission(user["role"], self.config.report_name, self.config.model_dump(), store_id=user["store_id"]):
            raise HTTPException(status_code=403, detail="User does not have permission to access this report")

    async def generate_config(self, token):
        user = await get_current_user(token)
        dumped_data = super().model_dump()
        user_role = user["role"]
        report_config_hash_str = (
            json.dumps(dumped_data["config"], sort_keys=True)
            + user_role
        )
        report_config_hash = hashlib.sha256(report_config_hash_str.encode()).hexdigest()
        return {**dumped_data, "config_key": report_config_hash}