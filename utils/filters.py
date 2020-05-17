from vkbottle.framework.framework.rule.filters import AbstractFilter


class NotFilter(AbstractFilter):
    async def check(self, event):
        for rule in self.rules:
            if await rule.check(event):
                return False
        return True
