from datetime import datetime
from bot.i18n import _

from bot.models.profile_item import ProfileItem
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

    async def get_available_items(self, page=0):
        return await ProfileItem.all(page, page_size=9)

    async def get_item(self, item_name):
        return await ProfileItem.get_by_name(item_name)
    
    async def get_user_items(self, user_id):
        user = await User.get(user_id, preload_profile_items=True)
        if not user:
            return []
        return user.profile_items

    async def buy_item(self, user_id, item_name):
        user = await User.get(user_id, preload_profile_items=True)
        profile_item = await ProfileItem.get_by_name(item_name)
        if not profile_item or not user:
            return _('Item not found')

        if user.currency < profile_item.price:
            return _('Not enough credits')

        user.profile_items.append(profile_item)
        user.currency -= profile_item.price
        try:
            await User.save(user)
            return _('Item bought. Enjoy!')
        except:
            return _('You already own this item')
            
