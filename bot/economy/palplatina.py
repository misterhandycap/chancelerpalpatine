from datetime import datetime

from bot.economy.exceptions import AlreadyOwnsItem, ItemNotFound, NotEnoughCredits
from bot.models.profile_item import ProfileItem
from bot.models.user import User
from bot.models.user_profile_item import UserProfileItem

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
            raise ItemNotFound()

        if user.currency < profile_item.price:
            raise NotEnoughCredits()

        user.profile_items.append(
            UserProfileItem(profile_item=profile_item))
        user.currency -= profile_item.price
        try:
            await User.save(user)
            return user
        except:
            raise AlreadyOwnsItem()

    async def equip_item(self, user_id, item_name):
        user_profile_item = await self._get_user_item_from_name(user_id, item_name)
        user_profile_item.equipped = True
        await UserProfileItem.save(user_profile_item)
        return user_profile_item

    async def unequip_item(self, user_id, item_name):
        user_profile_item = await self._get_user_item_from_name(user_id, item_name)
        user_profile_item.equipped = False
        await UserProfileItem.save(user_profile_item)
        return user_profile_item

    async def _get_user_item_from_name(self, user_id, item_name):
        user = await User.get(user_id, preload_profile_items=True) or User(id=user_id)
        user_profile_item = next(
            (upi for upi in user.profile_items if upi.profile_item.name == item_name), None)
        if not user_profile_item:
            raise ItemNotFound()
        return user_profile_item
            
