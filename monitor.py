from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.actions.telegram.notifiers import SendTelegramMessageSpiderFinished


@monitors.name('Item count monitor')
class ItemCountMonitor(Monitor):

    @monitors.name('Minimum number of items')
    def test_minimum_number_of_items(self):
        item_extracted = getattr(
            self.data.stats, 'item_scraped_count', 0)
        minimum_threshold = 10

        msg = 'Extracted less than {} items'.format(
            minimum_threshold)
        self.assertTrue(
            item_extracted >= minimum_threshold, msg=msg
        )

@monitors.name("Error count monitor")
class ErrorCountMonitor(Monitor):
    """Check for errors in the spider log.
    You can configure the expected number of ERROR log messages using
    ``SPIDERMON_MAX_ERRORS``. The default is ``0``."""

    @monitors.name("Should not have any errors")
    def test_max_errors_in_log(self):
        # errors_threshold = self.crawler.settings.getint(SPIDERMON_MAX_ERRORS, 0)
        errors_threshold = 1
        # no_of_errors = self.stats.get("log_count/ERROR", 0)
        no_of_errors = getattr(
            self.data.stats, 'log_count/ERROR', 0)
        msg = "Found {} errors in log, maximum expected is " "{}".format(
            no_of_errors, errors_threshold
        )
        self.assertTrue(no_of_errors <= errors_threshold, msg=msg)

class SpiderCloseMonitorSuite(MonitorSuite):

    monitors = [
        ItemCountMonitor,
        ErrorCountMonitor
    ]

    monitors_passed_actions = [
        SendTelegramMessageSpiderFinished,
    ]

    monitors_failed_actions = [
        SendTelegramMessageSpiderFinished,
    ]
