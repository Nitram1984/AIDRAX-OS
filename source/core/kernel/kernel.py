from bootstrap import bootstrap

class AidraxKernel:
    def __init__(self):
        self.boot_report = None

    def start(self):
        self.boot_report = bootstrap()
        return self.boot_report

if __name__ == "__main__":
    kernel = AidraxKernel()
    print(kernel.start())
