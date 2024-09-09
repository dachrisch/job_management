from typing import Any

import reflex as rx


class StatsCrawler:
    def fire_stats_toast(self, stats: dict[str, Any]):
        if stats['finish_reason'] == 'finished':
            return rx.toast.success(
                f'Scraped [{stats["item_scraped_count"]}] '
                f'items in {stats["elapsed_time_seconds"]} seconds')
        else:
            return rx.toast.error(f'Crawling failed: {stats}')
