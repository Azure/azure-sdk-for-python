The creation of the fl scatter gather node has several implmentation details that need to be figured out.
For the sake of transparency and sanity, I'll be implmenting a series of nodes that try to achieve these
goals sequentially. The implementation goals of the nodes will be as follows:

- 1: Use the Run an injected component inside a node, using the @pipeline decorator or not.
- 2: As 1, but have 2 injected components inside the node
- 3: As 2, but have the second components consume inputs from the outputs of the first
- 4: As 1, but have the component make use of an inputted compute, datastore, and data input that are potentially different from outer pipeline
- 5: As 1, but run the injected component an a specified number of times
- 6: As 5, but feed the input of one iteration back into subsequent runs of the injected code
- 7: Have the ouputs from multiple pipelines feed into a single pipeline.
- 8: Put everything together
- 9: Make robust datastore/compute injection that works on complex components that call/have sub-components (Jeff did this somehow, talk to him or Amit?)