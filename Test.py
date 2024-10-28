class Parent:
    def __init__(self,a ):
        # Initialize an attribute in the parent class
        self.test = a

    def move(self):
        # Increment the test attribute by 1
        self.test += 1


class Child(Parent):
    def __init__(self,a):
        # Initialize the parent class
        super().__init__(a)  # Corrected: Call super() without passing self


    # You can add new methods to the Child class here
    def new_method(self):
        super().move()
        super().move()

        print("This is a method only in the Child class")


# Create an instance of Parent
parent_instance = Parent(5)

print("Parent test value:", parent_instance.test)
parent_instance.move()
print("Parent test value after move:", parent_instance.test)

# Create an instance of Child
child_instance = Child(7)
print("Child test value:", child_instance.test)  # Inherited attribute from Parent
child_instance.move()  # Inherited method from Parent
print("Child test value after move:", child_instance.test)

# Call the unique method in Child
child_instance.new_method()
print("Child test value:", child_instance.test)  # Inherited attribute from Parent