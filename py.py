

def physics_book(func):
    def wrapper(*args,**kwargs):
        return func(*args,**kwargs)
    return wrapper



@physics_book
def library(author , **details):
    print("i want books")
    print(f"a physics book from {author}")
    print(details)


library("mf" , height = 25 , width = 15)
print(...)


    
