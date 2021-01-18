from datetime import datetime
from bot.models.user import User

class Palplatina():
    
    async def give_daily(self, user_id, user_name):
        user = await User.get(user_id)
        if not user:
            user = User()
            user.id = user_id
            user.name = user_name
            user.currency = 0
            user.daily_last_collected_at = None

        if user.daily_last_collected_at and (datetime.utcnow() - user.daily_last_collected_at).days < 1:
            return False
        else:
            user.daily_last_collected_at = datetime.utcnow()
            user.currency += 300
            
            await User.save(user)
            return user

    async def get_currency(self, user_id):
        user = await User.get(user_id)
        if not user:
            return 0
        return user.currency