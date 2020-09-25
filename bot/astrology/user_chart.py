from flatlib.chart import Chart


class UserChart():
    
    def __init__(self, user_id: str, chart: Chart):
        self.user_id = str(user_id)
        self.chart = chart

    def __eq__(self, value):
        try:
            return (
                value.user_id == self.user_id and 
                str(value.chart.date) == str(self.chart.date) and
                str(value.chart.pos) == str(self.chart.pos)    
            )
        except:
            return False
