from azure.core.paging import ItemPaged

class CustomClass():
    def not_right(self):
        pass

class SomeClient(): #@
    def list_thing(self): #@
        '''
        :rtype: CustomClass()
        '''
        return CustomClass()
