from azure.core.paging import ItemPaged

class CustomClass():
    def by_page(self):
        #Makes it own custom paging protocol
        pass

class SomeClient(): #@
    def list_thing(self): #@
        '''
        :rtype: CustomClass()
        '''
        return CustomClass()