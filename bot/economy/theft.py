from bot.models.merchants import Merchant
import random
from datetime import datetime
from bot.models.user import User

class Theft():
    async def merchant_losing_money(self, merchant_name, user_id):
        merchant = await Merchant.get(merchant_name)
        if not merchant:
            return
        merchant_amount = merchant.amount
        if merchant_amount == 0:
            return
        user = await User.get(user_id)
        if not user:
            user = User()
            user.id = user_id
            user.currency = 0
        user_amount = await user.currency

        theft_success = random.random() <= 0.7
        if theft_success == True:
            merchant_new_amount = merchant_amount - random.randint(1, merchant_amount * 0.25)
            user_new_amount = user_amount + merchant_new_amount
            return
        if theft_success == False:
            return

        await User.save(user)
        await Merchant.save(merchant)