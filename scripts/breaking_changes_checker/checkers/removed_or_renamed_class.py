from models import ClassChangesChecker
import jsondiff

class RemovedOrRenamedClassChecker(ClassChangesChecker):
    name = "RemovedOrRenamedClass"
    message = "The model or publicly exposed class '{}.{}' was deleted or renamed in the current version"

    def __init__(self):
        super().__init__()

    def run_check(self, class_nodes, **kwargs):
        module_name = kwargs.get("module_name", None)
        stable_nodes = kwargs.get("previous_nodes", {})
        bc_list = []
        for class_name, class_components in class_nodes.items():
            self.class_name = class_name
            if isinstance(class_name, jsondiff.Symbol):
                deleted_classes = []
                if self.class_name.label == "delete":
                    deleted_classes = class_components
                elif self.class_name.label == "replace":
                    deleted_classes = stable_nodes[module_name]["class_nodes"]
                
                for name in deleted_classes:
                    if name.endswith("Client"):
                        bc = (
                            "The client '{}.{}' was deleted or renamed in the current version",
                            "RemovedOrRenamedClient",
                            module_name, name
                        )
                    else:
                        bc = (
                            self.message,
                            self.name,
                            module_name, name
                        )
                    bc_list.append(bc)
        return bc_list