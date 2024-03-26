# Класс для узла списка состояний
class StateNode:
    def __init__(self, state):
        self.state = state
        self.prev_node = None


# Класс для односвязного списка состояний
class StateLinkedList:
    def __init__(self):
        self.head = None

    def add_state(self, state):
        new_node = StateNode(state)
        new_node.prev_node = self.head
        self.head = new_node

    def get_current_state(self):
        if self.head:
            return self.head.state
        else:
            return None

    def go_back(self):
        if self.head:
            self.head = self.head.prev_node

    def get_current_state_str(self) -> str:
        current_state = self.get_current_state()
        if current_state:
            current_state_str = str(current_state)[8:-2]
            return current_state_str

    def get_state_list(self) -> list:
        state_list = []
        current_node = self.head
        while current_node:
            state_list.append(current_node.state)
            current_node = current_node.prev_node
        return state_list
