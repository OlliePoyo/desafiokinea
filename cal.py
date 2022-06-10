from workalendar.america import BrazilBankCalendar

class BrazilAmbima(BrazilBankCalendar):  
    include_ash_wednesday = False

    def get_variable_days(self, year):
        """
        Define the brazilian variable holidays and the last
        day for only internal bank transactions
        """
        days = super().get_variable_days(year)[:-1]
        return days