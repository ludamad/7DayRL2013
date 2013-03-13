
class StatusType:
    def __init__(self, name, add_action, remove_action, step_action=None, duration=None, remove_criteria=None):
        self.name = name
        self.add_action = add_action
        self.remove_action = remove_action
        self.duration = duration
        self.step_action = step_action
        self.remove_criteria = remove_criteria

class Status:
    def __init__(self, type):
        self.type = type
        self.duration = type.duration
        self.removed = False
    def add(self, owner):
        self.type.add_action(owner)
    def remove(self, owner):
        if self.removed: 
            return
        self.type.remove_action(owner)
        self.removed = True
    def step(self, owner):
        if not self.removed and self.step_action:
            self.step_action(owner)

        if self.type.remove_criteria and self.type.remove_criteria(owner):
            self.remove(owner)
        elif self.duration:
            self.duration -= 1
            if self.duration <= 0:
                self.remove(owner)

class Statuses:
    def __init__(self):
        self.statuses = []
    def remove_status(self, owner, status_type):
        for status in self:
            if status.type == status_type:
                status.remove(owner)
        return None
    def has_status(self, status_type):
        for status in self:
            if status.type == status_type:
                return status
        return None
    def step(self, owner):
        for status in self: 
            status.step(owner)
        self.statuses = filter(lambda status: not status.removed, self.statuses)
    def add_status(self, owner, status_type):
        status = self.has_status(status_type)
        if status:
            status.duration = status_type.duration
        else:
            status = Status(status_type)
            status.add(owner)
            self.statuses.append(status)
    def __iter__(self):
        return iter(self.statuses)
    def __getitem__(self, idx):
        return self.statuses[idx]
