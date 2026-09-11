from experta import Fact, KnowledgeEngine, Rule, NOT, OR, L, Field

class MemoryRequirement(Fact):
    pass

class OperationRequirement(Fact):
    pass

class StructSelector(KnowledgeEngine):
    @Rule(NOT(MemoryRequirement(name="size")), salience=10)
    def ask_size(self):
        self.declare(MemoryRequirement(name="size", value=input("Size (static/dynamic): ").lower()))

    @Rule(NOT(MemoryRequirement(name="continuity")), salience=10)
    def ask_continuity(self):
        self.declare(MemoryRequirement(name="continuity", value=input("Continuity (contiguous/fragmented): ").lower()))

    @Rule(NOT(OperationRequirement(name="access_type")), salience=10)
    def ask_access_type(self):
        self.declare(OperationRequirement(name="access_type", value=input("Access (random/sequential/key): ").lower()))

    @Rule(NOT(OperationRequirement(name="retrieval")), salience=10)
    def ask_retrieval(self):
        self.declare(OperationRequirement(name="retrieval", value=input("Retrieval (LIFO/FIFO/priority/any): ").lower()))

    @Rule(NOT(OperationRequirement(name="ordering")), salience=10)
    def ask_ordering(self):
        self.declare(OperationRequirement(name="ordering", value=input("Ordering (sorted/unsorted): ").lower()))

    @Rule(NOT(OperationRequirement(name="often_modification")), salience=10)
    def ask_often_modification(self):
        self.declare(OperationRequirement(name="often_modification", value=input("Modifications (beginning/middle/end/none): ").lower()))

    @Rule(
        MemoryRequirement(name="size"),
        MemoryRequirement(name="continuity"),
        OperationRequirement(name="access_type"),
        OperationRequirement(name="retrieval"),
        OperationRequirement(name="ordering"),
        OperationRequirement(name="often_modification"),
        NOT(Fact(ready=True)),
        salience=5
    )
    def input_finished(self):
        self.declare(Fact(ready=True))
    
    @Rule(Fact(ready=True), OperationRequirement(name="retrieval", value="lifo"))
    def rec_stack(self):
        print("\nRecommendation: STACK")

    @Rule(Fact(ready=True), OperationRequirement(name="retrieval", value="fifo"))
    def rec_queue(self):
        print("\nRecommendation: QUEUE")

    @Rule(Fact(ready=True), OperationRequirement(name="retrieval", value="priority"))
    def rec_heap(self):
        print("\nRecommendation: PRIORITY QUEUE (HEAP)")

    @Rule(Fact(ready=True), 
          OperationRequirement(name="access_type", value="key"),
          OperationRequirement(name="ordering", value="unsorted"))
    def rec_hash(self):
        print("\nRecommendation: HASH TABLE")

    @Rule(Fact(ready=True),
          OperationRequirement(name="access_type", value="key"),
          OperationRequirement(name="ordering", value="sorted"))
    def rec_tree(self):
        print("\nRecommendation: BALANCED SEARCH TREE")

    @Rule(Fact(ready=True),
          MemoryRequirement(name="size", value="static"),
          OperationRequirement(name="access_type", value="random"))
    def rec_array(self):
        print("\nRecommendation: STATIC ARRAY")

    @Rule(Fact(ready=True),
          MemoryRequirement(name="size", value="dynamic"),
          OR(MemoryRequirement(name="continuity", value="fragmented"),
             OperationRequirement(name="often_modification", value="beginning")))
    def rec_list(self):
        print("\nRecommendation: LINKED LIST")

    @Rule(Fact(ready=True),
          MemoryRequirement(name="size", value="dynamic"),
          MemoryRequirement(name="continuity", value="contiguous"),
          OperationRequirement(name="access_type", value="random"))
    def rec_dyn_array(self):
        print("\nRecommendation: DYNAMIC ARRAY (Vector/ArrayList)")

if __name__ == "__main__":
    engine = StructSelector()
    engine.reset()
    engine.run()