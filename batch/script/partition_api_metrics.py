"""Copy api metric from a transient table to a partitioned table.

Millions of rows per day are added to the metric.api table.  To help with
query performance, copy the rows from this table to a partitioned table on a
daily basis.
"""
from selene.batch.base import SeleneScript
from selene.data.metric import ApiMetricsRepository
from selene.util.db import use_transaction


class PartitionApiMetrics(SeleneScript):
    def __init__(self):
        super(PartitionApiMetrics, self).__init__(__file__)

    @use_transaction
    def _run(self):
        api_metrics_repo = ApiMetricsRepository(self.db)
        api_metrics_repo.create_partition(self.args.date)
        api_metrics_repo.copy_to_partition(self.args.date)
        api_metrics_repo.remove_by_date(self.args.date)


if __name__ == '__main__':
    PartitionApiMetrics().run()
