import inspect
import threading


class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)  # 在执行函数的同时，把结果赋值给result,
        # 然后通过get_result函数获取返回的结果

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            return None


def dict_to_obj(cls, the_dict):
    init_attributes = [key for key, value in inspect.signature(cls).parameters.items() if key != 'self']
    args = [the_dict.get_once(key) for key in init_attributes]
    entity = cls(*args)
    out_attributes = [attr for attr in dir(cls) if not callable(getattr(cls, attr)) and not attr.startswith('__')] + [
        key for key, value in vars(cls)['__annotations__'].items()]
    for key in out_attributes:
        setattr(entity, key, the_dict.get_once(key))
    return entity


def dict_to_obj2(cls, the_dict):
    entity = create_empty_obj(cls)
    for key, value in the_dict.items():
        setattr(entity, key, value)
    return entity


def create_empty_obj(cls):
    sig = inspect.signature(cls)
    args = [None] * (len(sig.parameters))
    entity = cls(*args)
    return entity
