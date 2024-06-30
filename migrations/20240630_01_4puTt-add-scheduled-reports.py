"""
scheduled reports
"""

from yoyo import step

__depends__ = {'20240527_03_npNzg-reporting-seed-data'}

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS scheduled_reports(
            id serial primary key,
            frequency text,
            config jsonb,
            created_by text
        );
        """,
        "DROP TABLE scheduled_reports;",
    )
]
