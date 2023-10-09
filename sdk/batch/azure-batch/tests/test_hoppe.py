# import threading

# num = 0

# def add():
#     global num
#     for i in range(100000):
#         num += 1

# def main():
#     threadNum = 99
#     threads = []
#     for i in range(threadNum):
#         threads.append(threading.Thread(target=add))
#     for t in threads:
#         t.start()
#     for t in threads:
#         t.join()
#     print(num)

# if __name__ == '__main__':
#     main()

# # class A:
# #     def __init__(self, x):
# #         self.x = x

# #     def logX(self):
# #         print(self.x)


# # a1 = A("100")


# # A.logX = lambda self: print("Hello: " + self.x)

# # a1.logX = lambda: print("Hello 2:" )

# # a1.logX()

# try:
#   print(x)
# except NameError:
#   print("Variable x is not defined")
#   raise Exception("Newwwww")
# except Exception as e:
#   print('Exception Here here here')
#   print(e)
# else:
#   print("Something else went wrong")

class A:
    def __init__(self, x):
        self.x = x

    def logX(self):
        print(self.x)

a = A(100)
if (not None):
    print('None')


# import collections
# from azure.batch import models as _models
# _models.BatchTaskCollection()
# print(list(_models.BatchTaskCollection(value=[1,2,3])))