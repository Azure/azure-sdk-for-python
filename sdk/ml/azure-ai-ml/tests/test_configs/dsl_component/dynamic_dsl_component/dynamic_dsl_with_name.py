from mldesigner import command_component

from source_func import train_func

component1 = command_component(name="my_train")(train_func)
component2 = command_component(name="my_train1")(train_func)
