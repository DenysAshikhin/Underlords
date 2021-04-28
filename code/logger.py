class logger:
    def __init__(self, id):
        super().__init__()
        self.episodeName = id
        self.logDir = ""
        self.logFile = None

    def createLog(self):
        if not self.episodeName:
            print("w")
            # log
        self.logDir = "../logs/" + self.episodeName + ".txt"
        f = open(self.logDir, 'x')
        f.close()

    def writeLog(self, lines):
        try:
            with open(self.logDir, "a+") as f:
                for line in lines:
                    f.write("\n")
                    f.write(line)
        except IOError:
            print("Log")

        f.close()

    def readLog(self):
        try:
            with open(self.logDir, "r+") as f:
                line = f.readline().strip()
                while line:
                    line = f.readline()
                f.close()

        except IOError:
            print("Log")

        ### Two ways, line by line. Or read all at once and prcocess
        try:
            with open(self.logDir, "r+") as f:
                fileData = f.readlines()
            f.close()

            for line in fileData:
                line.strip()

        except IOError:
            print("Log")
