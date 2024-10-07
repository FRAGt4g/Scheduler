class Student:
    def __init__(self, id, hidden_component):
        self.id = id
        self.hidden_component = hidden_component

class QuickList:
    def __init__(self):
        self.objects = []
        self.index_map = {}

    def append(self, obj: Student):
        self.index_map[obj.id] = len(self.objects)
        self.objects.append(obj)

    def get_hidden_component(self, id):
        index = self.index_map.get(id)
        if index is not None:
            return self.objects[index].hidden_component
        else:
            return None

# Example usage
manager = QuickList()
obj1 = Student('obj1', 'hidden1')
obj2 = Student('obj2', 'hidden2')

manager.append(obj1)
manager.append(obj2)

print(manager.get_hidden_component('obj1'))  # Output: hidden1
print(manager.get_hidden_component('obj2'))  # Output: hidden2
print(manager.get_hidden_component('obj3'))  # Output: None