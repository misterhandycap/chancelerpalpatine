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
            return False, user
        
        user.daily_last_collected_at = datetime.utcnow()
        user.currency += 300
        
        await User.save(user)
        return True, user

    async def get_currency(self, user_id):
        user = await User.get(user_id)
        if not user:
            return 0
        return user.currency

    async def give_currency(self, user1, user2, amount):
       # user = User()
        user1 = await User.get(user1)
        #if not user:
        #   return 0
        user2 = await User.get(user2)
        if not user2:
            return 0
        transaction_criteria = [amount>0, user1.currency>amount, user2]
        currency_give = user2.currency + amount

        if currency_given > 0:
            return 0
        else:
            await User.save(user1)
            await User.save(user2)
            return 0