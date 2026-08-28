from .pipeline import RuntimePipeline

class RuntimeEngine:
    def __init__(self,pipeline:RuntimePipeline):
        self.pipeline=pipeline

    def run(self, capability:str, payload:dict):
        return self.pipeline.process(capability,payload)
