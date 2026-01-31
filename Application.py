from ApiHandler import ApiHandler

class Application:
    def __init__(self):
        self.apiHander = ApiHandler()
        print("Application built.")


    def Run(self):
        self.apiHander.ExtractContacts(showStats=True)
        # self.apiHander.MailchimpTest()
