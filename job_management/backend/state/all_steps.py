import asyncio

import reflex as rx

from job_management.backend.state.application import ApplicationState


class AllStepsState(rx.State):
    running: bool = False
    _ramp_up_delay: float = .5
    _update_interval: float = .2

    @rx.background
    async def run_all_steps(self):
        async with self:
            self.running = True

        async with self:
            application_state: ApplicationState = (await self.get_state(ApplicationState))

        yield ApplicationState.analyze_job()
        await asyncio.sleep(self._ramp_up_delay)
        while application_state.job_offer.state.is_analyzing:
            await asyncio.sleep(self._update_interval)

        yield ApplicationState.compose_application()
        await asyncio.sleep(self._ramp_up_delay)
        while application_state.job_offer.state.is_composing:
            await asyncio.sleep(self._update_interval)

        yield ApplicationState.store_in_google_doc()
        await asyncio.sleep(self._ramp_up_delay)
        while application_state.job_offer.state.is_storing:
            await asyncio.sleep(self._update_interval)

        async with self:
            self.running = False
