class SortableState:
    sort_value: str
    sort_reverse: bool

    async def toggle_sort(self):
        pass

    async def change_sort_value(self, new_value: str):
        pass
