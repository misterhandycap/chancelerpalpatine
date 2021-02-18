from bot.models.planets import Planet

class Planets():
    async def list_of_planets(self, region=None, climate=None, circuference=None, mass=None):
        return (await Planet.all(region=region, climate=climate, circuference=circuference, mass=mass))
